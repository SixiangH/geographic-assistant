import httpx
import pytest

from app.providers import ProviderError, WikipediaProvider


def test_official_summary_fallback_preserves_source_and_location(monkeypatch):
    requests = []

    def get(client, url, **kwargs):
        requests.append(url)
        if url.endswith('/w/api.php'):
            return httpx.Response(503, request=httpx.Request('GET', url))
        return httpx.Response(200, json={
            'type': 'standard', 'title': 'Pingo', 'extract': 'An ice-cored hill in permafrost.',
            'revision': '123', 'timestamp': '2026-01-01T00:00:00Z',
            'coordinates': {'lat': 69.4, 'lon': -133.0},
            'content_urls': {'desktop': {'page': 'https://en.wikipedia.org/wiki/Pingo'}},
        }, request=httpx.Request('GET', url))

    monkeypatch.setattr(httpx.Client, 'get', get)
    card = WikipediaProvider().fetch('Pingo')
    assert len(requests) == card['_tool_requests'] == 2
    assert card['definition'] == 'An ice-cored hill in permafrost.'
    assert card['sources'][0]['revision'] == '123'
    assert card['sources'][0]['url'] == 'https://en.wikipedia.org/wiki/Pingo'
    assert card['location']['lat'] == 69.4


def test_summary_disambiguation_is_not_presented_as_definition(monkeypatch):
    def get(client, url, **kwargs):
        return httpx.Response(503 if url.endswith('/w/api.php') else 200,
                              json={'type': 'disambiguation'}, request=httpx.Request('GET', url))
    monkeypatch.setattr(httpx.Client, 'get', get)
    with pytest.raises(ProviderError, match='no single verified article'):
        WikipediaProvider().fetch('Test')
