import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import ROOT, Settings
from app.main import create_app
from app.providers import AIRecognizer, ProviderError, WikipediaProvider
from app.recognition import Recognizer, validate_text


@pytest.fixture
def app(tmp_path):
    return create_app(Settings(database=tmp_path / "test.db", api_key="", online=False))


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


def analyze(client, text, **extra):
    return client.post("/api/analyze", json={"text": text, "session_id": "test-session", **extra})


def test_material_round_trip_and_local_cards(client):
    assert client.get("/api/sample").status_code == 404
    result = analyze(client, "France has an oceanic climate. The Alps influence precipitation and the water cycle.")
    assert result.status_code == 200
    payload = result.json()
    assert any(m["id"] == "wiki:Oceanic climate" for m in payload["mentions"])
    assert payload["usage"]["model_calls"] == 0
    for mention in payload["mentions"]:
        if mention["id"]:
            card = client.get("/api/card", params={"id": mention["id"]}).json()["card"]
            assert card["sources"]
    assert payload["mentions"] == sorted(payload["mentions"], key=lambda m: m["start"])


@pytest.mark.parametrize("text", ["", "   ", "这是用于学习地理的中文课文，温带海洋性气候。", "La géographie étudie les paysages et les relations entre les humains et leur environnement.", "The climate is mild.\x00"])
def test_input_rejections(client, text):
    response = analyze(client, text)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


def test_word_and_size_limits(client):
    assert analyze(client, "climate " * 10001).status_code == 422
    assert analyze(client, "é" * 510000).status_code == 422


def test_short_known_term(client):
    assert analyze(client, "France").status_code == 200


def test_longest_phrase_and_no_substring_matches(app):
    recognizer = Recognizer(app.state.store.records)
    text = "The temperate oceanic climate is different from the Mediterranean climate. Unclimatic is not a term."
    mentions = recognizer.recognize(text)
    assert [m["text"] for m in mentions] == ["temperate oceanic climate", "Mediterranean climate"]
    assert all(a["end"] <= b["start"] for a, b in zip(mentions, mentions[1:]))


def test_utf16_spans_and_original_material(client):
    text = "🌍 France has an oceanic climate.\r\n\r\nThe Atlantic Ocean affects its weather."
    payload = analyze(client, text).json()
    encoded = text.encode("utf-16-le")
    for m in payload["mentions"]:
        assert encoded[m["start"] * 2:m["end"] * 2].decode("utf-16-le") == m["text"]
    france = next(m for m in payload["mentions"] if m["text"] == "France")
    assert france["start"] == 3


def test_ambiguities_are_not_arbitrarily_resolved(client):
    mentions = analyze(client, "Georgia, Congo and Amazon are names that require geographical context.").json()["mentions"]
    for term in ("Georgia", "Congo", "Amazon"):
        mention = next(m for m in mentions if m["text"] == term)
        assert mention["id"] is None
        assert len(mention["candidates"]) >= 2


def test_pronoun_us_is_not_a_country(client):
    mentions = analyze(client, "Help us understand climate and tell us about France.").json()["mentions"]
    assert not any(m["text"].lower() == "us" for m in mentions)


def test_session_cache_does_not_repeat_model_calls(client):
    first = analyze(client, "France has an oceanic climate.").json()
    second = analyze(client, "France has an oceanic climate.").json()
    assert not first["usage"]["cache_hit"]
    assert second["usage"]["cache_hit"]
    other = client.post("/api/analyze", json={"text": "France has an oceanic climate.", "session_id": "another"}).json()
    assert not other["usage"]["cache_hit"]


def test_ai_requires_configuration(client):
    response = analyze(client, "France has an oceanic climate.", use_ai=True)
    assert response.status_code == 409


def test_ai_inferred_span_and_failure_fallback(tmp_path, monkeypatch):
    app = create_app(Settings(database=tmp_path / "ai.db", api_key="not-a-real-key", online=False))
    monkeypatch.setattr(app.state.ai, "extract", lambda text: ([{"text": "rainfall throughout the year", "title": "Oceanic climate", "category": "climate", "kind": "inferred", "confidence": .9}], {"model_calls": 1, "input_tokens": 20, "output_tokens": 10}, None))
    with TestClient(app) as client:
        result = analyze(client, "This region has rainfall throughout the year.", use_ai=True).json()
        assert result["mentions"][0]["kind"] == "inferred"
        assert result["mentions"][0]["id"] == "wiki:Oceanic climate"
        cached = analyze(client, "This region has rainfall throughout the year.", use_ai=True).json()
        assert cached["usage"]["model_calls"] == 0
        monkeypatch.setattr(app.state.ai, "extract", lambda text: ([], {"model_calls": 1, "input_tokens": 0, "output_tokens": 0}, "AI assistance unavailable"))
        failure = analyze(client, "The climate of France is influenced by the ocean.", use_ai=True).json()
        assert failure["warnings"]
        assert any(m["id"] == "country:FRA" for m in failure["mentions"])


