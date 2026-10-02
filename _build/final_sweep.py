"""Responsive sweep of the LIVE site (2 Oct 2026, before Annette's own test round).

Usage: python _build/final_sweep.py 320,360,390 [--shots]

Every page at every width given: mounted, sideways scroll and what causes it,
WCAG contrast (audit.py's probe, finished reveal state), the masthead over
footage, broken images after a full scroll, button text clipped, tiny type and
tap targets on phones, images without alt, leftover template tokens, JS errors,
console errors, failed requests, and the page meta. Read-only: nothing is
submitted. Results go to _build/livecheck/sweep_<widths>.json.
"""
import importlib.util, json, os, pathlib, re, sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("audit", HERE / "audit.py")
audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)

BASE = "https://ownyourstagestudio.com"
PATHS = ["/home", "/services", "/experience", "/assessment", "/panelists", "/about-us", "/faq",
         "/apply", "/strategy-session", "/panelist-application", "/host-agreement",
         "/panelist-agreement", "/terms", "/privacy", "/disclaimer"]
HEIGHT = {320: 640, 360: 740, 390: 844, 414: 896, 768: 1024, 834: 1112, 1024: 768,
          1280: 800, 1366: 768, 1536: 825, 1920: 1080}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
UA_PHONE = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36")
OUT = HERE / "livecheck"
SHOTS = OUT / "shots"
SHOTS.mkdir(parents=True, exist_ok=True)

EXTRA = r"""
(() => {
  const vw = innerWidth, phone = vw <= 480, root = document.querySelector('.oyss-mount .oyss');
  const vis = el => { const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0; };
  const out = {};
  out.mounted = !!root;
  out.overflow = document.documentElement.scrollWidth - innerWidth;
  out.brokenImg = [...document.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src'))
    .map(i => i.getAttribute('src').slice(-60));
  out.noAlt = [...document.querySelectorAll('.oyss-mount img')].filter(i => !i.hasAttribute('alt')).map(i => (i.getAttribute('src') || '').slice(-50));
  out.clippedBtn = [...document.querySelectorAll('.oyss-mount .btn, .oyss-mount button, .oyss-mount .cue')]
    .filter(b => vis(b) && b.scrollWidth > b.clientWidth + 1 && getComputedStyle(b).overflow !== 'visible')
    .map(b => b.textContent.trim().slice(0, 40));
  // a button whose text wraps onto more lines than its box shows, or wraps at all on a phone
  out.wrappedBtn = phone ? [...document.querySelectorAll('.oyss-mount .btn')].filter(b => vis(b)).filter(b => {
      const lh = parseFloat(getComputedStyle(b).lineHeight) || 20; return b.getBoundingClientRect().height > lh * 2.6;
    }).map(b => b.textContent.trim().slice(0, 40)) : [];
  const text = root ? root.innerText : '';
  out.tokens = (text.match(/(%%[A-Z_]+%%|\{\{[^}]*\}\}|\bundefined\b|\bNaN\b|\blorem\b|\bTODO\b|\bTBD\b|\[object Object\])/gi) || []).slice(0, 5);
  out.doubleWords = (text.match(/\b(\w{2,})\s+\1\b/gi) || []).filter(w => !/^(that that|had had)$/i.test(w)).slice(0, 5);
  out.tinyText = phone ? [...(root ? root.querySelectorAll('*') : [])].filter(el => {
      if (!vis(el)) return false;
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2);
      return own && parseFloat(getComputedStyle(el).fontSize) < 12;
    }).map(el => (el.className || el.tagName).toString().slice(0, 30) + ' ' + getComputedStyle(el).fontSize + ' "' + el.textContent.trim().slice(0, 30) + '"').slice(0, 6) : [];
  if (out.overflow > 1) {
    out.wide = [...document.querySelectorAll('body *')].filter(el => {
      const r = el.getBoundingClientRect(); return r.width > 0 && (r.right > vw + 1 || r.left < -1) && vis(el);
    }).slice(0, 8).map(el => (el.className || el.tagName).toString().slice(0, 50) + ' ' + Math.round(el.getBoundingClientRect().left) + '..' + Math.round(el.getBoundingClientRect().right));
  }
  const m = n => { const e = document.querySelector(n); return e ? (e.getAttribute('content') || e.getAttribute('href') || '') : null; };
  out.meta = { title: document.title, desc: m('meta[name="description"]'), canonical: m('link[rel="canonical"]'),
    ogTitle: m('meta[property="og:title"]'), ogImage: m('meta[property="og:image"]'), lang: document.documentElement.lang,
    viewport: m('meta[name="viewport"]'), icon: m('link[rel~="icon"]'),
    h1: [...document.querySelectorAll('.oyss-mount h1')].filter(vis).map(h => h.textContent.trim().slice(0, 60)) };
  return out;
})()
"""


