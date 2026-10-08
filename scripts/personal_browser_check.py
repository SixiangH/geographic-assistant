"""History and notebook acceptance tests / 历史与笔记本验收测试."""
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)


def upload(page, title, text):
    page.get_by_role("button", name="New material", exact=False).click()
    page.get_by_label("Lesson title", exact=False).fill(title)
    page.get_by_label("Learning material", exact=True).fill(text)
    page.locator("#use-ai").uncheck()
    page.get_by_role("button", name="Explore this reading", exact=False).click()
    expect(page.locator("#material-dialog")).not_to_be_visible()


def main():
    with sync_playwright() as p:
        chrome = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
        browser = p.chromium.launch(executable_path=str(chrome) if chrome.exists() else None, headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1050})
        page = context.new_page()
        errors, analysis_requests, card_requests = [], [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: analysis_requests.append(request.url) if "/api/analyze" in request.url else None)
        page.on("request", lambda request: card_requests.append(request.url) if "/api/card?" in request.url else None)
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        expect(page.locator(".card-title")).to_have_text("Oceanic climate")
        expect(page.locator("#history-count")).to_have_text("0")
        page.locator("#history-button").click()
        expect(page.locator(".collection-empty")).to_be_visible()
        page.get_by_role("button", name="Close collection").click()

        text = "🌍 France has an oceanic climate.\n\nA Mediterranean climate has dry summers and wetter winters."
        upload(page, "Two climates", text)
        expect(page.locator("#history-count")).to_have_text("1")
        page.locator(".mention").filter(has_text="oceanic climate").click()
        expect(page.locator(".card-title")).to_have_text("Oceanic climate")
        page.get_by_role("button", name="Save Oceanic climate", exact=True).click()
        expect(page.locator("#saved-count")).to_have_text("1")
        expect(page.get_by_role("button", name="Unsave Oceanic climate", exact=True)).to_have_attribute("aria-pressed", "true")
        page.locator("#saved-button").click()
        expect(page.locator(".collection-entry")).to_have_count(1)
        page.get_by_role("button", name="Add note for Oceanic climate").click()
        note = "Remember: ocean influence moderates temperature.\nCompare rainfall with Mediterranean climate. <script>text only</script>"
        page.get_by_label("Your note", exact=True).fill(note)
        page.get_by_role("button", name="Save note", exact=True).click()
        expect(page.locator(".collection-note")).to_have_text(note)
        page.screenshot(path=str(OUT / "saved-desktop.png"), full_page=True)
        page.get_by_role("button", name="Open Oceanic climate", exact=True).click()
        expect(page.locator(".card-title")).to_have_text("Oceanic climate")

        upload(page, "A river lesson", "The Nile flows through Egypt. Erosion changes a river's landscape.")
        expect(page.locator("#history-count")).to_have_text("2")
        page.locator("#history-button").click()
        expect(page.locator(".collection-entry-title").first).to_have_text("A river lesson")
        page.get_by_label("Search your collection").fill("Mediterranean")
        expect(page.locator(".collection-entry")).to_have_count(1)
        page.get_by_label("Search your collection").fill("")
        expect(page.locator(".collection-entry")).to_have_count(2)
        page.screenshot(path=str(OUT / "history-desktop.png"), full_page=True)
        before = len(analysis_requests)
        page.get_by_role("button", name="Open Two climates", exact=True).click()
        expect(page.locator("#passage")).to_have_text(text)
        assert len(analysis_requests) == before
        assert page.locator(".mention").count() >= 3
        page.locator(".mention").filter(has_text="oceanic climate").click()
        expect(page.get_by_role("button", name="Unsave Oceanic climate", exact=True)).to_be_visible()

        # Persist an ambiguity choice, then verify it survives reload.
        upload(page, "A place with two meanings", "Georgia has several geographical meanings. The climate varies by location.")
        page.locator(".mention").filter(has_text="Georgia").click()
        page.get_by_role("button", name="Georgia (country)", exact=False).click()
        expect(page.locator(".card-title")).to_have_text("Georgia (country)")
        page.reload(wait_until="networkidle")
        expect(page.locator("#history-count")).to_have_text("3")
        expect(page.locator("#saved-count")).to_have_text("1")
        page.locator("#history-button").click()
        page.get_by_role("button", name="Open A place with two meanings", exact=True).click()
        expect(page.locator(".card-title")).to_have_text("Georgia (country)")
        page.locator(".mention").filter(has_text="Georgia").click()
        expect(page.locator(".card-title")).to_have_text("Georgia (country)")

        # Reopening a historical snapshot must not require an online card request.
        page.route("**/api/card?**", lambda route: route.abort())
        page.locator("#history-button").click()
        before_analysis, before_cards = len(analysis_requests), len(card_requests)
        page.get_by_role("button", name="Open Two climates", exact=True).click()
        page.locator(".mention").filter(has_text="oceanic climate").click()
        expect(page.locator(".card-title")).to_have_text("Oceanic climate")
        assert len(analysis_requests) == before_analysis
        # History restores the previously viewed source snapshot.
        assert len(card_requests) == before_cards
        page.locator("#saved-button").click()
        expect(page.locator(".collection-note")).to_have_text(note)
        page.get_by_role("button", name="Open Oceanic climate", exact=True).click()
        expect(page.locator(".card-title")).to_have_text("Oceanic climate")
        assert len(card_requests) == before_cards
        assert page.locator(".source-item a").count() > 0

        # Independent collections, confirmation cancellation, and cross-tab counts.
        other = context.new_page()
        other.goto("http://127.0.0.1:8000", wait_until="networkidle")
        expect(other.locator("#history-count")).to_have_text("3")
        page.locator("#history-button").click()
        page.get_by_role("button", name="Delete A river lesson", exact=True).click()
        page.get_by_role("button", name="Cancel", exact=True).click()
        expect(page.locator(".collection-entry")).to_have_count(3)
        page.get_by_role("button", name="Delete A river lesson", exact=True).click()
        page.locator("#confirm-delete").click()
        expect(page.locator("#history-count")).to_have_text("2")
        expect(other.locator("#history-count")).to_have_text("2")
        page.locator("#clear-collection").click()
        page.locator("#confirm-delete").click()
        expect(page.locator("#history-count")).to_have_text("0")
        expect(page.locator("#saved-count")).to_have_text("1")
        page.get_by_role("button", name="Close collection").click()
        page.get_by_role("button", name="Unsave Oceanic climate", exact=True).click()
        expect(page.locator("#saved-count")).to_have_text("0")
        page.get_by_role("button", name="Save Oceanic climate", exact=True).click()
        expect(page.locator("#saved-count")).to_have_text("1")
        page.locator("#saved-button").click()
        page.locator("#clear-collection").click()
        page.locator("#confirm-delete").click()
        expect(page.locator("#saved-count")).to_have_text("0")
        page.get_by_role("button", name="Close collection").click()

        # A failed write must not pretend the star succeeded or discard the reading.
        page.evaluate("() => { personalStore.put = async () => { throw new Error('Storage is full.'); }; }")
        page.get_by_role("button", name="Save Oceanic climate", exact=True).click()
        expect(page.locator("#toast")).to_contain_text("Storage is full")
        expect(page.get_by_role("button", name="Save Oceanic climate", exact=True)).to_have_attribute("aria-pressed", "false")
        expect(page.locator("#saved-count")).to_have_text("0")
        assert page.locator("#passage").inner_text() == text

        upload(page, "Unsaved reading", "France has an oceanic climate, with rainfall throughout the year.")
        expect(page.locator("#reading-status")).to_contain_text("History was not saved")
        expect(page.locator("#history-count")).to_have_text("0")
        assert "rainfall throughout the year" in page.locator("#passage").inner_text()

        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#saved-button").click()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.screenshot(path=str(OUT / "saved-mobile.png"), full_page=True)
        page.get_by_role("button", name="Close collection").click()
        page.locator("#history-button").click()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert errors == [], errors
        browser.close()
        print(json.dumps({"personal_checks": "passed", "page_errors": errors, "paid_model_calls": 0}))


if __name__ == "__main__":
    main()
