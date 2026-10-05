"""Full-fix scenario, phone: touch-fling scroll down the home page and sample how much of the
viewport is still in the dim (unlit) state mid-fling; then the menu and the assessment."""
import re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
import simnew

SCEN = sys.argv[1] if len(sys.argv) > 1 else 'full'
simnew.SCEN = SCEN
OUT = Path(__file__).parent / "shots"

DIM = """() => { const H = innerHeight; let dim = 0, vis = 0;
  document.querySelectorAll('.oyss-mount [data-lit]').forEach(e => { const r = e.getBoundingClientRect();
    const h = Math.max(0, Math.min(r.bottom, H) - Math.max(r.top, 0)); if (!h) return;
    vis += h; if (parseFloat(getComputedStyle(e).opacity) < 0.6) dim += h; });
  return {y: Math.round(scrollY), dimPx: Math.round(dim), visPx: Math.round(vis)}; }"""


def page_for(p, b, path):
    ctx = b.new_context(**p.devices["iPhone 13"])
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:160]))

    def handle(route):
        r = route.fetch()
        hdrs = {k: v for k, v in r.headers.items() if k.lower() not in ('content-length', 'content-encoding')}
        hdrs['content-type'] = 'text/html; charset=utf-8'
        route.fulfill(status=r.status, body=simnew.patch(r.text(), path), headers=hdrs)
    pg.route(re.compile(r'https://ownyourstagestudio\.com' + re.escape(path) + r'(\?.*)?$'), handle)
    pg.goto(f"https://ownyourstagestudio.com{path}?cb={int(time.time() * 1000)}", wait_until="commit")
    return ctx, pg, errs


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    # 1. fling scroll on home, sampled while the gesture runs
    ctx, pg, errs = page_for(p, b, '/home')
    pg.wait_for_function("document.documentElement.classList.contains('oyss-mounted')", timeout=15000)
    pg.wait_for_timeout(600)
    cdp = ctx.new_cdp_session(pg)
    worst = 0
    for i in range(6):
        pg.mouse.move(200, 500)
        for _ in range(7):
            pg.mouse.wheel(0, 200)
            pg.wait_for_timeout(16)
        for _ in range(6):
            s = pg.evaluate(DIM)
            frac = s['dimPx'] / max(1, s['visPx'])
            worst = max(worst, frac)
            pg.wait_for_timeout(80)
        print(f"  after fling {i + 1}: y={s['y']} dim {s['dimPx']}/{s['visPx']} px", flush=True)
        if i == 2:
            pg.screenshot(path=str(OUT / f"{SCEN}_fling_mid.png"))
    print(f"home fling: worst dim share of the viewport {worst:.0%}; errors {errs[:2]}")
    ctx.close()

    # 2. menu opens (engine), 3. assessment answers advance
    ctx, pg, errs = page_for(p, b, '/assessment')
    pg.wait_for_function("!!window.__oyssLoader", timeout=15000)
    pg.wait_for_timeout(800)
    btn = pg.locator('.oyss-mount .masthead button').first
    btn.tap()
    pg.wait_for_timeout(500)
    opened = pg.evaluate("""() => { const b = document.querySelector('.oyss-mount .masthead button');
        return b ? b.getAttribute('aria-expanded') : null }""")
    pg.screenshot(path=str(OUT / f"{SCEN}_menu.png"))
    btn.tap()
    pg.wait_for_timeout(400)
    start = pg.locator('.oyss-mount').get_by_role('button', name=re.compile('start|begin', re.I)).first
    if start.count():
        start.tap(); pg.wait_for_timeout(600)
    qchecked = lambda: pg.evaluate("document.querySelectorAll('.oyss-mount input[type=radio]:checked').length")
    q0 = pg.evaluate("document.querySelector('.oyss-mount').innerText.match(/Question \\d+ of \\d+/i)?.[0] || ''")
    opt = pg.locator('.oyss-mount label.choice:visible').first
    if opt.count():
        opt.scroll_into_view_if_needed(); opt.tap(); pg.wait_for_timeout(1200)
    print('radios checked after tap:', qchecked())
    q1 = pg.evaluate("document.querySelector('.oyss-mount').innerText.match(/Question \\d+ of \\d+/i)?.[0] || ''")
    pg.screenshot(path=str(OUT / f"{SCEN}_assessment.png"))
    print(f"menu aria-expanded after tap: {opened}; assessment {q0!r} -> {q1!r}; errors {errs[:2]}")
    ctx.close()
    b.close()
