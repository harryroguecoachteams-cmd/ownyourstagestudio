"""Full visitor test of the live GHL site, desktop and mobile.

Pages: mount, JS errors, broken images, sideways scroll, internal links, widgets.
Flows: mobile menu, assessment (answer, email result, PDF), host + panelist
applications, both agreements (sign), home "Let's talk" GHL form, calendar and
payment links. Every submission uses TEST data on example.com addresses.
"""
import json, os, sys, time, urllib.request
from playwright.sync_api import sync_playwright

BASE = "https://ownyourstagestudio.com"
PATHS = ["/home", "/services", "/experience", "/assessment", "/panelists", "/about-us", "/faq",
         "/apply", "/strategy-session", "/panelist-application", "/host-agreement",
         "/panelist-agreement", "/terms", "/privacy", "/disclaimer"]
OUT = os.path.join(os.path.dirname(__file__), "usertest")
os.makedirs(OUT, exist_ok=True)
STAMP = time.strftime("%H%M%S")
results, links = [], set()


def log(name, ok, note=""):
    results.append((name, ok, note))
    print(("PASS " if ok else "FAIL ") + name + (f"  ({note})" if note else ""), flush=True)


def settle(pg):
    try:
        pg.wait_for_selector(".oyss-mount .oyss", timeout=20000)
    except Exception:
        pass
    pg.wait_for_timeout(1200)


