"""Read-only live check of the GHL site (first run 29 Sep 2026, a995101 + ee64e46).

Usage: python _build/live_check_readonly.py [pages] [exit] [sign]   (default: all three)

Nothing reaches Annette's CRM or inbox: every request to the GHL inbound
webhook and to the documents relay is intercepted (payload captured, fake
reply). The captured relay payload is then posted to the live relay in DRY
mode with the test key, which validates it exactly like a real signing and
returns the email it would send, without sending it.
"""
import base64, json, math, os, re, sys, time, urllib.request
from playwright.sync_api import sync_playwright

BASE = "https://ownyourstagestudio.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
UA_PHONE = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "livecheck")
os.makedirs(OUT, exist_ok=True)
EMAIL = "events+oyss-test@ownyourstagestudio.com"
READING = {"/home", "/services", "/experience", "/panelists", "/about-us", "/faq"}
PATHS = ["/home", "/services", "/experience", "/assessment", "/panelists", "/about-us", "/faq",
         "/apply", "/strategy-session", "/panelist-application", "/host-agreement",
         "/panelist-agreement", "/terms", "/privacy", "/disclaimer"]
results, captured = [], {"hook": [], "relay": [], "other_block": []}


def log(name, ok, note=""):
    results.append({"name": name, "ok": bool(ok), "note": note})
    print(("PASS " if ok else "FAIL ") + name + (f"  ({note})" if note else ""), flush=True)


def guard(ctx):
    """Intercept the webhook and the relay on every page of this context."""
    cors = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS"}

    def hook(route, req):
        if req.method == "OPTIONS":
            return route.fulfill(status=204, headers=cors)
        try:
            captured["hook"].append(json.loads(req.post_data or "{}"))
        except Exception:
            captured["hook"].append({"raw": (req.post_data or "")[:200]})
        route.fulfill(status=200, headers=cors, content_type="application/json",
                      body='{"status":"Success: test intercept"}')

    def relay(route, req):
        if req.method == "OPTIONS":
            return route.fulfill(status=204, headers=cors)
        try:
            captured["relay"].append(json.loads(req.post_data or "{}"))
        except Exception:
            captured["relay"].append({"raw": (req.post_data or "")[:200]})
        route.fulfill(status=503, headers=cors, content_type="application/json",
                      body='{"ok":false,"error":"not_configured"}')

    ctx.route(re.compile(r"https://services\.leadconnectorhq\.com/hooks/.*"), hook)
    ctx.route(re.compile(r"https://roguecoachteams\.com/relay/.*"), relay)


def settle(pg):
    try:
        pg.wait_for_selector(".oyss-mount .oyss", timeout=25000)
    except Exception:
        pass
    pg.wait_for_timeout(1500)


def new_ctx(b, w, h, **kw):
    phone = w < 500
    ctx = b.new_context(user_agent=UA_PHONE if phone else UA, viewport={"width": w, "height": h},
                        is_mobile=phone, has_touch=phone, **kw)
    guard(ctx)
    return ctx


PROBE = """() => {
  const d = document.documentElement, bar = document.querySelector('.prompt');
  const r = bar && !bar.hidden ? bar.getBoundingClientRect() : null;
  const vis = el => el && getComputedStyle(el).display !== 'none' && el.getBoundingClientRect().width > 0;
  return {
    mounted: d.classList.contains('oyss-mounted'),
    ovf: d.scrollWidth - innerWidth,
    bar: !!bar, exit: !!document.querySelector('.exit'),
    barIn: !!(bar && bar.classList.contains('is-in')),
    barBox: r ? [Math.round(r.left), Math.round(r.right), Math.round(r.width)] : null,
    ctaShort: bar ? vis(bar.querySelector('.prompt__cta-s')) : null,
    ctaLong: bar ? vis(bar.querySelector('.prompt__cta-l')) : null,
    docs: typeof window.OYSS_DOCS === 'string' ? window.OYSS_DOCS : null
  };
}"""


