"""Simulate GHL: tracking code at end of body, page custom code injected late
inside a padded builder column. Check every page mounts, nothing hits GitHub,
no JS errors, no broken media, no horizontal overflow."""
import json, os, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE = Path(r"F:/Annette/own your studio/oyss-site/_ghl_native")
OUT = Path(__file__).parent / "sim"
OUT.mkdir(exist_ok=True)
tracking = (SITE / "site_tracking_body.html").read_text(encoding="utf8")
pages = sys.argv[1:] or [p.stem for p in sorted((SITE / "pages").glob("*.html"))]

SHELL = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>h1,h2,p,a,button{font-family:Arial;color:#123}.hl_page-preview--content{max-width:1170px;margin:0 auto;padding:40px}</style></head>
<body><div id="__nuxt"><div id="preview-container" class="hl_page-preview--content"><div class="c-custom-code" id="cc"></div></div></div><div id="teleports"></div>
<script>setTimeout(function(){document.getElementById('cc').innerHTML=window.__PAGE__;},600);</script>
%TRACK%
</body></html>"""

res = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for name in pages:
        page_html = (SITE / "pages" / f"{name}.html").read_text(encoding="utf8")
        html = SHELL.replace("%TRACK%", tracking)
        f = OUT / f"{name}.html"
        f.write_text(html.replace("window.__PAGE__", json.dumps(page_html).replace("</", "<\/")), encoding="utf8")
        for w, h in [(1366, 800), (390, 844)]:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            errs, gh, bad = [], [], []
            pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            pg.on("request", lambda r: gh.append(r.url) if "github.io" in r.url else None)
            pg.on("response", lambda r: bad.append(f"{r.status} {r.url[:90]}") if r.status >= 400 else None)
            pg.goto(f.as_uri(), wait_until="load")
            pg.wait_for_timeout(2500)
            # scroll through to trigger lazy media and reveals
            for y in range(0, 9000, 900):
                pg.mouse.wheel(0, 700); pg.wait_for_timeout(40)
            pg.wait_for_timeout(800)
            info = pg.evaluate("""() => ({
              mounted: !!document.querySelector('.oyss-mount .oyss'),
              hiddenNuxt: getComputedStyle(document.getElementById('__nuxt')).display,
              overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
              brokenImgs: [...document.querySelectorAll('.oyss-mount img')].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src.slice(-40)),
              height: document.body.scrollHeight,
              mastheadLeft: (document.querySelector('.masthead')||{getBoundingClientRect:()=>({left:-1})}).getBoundingClientRect().left
            })""")
            if w == 1366:
                pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
                pg.screenshot(path=str(OUT / f"{name}_{w}.png"))
            res.append(dict(page=name, w=w, errors=errs, github=len(gh), http_bad=bad[:5], **info))
            ctx.close()
    b.close()
for r in res:
    flag = "OK " if (r["mounted"] and not r["errors"] and not r["github"] and not r["brokenImgs"] and r["overflow"] <= 0 and not r["http_bad"]) else "BAD"
    print(flag, json.dumps(r))
