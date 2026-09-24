"""Rerun of the three flows user_test.py could not drive: assessment, host application,
home "Let's talk" GHL form. Desktop and mobile. TEST data on example.com, unique phones."""
import os, sys, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(__file__))

BASE = "https://ownyourstagestudio.com"
OUT = os.path.join(os.path.dirname(__file__), "usertest")
STAMP = time.strftime("%H%M%S")
res = []


def log(n, ok, note=""):
    res.append((n, ok)); print(("PASS " if ok else "FAIL ") + n + (f"  ({note})" if note else ""), flush=True)


def settle(pg):
    try: pg.wait_for_selector(".oyss-mount .oyss", timeout=20000)
    except Exception: pass
    pg.wait_for_timeout(1500)


def assessment(ctx, label):
    pg = ctx.new_page(); pg.goto(BASE + "/assessment", wait_until="load"); settle(pg)
    try:
        for q in range(1, 13):
            lab = pg.locator(f"fieldset[data-q='{q}'] label.choice").nth(2)
            lab.scroll_into_view_if_needed(); lab.click(); pg.wait_for_timeout(1200)
        btn = pg.locator("#assessment-form button[type=submit]")
        btn.scroll_into_view_if_needed(); btn.click()
        pg.wait_for_selector("#assessment-result:not([hidden])", timeout=10000)
        log(f"{label} assessment result", True, pg.inner_text("#result-pct") + " " + pg.inner_text("#result-level"))
        with pg.expect_download(timeout=30000) as d:
            pg.locator("#result-pdf").click()
        log(f"{label} assessment PDF", d.value.suggested_filename.endswith(".pdf"), d.value.suggested_filename)
        pg.fill("#result-mail [name=first_name]", "TEST")
        pg.fill("#result-mail [name=email]", f"oyss-test4-assess-{label}-{STAMP}@example.com")
        pg.locator("#result-mail button[type=submit]").click()
        pg.wait_for_selector("#result-mail-done:not([hidden])", timeout=15000)
        log(f"{label} assessment email", True, pg.inner_text("#result-mail-done")[:60])
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, f"{label}_assessment_fail.png"), full_page=True)
        log(f"{label} assessment", False, str(e)[:200])
    pg.close()


def fill_visible(pg, f, label, phone):
    for el in f.locator("input, textarea, select").all():
        try:
            t = (el.get_attribute("type") or "").lower(); n = (el.get_attribute("name") or "").lower()
            if t in ("hidden", "submit", "button"): continue
            if t in ("radio", "checkbox"):
                lab = el.locator("xpath=ancestor::label[1]")
                vis = lab.count() and lab.first.is_visible()
                if not vis: continue
                if t == "radio" and f.locator(f"input[name='{el.get_attribute('name')}']:checked").count(): continue
                if not el.is_checked(): el.check(force=True)
                continue
            if not el.is_visible() or el.input_value(): continue
            if el.evaluate("e => e.tagName") == "SELECT": el.select_option(index=1); continue
            if t == "email": el.fill(f"oyss-test4-host-{label}-{STAMP}@example.com")
            elif t == "tel": el.fill(phone)
            elif t == "url": el.fill("https://example.com")
            elif t == "number": el.fill("5")
            elif t == "date": el.fill("2026-10-15")
            elif n == "name": el.fill("TEST Claude")
            elif n == "business": el.fill("TEST Claude Consulting")
            elif "first" in n: el.fill("TEST")
            elif "last" in n: el.fill("Claude")
            else: el.fill("Test submission from the site QA run. Please ignore.")
        except Exception as e:
            print("   skip field", n, str(e)[:80])


def host_app(ctx, label, phone):
    pg = ctx.new_page(); pg.goto(BASE + "/apply", wait_until="load"); settle(pg)
    try:
        f = pg.locator("#host-application")
        for step in range(20):
            fill_visible(pg, f, label, phone)
            sub = f.locator("button[type=submit]")
            if sub.is_visible():
                pg.wait_for_timeout(500); sub.click(timeout=10000); break
            nxt = f.locator(".quiz__next")
            print("   step", step + 1, pg.inner_text("#host-application .quiz__count"))
            nxt.click(timeout=10000); pg.wait_for_timeout(1200)
        pg.wait_for_selector("#apply-done:not([hidden])", timeout=20000)
        log(f"{label} host application", True, " ".join(pg.inner_text("#apply-done").split())[:60])
    except Exception as e:
        err = pg.evaluate("() => [...document.querySelectorAll('[role=alert], .quiz__hint')].filter(e=>!e.hidden && e.offsetParent).map(e=>e.innerText).join(' | ')")
        pg.screenshot(path=os.path.join(OUT, f"{label}_host_fail.png"), full_page=True)
        log(f"{label} host application", False, (str(e)[:150] + " || " + err)[:300])
    pg.close()


def lets_talk(ctx, label, phone):
    pg = ctx.new_page(); pg.goto(BASE + "/home", wait_until="load"); settle(pg)
    try:
        sel = "iframe[src*='dvJo5tJIIPvpcprpSPcc']"
        pg.wait_for_selector(sel, state="attached", timeout=30000)
        pg.locator(sel).scroll_into_view_if_needed(); pg.wait_for_timeout(4000)
        fr = pg.frame_locator(sel)
        fr.locator("input:visible").first.wait_for(timeout=45000)
        inputs = fr.locator("input:visible, textarea:visible")
        n = inputs.count(); print("  lets-talk inputs:", n)
        for i in range(n):
            el = inputs.nth(i)
            t = (el.get_attribute("type") or "text").lower()
            nm = ((el.get_attribute("name") or "") + " " + (el.get_attribute("placeholder") or "")).lower()
            if t == "checkbox": el.check(force=True); continue
            if t in ("submit", "hidden", "radio"): continue
            if t == "email" or "email" in nm: el.fill(f"oyss-test4-letstalk-{label}-{STAMP}@example.com")
            elif t == "tel" or "phone" in nm: el.fill(phone)
            elif "first" in nm: el.fill("TEST")
            elif "last" in nm: el.fill("Claude")
            else: el.fill("Test message from the site QA run. Please ignore.")
        fr.locator("button").last.click(timeout=10000)
        pg.wait_for_timeout(6000)
        txt = fr.locator("body").inner_text()[:300].replace("\n", " ")
        ok = any(w in txt.lower() for w in ("thank", "received", "success", "submitted", "reply"))
        pg.screenshot(path=os.path.join(OUT, f"{label}_letstalk.png"))
        log(f"{label} Let's talk form", ok, txt[:100])
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, f"{label}_letstalk_fail.png"))
        log(f"{label} Let's talk form", False, str(e)[:200])
    pg.close()


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for label, (w, h), ph in [("desktop", (1366, 800), "+13055550181"), ("mobile", (390, 844), "+13055550191")]:
        ctx = b.new_context(viewport={"width": w, "height": h}, accept_downloads=True,
                            is_mobile=(label == "mobile"), has_touch=(label == "mobile"))
        host_app(ctx, label, ph)
        lets_talk(ctx, label, ph[:-1] + "2")
        ctx.close()
    b.close()
print(f"{sum(1 for r in res if r[1])}/{len(res)} passed")