def pages(b):
    for w, h in [(1366, 800), (390, 844), (360, 780)]:
        ctx = new_ctx(b, w, h)
        for path in PATHS:
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
            pg.goto(BASE + path, wait_until="load", timeout=60000); settle(pg)
            want = path in READING
            # read the page top to bottom like a person, so the bar can earn its way in
            for _ in range(30):
                pg.mouse.wheel(0, 700); pg.wait_for_timeout(60)
            pg.wait_for_timeout(900)
            info = pg.evaluate(PROBE)
            ok = (info["mounted"] and info["ovf"] <= 0 and not errs and info["bar"] == want
                  and info["exit"] == want and info["docs"] == "https://roguecoachteams.com/relay/oyss-docs.php")
            if want and w < 500:
                # the 28 Sep phone bug: the bar (shown) must fit the screen and use the short label
                if not info["barIn"]:
                    pg.evaluate("() => { const b = document.querySelector('.prompt'); b.hidden = false; b.classList.add('is-in'); }")
                    pg.wait_for_timeout(700)
                    info = dict(pg.evaluate(PROBE), forced=True)
                bb = info["barBox"]
                ok = ok and bb is not None and bb[0] >= 0 and bb[1] <= w and info["ovf"] <= 0 \
                    and info["ctaShort"] and not info["ctaLong"]
            log(f"page {w} {path}", ok, json.dumps({k: v for k, v in info.items() if k != "docs"})
                + (" errs=" + "; ".join(errs) if errs else ""))
            pg.close()
        ctx.close()


EXIT_PROBE = """() => {
  const ex = document.querySelector('.exit'); if (!ex) return {found: false};
  const box = ex.querySelector('.exit__box, .exit__card, [role=dialog], .exit__inner') || ex.firstElementChild;
  const r = box.getBoundingClientRect(), d = document.documentElement;
  const top = document.elementFromPoint(innerWidth / 2, 12);
  const mid = document.elementFromPoint(r.left + r.width / 2, r.top + Math.min(r.height / 2, 40));
  return {found: true, open: ex.classList.contains('is-in') && !ex.hidden,
          z: getComputedStyle(ex).zIndex, box: [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)],
          vw: innerWidth, vh: innerHeight, ovf: d.scrollWidth - innerWidth,
          topIsOverlay: !!(top && ex.contains(top)), midIsDialog: !!(mid && box.contains(mid))};
}"""


def exit_popup(b):
    # desktop: the pointer leaving through the top of the window, after 6 s
    ctx = new_ctx(b, 1366, 800); pg = ctx.new_page()
    pg.goto(BASE + "/home", wait_until="load"); settle(pg)
    pg.wait_for_timeout(6500)
    pg.mouse.move(600, 300); pg.mouse.move(600, 2)
    pg.evaluate("document.dispatchEvent(new MouseEvent('mouseout', {clientY: 1, relatedTarget: null, bubbles: true}))")
    pg.wait_for_timeout(1000)
    i = pg.evaluate(EXIT_PROBE)
    pg.screenshot(path=os.path.join(OUT, "exit_1366.png"))
    log("exit pop-up 1366: opens on leaving through the top, above the masthead", i.get("open") and i["topIsOverlay"]
        and i["midIsDialog"] and i["ovf"] <= 0 and i["box"][2] <= i["vw"], json.dumps(i))
    ctx.close()
    # phones: read past 45%, then a fast flick back toward the top
    for w, h in [(390, 844), (360, 780)]:
        ctx = new_ctx(b, w, h); pg = ctx.new_page()
        pg.goto(BASE + "/home", wait_until="load"); settle(pg)
        # speed is measured between consecutive scroll events, so the last two must be ~50 ms apart
        pg.evaluate("window.scrollTo({top: document.documentElement.scrollHeight * 0.6, behavior: 'instant'})")
        pg.wait_for_timeout(600)
        pg.evaluate("() => { window.scrollTo({top: 420, behavior: 'instant'});"
                    " setTimeout(() => window.scrollTo({top: 80, behavior: 'instant'}), 50); }")
        pg.wait_for_timeout(1400)
        i = pg.evaluate(EXIT_PROBE)
        pg.screenshot(path=os.path.join(OUT, f"exit_{w}.png"))
        ok = i.get("open") and i["topIsOverlay"] and i["midIsDialog"] and i["ovf"] <= 0 \
            and i["box"][0] >= 0 and i["box"][2] <= w
        log(f"exit pop-up {w}: opens on the upward flick, above the masthead, fits the phone", ok, json.dumps(i))
        ctx.close()


