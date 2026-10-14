"""Demo reading and online Saved acceptance / 内置材料与在线收藏验收。"""
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)


def main():
    manifest = json.loads((ROOT / "data/demo-materials/manifest.json").read_text(encoding="utf-8"))
    online = dict(next(card for card in json.loads((ROOT / "data/knowledge.json").read_text(encoding="utf-8")) if card["id"] == "wiki:Glacier"),
                  id="remote:Pingo", title="Pingo", aliases=["Pingo"], definition="A pingo is an ice-cored hill in a permafrost landscape.")
    online.pop("question", None)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1050})
        errors, requests = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append(request.url) if "/api/analyze" in request.url else None)
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        page.locator("#material-dialog .close-dialog").click()
        page.locator("#new-material").click()
        expect(page.locator("#demo-material option")).to_have_count(11)
        expect(page.locator("#load-demo-material")).to_be_disabled()
        assert page.locator("#demo-material").evaluate("e => { const s = getComputedStyle(e); return e.clientHeight - parseFloat(s.paddingTop) - parseFloat(s.paddingBottom) >= parseFloat(s.fontSize) * 1.5; }")
        before = len(requests)
        for material in manifest:
            page.locator("#demo-material").select_option(material["id"])
            page.locator("#load-demo-material").click()
            expect(page.locator("#material-title")).to_have_value(material["title"])
            expected_text = (ROOT / "data/demo-materials" / material["filename"]).read_text(encoding="utf-8-sig")
            expect(page.locator("#material-text")).to_have_value(expected_text)
            expect(page.locator("#input-count")).to_have_text(f"{material['word_count']:,} words")
        assert len(requests) == before, "Choosing a demo must not trigger AI or analysis"
        page.locator("#demo-material").select_option(manifest[0]["id"])
        page.locator("#load-demo-material").click()
        expect(page.locator("#material-title")).to_have_value(manifest[0]["title"])
        page.screenshot(path=str(OUT / "demo-materials-desktop.png"))
        page.locator("#use-ai").uncheck()
        page.locator("#material-mode").select_option("explore")
        page.locator("#analyze-button").click()
        expect(page.locator("#material-dialog")).not_to_be_visible(timeout=20000)
        expect(page.locator("#history-count")).to_have_text("1")
        assert "Source URL:" in page.locator("#passage").inner_text()
        assert page.locator(".mention").count() > 0
        assert len(page.locator("#material-summary").inner_text().split()) <= 50

        # Mock a newly discovered online term: no paid requests are made.
        page.route("**/api/analyze", lambda route: route.fulfill(json={
            "mentions": [{"id": "remote:Pingo", "text": "pingo", "title": "Pingo", "category": "landform", "kind": "explicit", "confidence": .95, "start": 2, "end": 7}],
            "summary": {"text": "An ice-cored hill forms in permafrost.", "kind": "local", "word_count": 7},
            "warnings": [], "word_count": 8, "duration_ms": 1,
            "usage": {"model_calls": 0, "input_tokens": 0, "output_tokens": 0, "tool_requests": 0, "cache_hit": False, "estimated_cost_usd": 0}
        }))
        page.route("**/api/card?id=remote%3APingo", lambda route: route.fulfill(json={"card": online, "retrieval": {"origin": "online", "tool_requests": 1, "model_calls": 0}}))
        page.locator("#new-material").click()
        page.locator("#material-title").fill("Frozen landscapes")
        page.locator("#material-mode").select_option("explore")
        page.locator("#material-text").fill("A pingo forms in a cold permafrost landscape.")
        page.locator("#analyze-button").click()
        expect(page.locator("#material-dialog")).not_to_be_visible()
        page.locator(".mention").filter(has_text="pingo").click()
        page.get_by_role("button", name="Save Pingo", exact=True).click()
        expect(page.locator("#saved-count")).to_have_text("1")
        assert not any(r["id"] == "remote:Pingo" for r in page.request.get("http://127.0.0.1:8000/api/library?q=Pingo").json()["results"])
        page.reload(wait_until="networkidle")
        page.locator("#material-dialog .close-dialog").click()
        # Reopening a complete Saved snapshot must work with all card lookups blocked.
        page.unroute("**/api/card?id=remote%3APingo")
        page.route("**/api/card?**", lambda route: route.abort())
        page.locator("#saved-button").click()
        page.get_by_role("button", name="Open Pingo", exact=True).click()
        expect(page.locator(".card-title")).to_have_text("Pingo")
        expect(page.locator("#card-view .card-definition")).to_have_text(online["definition"])
        assert page.locator(".source-item a").count() > 0
        expect(page.get_by_role("button", name="Unsave Pingo", exact=True)).to_be_visible()
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#new-material").click()
        page.locator("#demo-material").select_option(manifest[0]["id"])
        page.locator("#load-demo-material").click()
        expect(page.locator("#material-title")).to_have_value(manifest[0]["title"])
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert page.locator("#material-dialog").evaluate("e => e.scrollWidth <= e.clientWidth")
        page.screenshot(path=str(OUT / "demo-materials-mobile.png"))
        assert errors == [], errors
        browser.close()
        print(json.dumps({"demo_materials": 10, "saved_online_snapshot": "passed", "mobile": "passed", "page_errors": errors, "paid_model_calls": 0}))


if __name__ == "__main__":
    main()
