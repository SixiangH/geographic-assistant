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


def test_sample_round_trip_and_local_cards(client):
    sample = client.get("/api/sample").json()
    result = analyze(client, sample["text"])
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
    assert 300 <= len(records) <= 500
    for record in records:
        assert record["definition"] and record["sources"]
        assert all(source["url"].startswith("https://") for source in record["sources"])
        assert all(rel["id"] in ids for rel in record["relations"])


def test_model_http_error_does_not_leak_secrets(monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ConnectError("secret-key-do-not-expose")
    monkeypatch.setattr(httpx.Client, "post", fail)
    mentions, usage, warning = AIRecognizer(Settings(api_key="secret-key")).extract("France has an oceanic climate.")
    assert mentions == [] and usage["model_calls"] == 1
    assert "secret" not in warning


def test_wikipedia_disambiguation_is_unavailable(monkeypatch):
    payload = {"query": {"pages": [{"title": "Test", "pageprops": {"disambiguation": ""}, "extract": "A list of meanings"}]}}
    monkeypatch.setattr(httpx.Client, "get", lambda *a, **kw: httpx.Response(200, json=payload, request=httpx.Request("GET", "https://en.wikipedia.org/")))
    with pytest.raises(ProviderError):
        WikipediaProvider().fetch("Test")
