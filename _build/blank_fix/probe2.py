import time, json, sys
from playwright.sync_api import sync_playwright
def run(label, ctxargs, tap_at=None, url="https://ownyourstagestudio.com/home"):
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        ctx = b.new_context(**ctxargs)
        pg = ctx.new_page()
        t0 = time.time()
        pg.goto(url + "?cb=%d" % int(time.time()*1000), wait_until="commit")
        mounted_at = None; tapped=False
        while time.time() - t0 < 12:
            el = time.time() - t0
            if tap_at and not tapped and el >= tap_at:
                if ctxargs.get('has_touch'): pg.touchscreen.tap(200, 300)
                else: pg.mouse.move(200, 300)
                tapped = True; print(label, 'interaction at %.2f' % el)
            m = pg.evaluate("document.documentElement.classList.contains('oyss-mounted')")
            if m: mounted_at = el; break
            time.sleep(0.1)
        print(label, 'mounted at', None if mounted_at is None else round(mounted_at,2), flush=True)
        b.close()
dev = None
with sync_playwright() as p: dev = p.devices["Pixel 7"]
run('mobile-notouch', dev)
run('mobile-tap@1.5', dev, tap_at=1.5)
run('desktop-noinput', {"viewport": {"width":1366,"height":800}})
run('desktop-mousemove@1.5', {"viewport": {"width":1366,"height":800}}, tap_at=1.5)
