from __future__ import annotations

import copy
import asyncio
import hashlib
import json
import math
import threading
import time
from collections import OrderedDict
from contextlib import asynccontextmanager, contextmanager, suppress
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import ROOT, Settings, settings
from app.knowledge import KnowledgeStore
from app.providers import AIRecognizer, ProviderError, WikipediaProvider
from app.recognition import Recognizer, validate_text
from app.summary import Summarizer
from app.study_quiz import StudyQuiz


class AnalysisRequest(BaseModel):
    text: str = Field(max_length=1_000_000)
    use_ai: bool = False
    summarize_with_ai: bool = False
    generate_quiz: bool = False
    session_id: str = Field(default="local", max_length=64, pattern=r"^[a-zA-Z0-9-]+$")
    material_id: str | None = Field(default=None, max_length=64, pattern=r"^[a-zA-Z0-9-]+$")
    material_title: str = Field(default="", max_length=200)


class QuizRequest(BaseModel):
    answer: int = Field(ge=0, le=10)


def public_card(card):
    result = copy.deepcopy(card)
    if result.get("question"):
        result["question"].pop("answer", None)
        result["question"].pop("feedback", None)
    location = result.get("location")
    if location:
        lat, lon = location["lat"], location["lon"]
        if not all(isinstance(v, (float, int)) and math.isfinite(v) for v in (lat, lon)):
            result["location"] = None
        else:
            location["osm_url"] = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map={location.get('zoom', 5)}/{lat}/{lon}"
            location["earth_url"] = f"https://earth.google.com/web/search/{lat},{lon}"
    return result


