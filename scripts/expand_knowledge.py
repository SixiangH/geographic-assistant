"""Extend attributed offline topics / 扩充附来源的离线条目. No model calls / 不调用模型."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import httpx

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "additional-topics.txt"
KNOWLEDGE = ROOT / "data" / "knowledge.json"
API = "https://en.wikipedia.org/w/api.php"
UA = "GeographyLearningAgent/0.1 (educational source snapshots)"


def topics():
    result = []
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        title, category, aliases = line.split("|", 2)
        result.append((title, category, [a.strip() for a in aliases.split(";") if a.strip()]))
    if len({t[0] for t in result}) != len(result):
        raise ValueError("Duplicate catalog titles")
    return result


async def expand():
    records = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
    original_count = len(records)
    existing = {r["id"] for r in records}
    pending = [t for t in topics() if "wiki:" + t[0] not in existing]
    skipped = []
    cache = ROOT / ".runtime" / "topic-snapshots"
    cache.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=45, headers={"User-Agent": UA}, follow_redirects=True) as client:
        for offset in range(0, len(pending), 12):
            batch = pending[offset:offset + 12]
            params = {"action": "query", "format": "json", "formatversion": 2,
                      "prop": "extracts|coordinates|info|revisions|pageprops", "inprop": "url",
                      "exintro": 1, "explaintext": 1, "exlimit": 20,
                      "rvprop": "ids|timestamp", "redirects": 1,
                      "titles": "|".join(t[0] for t in batch)}
            snapshot = cache / (hashlib.sha256(params["titles"].encode()).hexdigest() + ".json")
            payload = json.loads(snapshot.read_text(encoding="utf-8")) if snapshot.exists() else None
            for attempt in range(8):
                if payload is not None:
                    break
                try:
                    response = await client.get(API, params=params)
                    if response.status_code == 429:
                        delay = max(15 * (attempt + 1), float(response.headers.get("Retry-After", "60")))
                        print(f"Source rate limit; retrying in {delay:.0f}s", flush=True)
                        await asyncio.sleep(delay)
                        response.raise_for_status()
                    response.raise_for_status()
                    payload = response.json()
                    if "error" in payload:
                        raise ValueError(payload["error"])
                    snapshot.write_text(json.dumps(payload), encoding="utf-8")
                    break
                except (httpx.HTTPError, ValueError):
                    payload = None
                    if attempt == 7:
                        raise
                    await asyncio.sleep(2 * (attempt + 1))
            query = payload.get("query", {})
            redirects = {x["from"]: x["to"] for x in query.get("redirects", []) + query.get("normalized", [])}
            pages = {p["title"]: p for p in query.get("pages", [])}
            for title, category, extra_aliases in batch:
                resolved = title
                for _ in range(8):
                    resolved = redirects.get(resolved, resolved)
                page = pages.get(resolved, {})
                revision = page.get("revisions", [{}])[0]
                excerpt = " ".join(page.get("extract", "").split()[:180])
                if "missing" in page or "disambiguation" in page.get("pageprops", {}) or not excerpt or not revision.get("revid"):
                    skipped.append(title)
                    continue
                url = page.get("fullurl", "https://en.wikipedia.org/wiki/" + quote(resolved.replace(" ", "_")))
                coords = page.get("coordinates", [])
                # Retain only editorial aliases, not a redirect's possibly broad canonical name.
                aliases = list(dict.fromkeys([title] + extra_aliases))
                display = re.sub(r" \([^)]*\)$", "", title)
                records.append({"id": "wiki:" + title, "title": display, "aliases": aliases,
                    "category": category, "definition": excerpt, "excerpt": excerpt,
                    "excerpt_label": "Wikipedia excerpt", "features": [], "examples": [],
                    "facts": [], "relations": [], "question": None,
                    "location": {"lat": coords[0]["lat"], "lon": coords[0]["lon"],
                                 "kind": "Representative point", "zoom": 4} if coords else None,
                    "sources": [{"title": "Wikipedia — " + resolved, "url": url,
                        "license": "CC BY-SA 4.0 (see article history)",
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        "revision": str(revision["revid"]), "revision_at": revision.get("timestamp"),
                        "wikidata_id": page.get("pageprops", {}).get("wikibase_item")}],
                    "origin": "local", "review_status": "source excerpt", "version": "1"})
            print(f"Fetched {min(offset + 12, len(pending))}/{len(pending)} topics", flush=True)
            await asyncio.sleep(2)
    # Link concepts literally mentioned in the source excerpt; no inferred causal claims.
    alias_owners = {}
    for r in records:
        for alias in r["aliases"]:
            alias_owners.setdefault(alias.casefold(), set()).add(r["id"])
    for r in records[original_count:]:
        for other in records:
            if other["id"] == r["id"] or other["category"] in {"country", "place"}:
                continue
            if any(len(a) >= 5 and len(alias_owners[a.casefold()]) == 1 and
                   re.search(r"(?<!\w)" + re.escape(a) + r"(?!\w)", r["excerpt"], re.I)
                   for a in other["aliases"]):
                r["relations"].append({"id": other["id"], "title": other["title"],
                    "label": "mentioned in source", "source_url": r["sources"][0]["url"]})
                if len(r["relations"]) == 6:
                    break
    # Commit only after all network batches succeed; preserve the existing library on failure.
    temp = KNOWLEDGE.with_suffix(".tmp")
    temp.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(KNOWLEDGE)
    print(f"Added {len(records) - original_count}; total {len(records)}; skipped {skipped}", flush=True)
    return skipped


if __name__ == "__main__":
    asyncio.run(expand())