def run(widths, shots):
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        for w in widths:
            phone = w <= 480
            ctx = b.new_context(viewport={"width": w, "height": HEIGHT.get(w, 900)}, device_scale_factor=1,
                                user_agent=UA_PHONE if phone else UA, is_mobile=phone, has_touch=phone)
            # never let a stray script post anything from this sweep
            ctx.route(re.compile(r"https://(services\.leadconnectorhq\.com/hooks|roguecoachteams\.com/relay)/.*"),
                      lambda route, req: route.fulfill(status=200, body="{}"))
            for path in PATHS:
                pg = ctx.new_page()
                errs, cons, bad = [], [], []
                pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
                pg.on("console", lambda m: cons.append(m.text[:160]) if m.type == "error" else None)
                pg.on("response", lambda r: bad.append(f"{r.status} {r.url[:110]}") if r.status >= 400 else None)
                pg.on("requestfailed", lambda r: bad.append(f"FAILED {r.failure} {r.url[:110]}")
                      if "google" not in r.url and "facebook" not in r.url else None)
                row = {"path": path, "w": w}
                try:
                    pg.goto(BASE + path, wait_until="load", timeout=60000)
                    try:
                        pg.wait_for_selector(".oyss-mount .oyss", timeout=25000)
                    except Exception:
                        pass
                    pg.wait_for_timeout(1500)
                    if shots:
                        pg.screenshot(path=str(SHOTS / f"{path.strip('/')}_{w}_top.png"))
                    for _ in range(40):
                        pg.mouse.wheel(0, 700); pg.wait_for_timeout(35)
                    pg.wait_for_timeout(1200)
                    pg.evaluate(audit.LIGHT_ALL); pg.wait_for_timeout(300)
                    row.update(pg.evaluate(EXTRA))
                    pr = pg.evaluate(audit.PROBE)
                    row["contrast"] = pr["contrast"][:10]
                    row["escapes"] = pr["escapes"][:6]
                    row["smallTap"] = pr["small"][:8]
                    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
                    row["masthead"] = audit.masthead_contrast(pg, OUT / f"_mast_{w}.png")
                    if shots and w in (390, 1366):
                        pg.screenshot(path=str(SHOTS / f"{path.strip('/')}_{w}_full.png"), full_page=True)
                except Exception as e:
                    row["exception"] = str(e)[:200]
                row["jsErrors"], row["console"], row["http"] = errs[:5], cons[:5], bad[:8]
                rows.append(row)
                flags = [k for k in ("overflow", "brokenImg", "noAlt", "clippedBtn", "wrappedBtn", "tokens", "doubleWords",
                                     "tinyText", "contrast", "escapes", "masthead", "jsErrors", "http", "exception")
                         if (row.get(k) if k != "overflow" else (row.get(k) or 0) > 1)]
                print(f"{w:>5} {path:<22} {'OK' if not flags else 'CHECK ' + ','.join(flags)}", flush=True)
                pg.close()
            ctx.close()
        b.close()
    return rows


if __name__ == "__main__":
    widths = [int(x) for x in sys.argv[1].split(",")]
    rows = run(widths, "--shots" in sys.argv)
    name = OUT / f"sweep_{'-'.join(map(str, widths))}.json"
    json.dump(rows, open(name, "w", encoding="utf-8"), indent=1)
    print("saved", name)
