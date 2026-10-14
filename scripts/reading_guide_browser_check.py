"""Reading-first guide acceptance / 阅读优先引导学习验收。"""
import json
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

OUT = Path(__file__).resolve().parents[1] / 'test-results'
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1050})
    errors, analyses = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda r: analyses.append(r.url) if r.url.endswith('/api/analyze') else None)
    page.goto('http://127.0.0.1:8000', wait_until='networkidle')
    assert analyses == []
    expect(page.locator('#passage')).to_contain_text('Start with your own reading')
    expect(page.locator('#material-dialog')).to_be_visible()
    expect(page.locator('#material-text')).to_have_value('')
    expect(page.locator('#use-sample')).to_have_count(0)
    page.locator('#material-dialog .close-dialog').click()
    expect(page.locator('#history-count')).to_have_text('0')
    expect(page.locator('.intro-description')).to_have_count(0)
    assert 'Completion means you finished the activities' not in page.locator('body').inner_text()
    quiz = {'kind': 'ai', 'warning': None, 'questions': [
        {'id': 'q1', 'type': 'multiple_choice', 'question': 'What do forests protect?', 'options': ['Soil', 'Ocean currents', 'Volcanoes'], 'answer': 0, 'explanation': 'The reading connects forests with soil protection.', 'evidence': 'Forests protect soil.'},
        {'id': 'q2', 'type': 'true_false', 'question': 'Water can move between land and the atmosphere.', 'options': ['True', 'False'], 'answer': 0, 'explanation': 'The water cycle connects land and atmosphere.', 'evidence': 'The water cycle connects land and atmosphere.'}]}
    def analyze(route):
        body = route.request.post_data_json
        assert body['generate_quiz'] is True and 'recommend_targets' not in body
        result = route.fetch(post_data=json.dumps({**body, 'use_ai': False, 'generate_quiz': False, 'summarize_with_ai': False})).json()
        result['study_quiz'] = quiz; route.fulfill(json=result)
    page.route('**/api/analyze', analyze)
    page.locator('#new-material').click()
    expect(page.locator('#material-mode')).to_have_value('guided')
    page.locator('#use-ai').uncheck()
    text = 'Forests protect soil. Forests provide habitat. Forests influence local water. The water cycle connects land and atmosphere. France has varied landscapes.'
    page.locator('#material-text').fill(text)
    page.locator('#material-title').fill('Reading-first forests')
    page.locator('#analyze-button').click()
    expect(page.locator('#study-setup')).to_be_visible()
    expect(page.locator('#study-targets input:checked')).to_have_count(0)
    expect(page.locator('#study-targets label').first).to_contain_text('Forest · 3 mentions')
    assert page.locator('#study-goal, #study-prediction-confidence, #study-assessment').count() == 0
    page.locator('#study-targets input[value="wiki:Forest"]').check()
    page.locator('#study-targets input[value="wiki:Water cycle"]').check()
    page.get_by_role('button', name='Start reading', exact=True).click()
    expect(page.locator('#simple-study-content')).to_be_visible()
    assert page.locator('.material-summary-panel').evaluate('e=>e.open')
    expect(page.locator('.summary-limit, #summary-meta')).to_have_count(0)
    assert len(page.locator('#material-summary').inner_text().split()) <= 50
    expect(page.locator('#material-summary')).to_have_text('Enable AI when submitting your material to get a summary.')
    assert page.locator('.summary-content').evaluate('e=>getComputedStyle(e).overflowY') == 'visible'
    page.locator('.summary-heading').click()
    expect(page.locator('#material-summary')).not_to_be_visible()
    page.locator('.summary-heading').click()
    expect(page.locator('#material-summary')).to_be_visible()
    expect(page.locator('#concept-understanding')).to_have_value('')
    assert page.locator('.guided-comparison').count() == 0
    for word in ['Forest', 'Water cycle']:
        page.locator('.guided-concept-list').get_by_role('button', name=word, exact=True).click()
        page.locator('#concept-understanding').fill('I understand this concept connects the geographical processes in the material.')
        page.get_by_role('button', name='Submit and compare', exact=True).click()
        expect(page.locator('.guided-comparison')).to_be_visible()
        assert page.locator('.guided-comparison a').count() > 0
        expect(page.locator('.guided-reviewed input')).to_have_count(0)
    expect(page.locator('.guided-completion')).to_contain_text('✓ Completed · Unfamiliar concepts 2/2')
    expect(page.locator('#guided-task-status')).to_be_visible()
    assert page.locator('#guided-task-status').evaluate('e => e.parentElement.classList.contains("explore-panel")')
    page.set_viewport_size({'width': 1440, 'height': 700})
    page.evaluate('window.scrollTo(0, 500)')
    status_y = page.locator('#guided-task-status').bounding_box()['y']
    page.screenshot(path=str(OUT / 'reading-guide-desktop.png'))
    page.locator('#guided-tab-quiz').click()
    assert abs(page.locator('#guided-task-status').bounding_box()['y'] - status_y) < 2
    assert page.locator('#explore-scroll').evaluate('e=>e.scrollHeight > e.clientHeight + 20')
    assert page.locator('.explore-panel').evaluate('e => [...e.querySelectorAll("*")].filter(n => !["TEXTAREA", "INPUT"].includes(n.tagName) && n.getClientRects().length && ["auto", "scroll"].includes(getComputedStyle(n).overflowY) && n.scrollHeight > n.clientHeight + 2).every(n => n.id === "explore-scroll")')
    page.locator('#explore-scroll').evaluate('e=>e.scrollTop=500')
    assert abs(page.locator('#guided-task-status').bounding_box()['y'] - status_y) < 2
    page.locator('#explore-scroll').evaluate('e=>e.scrollTop=0')
    bounds = page.locator('#explore-scroll').bounding_box()
    page.mouse.move(bounds['x'] + bounds['width'] - 12, bounds['y'] + 80)
    page.mouse.wheel(0, 400)
    page.wait_for_function("() => document.querySelector('#explore-scroll').scrollTop > 0")
    assert abs(page.locator('#guided-task-status').bounding_box()['y'] - status_y) < 2
    expect(page.locator('.guided-quiz-question')).to_have_count(2)
    page.locator('[data-question="q1"]').get_by_role('button', name='Ocean currents', exact=True).click()
    expect(page.locator('[data-question="q1"] .quiz-feedback')).to_contain_text('Not quite. Correct answer: Soil')
    page.locator('[data-question="q2"]').get_by_role('button', name='True', exact=True).click()
    expect(page.locator('[data-question="q2"] .quiz-feedback')).to_contain_text('Correct')
    expect(page.locator('.guided-completion')).to_contain_text('✓ Completed · Questions 2/2')
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(OUT / 'reading-guide-mobile.png'), full_page=True)
    page.reload(wait_until='networkidle')
    expect(page.locator('#material-dialog')).to_be_visible()
    page.locator('#material-dialog .close-dialog').click()
    before = len(analyses)
    page.locator('#history-button').click()
    page.get_by_role('button', name='Open Reading-first forests', exact=True).click()
    expect(page.locator('.guided-completion')).to_contain_text('✓ Completed · Questions 2/2')
    expect(page.locator('.guided-completion')).to_contain_text('✓ Completed · Unfamiliar concepts 2/2')
    assert len(analyses) == before
    page.locator('#study-start').click()
    page.locator('#study-targets input').evaluate_all('items=>items.forEach(e=>e.checked=false)')
    page.get_by_role('button', name='Start reading', exact=True).click()
    expect(page.locator('.guided-completion')).to_contain_text('Unfamiliar concepts: none selected')
    page.locator('#study-start').click()
    expect(page.locator('#study-targets input:checked')).to_have_count(0)
    page.locator('#study-targets input[value="wiki:Forest"]').check()
    page.locator('#study-targets input[value="wiki:Water cycle"]').check()
    page.get_by_role('button', name='Start reading', exact=True).click()
    expect(page.locator('.guided-completion')).to_contain_text('✓ Completed · Unfamiliar concepts 2/2')
    assert len(analyses) == before
    page.locator('#guided-tab-explore').click()
    expect(page.locator('#guided-task-status')).to_be_visible()
    assert page.locator('#card-view').evaluate('e=>getComputedStyle(e).overflowY') == 'visible'
    expect(page.locator('#concept-search')).to_be_visible()
    page.evaluate("loadCard('wiki:Forest')")
    page.get_by_role('button', name='Save Forest', exact=True).click()
    page.locator('#guided-tab-quiz').click()
    page.locator('#saved-button').click()
    page.get_by_role('button', name='Open Forest', exact=True).click()
    expect(page.locator('#card-view')).to_be_visible()
    expect(page.get_by_role('button', name='Unsave Forest', exact=True)).to_be_visible()
    page.locator('#study-mode').select_option('explore')
    expect(page.locator('#guided-task-status')).to_be_visible()
    expect(page.locator('.simple-study-nav')).not_to_be_visible()
    expect(page.locator('#concept-search')).to_be_visible()
    assert errors == [], errors
    browser.close()
    print(json.dumps({'empty_home': 'passed', 'guided_default': 'passed', 'frequency_no_preselection': 'passed', 'understanding_and_comparison': 'passed', 'quiz_feedback_completion': 'passed', 'history_restore': 'passed', 'explore': 'passed', 'mobile': 'passed', 'paid_model_calls': 0}))
