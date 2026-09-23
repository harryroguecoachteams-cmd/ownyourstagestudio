import json, os, sys
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(__file__)
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8899/assessment.html'
posted = []

with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome', headless=True)
    for w, h in [(1366, 800), (390, 844)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, accept_downloads=True)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('https://hook.test/**', lambda r: (posted.append(r.request.post_data), r.fulfill(status=200, body='{}')))
        pg.add_init_script("window.OYSS_ENDPOINT='https://hook.test/x';")
        pg.goto(URL, wait_until='networkidle')
        # answer every question: q1..q12, alternate 2/3 to vary pillars
        for q in range(1, 13):
            v = 2 if q in (3, 4) else 3
            pg.evaluate(f"(()=>{{const i=document.querySelector('input[name=q{q}][value=\"{v}\"]'); i.checked=true; i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()")
        pg.evaluate("document.getElementById('assessment-form').requestSubmit()")
        pg.wait_for_timeout(2000)
        vis = pg.evaluate("!document.getElementById('assessment-result').hidden")
        level = pg.text_content('#result-level')
        cal = pg.evaluate("!!document.querySelector('#assessment-result iframe')")
        keep = pg.locator('#result-keep')
        keep.scroll_into_view_if_needed()
        pg.wait_for_timeout(500)
        keep.screenshot(path=os.path.join(OUT, f'keep_{w}.png'))
        # PDF
        with pg.expect_download(timeout=20000) as d:
            pg.click('#result-pdf')
        dl = d.value
        pdfp = os.path.join(OUT, f'result_{w}.pdf')
        dl.save_as(pdfp)
        # email: empty first
        pg.click('#result-mail button[type=submit]')
        e1 = pg.text_content('#result-mail-err')
        pg.fill('#result-mail input[name=first_name]', 'Test')
        pg.fill('#result-mail input[name=email]', 'test@example.com')
        pg.click('#result-mail button[type=submit]')
        pg.wait_for_timeout(800)
        done = pg.text_content('#result-mail-done')
        overflow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        keep.screenshot(path=os.path.join(OUT, f'keep_done_{w}.png'))
        book = pg.get_attribute('#assessment-result .actions a.btn--primary', 'href')
        print(json.dumps(dict(w=w, vis=vis, level=level, calendar_iframe=cal, pdf=dl.suggested_filename,
                              pdf_bytes=os.path.getsize(pdfp), empty_err=e1, done=done, overflow=overflow,
                              book=book, errors=errs)))
        ctx.close()
    b.close()
d = json.loads(posted[-1])
print({k: (v[:80] + '...' if isinstance(v, str) and len(v) > 80 else v) for k, v in d.items()})