def draw(pg):
    cv = pg.query_selector("#sigpad-canvas"); cv.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    bb = cv.bounding_box()
    x0, y0 = bb["x"] + bb["width"] * 0.12, bb["y"] + bb["height"] * 0.62
    pg.mouse.move(x0, y0); pg.mouse.down()
    for k in range(50):
        t = k / 49
        pg.mouse.move(x0 + t * bb["width"] * 0.6, y0 - math.sin(t * math.pi * 3) * bb["height"] * 0.2)
    pg.mouse.up()


FILL = r"""(args) => {
  const [formSel, email, phone] = args;
  const f = document.querySelector(formSel); if (!f) return 'no form';
  const seen = new Set();
  f.querySelectorAll('input, textarea, select').forEach(el => {
    if (el.type === 'hidden' || el.disabled) return;
    const n = el.name || el.id;
    if (el.type === 'radio') { if (seen.has(n)) return; seen.add(n); el.checked = true; }
    else if (el.type === 'checkbox') { el.checked = true; }
    else if (el.tagName === 'SELECT') { if (el.options.length > 1) el.selectedIndex = 1; }
    else if (el.type === 'email') el.value = email;
    else if (el.type === 'tel') el.value = phone;
    else if (el.type === 'url') el.value = 'https://example.com';
    else if (el.tagName === 'TEXTAREA') el.value = 'TEST, read-only live check. Nothing was sent.';
    else if (/first/i.test(n)) el.value = 'TEST';
    else if (/last/i.test(n)) el.value = 'QA';
    else if (/legal/i.test(n)) el.value = 'TEST QA Signer';
    else el.value = 'TEST QA';
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
  });
  return 'ok';
}"""


def sign(b, path, key):
    ctx = new_ctx(b, 1366, 800, accept_downloads=True); pg = ctx.new_page()
    n_hook, n_relay = len(captured["hook"]), len(captured["relay"])
    pg.goto(BASE + path, wait_until="load"); settle(pg)
    try:
        pg.evaluate("document.getElementById('agreement-end').scrollIntoView()")
        for _ in range(8):
            pg.mouse.wheel(0, 900); pg.wait_for_timeout(120)
        pg.wait_for_timeout(800)
        pg.evaluate(FILL, ["#agreement-form", EMAIL, "+1 555 010 0199"])
        draw(pg)
        with pg.expect_download(timeout=30000) as d:
            pg.click("#agreement-form [type=submit]")
        name = d.value.suggested_filename
        d.value.save_as(os.path.join(OUT, name))
        pg.wait_for_selector("#signed-state:not([hidden])", timeout=15000)
        pg.wait_for_timeout(2500)
        hooks, relays = captured["hook"][n_hook:], captured["relay"][n_relay:]
        pdf = open(os.path.join(OUT, name), "rb").read()
        log(f"{key}: signed on the live page, PDF downloaded", pdf[:5] == b"%PDF-", f"{name}, {len(pdf):,} bytes")
        h = hooks[-1] if hooks else {}
        log(f"{key}: workflow webhook payload (intercepted)", bool(hooks) and h.get("email") == EMAIL
            and "#signed=" in (h.get("signed_copy_url") or ""), f"tag={h.get('tag')} fields={len(h)}")
        r = relays[-1] if relays else {}
        rp = base64.b64decode(r.get("pdf", "") or b"") if r else b""
        log(f"{key}: relay payload (intercepted) is the downloaded PDF", bool(relays) and rp == pdf,
            f"agreement={r.get('agreement')} relay_posts={len(relays)}")
        pg.screenshot(path=os.path.join(OUT, f"{key}_signed.png"))
        ctx.close()
        return h, r
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, f"{key}_fail.png"), full_page=True)
        log(f"{key} signing", False, str(e)[:200])
        ctx.close()
        return {}, {}