def create_app(config: Settings | None = None):
    config = config or settings
    store = KnowledgeStore(config.database)
    recognizer = Recognizer(store.records)
    ai = AIRecognizer(config)
    summarizer = Summarizer(config)
    study_quiz = StudyQuiz(config)
    wiki = WikipediaProvider()
    cache = OrderedDict()
    lock = threading.Lock()
    request_locks = [threading.Lock() for _ in range(64)]
    capacity = threading.BoundedSemaphore(8)

    @contextmanager
    def work_slot(key):
        # Same submissions share a lock; independent students can run concurrently.
        index = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % len(request_locks)
        with request_locks[index]:
            if not capacity.acquire(timeout=20):
                raise HTTPException(503, "The class is submitting several readings at once. Please try again in a moment; your material is still in the form.")
            try:
                yield
            finally:
                capacity.release()

    def cached_result(key):
        with lock:
            now = time.monotonic()
            for old in list(cache):
                if now - cache[old][0] > 600:
                    del cache[old]
            if key not in cache:
                return None
            result = copy.deepcopy(cache[key][1])
            result["usage"] = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0, "tool_requests": 0, "cache_hit": True, "estimated_cost_usd": 0}
            return result

    def remember_result(key, result):
        with lock:
            cache[key] = (time.monotonic(), copy.deepcopy(result))
            while len(cache) > 32:
                cache.popitem(last=False)

    @asynccontextmanager
    async def lifespan(app):
        async def expire_results():
            while True:
                await asyncio.sleep(30)
                if lock.acquire(blocking=False):
                    try:
                        for key in list(cache):
                            if time.monotonic() - cache[key][0] > 600:
                                del cache[key]
                    finally:
                        lock.release()
        task = asyncio.create_task(expire_results())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            cache.clear()

    app = FastAPI(title="Geography Learning Agent", docs_url="/api/docs", redoc_url=None, lifespan=lifespan)
    app.state.store, app.state.ai, app.state.wiki = store, ai, wiki
    app.state.summarizer = summarizer
    app.state.study_quiz = study_quiz

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        size = request.headers.get("content-length", "0")
        if size.isdigit() and int(size) > 6_100_000:
            return JSONResponse({"detail": "The request is too large."}, status_code=413)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-src https://www.openstreetmap.org; object-src 'none'; base-uri 'self'; form-action 'self'"
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store"
        elif request.url.path == "/" or (request.url.path.startswith("/static/") and request.url.path.endswith(".js")):
            response.headers["Cache-Control"] = "no-cache"
        return response

    @app.get("/api/status")
    def status():
        return {"name": "Geography Learning Agent", "knowledge_count": len(store.records), "ai_available": bool(config.api_key), "online_enabled": config.online, "version": "0.1.0"}

    @app.get("/api/demo-materials")
    def demo_materials():
        return {"materials": json.loads((ROOT / "data" / "demo-materials" / "manifest.json").read_text(encoding="utf-8"))}

    @app.get("/api/demo-materials/{identifier}")
    def demo_material(identifier: str):
        manifest = demo_materials()["materials"]
        entry = next((item for item in manifest if item["id"] == identifier), None)
        if not entry:
            raise HTTPException(404, "This demo material is unavailable.")
        text = (ROOT / "data" / "demo-materials" / entry["filename"]).read_text(encoding="utf-8-sig")
        return {**entry, "text": text}

    @app.post("/api/analyze")
    def analyze(body: AnalysisRequest):
        try:
            validate_text(body.text, store.records)
        except ValueError as e:
            raise HTTPException(422, str(e))
        if body.use_ai and not config.api_key:
            raise HTTPException(409, "AI assistance is not configured. Turn it off to use local recognition.")
        key = hashlib.sha256((body.session_id + str(body.use_ai) + str(body.summarize_with_ai) + str(body.generate_quiz) + body.text + body.material_title + (body.material_id or "")).encode()).hexdigest()
        with work_slot(key):
            cached = cached_result(key)
            if cached is not None:
                return cached
            started = time.perf_counter()
            current_recognizer = recognizer
            mentions = current_recognizer.recognize(body.text)
            warnings = []
            usage = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0}
            if body.use_ai:
                discoveries, usage, warning = ai.extract(body.text)
                mentions = current_recognizer.merge_ai(body.text, mentions, discoveries)
                if warning: warnings.append(warning)
            source_requests = 0
            with ThreadPoolExecutor(max_workers=2) as executor:
                quiz_future = executor.submit(study_quiz.generate, body.text, body.use_ai and body.generate_quiz)
                if body.use_ai and body.summarize_with_ai:
                    summary, summary_usage = summarizer.summarize(body.text, True)
                else:
                    summary = {"text": "", "kind": "disabled", "word_count": 0, "warning": None}
                    summary_usage = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0}
                quiz, quiz_usage = quiz_future.result()
            for field in ("model_calls", "input_tokens", "output_tokens"):
                usage[field] += summary_usage[field]
            if summary_usage.get("unaccounted_calls"):
                usage["unaccounted_calls"] = 1
            for field in ("model_calls", "input_tokens", "output_tokens"):
                usage[field] += quiz_usage[field]
            if quiz_usage.get("unaccounted_calls"):
                usage["unaccounted_calls"] = 1
            if body.generate_quiz and quiz["warning"]:
                warnings.append(quiz["warning"])
            for mention in mentions:
                mention.pop("py_start", None)
                mention.pop("py_end", None)
            cost = 0 if not usage["model_calls"] else None
            if config.input_price and config.output_price and usage["model_calls"] and not usage.get("unaccounted_calls"):
                try: cost = (usage["input_tokens"] * float(config.input_price) + usage["output_tokens"] * float(config.output_price)) / 1_000_000
                except ValueError: pass
            result = {"mentions": mentions, "summary": summary, "ai_enabled": body.use_ai, "study_quiz": quiz, "warnings": warnings,
                      "word_count": len(body.text.split()), "duration_ms": round((time.perf_counter()-started)*1000), "usage": {**usage, "tool_requests": source_requests, "cache_hit": False, "estimated_cost_usd": cost}}
            if not warnings:
                remember_result(key, result)
            return result

    @app.get("/api/search")
    def search(q: str = Query(min_length=2, max_length=120)):
        return {"results": store.search(q)}

    @app.post("/api/study-quiz")
    def generate_study_quiz(body: AnalysisRequest):
        try:
            validate_text(body.text, store.records)
        except ValueError as error:
            raise HTTPException(422, str(error))
        if not config.api_key:
            raise HTTPException(409, "AI is not configured. Concept learning is still available.")
        key = "quiz:" + hashlib.sha256((body.session_id + body.text).encode()).hexdigest()
        with work_slot(key):
            cached = cached_result(key)
            if cached is not None:
                return cached
            quiz, usage = study_quiz.generate(body.text, True)
            cost = None
            if config.input_price and config.output_price and not usage.get("unaccounted_calls"):
                try: cost = (usage["input_tokens"] * float(config.input_price) + usage["output_tokens"] * float(config.output_price)) / 1_000_000
                except ValueError: pass
            result = {"quiz": quiz, "usage": {**usage, "estimated_cost_usd": cost, "cache_hit": False}}
            if quiz["kind"] == "ai":
                remember_result(key, result)
            return result

    @app.get("/api/library")
    def library(q: str = Query(default="", max_length=120),
                category: Literal["all", "country", "place", "physical", "climate", "landform", "process", "concept", "human"] = "all",
                page: int = Query(default=1, ge=1), page_size: int = Query(default=30, ge=1, le=60)):
        query = q.strip().casefold()
        categories = {}
        for record in store.records:
            categories[record["category"]] = categories.get(record["category"], 0) + 1
        matches = [r for r in store.records if (category == "all" or r["category"] == category)
                   and (not query or any(query in a.casefold() for a in r["aliases"])
                        or query in r["definition"].casefold())]
        matches.sort(key=lambda r: (bool(query) and r["title"].casefold() != query, r["title"].casefold(), r["id"]))
        pages = max(1, math.ceil(len(matches) / page_size))
        current = min(page, pages)
        start = (current - 1) * page_size
        return {"total": len(matches), "library_total": len(store.records), "categories": categories,
                "page": current, "pages": pages, "page_size": page_size,
                "results": [{"id": r["id"], "title": r["title"], "category": r["category"],
                             "preview": r["definition"][:180], "materials": r.get("materials", [])}
                            for r in matches[start:start + page_size]]}

    @app.get("/api/card")
    def card(id: str = Query(min_length=1, max_length=180),
             material_id: str | None = Query(default=None, max_length=64, pattern=r"^[a-zA-Z0-9-]+$"),
             material_title: str = Query(default="", max_length=200)):
        record, origin = store.get(id)
        if record:
            return {"card": public_card(record), "retrieval": {"origin": origin, "tool_requests": 0, "model_calls": 0}}
        if not id.startswith("remote:"):
            raise HTTPException(404, "This concept is not in the local knowledge collection.")
        if not config.online:
            raise HTTPException(503, "Online lookup is disabled. Try a term from the local collection.")
        title = id.removeprefix("remote:")
        if not title.strip() or any(c in title for c in "|\n\r") or ":" in title or len(title) > 120:
            raise HTTPException(422, "Please use a plain encyclopedia article name.")
        try:
            record = wiki.fetch(title)
        except ProviderError as e:
            raise HTTPException(503, str(e))
        tool_requests = record.pop("_tool_requests", len(record["sources"]))
        store.save(id, record)
        return {"card": public_card(record), "retrieval": {"origin": "online", "tool_requests": tool_requests, "model_calls": 0}}

    @app.post("/api/quiz")
    def quiz(body: QuizRequest, id: str = Query(max_length=180)):
        record, _ = store.get(id)
        question = record.get("question") if record else None
        if not question or body.answer >= len(question["options"]):
            raise HTTPException(404, "This question or answer is unavailable.")
        return {"correct": body.answer == question["answer"], "answer": question["answer"], "feedback": question["feedback"]}

    @app.get("/api/world")
    def world():
        return FileResponse(ROOT / "data" / "world.geojson", media_type="application/geo+json")

    @app.get("/")
    def home():
        built = ROOT / "app" / "static" / "ui" / "index.html"
        return FileResponse(built if built.exists() else ROOT / "app" / "static" / "legacy-index.html")

    app.mount("/static", StaticFiles(directory=ROOT / "app" / "static"), name="static")
    return app


app = create_app()
