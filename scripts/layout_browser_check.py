"""Long-reading layout acceptance / 长材料布局验收。"""
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

OUT = Path(__file__).resolve().parents[1] / "test-results"
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto("http://127.0.0.1:8000", wait_until="networkidle")
    page.locator(".card-title").wait_for()
    left = page.locator(".reading-panel > .panel-heading").bounding_box()
    right = page.locator(".explore-panel > .panel-heading").bounding_box()
    assert abs(left["y"] - right["y"]) < 1
    text = ("Forests protect soil. Lakes store water, while erosion shapes landscapes.\n\n" * 70) + "At the end of this reading, deforestation affects habitats."
    page.get_by_role("button", name="New material", exact=False).click()
    page.get_by_label("Learning material", exact=True).fill(text)
    page.get_by_label("Lesson title", exact=False).fill("A long geography reading")
    page.locator("#use-ai").uncheck()
    page.get_by_role("button", name="Explore this reading", exact=False).click()
    page.locator("#material-dialog").wait_for(state="hidden")
    assert page.locator("#passage").inner_text() == text
    assert page.locator("#passage").evaluate("e => e.scrollHeight <= e.clientHeight + 1")
    page.locator(".mention").filter(has_text="deforestation").scroll_into_view_if_needed()
    y = page.evaluate("window.scrollY")
    assert y > 2000
    panel = page.locator(".explore-panel").bounding_box()
    assert abs(panel["y"] - 16) < 1 and panel["y"] + panel["height"] <= 900
    page.locator("#card-view").evaluate("e => e.scrollTop = e.scrollHeight")
    page.locator(".mention").filter(has_text="deforestation").click()
    expect(page.locator(".card-title")).to_have_text("Deforestation")
    assert abs(page.evaluate("window.scrollY") - y) < 1
    assert page.locator("#card-view").evaluate("e => e.scrollTop") == 0
    title = page.locator(".card-title").bounding_box()
    assert 16 < title["y"] < 850
    page.screenshot(path=str(OUT / "long-reading-sticky.png"))
    before = page.locator("#card-view").bounding_box()["height"]
    page.locator(".summary-heading").click()
    assert page.locator("#card-view").bounding_box()["height"] > before
    page.locator(".summary-heading").click()
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.locator("#passage").inner_text() == text
    assert page.locator("#passage").evaluate("e => e.scrollHeight <= e.clientHeight + 1")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert page.locator(".explore-panel").evaluate("e => getComputedStyle(e).position") == "static"
    assert not errors, errors
    browser.close()
    print("Long-reading desktop/mobile layout checks passed; no paid model calls.")