def signed_copy(b, url, key):
    for w, h in [(390, 844), (1366, 800)]:
        ctx = new_ctx(b, w, h, accept_downloads=True); pg = ctx.new_page()
        n_hook, n_relay = len(captured["hook"]), len(captured["relay"])
        pg.goto(url, wait_until="load"); settle(pg); pg.wait_for_timeout(1500)
        i = pg.evaluate("""() => {
          const btn = [...document.querySelectorAll('.signedhero .btn')][0];
          const cue = document.querySelector('.signedhero .cue');
          const eb = document.querySelector('.oyss .stage .eyebrow');
          const lead = document.querySelector('.oyss .stage .lead');
          const r = btn ? btn.getBoundingClientRect() : null;
          return {title: document.title, eyebrow: eb && eb.textContent, lead: lead && lead.textContent.slice(0, 90),
                  btnBottom: r && Math.round(r.bottom), vh: innerHeight, cue: !!cue,
                  ovf: document.documentElement.scrollWidth - innerWidth};
        }""")
        first_screen = i["btnBottom"] is not None and i["btnBottom"] <= i["vh"]
        ok = (i["eyebrow"] or "").strip() == "Signed copy" and (i["lead"] or "").startswith("Signed by TEST QA Signer") \
            and first_screen and i["cue"] and i["ovf"] <= 0
        pg.screenshot(path=os.path.join(OUT, f"{key}_copy_{w}.png"))
        log(f"{key}: signed-copy link at {w}: header, download and signature link on the first screen", ok, json.dumps(i))
        try:
            with pg.expect_download(timeout=30000) as d:
                pg.click(".signedhero .btn")
            p = os.path.join(OUT, f"{key}_copy_{w}_" + d.value.suggested_filename)
            d.value.save_as(p)
            log(f"{key}: signed-copy link at {w}: PDF downloads", open(p, "rb").read(5) == b"%PDF-", os.path.basename(p))
        except Exception as e:
            log(f"{key}: signed-copy link at {w}: PDF downloads", False, str(e)[:160])
        log(f"{key}: viewing the copy posts nothing", len(captured["hook"]) == n_hook and len(captured["relay"]) == n_relay)
        ctx.close()


def relay_dry(r, key):
    """The captured payload, posted to the LIVE relay in dry mode with the test key."""
    tk = open("E:/_shared/secrets/oyss_docs_test.txt").read().strip()
    body = dict(r, dry=True)
    req = urllib.request.Request("https://roguecoachteams.com/relay/oyss-docs.php", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "text/plain;charset=UTF-8", "X-OYSS-Test": tk,
                                          "User-Agent": "Mozilla/5.0 oyss-live-check"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            j = json.loads(resp.read().decode())
            code = resp.status
    except urllib.error.HTTPError as e:
        code, j = e.code, {"body": e.read().decode()[:200]}
    ok = code == 200 and j.get("dry") and j.get("pdf_bytes", 0) > 1000
    log(f"{key}: live relay accepts the page's payload (dry, nothing sent)", ok,
        f"{code} subject={j.get('subject')!r} file={j.get('filename')!r} bytes={j.get('pdf_bytes')}")
    if j.get("html"):
        open(os.path.join(OUT, f"{key}_relay_email.html"), "w", encoding="utf-8").write(j["html"])


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    which = sys.argv[1:] or ["pages", "exit", "sign"]
    if "pages" in which: pages(b)
    if "exit" in which: exit_popup(b)
    if "sign" in which:
        for path, key in [("/panelist-agreement", "panelist"), ("/host-agreement", "host")]:
            h, r = sign(b, path, key)
            if h.get("signed_copy_url"):
                signed_copy(b, h["signed_copy_url"], key)
            if r:
                relay_dry(r, key)
    b.close()

json.dump({"results": results, "hook_tags": [h.get("tag") for h in captured["hook"]]},
          open(os.path.join(OUT, "results.json"), "w"), indent=1)
print(f"\n{sum(r['ok'] for r in results)}/{len(results)} passed; intercepted webhook posts "
      f"{len(captured['hook'])}, relay posts {len(captured['relay'])} (none reached GHL or the relay)")