def test_invalid_ai_spans_are_ignored(app):
    recognizer = Recognizer(app.state.store.records)
    assert recognizer.merge_ai("France", [], [{"text": "Germany", "title": "Germany", "category": "country", "confidence": 1}]) == []
    assert recognizer.merge_ai("France", [], [{"text": "France", "title": "France", "category": "company", "confidence": 1}]) == []


def test_inferred_climate_cannot_replace_country_or_partial_overlap(app):
    recognizer = Recognizer(app.state.store.records)
    for text, phrase in [("France has rainfall throughout the year.", "France has rainfall throughout the year"),
                         ("Coastal erosion and rainfall occur here.", "erosion and rainfall")]:
        spans = recognizer.recognize(text)
        merged = recognizer.merge_ai(text, spans, [{"text": phrase, "title": "Oceanic climate",
                    "category": "climate", "kind": "inferred", "confidence": .95}])
        assert merged == spans


def test_quiz_answers_are_server_side(client):
    card = client.get("/api/card", params={"id": "wiki:Oceanic climate"}).json()["card"]
    assert "answer" not in card["question"]
    assert "feedback" not in card["question"]
    wrong = client.post("/api/quiz?id=wiki:Oceanic%20climate", json={"answer": 1}).json()
    assert wrong["correct"] is False
    right = client.post("/api/quiz?id=wiki:Oceanic%20climate", json={"answer": 0}).json()
    assert right["correct"] is True
    assert client.post("/api/quiz?id=wiki:Oceanic%20climate", json={"answer": 9}).status_code == 404


def test_country_population_year_map_and_sources(client):
    card = client.get("/api/card", params={"id": "country:FRA"}).json()["card"]
    population = next(f for f in card["facts"] if f["label"].startswith("Population"))
    assert population["year"] > 1900
    assert "https://earth.google.com/" in card["location"]["earth_url"]
    assert card["sources"][0]["license"] == "Public domain"


def test_online_disabled_and_unknown_id(client):
    assert client.get("/api/card?id=remote:Berlin").status_code == 503
    assert client.get("/api/card?id=missing").status_code == 404


def test_remote_card_cache_and_failure(tmp_path, monkeypatch):
    app = create_app(Settings(database=tmp_path / "online.db", online=True))
    card = dict(app.state.store.by_id["wiki:Oceanic climate"], id="remote:Test climate", origin="online")
    calls = []
    def fetch(title):
        calls.append(title)
        if title == "Unknown": raise ProviderError("Verified explanation unavailable")
        return card
    monkeypatch.setattr(app.state.wiki, "fetch", fetch)
    with TestClient(app) as client:
        first = client.get("/api/card?id=remote:Test%20climate").json()
        second = client.get("/api/card?id=remote:Test%20climate").json()
        assert first["retrieval"]["origin"] == "online"
        assert second["retrieval"]["origin"] == "cache"
        assert calls == ["Test climate"]
        assert client.get("/api/card?id=remote:Unknown").status_code == 503
        assert client.get("/api/card?id=remote:File:thing").status_code == 422


def test_search_world_and_security_headers(client):
    assert client.get("/api/search?q=oceanic").json()["results"][0]["id"] == "wiki:Oceanic climate"
    assert client.get("/api/world").json()["type"] == "FeatureCollection"
    response = client.get("/")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert client.get("/api/status").headers["cache-control"] == "no-store"


def test_seed_integrity():
    records = json.loads((ROOT / "data" / "knowledge.json").read_text(encoding="utf-8"))
    ids = {r["id"] for r in records}
    assert len(ids) == len(records)
    assert len(records) >= 393
    catalog = (ROOT / "data" / "additional-topics.txt").read_text(encoding="utf-8").splitlines()
    required = {"wiki:" + line.split("|", 1)[0] for line in catalog if line and not line.startswith("#")}
    assert required <= ids
    for record in records:
        assert record["definition"] and record["sources"]
        assert all(source["url"].startswith("https://") for source in record["sources"])
        assert all(rel["id"] in ids for rel in record["relations"])


