"""Live go-live test, 28 Sep 2026 (feedback 11-16 batch).

Real submissions to ownyourstagestudio.com with TEST data on plus-addresses of
the RCT inbox (roguecoachteams+oyss-...@gmail.com), so the emails can be read
back. Every webhook call to the GHL inbound webhook is recorded (status and
payload). Pages: mount, JS errors, sideways scroll, and the sticky bar / exit
pop-up only on the reading pages.
"""
import json, math, os, sys, time
from playwright.sync_api import sync_playwright

BASE = "https://ownyourstagestudio.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
OUT = os.path.join(os.path.dirname(__file__), "livetest_0928")
os.makedirs(OUT, exist_ok=True)
TAG = time.strftime("%H%M")
MAIL = lambda k: f"roguecoachteams+oyss-{k}-0928-{TAG}@gmail.com"
READING = {"/home", "/services", "/experience", "/panelists", "/about-us", "/faq"}
PATHS = ["/home", "/services", "/experience", "/assessment", "/panelists", "/about-us", "/faq",
         "/apply", "/strategy-session", "/panelist-application", "/host-agreement",
         "/panelist-agreement", "/terms", "/privacy", "/disclaimer"]
results, hooks = [], []


def log(name, ok, note=""):
    results.append({"name": name, "ok": bool(ok), "note": note})
    print(("PASS " if ok else "FAIL ") + name + (f"  ({note})" if note else ""), flush=True)


def settle(pg):
    try:
        pg.wait_for_selector(".oyss-mount .oyss", timeout=25000)
    except Exception:
        pass
    pg.wait_for_timeout(1500)


