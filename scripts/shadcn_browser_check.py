"""shadcn integration acceptance / shadcn 集成验收。"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

out = Path(__file__).resolve().parents[1] / 'test-results'
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe', headless=True)
    page = browser.new_page(viewport={'width':1440,'height':1000})
    errors, page_errors, failed = [], [], []
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: page_errors.append(str(e)))
    page.on('requestfailed', lambda r: failed.append(r.url))
    page.goto('http://127.0.0.1:8000',wait_until='networkidle')
    expect(page.locator('.card-title')).to_have_text('Oceanic climate')
    assert page.locator('#root').count()==1
    assert page.locator('[data-slot=card]').count()==2
    assert page.locator('[data-slot=separator]').count()==1
    assert page.locator('#new-material').get_attribute('data-slot')=='button'
    assert page.locator('#study-mode').get_attribute('data-slot')=='native-select'
    page.locator('#new-material').click()
    expect(page.locator('#use-ai')).to_be_checked()
    page.locator('#use-ai').uncheck()
    assert page.locator('#material-text').get_attribute('data-slot')=='textarea'
    assert page.locator('#material-title').get_attribute('data-slot')=='input'
    assert page.locator('#material-text').evaluate('e=>e.getBoundingClientRect().height')<=365
    page.get_by_role('button',name='Close material dialog').click()
    page.get_by_role('tab',name='Connect',exact=True).click()
    assert page.locator('.related-button[data-slot=button]').count()>0
    # Tab state is controlled by the existing agent, not a second React controller.
    expect(page.locator('#tab-connect')).to_have_attribute('aria-selected','true')
    page.get_by_role('tab',name='Learn',exact=True).click()
    page.get_by_role('button',name='Library',exact=False).click()
    page.locator('#library-query').fill('Forest')
    page.get_by_role('button',name='Explore Forest',exact=True).click()
    expect(page.locator('.card-title')).to_have_text('Forest')
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('#new-material').click()
    assert page.locator('#material-text').evaluate('e=>e.getBoundingClientRect().height')<=365
    page.screenshot(path=str(out/'shadcn-material-mobile.png'))
    page.get_by_role('button',name='Close material dialog').click()
    assert errors==[],errors
    assert page_errors==[],page_errors
    assert failed==[],failed
    browser.close()
    print('shadcn component, CSP, mobile form, and controller compatibility checks passed.')