def test_library_browses_every_local_record(client, app):
    first = client.get("/api/library?page_size=60").json()
    ids = []
    for page in range(1, first["pages"] + 1):
        response = client.get(f"/api/library?page_size=60&page={page}").json()
        ids.extend(r["id"] for r in response["results"])
    assert len(ids) == len(set(ids)) == len(app.state.store.records)
    assert set(ids) == set(app.state.store.by_id)
    assert sum(first["categories"].values()) == first["library_total"]
    assert client.get("/api/library?q=FORESTS&category=landform").json()["total"] > 0
    exact = client.get("/api/library?q=Lake").json()
    assert exact["results"][0]["title"] == "Lake"
    empty = client.get("/api/library?q=nosuchgeographyentry").json()
    assert empty["total"] == 0 and empty["results"] == []
    assert client.get("/api/library?page=99999&page_size=60").json()["page"] == first["pages"]
    for query in ["category=unknown", "page=0", "page_size=1000"]:
        assert client.get("/api/library?" + query).status_code == 422


def test_extended_geography_vocabulary_is_offline(client):
    text = "Forests and lakes support wetlands. Deforestation and soil erosion can affect groundwater. Reforestation, eutrophication, coastal erosion and sea-level rise are geography topics."
    result = analyze(client, text).json()
    ids = {m["id"] for m in result["mentions"]}
    expected = {"wiki:Forest", "wiki:Lake", "wiki:Wetland", "wiki:Deforestation",
                "wiki:Soil erosion", "wiki:Groundwater", "wiki:Reforestation",
                "wiki:Eutrophication", "wiki:Coastal erosion", "wiki:Sea level rise"}
    assert expected <= ids
    assert result["usage"]["model_calls"] == 0
    for identifier in expected:
        card = client.get("/api/card", params={"id": identifier}).json()["card"]
        assert card["definition"] and card["sources"][0]["revision"]
        assert card["origin"] == "local"
    assert "Soil erosion" in [r["title"] for r in client.get("/api/search?q=soil%20erosion").json()["results"]]


