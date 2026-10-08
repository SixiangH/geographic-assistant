"""Browser acceptance checks / 浏览器验收检查. Run against the local server."""
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)


def main():
    with sync_playwright() as p:
        chrome = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
        browser = p.chromium.launch(executable_path=str(chrome) if chrome.exists() else None, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        page.locator(".card-title").filter(has_text="Oceanic climate").wait_for()
        assert page.locator(".mention").count() >= 15
        sample = page.request.get("http://127.0.0.1:8000/api/sample").json()["text"]
        assert page.locator("#passage").inner_text() == sample
        page.screenshot(path=str(OUT / "desktop.png"), full_page=True)
        page.get_by_role("button", name="A. Mild temperatures with rainfall throughout the year", exact=True).click()
        page.locator(".quiz-feedback").filter(has_text="That's right").wait_for()
        page.get_by_role("button", name="Places", exact=True).click()
        assert page.locator(".mention").count() < 15
        assert page.locator("#passage").inner_text() == sample
        page.get_by_label("Highlights", exact=True).uncheck()
        assert page.locator(".mention").count() == 0
        assert page.locator("#passage").inner_text() == sample
        page.get_by_label("Highlights", exact=True).check()
        page.get_by_role("button", name="All concepts", exact=True).click()
        page.locator(".mention").filter(has_text="France").first.click()
        page.locator(".card-title").filter(has_text="France").wait_for()
        page.get_by_role("tab", name="Locate").click()
        assert page.locator(".world-map .map-land.selected").count() == 1
        assert "France" in page.locator(".world-map").get_attribute("aria-label")
        page.get_by_role("button", name="Zoom in", exact=True).click()
        assert page.locator(".world-map").get_attribute("viewBox") != "0 0 720 360"
        assert page.get_by_role("link", name="Explore in Google Earth").get_attribute("href").startswith("https://earth.google.com/")

        page.get_by_role("button", name="New material", exact=False).click()
        text = "Georgia and Congo have different geographical meanings. The Amazon River flows through Brazil.\n\n<img src=x onerror=alert(1)> Erosion shapes the landscape."
        page.get_by_label("Learning material", exact=True).fill(text)
        page.get_by_label("Lesson title", exact=False).fill("A new geography lesson")
        page.get_by_role("button", name="Explore this reading", exact=False).click()
        page.locator("#material-dialog").wait_for(state="hidden")
        assert page.locator("#passage").inner_text() == text
        assert page.locator("#passage img").count() == 0
        page.locator(".mention").filter(has_text="Georgia").click()
        page.get_by_role("button", name="Georgia (country)", exact=False).click()
        page.locator(".card-title").filter(has_text="Georgia (country)").wait_for()
        assert page.locator("#passage").inner_text() == text

        page.get_by_role("button", name="New material", exact=False).click()
        page.get_by_label("Learning material", exact=True).fill("这是一篇中文地理课文。")
        page.get_by_role("button", name="Explore this reading", exact=False).click()
        page.locator("#material-error").wait_for(state="visible")
        assert "English" in page.locator("#material-error").inner_text()
        page.locator("#material-file").set_input_files({"name": "rivers.txt", "mimeType": "text/plain", "buffer": b"The Nile is a river in Africa. Erosion and weathering shape its landscape."})
        assert page.get_by_label("Lesson title", exact=False).input_value() == "rivers"
        page.get_by_role("button", name="Explore this reading", exact=False).click()
        page.locator("#material-dialog").wait_for(state="hidden")
        assert "The Nile" in page.locator("#passage").inner_text()

        page.get_by_label("Search the geography library").fill("water cycle")
        page.locator(".search-result").filter(has_text="Water cycle").first.click()
        page.locator(".card-title").filter(has_text="Water cycle").wait_for()
        page.get_by_role("tab", name="Connect").click()
        assert page.locator(".connection-row").count() == 4
        page.locator(".related-button").filter(has_text="Evaporation").click()
        page.locator(".card-title").filter(has_text="Evaporation").wait_for()

        page.set_viewport_size({"width": 390, "height": 844})
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        page.locator(".card-title").filter(has_text="Oceanic climate").wait_for()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.screenshot(path=str(OUT / "mobile.png"), full_page=True)
        page.get_by_role("button", name="New material", exact=False).click()
        assert page.locator("#material-dialog").is_visible()
        page.screenshot(path=str(OUT / "mobile-dialog.png"), full_page=True)
        # Server configuration changes must refresh without losing the passage.
        original_text = page.locator("#passage").inner_text()
        availability = {"enabled": False}
        page.route("**/api/status", lambda route: route.fulfill(json={"knowledge_count": 393, "ai_available": availability["enabled"], "online_enabled": True}))
        page.evaluate("window.dispatchEvent(new Event('focus'))")
        expect(page.locator("#use-ai")).to_be_disabled()
        availability["enabled"] = True
        page.get_by_role("button", name="Close material dialog").click()
        page.get_by_role("button", name="New material", exact=False).click()
        expect(page.locator("#use-ai")).to_be_enabled()
        page.locator("#use-ai").check()
        assert page.locator("#use-ai").is_checked()
        page.locator("#use-ai").uncheck()
        assert page.locator("#passage").inner_text() == original_text
        assert errors == [], errors
        browser.close()
        print(json.dumps({"browser_checks": "passed", "page_errors": errors, "screenshots": ["desktop.png", "mobile.png", "mobile-dialog.png"]}))


if __name__ == "__main__":
    main()
