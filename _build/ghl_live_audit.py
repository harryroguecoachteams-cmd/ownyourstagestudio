import json, os, re, urllib.request
from playwright.sync_api import sync_playwright

BASE = "https://ownyourstagestudio.com"
PATHS = ["/home", "/services", "/experience", "/assessment", "/panelists", "/about-us", "/faq",
         "/apply", "/strategy-session", "/panelist-application", "/host-agreement",
         "/panelist-agreement", "/terms", "/privacy", "/disclaimer"]
OUT = os.path.join(os.path.dirname(__file__), "live")
os.makedirs(OUT, exist_ok=True)
links = set()
rows = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for w, h in [(1366, 800), (390, 844)]:
        ctx = b.new_context(viewport={"width": w, "height": h})
        for path in PATHS:
            pg = ctx.new_page()
            errs, gh, bad = [], [], []
            pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
            pg.on("request", lambda r: gh.append(r.url) if "github.io" in r.url else None)
            pg.on("response", lambda r: bad.append(f"{r.status} {r.url[:100]}") if r.status >= 400 and "filesafe" in r.url else None)
            pg.goto(BASE + path, wait_until="load", timeout=60000)
            try:
                pg.wait_for_selector(".oyss-mount .oyss", timeout=15000)
            except Exception:
                pass
            pg.wait_for_timeout(1500)
            for _ in range(25):
                pg.mouse.wheel(0, 900); pg.wait_for_timeout(40)
            pg.wait_for_timeout(1200)
            info = pg.evaluate("""() => ({
              title: document.title,
              mounted: !!document.querySelector('.oyss-mount .oyss'),
              overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
              broken: [...document.querySelectorAll('.oyss-mount img')].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src.slice(-36)),
              links: [...document.querySelectorAll('.oyss-mount a[href^="/"]')].map(a => a.getAttribute('href').split('#')[0]),
              iframes: [...document.querySelectorAll('.oyss-mount iframe')].map(f => f.src.slice(0, 70))
            })""")
            links.update(info.pop("links"))
            if w == 1366:
                pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)
                pg.screenshot(path=os.path.join(OUT, path.strip('/') + ".png"))
            ok = info["mounted"] and not errs and not gh and not info["broken"] and info["overflow"] <= 0 and not bad
            rows.append(("OK " if ok else "BAD") + f" {w} {path:22} " + json.dumps(dict(errors=errs[:2], github=len(gh), bad=bad[:3], **info)))
            pg.close()
        ctx.close()
    b.close()
print("\n".join(rows))
print("\nINTERNAL LINKS:")
for l in sorted(links):
    try:
        req = urllib.request.Request(BASE + (l or "/"), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf8", "ignore")
            t = re.search(r"<title[^>]*>([^<]*)", body)
            print(r.status, l, "|", (t.group(1) if t else "")[:60])
    except Exception as e:
        print("ERR", l, e)