def test_model_http_error_does_not_leak_secrets(monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ConnectError("secret-key-do-not-expose")
    monkeypatch.setattr(httpx.Client, "post", fail)
    mentions, usage, warning = AIRecognizer(Settings(api_key="secret-key")).extract("France has an oceanic climate.")
    assert mentions == [] and usage["model_calls"] == 1
    assert "secret" not in warning


def test_online_discovery_stays_out_of_library_even_after_card_lookup(tmp_path, monkeypatch):
    config = Settings(database=tmp_path / "learn.db", api_key="mock-key", online=True)
    app = create_app(config)
    monkeypatch.setattr(app.state.ai, "extract", lambda text: ([{"text": "pingo", "title": "Pingo", "category": "landform", "kind": "explicit", "confidence": .95}], {"model_calls": 1, "input_tokens": 10, "output_tokens": 10}, None))
    calls = []
    def fetch(title):
        calls.append(title)
        return dict(app.state.store.by_id["wiki:Glacier"], id="remote:Pingo", title="Pingo", aliases=["Pingo"], _tool_requests=1)
    monkeypatch.setattr(app.state.wiki, "fetch", fetch)
    with TestClient(app) as client:
        response = analyze(client, "A pingo is a geographical landform.", use_ai=True, material_id="lesson-one", material_title="Frozen landscapes").json()
        assert response["usage"]["tool_requests"] == 0 and calls == []
        assert any(m["id"] == "remote:Pingo" for m in response["mentions"])
        card = client.get("/api/card?id=remote:Pingo&material_id=lesson-one&material_title=Frozen%20landscapes").json()["card"]
        assert "materials" not in card and card.get("origin") != "learned"
        assert not any(r["id"] == "remote:Pingo" for r in client.get("/api/library?q=Pingo").json()["results"])
        assert client.get("/api/search?q=Pingo").json()["results"] == []
        second = analyze(client, "A pingo is a geographical landform.", material_id="lesson-two", material_title="Ice and land").json()
        assert not any(m["id"] == "remote:Pingo" for m in second["mentions"])
        assert second["usage"]["model_calls"] == 0
        assert calls == ["Pingo"]
    restarted = create_app(Settings(database=config.database, api_key="", online=False))
    with TestClient(restarted) as client:
        card = client.get("/api/card?id=remote:Pingo").json()["card"]
        assert "materials" not in card
        assert client.get("/api/status").json()["knowledge_count"] == 711
        assert not any(r["id"] == "remote:Pingo" for r in client.get("/api/library?q=Pingo").json()["results"])


def test_failed_discovery_is_not_saved_and_can_retry(tmp_path, monkeypatch):
    app = create_app(Settings(database=tmp_path / "failure.db", api_key="mock-key", online=True))
    monkeypatch.setattr(app.state.ai, "extract", lambda text: ([{"text": "pingo", "title": "Pingo", "category": "landform", "kind": "explicit", "confidence": .95}], {"model_calls": 1, "input_tokens": 1, "output_tokens": 1}, None))
    def fail(title):
        raise ProviderError("Source temporarily unavailable")
    monkeypatch.setattr(app.state.wiki, "fetch", fail)
    with TestClient(app) as client:
        response = analyze(client, "A pingo is a geographical landform.", use_ai=True, material_id="failed-lesson").json()
        assert response["warnings"] == [] and response["usage"]["tool_requests"] == 0
        assert client.get("/api/card?id=remote:Pingo").status_code == 503
        assert not any(r["id"] == "remote:Pingo" for r in client.get("/api/library?q=Pingo").json()["results"])
        monkeypatch.setattr(app.state.wiki, "fetch", lambda title: dict(app.state.store.by_id["wiki:Glacier"], id="remote:Pingo", title="Pingo"))
        result = client.get("/api/card?id=remote:Pingo&material_id=failed-lesson&material_title=Retry%20lesson")
        assert result.status_code == 200 and "materials" not in result.json()["card"]
        assert not any(r["id"] == "remote:Pingo" for r in client.get("/api/library?q=Pingo").json()["results"])


def test_legacy_learned_records_are_excluded_without_erasing_database(tmp_path):
    import sqlite3
    database = tmp_path / "legacy.db"
    with sqlite3.connect(database) as con:
        con.execute("CREATE TABLE learned (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        con.execute("INSERT INTO learned VALUES (?, ?)", ("remote:Pingo", json.dumps({"id": "remote:Pingo", "title": "Pingo"})))
    with TestClient(create_app(Settings(database=database, online=False))) as client:
        assert client.get("/api/status").json()["knowledge_count"] == 711
        assert not any(r["id"] == "remote:Pingo" for r in client.get("/api/library?q=Pingo").json()["results"])
    with sqlite3.connect(database) as con:
        assert con.execute("SELECT COUNT(*) FROM learned").fetchone()[0] == 1


def test_bundled_demo_materials_are_complete_and_analyzable(client):
    materials = client.get("/api/demo-materials").json()["materials"]
    assert len(materials) == 10 and len({m["id"] for m in materials}) == 10
    for material in materials:
        response = client.get(f"/api/demo-materials/{material['id']}")
        assert response.status_code == 200
        payload = response.json()
        assert payload["text"] == (ROOT / "data/demo-materials" / material["filename"]).read_text(encoding="utf-8-sig")
        assert payload["word_count"] == len(payload["text"].split())
        assert "Source URL:" in payload["text"] and "License:" in payload["text"]
        analysis = analyze(client, payload["text"], material_id="demo-test", material_title=payload["title"])
        assert analysis.status_code == 200
        assert analysis.json()["mentions"]
        assert analysis.json()["summary"]["word_count"] <= 50
    assert client.get("/api/demo-materials/not-a-demo").status_code == 404


def test_summary_disabled_without_ai(client):
    for text in ["France", "Forests support biodiversity. Lakes store fresh water. Soil erosion affects landscapes.", "Geography " * 150 + "."]:
        payload = analyze(client, text).json()
        summary = payload["summary"]
        assert summary["text"] == "" and summary["kind"] == "disabled"
        assert summary["word_count"] == 0 and payload["ai_enabled"] is False
        assert payload["usage"]["model_calls"] == 0


def test_ai_summary_limit_usage_cache_and_failure(tmp_path, monkeypatch):
    from app.summary import Summarizer
    config = Settings(database=tmp_path / "summary.db", api_key="mock-key", online=False)
    app = create_app(config)
    monkeypatch.setattr(app.state.ai, "extract", lambda text: ([], {"model_calls": 1, "input_tokens": 10, "output_tokens": 5}, None))
    requests = []
    original_post = httpx.Client.post
    def answer(self, url, *args, **kwargs):
        if not str(url).startswith("https://api.openai.com/"):
            return original_post(self, url, *args, **kwargs)
        requests.append(kwargs["json"])
        return httpx.Response(200, json={"status": "completed", "usage": {"input_tokens": 20, "output_tokens": 150},
            "output": [{"content": [{"type": "output_text", "text": json.dumps({"summary": "Geography " * 130})}]}]},
            request=httpx.Request("POST", "https://api.openai.com/v1/responses"))
    monkeypatch.setattr(httpx.Client, "post", answer)
    with TestClient(app) as client:
        payload = analyze(client, "Forests support biodiversity and lakes store fresh water.", use_ai=True, summarize_with_ai=True).json()
        assert payload["summary"]["word_count"] <= 50 and payload["summary"]["kind"] == "ai"
        assert payload["usage"]["model_calls"] == 2 and payload["usage"]["input_tokens"] == 30
        cached = analyze(client, "Forests support biodiversity and lakes store fresh water.", use_ai=True, summarize_with_ai=True).json()
        assert cached["summary"] == payload["summary"] and cached["usage"]["model_calls"] == 0
        assert len(requests) == 1 and requests[0]["store"] is False
    monkeypatch.setattr(httpx.Client, "post", lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError("secret-token")))
    summary, usage = Summarizer(config).summarize("Forests support biodiversity.", True)
    assert summary["kind"] == "extractive" and summary["warning"] and "secret" not in summary["warning"]
    assert usage["model_calls"] == 1
    representative = Summarizer.representative_text("Forests cover land. " * 3000 + "Glaciers contain frozen water.")
    assert "Glaciers contain frozen water." in representative


def test_wikipedia_disambiguation_is_unavailable(monkeypatch):
    payload = {"query": {"pages": [{"title": "Test", "pageprops": {"disambiguation": ""}, "extract": "A list of meanings"}]}}
    monkeypatch.setattr(httpx.Client, "get", lambda *a, **kw: httpx.Response(200, json=payload, request=httpx.Request("GET", "https://en.wikipedia.org/")))
    with pytest.raises(ProviderError):
        WikipediaProvider().fetch("Test")


@pytest.mark.parametrize("status,code,expected", [
    (401, "invalid_api_key", "rejected the API key"),
    (403, "permission_denied", "permission"),
    (429, "insufficient_quota", "no available quota"),
    (429, "rate_limit_exceeded", "rate-limited"),
    (404, "model_not_found", "model is unavailable"),
    (500, "server_error", "temporarily unavailable"),
])
def test_ai_failure_reasons_are_actionable_and_secret_safe(tmp_path, monkeypatch, status, code, expected):
    from app.summary import Summarizer
    from app.providers import AIRecognizer
    config = Settings(database=tmp_path / "errors.db", api_key="secret-key", online=False)
    def answer(*args, **kwargs):
        return httpx.Response(status, json={"error": {"code": code, "message": "secret-key private-material"}},
            request=httpx.Request("POST", "https://api.openai.com/v1/responses"))
    monkeypatch.setattr(httpx.Client, "post", answer)
    summary, usage = Summarizer(config).summarize("Forests protect soil.", True)
    assert summary["kind"] == "extractive" and expected in summary["warning"]
    assert "secret-key" not in summary["warning"] and "private-material" not in summary["warning"]
    mentions, _, warning = AIRecognizer(config).extract("Forests protect soil.")
    assert not mentions and expected in warning and "secret-key" not in warning


@pytest.mark.parametrize("error,expected", [(httpx.ConnectError("secret-key"), "could not connect"),
                                           (httpx.ReadTimeout("secret-key"), "timed out")])
def test_ai_transport_failure_is_distinct(tmp_path, monkeypatch, error, expected):
    from app.summary import Summarizer
    config = Settings(database=tmp_path / "transport.db", api_key="secret-key", online=False)
    monkeypatch.setattr(httpx.Client, "post", lambda *a, **k: (_ for _ in ()).throw(error))
    summary, _ = Summarizer(config).summarize("Lakes store fresh water.", True)
    assert expected in summary["warning"] and "secret-key" not in summary["warning"]