def watch(pg):
    def on_resp(r):
        if "leadconnectorhq.com/hooks" in r.url:
            try:
                body = json.loads(r.request.post_data or "{}")
            except Exception:
                body = {}
            hooks.append({"status": r.status, "tag": body.get("tag"), "email": body.get("email"), "payload": body})
    pg.on("response", on_resp)


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
    else if (el.type === 'number') el.value = '5';
    else if (el.type === 'date') el.value = '2026-11-12';
    else if (el.type === 'time') el.value = '12:00';
    else if (el.tagName === 'TEXAREA' || el.tagName === 'TEXTAREA') el.value = 'TEST submission from the go-live QA run. Please ignore.';
    else if (/first/i.test(n)) el.value = 'TEST';
    else if (/last/i.test(n)) el.value = 'QA';
    else if (/legal/i.test(n)) el.value = 'TEST QA Signer';
    else el.value = 'TEST QA';
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
  });
  return 'ok';
}"""


def pages(b):
    for w, h in [(1366, 800), (390, 844)]:
        ctx = b.new_context(user_agent=UA, viewport={"width": w, "height": h}, is_mobile=(w < 500), has_touch=(w < 500))
        for path in PATHS:
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
            pg.goto(BASE + path, wait_until="load", timeout=60000); settle(pg)
            info = pg.evaluate("""() => ({mounted: document.documentElement.classList.contains('oyss-mounted'),
                ovf: document.documentElement.scrollWidth - innerWidth,
                bar: !!document.querySelector('.prompt'), exit: !!document.querySelector('.exit'),
                orbit: !!document.querySelector('.orbit__stage')})""")
            want = path in READING
            ok = info["mounted"] and info["ovf"] <= 0 and not errs and info["bar"] == want and info["exit"] == want
            log(f"page {w} {path}", ok, json.dumps(info) + (" errs=" + "; ".join(errs) if errs else ""))
            pg.close()
        ctx.close()


def exit_lead(b):
    ctx = b.new_context(user_agent=UA, viewport={"width": 1366, "height": 800})
    pg = ctx.new_page(); watch(pg)
    pg.goto(BASE + "/home", wait_until="load"); settle(pg)
    pg.wait_for_timeout(6500)   # the exit trigger arms after 6 seconds
    pg.mouse.move(600, 300); pg.mouse.move(600, 2)
    pg.evaluate("document.dispatchEvent(new MouseEvent('mouseout', {clientY: 1, relatedTarget: null, bubbles: true}))")
    pg.wait_for_timeout(900)
    opened = pg.evaluate("(()=>{const e=document.querySelector('.exit'); return !!e && e.classList.contains('is-in')})()")
    log("exit pop-up opens on the live home page", opened)
    if opened:
        pg.screenshot(path=os.path.join(OUT, "exit_open.png"))
        pg.fill(".exit__form input[name=first_name]", "TEST")
        pg.fill(".exit__form input[name=email]", MAIL("exit"))
        pg.click(".exit__send"); pg.wait_for_timeout(2500)
        done = pg.evaluate("!document.querySelector('.exit__done').hidden")
        log("exit pop-up lead submitted, thank-you shown", done, MAIL("exit"))
        pg.screenshot(path=os.path.join(OUT, "exit_done.png"))
    ctx.close()


def draw(pg):
    cv = pg.query_selector("#sigpad-canvas"); cv.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
    bb = cv.bounding_box()
    x0, y0 = bb["x"] + bb["width"] * 0.12, bb["y"] + bb["height"] * 0.62
    pg.mouse.move(x0, y0); pg.mouse.down()
    for i in range(50):
        t = i / 49
        pg.mouse.move(x0 + t * bb["width"] * 0.6, y0 - math.sin(t * math.pi * 3) * bb["height"] * 0.2)
    pg.mouse.up()


def agreement(b, path, key):
    ctx = b.new_context(user_agent=UA, viewport={"width": 1366, "height": 800}, accept_downloads=True)
    pg = ctx.new_page(); watch(pg)
    pg.goto(BASE + path, wait_until="load"); settle(pg)
    try:
        pg.evaluate("document.getElementById('agreement-end').scrollIntoView()")
        for _ in range(8):
            pg.mouse.wheel(0, 900); pg.wait_for_timeout(120)
        pg.wait_for_timeout(800)
        pg.evaluate(FILL, ["#agreement-form", MAIL(key), "+1 555 010 0" + TAG[-3:]])
        draw(pg)
        with pg.expect_download(timeout=30000) as d:
            pg.click("#agreement-form [type=submit]")
        name = d.value.suggested_filename
        d.value.save_as(os.path.join(OUT, name))
        pg.wait_for_selector("#signed-state:not([hidden])", timeout=15000)
        log(f"{key} signed on the live page, PDF saved", name.endswith(".pdf"), name)
        pg.screenshot(path=os.path.join(OUT, f"{key}_signed.png"))
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, f"{key}_fail.png"), full_page=True)
        log(f"{key} signing", False, str(e)[:200])
    ctx.close()


def stepped(b, path, form, done, key, phone):
    ctx = b.new_context(user_agent=UA, viewport={"width": 1366, "height": 800})
    pg = ctx.new_page(); watch(pg)
    pg.goto(BASE + path, wait_until="load"); settle(pg)
    try:
        pg.evaluate(FILL, [f"#{form}", MAIL(key), phone])
        for _ in range(6):
            nxt = pg.locator(f"#{form} .quiz__next")
            if nxt.count() and nxt.is_visible():
                nxt.click(); pg.wait_for_timeout(700)
            else:
                break
        pg.click(f"#{form} [type=submit]", timeout=8000)
        pg.wait_for_selector(f"#{done}:not([hidden])", timeout=20000)
        log(f"{key} submitted through the stepper", True, MAIL(key))
    except Exception as e:
        err = pg.evaluate("() => [...document.querySelectorAll('[role=alert]:not([hidden]), .quiz__hint')].map(e=>e.innerText).join(' | ')")
        pg.screenshot(path=os.path.join(OUT, f"{key}_fail.png"), full_page=True)
        log(f"{key} submit", False, (str(e)[:120] + " " + err)[:220])
    ctx.close()


def assessment(b):
    ctx = b.new_context(user_agent=UA, viewport={"width": 1366, "height": 800}, accept_downloads=True)
    pg = ctx.new_page(); watch(pg)
    pg.goto(BASE + "/assessment", wait_until="load"); settle(pg)
    try:
        for q in range(1, 13):
            lab = pg.locator(f"fieldset[data-q='{q}'] label.choice").nth(2)
            lab.scroll_into_view_if_needed(); lab.click(); pg.wait_for_timeout(1200)
        btn = pg.locator("#assessment-form button[type=submit]")
        btn.scroll_into_view_if_needed(); btn.click()
        pg.wait_for_selector("#assessment-result:not([hidden])", timeout=10000)
        pg.fill("#result-mail [name=first_name]", "TEST")
        pg.fill("#result-mail [name=email]", MAIL("assess"))
        pg.locator("#result-mail button[type=submit]").click()
        pg.wait_for_selector("#result-mail-done:not([hidden])", timeout=15000)
        log("assessment result emailed", True, pg.inner_text("#result-pct") + " " + pg.inner_text("#result-level"))
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, "assessment_fail.png"), full_page=True)
        log("assessment", False, str(e)[:200])
    ctx.close()


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    which = sys.argv[1:] or ["pages", "exit", "agreements", "apps", "assessment"]
    if "pages" in which: pages(b)
    if "exit" in which: exit_lead(b)
    if "agreements" in which:
        agreement(b, "/panelist-agreement", "panagr")
        agreement(b, "/host-agreement", "hostagr")
    if "apps" in which:
        stepped(b, "/panelist-application", "panelist-application", "pan-done", "panapp", "+1 555 010 1" + TAG[-3:])
        stepped(b, "/apply", "host-application", "apply-done", "hostapp", "+1 555 010 2" + TAG[-3:])
    if "assessment" in which: assessment(b)
    b.close()

for h in hooks:
    print("WEBHOOK", h["status"], h["tag"], h["email"])
json.dump({"results": results, "hooks": hooks}, open(os.path.join(OUT, f"results_{TAG}.json"), "w"), indent=1)
print(f"\n{sum(r['ok'] for r in results)}/{len(results)} passed; webhooks {len(hooks)} "
      f"({sum(1 for h in hooks if h['status'] == 200)} with 200)")