def scroll_all(pg):
    for _ in range(30):
        pg.mouse.wheel(0, 900)
        pg.wait_for_timeout(40)
    pg.wait_for_timeout(800)


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
    else if (el.tagName === 'TEXTAREA') el.value = 'Test submission from the site QA run. Please ignore.';
    else if (/first/i.test(n)) el.value = 'TEST';
    else if (/last/i.test(n)) el.value = 'Claude';
    else el.value = 'TEST Claude';
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
  });
  return 'ok';
}"""


def page_checks(ctx, label):
    for path in PATHS:
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)[:140]))
        pg.on("response", lambda r: bad.append(f"{r.status} {r.url[-60:]}")
              if r.status >= 400 and ("filesafe" in r.url or "ownyourstagestudio" in r.url) else None)
        pg.goto(BASE + path, wait_until="load", timeout=60000)
        settle(pg)
        scroll_all(pg)
        info = pg.evaluate("""() => ({
          mounted: !!document.querySelector('.oyss-mount .oyss'),
          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
          broken: [...document.querySelectorAll('.oyss-mount img')].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src.slice(-40)),
          links: [...document.querySelectorAll('.oyss-mount a[href^="/"]')].map(a => a.getAttribute('href').split('#')[0]),
          ext: [...document.querySelectorAll('.oyss-mount a[href^="http"]')].map(a => a.href),
          title: document.title
        })""")
        links.update(info["links"])
        links.update(u for u in info["ext"] if "fastpaydirect" in u or "ownyourstagestudio" in u)
        probs = []
        if not info["mounted"]: probs.append("not mounted")
        if info["overflow"] > 1: probs.append(f"sideways scroll {info['overflow']}px")
        if info["broken"]: probs.append("broken img " + ",".join(info["broken"]))
        if errs: probs.append("JS: " + errs[0])
        if bad: probs.append("HTTP " + bad[0])
        log(f"{label} {path}", not probs, "; ".join(probs) or info["title"][:50])
        if path in ("/home", "/experience", "/about-us", "/host-agreement") :
            pg.screenshot(path=os.path.join(OUT, f"{label}{path.replace('/', '_')}.png"), full_page=True)
        pg.close()


def mobile_menu(ctx):
    pg = ctx.new_page(); pg.goto(BASE + "/home", wait_until="load"); settle(pg)
    try:
        pg.click("button.burger", timeout=8000); pg.wait_for_timeout(700)
        exp = pg.get_attribute("button.burger", "aria-expanded")
        vis = pg.is_visible("#primary-nav a >> nth=0")
        pg.screenshot(path=os.path.join(OUT, "mobile_menu.png"))
        log("mobile menu opens", exp == "true" and vis, f"expanded={exp} link visible={vis}")
        pg.click("#primary-nav a[href*='assessment']", timeout=8000)
        pg.wait_for_load_state("load"); settle(pg)
        log("mobile menu link navigates", "assessment" in pg.url, pg.url)
    except Exception as e:
        log("mobile menu", False, str(e)[:120])
    pg.close()


def assessment(ctx, label):
    pg = ctx.new_page(); pg.goto(BASE + "/assessment", wait_until="load"); settle(pg)
    try:
        for i in range(40):
            vis = pg.locator("#assessment-form fieldset[data-q]:visible")
            if vis.count() == 0: break
            opts = vis.first.locator("input[type=radio]")
            opts.nth(min(2, opts.count() - 1)).check(force=True)
            pg.wait_for_timeout(700)
            if pg.is_visible("#assessment-form button[type=submit]"):
                break
        pg.click("#assessment-form button[type=submit]", timeout=8000)
        pg.wait_for_selector("#assessment-result:not([hidden])", timeout=10000)
        pct = pg.inner_text("#result-pct")
        lvl = pg.inner_text("#result-level")
        log(f"{label} assessment result shown", True, f"{pct} {lvl}")
        with pg.expect_download(timeout=20000) as d:
            pg.click("#result-pdf")
        name = d.value.suggested_filename
        log(f"{label} assessment PDF download", name.endswith(".pdf"), name)
        pg.fill("#result-mail [name=first_name]", "TEST")
        pg.fill("#result-mail [name=email]", f"oyss-test3-assess-{label}-{STAMP}@example.com")
        pg.click("#result-mail button[type=submit]")
        pg.wait_for_selector("#result-mail-done:not([hidden])", timeout=15000)
        log(f"{label} assessment email result", True, pg.inner_text("#result-mail-done")[:60])
        pg.screenshot(path=os.path.join(OUT, f"{label}_assessment_result.png"), full_page=False)
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, f"{label}_assessment_fail.png"))
        log(f"{label} assessment flow", False, str(e)[:160])
    pg.close()


def app_form(ctx, label, path, form, done, key, phone):
    pg = ctx.new_page(); pg.goto(BASE + path, wait_until="load"); settle(pg)
    try:
        r = pg.evaluate(FILL, [f"#{form}", f"oyss-test3-{key}-{label}-{STAMP}@example.com", phone])
        pg.click(f"#{form} [type=submit]", timeout=8000)
        pg.wait_for_selector(f"#{done}:not([hidden])", timeout=15000)
        log(f"{label} {key} submit", True, pg.inner_text(f"#{done}")[:70].replace("\n", " "))
    except Exception as e:
        err = pg.evaluate("() => [...document.querySelectorAll('[role=alert]:not([hidden]), .notice--action:not([hidden])')].map(e=>e.innerText).join(' | ')")
        pg.screenshot(path=os.path.join(OUT, f"{label}_{key}_fail.png"), full_page=True)
        log(f"{label} {key} submit", False, (str(e)[:100] + " " + err)[:200])
    pg.close()


def agreement(ctx, label, path, key, phone, paylink):
    pg = ctx.new_page(); pg.goto(BASE + path, wait_until="load"); settle(pg)
    try:
        pg.evaluate("document.getElementById('agreement-end') && document.getElementById('agreement-end').scrollIntoView()")
        scroll_all(pg)
        pg.wait_for_timeout(800)
        pg.evaluate(FILL, ["#agreement-form", f"oyss-test3-{key}-{label}-{STAMP}@example.com", phone])
        pg.click("#agreement-form [type=submit]", timeout=8000)
        pg.wait_for_selector("#signed-state:not([hidden])", timeout=15000)
        hrefs = pg.evaluate("() => [...document.querySelectorAll('#signed-state a')].map(a=>a.href)")
        demo = "Demonstration build" in pg.inner_text("#signed-state")
        ok = (paylink in " ".join(hrefs)) and not demo
        log(f"{label} {key} sign", ok, f"pay links={len([h for h in hrefs if 'fastpay' in h])} demo text={demo}")
        pg.screenshot(path=os.path.join(OUT, f"{label}_{key}_signed.png"))
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, f"{label}_{key}_fail.png"), full_page=True)
        log(f"{label} {key} sign", False, str(e)[:160])
    pg.close()


def lets_talk(ctx, label, phone):
    pg = ctx.new_page(); pg.goto(BASE + "/home", wait_until="load"); settle(pg)
    try:
        fr_el = pg.wait_for_selector("iframe[src*='widget/form/dvJo5tJIIPvpcprpSPcc']", timeout=20000)
        fr_el.scroll_into_view_if_needed(); pg.wait_for_timeout(2500)
        fr = fr_el.content_frame()
        fr.wait_for_selector("input", timeout=20000)
        email = f"oyss-test3-letstalk-{label}-{STAMP}@example.com"
        for inp in fr.query_selector_all("input, textarea"):
            t = (inp.get_attribute("type") or "text").lower()
            nm = ((inp.get_attribute("name") or "") + (inp.get_attribute("placeholder") or "")).lower()
            if t in ("hidden", "submit"): continue
            if t == "checkbox": inp.check(force=True); continue
            if t == "email" or "email" in nm: inp.fill(email)
            elif t == "tel" or "phone" in nm: inp.fill(phone)
            elif "first" in nm: inp.fill("TEST")
            elif "last" in nm: inp.fill("Claude")
            else: inp.fill("Test message from the site QA run. Please ignore.")
        fr.click("button[type=submit], button:has-text('Submit'), button:has-text('Send')", timeout=8000)
        pg.wait_for_timeout(5000)
        txt = fr.inner_text("body")[:300].replace("\n", " ")
        ok = any(w in txt.lower() for w in ("thank", "received", "success", "submitted"))
        log(f"{label} home Let's talk form", ok, txt[:90])
        pg.screenshot(path=os.path.join(OUT, f"{label}_letstalk.png"))
        return email
    except Exception as e:
        log(f"{label} home Let's talk form", False, str(e)[:160])
    finally:
        pg.close()


def calendar(ctx, label):
    pg = ctx.new_page(); pg.goto(BASE + "/strategy-session", wait_until="load"); settle(pg)
    try:
        fr_el = pg.wait_for_selector("iframe[src*='widget/booking/cNJmGXJ4ed9YpmzNEElE']", timeout=20000)
        fr_el.scroll_into_view_if_needed(); pg.wait_for_timeout(6000)
        txt = fr_el.content_frame().inner_text("body")[:400].replace("\n", " ")
        log(f"{label} calendar widget loads", len(txt) > 40, txt[:90])
        pg.screenshot(path=os.path.join(OUT, f"{label}_calendar.png"))
    except Exception as e:
        log(f"{label} calendar widget loads", False, str(e)[:160])
    pg.close()


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for label, (w, h), phone in [("desktop", (1366, 800), "+13055550171"), ("mobile", (390, 844), "+13055550172")]:
        ctx = b.new_context(viewport={"width": w, "height": h}, accept_downloads=True,
                            is_mobile=(label == "mobile"), has_touch=(label == "mobile"))
        page_checks(ctx, label)
        if label == "mobile":
            mobile_menu(ctx)
        assessment(ctx, label)
        app_form(ctx, label, "/apply", "host-application", "apply-done", "host-app", phone)
        app_form(ctx, label, "/panelist-application", "panelist-application", "pan-done", "panelist-app", phone.replace("1", "3", 1) if False else phone[:-1] + "3")
        agreement(ctx, label, "/host-agreement", "host-agreement", phone[:-1] + "4", "6a8f2bcbf9c8c807930ba334")
        agreement(ctx, label, "/panelist-agreement", "panelist-agreement", phone[:-1] + "5", "6ab42a504ae1d45672839331")
        lets_talk(ctx, label, phone[:-1] + "6")
        calendar(ctx, label)
        ctx.close()
    b.close()

# every internal path and payment link answers
for u in sorted(links):
    url = u if u.startswith("http") else BASE + u
    try:
        code = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).status
    except Exception as e:
        code = getattr(e, "code", str(e)[:40])
    log(f"link {u[:70]}", code == 200, str(code))

fails = [r for r in results if not r[1]]
print(f"\n{len(results) - len(fails)}/{len(results)} passed")
json.dump(results, open(os.path.join(OUT, "results.json"), "w"), indent=1)
