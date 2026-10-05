"""Serve the LIVE GHL pages with the new build swapped in (route interception),
then time first paint / engine arrival with no user interaction.

usage: python simnew.py <scenario> <device> <path> [<path> ...]
  scenario: live  - untouched live page (control)
            pageonly - new page block + new body code, OLD head code (no styles in head)
            full - new page block + new body code + new head code (styles in <head>)
  device: a Playwright device name, or 'desktop'
"""
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(r"F:\Annette\own your studio\oyss-site")
NATIVE = REPO / "_ghl_native"
SLUG2PAGE = {'/home': 'index', '/services': 'services', '/experience': 'experience', '/assessment': 'assessment',
             '/panelists': 'panelists', '/about-us': 'about', '/faq': 'faq', '/apply': 'apply',
             '/strategy-session': 'contact', '/panelist-application': 'apply-panelist',
             '/host-agreement': 'agreements__host', '/panelist-agreement': 'agreements__panelist',
             '/terms': 'terms', '/privacy': 'privacy', '/disclaimer': 'disclaimer'}
SCEN, DEVICE, PATHS = (sys.argv[1], sys.argv[2], sys.argv[3:]) if len(sys.argv) > 2 else ('full', 'iPhone 13', [])
OUT = Path(__file__).parent / "shots"
OUT.mkdir(exist_ok=True)
HEAD_NEW = (NATIVE / "site_tracking_head.html").read_text(encoding="utf8")
HEAD_OLD = (REPO / "_ghl_head.html").read_text(encoding="utf8")
BODY_NEW = (NATIVE / "site_tracking_body.html").read_text(encoding="utf8")


def patch(html, path):
    if SCEN == 'live':
        return html
    page = SLUG2PAGE[path]
    block = (NATIVE / "pages" / f"{page}.html").read_text(encoding="utf8")
    # 1. SSR markup of the custom code element: swap the old block for the new one
    a = html.find('<!-- OYSS page:')
    b = html.find('</template>', a) + len('</template>')
    assert a > 0 and b > a
    html = html[:a] + block.rstrip('\n') + html[b:]
    # 2. head: what GHL's SSR does with the head code's <style> tags
    head = HEAD_NEW if SCEN == 'full' else HEAD_OLD
    if SCEN == 'full':
        styles = ''.join(f'<style>{m}</style>' for m in re.findall(r'<style\b[^>]*>(.*?)</style>', head, re.S))
        h = html.find('</head>')
        html = html[:h] + styles + html[h:]
    # 3. the Nuxt payload: page block, head code, body code
    s = html.find('id="__NUXT_DATA__"')
    j = html.find('>', s) + 1
    k = html.find('</script>', j)
    data = json.loads(html[j:k])
    hits = {'page': 0, 'head': 0, 'body': 0}
    for i, v in enumerate(data):
        if not isinstance(v, str):
            continue
        if v.lstrip().startswith('<!-- OYSS page:'):
            data[i] = block; hits['page'] += 1
        elif v.startswith('<!-- Own Your Stage Studio: link preview'):
            data[i] = head; hits['head'] += 1
        elif v.startswith('<!-- Own Your Stage Studio: site stylesheet, light engine'):
            data[i] = BODY_NEW; hits['body'] += 1
    assert all(hits.values()), hits
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003C')
    return html[:j] + js + html[k:]


PROBE = """() => ({
  booted: document.documentElement.classList.contains('oyss-booted'),
  mounted: document.documentElement.classList.contains('oyss-mounted'),
  loader: !!window.__oyssLoader, mounts: document.querySelectorAll('.oyss-mount').length,
  lit: document.querySelectorAll('.oyss-mount [data-lit].lit').length,
  total: document.querySelectorAll('.oyss-mount [data-lit]').length,
  spot: (function(){var s=document.querySelector('.oyss-mount .spot');return s?getComputedStyle(s).opacity:null})(),
  overflowX: document.documentElement.scrollWidth - window.innerWidth,
  mh: getComputedStyle(document.documentElement).getPropertyValue('--oyss-mh'),
})"""

if __name__ == '__main__':
  with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    for path in PATHS:
        ctx = b.new_context(**p.devices[DEVICE]) if DEVICE != 'desktop' else b.new_context(viewport={'width': 1366, 'height': 800})
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        pg.on('console', lambda m: errs.append('console.' + m.type + ': ' + m.text[:160]) if m.type == 'error' else None)

        def make_handler(path):
            def handle(route):
                r = route.fetch()
                hdrs = {k: v for k, v in r.headers.items() if k.lower() not in ('content-length', 'content-encoding')}
                hdrs['content-type'] = 'text/html; charset=utf-8'
                route.fulfill(status=r.status, body=patch(r.text(), path), headers=hdrs)
            return handle

        pg.route(re.compile(r'https://ownyourstagestudio\.com' + re.escape(path) + r'(\?.*)?$'), make_handler(path))
        t0 = time.time()
        pg.goto(f"https://ownyourstagestudio.com{path}?cb={int(time.time() * 1000)}", wait_until="commit")
        first_mount = engine = None
        spots = []
        while time.time() - t0 < 9:
            st = pg.evaluate(PROBE)
            el = round(time.time() - t0, 2)
            if st['mounted'] and first_mount is None:
                first_mount = el
                pg.screenshot(path=str(OUT / f"{SCEN}_{DEVICE.replace(' ', '')}_{path.strip('/')}_first.png"))
            if st['loader'] and engine is None:
                engine = el
            if st['spot'] is not None:
                spots.append(float(st['spot']))
            if engine and time.time() - t0 > engine + 2.5:
                break
            time.sleep(0.05)
        st = pg.evaluate(PROBE)
        pg.screenshot(path=str(OUT / f"{SCEN}_{DEVICE.replace(' ', '')}_{path.strip('/')}_settled.png"))
        print(f"{SCEN:8} {DEVICE:9} {path:22} first-mount {first_mount}  engine {engine}  "
              f"booted {st['booted']} mounts {st['mounts']} lit {st['lit']}/{st['total']} overflowX {st['overflowX']} "
              f"mh {st['mh']!r} spot-min {min(spots) if spots else None}  errors {errs[:3]}", flush=True)
        ctx.close()
    b.close()
