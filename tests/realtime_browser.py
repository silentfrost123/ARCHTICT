from playwright.sync_api import sync_playwright,expect
with sync_playwright() as p:
 browser=p.chromium.launch()
 hc=browser.new_context(viewport={'width':1440,'height':900});h=hc.new_page();errors=[]
 h.on('pageerror',lambda e:errors.append(str(e)));h.goto('http://127.0.0.1:8000');h.wait_for_selector('.category')
 room=h.url.split('room=')[1];root='http://127.0.0.1:8000';api=root+'/api/room/'+room
 projection=hc.new_page();projection.goto(root+'/projector?room='+room);projection.wait_for_selector('.category')
 projection.set_viewport_size({'width':1920,'height':1080});projection.screenshot(path='data/projector-check.png',full_page=True)
 assert not projection.evaluate('document.body.scrollHeight>innerHeight'), 'projector board should fit 16:9'
 m1c=browser.new_context(viewport={'width':390,'height':844});m1=m1c.new_page();m1.on('pageerror',lambda e:errors.append(str(e)))
 m1.goto(root+'/join?room='+room);m1.fill('#f-name','Player One');m1.locator('#join-form button[type=submit]').click();m1.wait_for_selector('.participant-info')
 m2c=browser.new_context(viewport={'width':390,'height':844});m2=m2c.new_page();m2.goto(root+'/join?room='+room);m2.fill('#f-name','Player Two');m2.locator('#join-form button[type=submit]').click();m2.wait_for_selector('.participant-info')
 hc.request.post(api+'/settings',data={'settings':{'doubleChance':0}})
 h.locator('[data-action=select][data-id="architects-1"]').click();m1.wait_for_selector('#answer-form');m2.wait_for_selector('#answer-form');projection.wait_for_selector('.question-stage')
 assert 'correctAnswer' not in projection.evaluate('S.current'), 'projector receives no correct answer'
 assert 'correctAnswer' not in m1.evaluate('S.current'), 'participant receives no correct answer'
 m1.locator('[data-action=chooseAnswer]').first.click()
 m2.locator('[data-action=chooseAnswer]').first.click();m2.locator('[data-submit-answer]').click();m2.wait_for_selector('.answer-reveal')
 # Wait for actual server message to reach the first client.
 m1.wait_for_function('S.current.submissions === 1')
 assert m1.locator('#chosen-answer').input_value()=='Frank Lloyd Wright','unsent answer retained across updates'
 m1.locator('[data-submit-answer]').click();m1.wait_for_selector('.answer-reveal')
 h.locator('[data-action=correct]').click();projection.wait_for_selector('.answer-reveal');m1.wait_for_function('S.me.score === 100')
 m1.reload();m1.wait_for_selector('.participant-info');assert m1.evaluate('S.me.score')==100,'refresh restores score'
 h.reload();h.wait_for_selector('.question-stage');assert h.evaluate('S.teams[0].score')==100,'host refresh restores team score'
 h.locator('[data-action=board]').click();h.wait_for_selector('.category');h.screenshot(path='data/desktop-900-check.png',full_page=True)
 # Dialog CRUD through UI.
 h.locator('[data-page=library]').click();h.wait_for_selector('table');h.locator('[data-action=questionEdit]').first.click();h.fill('[name=question]','Which material is this test about?');h.fill('[name=correctAnswer]','Timber');h.locator('#question-form button[type=submit]').click();h.wait_for_selector('#question-form',state='detached');h.fill('#library-search','Which material is this test');assert h.locator('tbody tr').count()==1
 assert not errors,errors
 print('PASS: separate host/projector/two mobile clients; live questions and scores; answer privacy; draft retention; refresh recovery; question creation; 16:9 fit; no JS errors.')
 browser.close()
