from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 browser=p.chromium.launch()
 context=browser.new_context(viewport={'width':1440,'height':1050})
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8000');page.wait_for_selector('.category');page.screenshot(path='data/board-check.png',full_page=True)
 print('cards',page.locator('.category').count(),'points',page.locator('.point').count())
 page.locator('[data-action="select"]').first.click();page.wait_for_selector('.question-stage');page.locator('[data-action="peek"]').click();page.locator('[data-action="correct"]').click();page.wait_for_selector('.answer-reveal');page.locator('[data-action="board"]').click();page.wait_for_selector('.category')
 page.locator('[data-page="library"]').click();page.wait_for_selector('table');page.locator('[data-action="questionEdit"]').first.click();page.wait_for_selector('#question-form');page.locator('[data-action="close"]').first.click()
 page.locator('[data-page="settings"]').click();page.wait_for_selector('#settings-form');page.locator('[data-action="saveSettings"]').click()
 page.locator('[data-page="teams"]').click();page.wait_for_selector('.stat-grid')
 print('errors',errors)
 # Mobile anonymous join view
 mobile=browser.new_context(viewport={'width':390,'height':844});mp=mobile.new_page();mp.goto('http://127.0.0.1:8000/join?room='+page.url.split('room=')[1]);mp.wait_for_selector('#join-form');mp.screenshot(path='data/mobile-check.png',full_page=True)
 print('mobile overflow',mp.evaluate('document.body.scrollWidth>innerWidth'))
 browser.close()
