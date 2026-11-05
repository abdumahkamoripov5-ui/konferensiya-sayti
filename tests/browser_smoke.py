"""Optional live-browser check: .venv/Scripts/python tests/browser_smoke.py.

Requires playwright and a running local server. Does not submit production data.
"""
from pathlib import Path
import os

from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, executable_path=os.environ.get('BROWSER_EXECUTABLE'))
    page = browser.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    for width, height in ((1440, 900), (390, 844)):
        page.set_viewport_size({'width': width, 'height': height})
        for prefix in ('', '/en', '/tr'):
            for path in ('/', '/dastur', '/maxfiylik', '/talablar', '/royxatdan-otish'):
                response = page.goto('http://127.0.0.1:5000' + prefix + path)
                assert response.status == 200, (prefix, path, response.status)
                assert page.locator('h1').is_visible(), (prefix, path)
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), (width, prefix, path, 'horizontal overflow')
        page.goto('http://127.0.0.1:5000/')
        if width <= 1100:
            page.locator('#burger').click()
            assert page.locator('#burger').get_attribute('aria-expanded') == 'true'
            page.keyboard.press('Escape')
            assert page.locator('#burger').get_attribute('aria-expanded') == 'false'

    page.goto('http://127.0.0.1:5000/en/talablar')
    upload = page.locator('#maqola-fayl')
    upload.set_input_files({'name': 'sample.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4\n'})
    assert 'sample.pdf' in page.locator('#file-feedback').inner_text()
    # Lower the browser-only threshold to exercise the same size guard without a huge test file.
    upload.evaluate('(input) => input.dataset.maxBytes = "1"')
    upload.set_input_files({'name': 'large.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4\n'})
    assert upload.evaluate('(input) => input.validity.customError')
    assert upload.get_attribute('aria-invalid') == 'true'
    assert not errors, errors
    output = Path('data/browser-check')
    output.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(output / 'mobile-upload.png'), full_page=True)
    browser.close()
    print('PASS: 30 page views, mobile menu, no horizontal overflow, file size feedback, no JavaScript errors.')
