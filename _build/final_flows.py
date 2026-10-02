"""Every visitor flow on the LIVE site, read-only (2 Oct 2026, before Annette's test round).

Usage: python _build/final_flows.py

Nothing reaches Annette's CRM or inbox: the inbound webhook and the documents
relay are intercepted (payload captured, fake success). The GHL "Let's talk"
form and the calendar are only rendered, never submitted. Agreements and the
exit pop-up are covered by live_check_readonly.py.
"""
import json, os, re, sys, urllib.request, urllib.error
from playwright.sync_api import sync_playwright

BASE = "https://ownyourstagestudio.com"
PATHS = ["/home", "/services", "/experience", "/assessment", "/panelists", "/about-us", "/faq",
         "/apply", "/strategy-session", "/panelist-application", "/host-agreement",
         "/panelist-agreement", "/terms", "/privacy", "/disclaimer"]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
UA_PHONE = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "livecheck", "flows")
os.makedirs(OUT, exist_ok=True)
EMAIL = "events+oyss-test@ownyourstagestudio.com"
results, captured = [], []
links = {}   # href -> set of pages it appears on


def log(name, ok, note=""):
    results.append({"name": name, "ok": bool(ok), "note": note})
    print(("PASS " if ok else "FAIL ") + name + (f"  ({note})" if note else ""), flush=True)


def ctx_for(b, w, h, **kw):
    phone = w < 500
    c = b.new_context(user_agent=UA_PHONE if phone else UA, viewport={"width": w, "height": h},
                      is_mobile=phone, has_touch=phone, **kw)
    cors = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "POST, OPTIONS"}

    def hook(route, req):
        if req.method == "OPTIONS":
            return route.fulfill(status=204, headers=cors)
        try:
            captured.append(json.loads(req.post_data or "{}"))
        except Exception:
            captured.append({"raw": (req.post_data or "")[:200]})
        route.fulfill(status=200, headers=cors, content_type="application/json", body='{"status":"Success: test intercept"}')
    c.route(re.compile(r"https://(services\.leadconnectorhq\.com/hooks|roguecoachteams\.com/relay)/.*"), hook)
    return c


def settle(pg):
    try:
        pg.wait_for_selector(".oyss-mount .oyss", timeout=25000)
    except Exception:
        pass
    pg.wait_for_timeout(1500)


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
    else if (el.tagName === 'TEXTAREA') el.value = 'TEST, read-only flow check. Nothing was sent.';
    else if (/first/i.test(n)) el.value = 'TEST';
    else if (/last/i.test(n)) el.value = 'QA';
    else el.value = 'TEST QA';
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
  });
  return 'ok';
}"""


def collect_links(b):
    for w, h in [(1366, 800), (390, 844)]:
        c = ctx_for(b, w, h)
        for path in PATHS:
            pg = c.new_page(); pg.goto(BASE + path, wait_until="load", timeout=60000); settle(pg)
            info = pg.evaluate("""() => ({
              links: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
              ids: [...document.querySelectorAll('[id]')].map(e => e.id),
              year: (document.querySelector('.oyss-mount footer, .oyss-mount .footer') || {innerText: ''}).innerText.match(/(©|&copy;|Copyright)\\s*(\\d{4})/)
            })""")
            for href in info["links"]:
                links.setdefault(href, set()).add(path)
                if href.startswith("#") and len(href) > 1 and href[1:] not in info["ids"]:
                    log(f"anchor {href} on {path} @{w}", False, "no element with that id")
            if w == 1366 and path == "/home":
                log("footer copyright year", bool(info["year"]) and info["year"][2] == "2026", str(info["year"]))
            pg.close()
        c.close()


def check_links():
    seen_fail = 0
    for href, where in sorted(links.items()):
        if href.startswith(("#", "javascript:")) or not href.strip():
            continue
        if href.startswith(("mailto:", "tel:", "sms:")):
            log(f"contact link {href}", re.match(r"^(mailto:[^@\s]+@[^@\s]+\.\w+|tel:\+?[\d\s()-]{7,}|sms:.+)", href) is not None, ", ".join(sorted(where))[:80])
            continue
        url = href if href.startswith("http") else BASE + (href if href.startswith("/") else "/" + href)
        url = url.split("#")[0]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                code, final = r.status, r.url
        except urllib.error.HTTPError as e:
            code, final = e.code, url
        except Exception as e:
            code, final = str(e)[:60], url
        ok = code == 200 or (isinstance(code, int) and code in (401, 403, 405, 429, 999) and "ownyourstagestudio" not in url)
        log(f"link {href[:90]}", ok, f"{code} final={final[:80]} on {', '.join(sorted(where))[:70]}")
        seen_fail += not ok


def nav_desktop(b):
    c = ctx_for(b, 1366, 800); pg = c.new_page(); pg.goto(BASE + "/home", wait_until="load"); settle(pg)
    try:
        info = pg.evaluate("""() => {
          const drop = document.querySelector('.navdrop');
          const btn = drop && drop.querySelector('button, .navdrop__btn, a');
          return {drop: !!drop, items: [...document.querySelectorAll('.masthead nav a')].map(a => a.textContent.trim() + ' -> ' + a.getAttribute('href'))};
        }""")
        log("desktop nav links", len(info["items"]) >= 5, " | ".join(info["items"])[:300])
        dd = pg.locator(".navdrop").first
        if dd.count():
            dd.hover(); pg.wait_for_timeout(600)
            vis = pg.evaluate("(()=>{const m=document.querySelector('.navdrop__menu'); if(!m) return null; const r=m.getBoundingClientRect(); return getComputedStyle(m).visibility!=='hidden' && r.height>20})()")
            pg.screenshot(path=os.path.join(OUT, "nav_dropdown_hover.png"))
            log("desktop 'What we do' dropdown opens on hover", bool(vis))
            pg.mouse.move(10, 600); pg.wait_for_timeout(500)
            pg.keyboard.press("Tab")
    except Exception as e:
        log("desktop nav", False, str(e)[:160])
    c.close()


def mobile_menu(b, w, h):
    c = ctx_for(b, w, h); pg = c.new_page(); pg.goto(BASE + "/home", wait_until="load"); settle(pg)
    try:
        burger = pg.locator("button.burger")
        if not burger.is_visible():
            log(f"menu button @{w}", w >= 1040, "no burger shown (desktop nav instead)")
            c.close(); return
        burger.click(); pg.wait_for_timeout(700)
        exp = burger.get_attribute("aria-expanded")
        n = pg.evaluate("[...document.querySelectorAll('#primary-nav a')].filter(a=>a.getBoundingClientRect().height>0).length")
        locked = pg.evaluate("getComputedStyle(document.body).overflow")
        pg.screenshot(path=os.path.join(OUT, f"menu_open_{w}.png"))
        log(f"menu opens @{w}", exp == "true" and n >= 5, f"links visible={n} body overflow={locked}")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
        log(f"menu closes on Escape @{w}", burger.get_attribute("aria-expanded") == "false")
        burger.click(); pg.wait_for_timeout(600)
        pg.locator("#primary-nav a[href*='faq']").first.click()
        pg.wait_for_load_state("load"); settle(pg)
        log(f"menu link navigates @{w}", "/faq" in pg.url, pg.url)
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, f"menu_fail_{w}.png"))
        log(f"mobile menu @{w}", False, str(e)[:160])
    c.close()


def assessment(b, w, h):
    c = ctx_for(b, w, h, accept_downloads=True); pg = c.new_page()
    pg.goto(BASE + "/assessment", wait_until="load"); settle(pg)
    n0 = len(captured)
    try:
        for q in range(1, 13):
            lab = pg.locator(f"fieldset[data-q='{q}'] label.choice").nth(2)
            lab.scroll_into_view_if_needed(); lab.click(); pg.wait_for_timeout(1100)
        btn = pg.locator("#assessment-form button[type=submit]")
        btn.scroll_into_view_if_needed(); btn.click()
        pg.wait_for_selector("#assessment-result:not([hidden])", timeout=10000)
        res = pg.inner_text("#result-pct") + " " + pg.inner_text("#result-level")
        pg.screenshot(path=os.path.join(OUT, f"assessment_result_{w}.png"))
        log(f"assessment result @{w}", True, res)
        try:
            with pg.expect_download(timeout=20000) as d:
                pg.click("#result-pdf")
            p = os.path.join(OUT, f"assessment_{w}_" + d.value.suggested_filename); d.value.save_as(p)
            log(f"assessment PDF @{w}", open(p, "rb").read(5) == b"%PDF-", os.path.basename(p))
        except Exception as e:
            log(f"assessment PDF @{w}", False, str(e)[:120])
        pg.fill("#result-mail [name=first_name]", "TEST")
        pg.fill("#result-mail [name=email]", EMAIL)
        pg.locator("#result-mail button[type=submit]").click()
        pg.wait_for_selector("#result-mail-done:not([hidden])", timeout=15000)
        got = captured[n0:]
        pay = got[-1] if got else {}
        log(f"assessment email-me-my-result @{w}", bool(got) and pay.get("email") == EMAIL,
            f"tag={pay.get('tag')} fields={len(pay)} done='{pg.inner_text('#result-mail-done')[:60]}'")
    except Exception as e:
        pg.screenshot(path=os.path.join(OUT, f"assessment_fail_{w}.png"), full_page=True)
        log(f"assessment @{w}", False, str(e)[:200])
    c.close()


def stepped(b, w, h, path, form, done, key):
    c = ctx_for(b, w, h); pg = c.new_page(); pg.goto(BASE + path, wait_until="load"); settle(pg)
    n0 = len(captured)
    try:
        # walk the stepper honestly first: Next with nothing filled must not advance
        nxt = pg.locator(f"#{form} .quiz__next")
        if nxt.count() and nxt.first.is_visible():
            nxt.first.click(); pg.wait_for_timeout(500)
            hint = pg.evaluate(f"[...document.querySelectorAll('#{form} [role=alert]:not([hidden]), #{form} .quiz__hint, #{form} :invalid')].length")
            log(f"{key} @{w}: empty step is stopped", hint > 0, f"hints/invalid={hint}")
        pg.evaluate(FILL, [f"#{form}", EMAIL, "+1 555 010 0199"])
        steps = 0
        for _ in range(8):
            nxt = pg.locator(f"#{form} .quiz__next:visible")
            if nxt.count():
                nxt.first.click(); pg.wait_for_timeout(600); steps += 1
            else:
                break
        pg.click(f"#{form} [type=submit]", timeout=8000)
        pg.wait_for_selector(f"#{done}:not([hidden])", timeout=20000)
        got = captured[n0:]
        pay = got[-1] if got else {}
        pg.screenshot(path=os.path.join(OUT, f"{key}_done_{w}.png"))
        log(f"{key} @{w}: submitted through {steps} steps", bool(got) and pay.get("email") == EMAIL,
            f"tag={pay.get('tag')} fields={len(pay)}")
    except Exception as e:
        err = pg.evaluate("() => [...document.querySelectorAll('[role=alert]:not([hidden]), .quiz__hint')].map(e=>e.innerText).join(' | ')")
        pg.screenshot(path=os.path.join(OUT, f"{key}_fail_{w}.png"), full_page=True)
        log(f"{key} @{w}", False, (str(e)[:120] + " " + err)[:220])
    c.close()


def lets_talk(b, w, h):
    c = ctx_for(b, w, h); pg = c.new_page(); pg.goto(BASE + "/home", wait_until="load"); settle(pg)
    try:
        fr_el = pg.wait_for_selector("iframe[src*='widget/form/']", timeout=20000)
        fr_el.scroll_into_view_if_needed(); pg.wait_for_timeout(3000)
        fr = fr_el.content_frame(); fr.wait_for_selector("input", timeout=20000)
        n = len(fr.query_selector_all("input:not([type=hidden]), textarea"))
        box = fr_el.bounding_box()
        inner_h = fr.evaluate("document.documentElement.scrollHeight")
        pg.screenshot(path=os.path.join(OUT, f"letstalk_{w}.png"))
        log(f"home Let's talk form renders @{w}", n >= 3 and box["width"] <= w,
            f"fields={n} frame {round(box['width'])}x{round(box['height'])} content h={inner_h}")
        if inner_h > box["height"] + 4:
            log(f"Let's talk form fits its frame @{w}", False, f"content {inner_h}px in a {round(box['height'])}px frame")
    except Exception as e:
        log(f"home Let's talk form @{w}", False, str(e)[:160])
    c.close()


def calendar(b, w, h):
    c = ctx_for(b, w, h); pg = c.new_page(); pg.goto(BASE + "/strategy-session", wait_until="load"); settle(pg)
    try:
        fr_el = pg.wait_for_selector("iframe[src*='widget/booking/']", timeout=20000)
        fr_el.scroll_into_view_if_needed(); pg.wait_for_timeout(7000)
        txt = fr_el.content_frame().inner_text("body")[:500].replace("\n", " ")
        box = fr_el.bounding_box()
        pg.screenshot(path=os.path.join(OUT, f"calendar_{w}.png"))
        log(f"calendar loads @{w}", len(txt) > 40 and box["width"] <= w, txt[:110])
    except Exception as e:
        log(f"calendar @{w}", False, str(e)[:160])
    c.close()


def faq(b):
    c = ctx_for(b, 390, 844); pg = c.new_page(); pg.goto(BASE + "/faq", wait_until="load"); settle(pg)
    try:
        n = pg.locator("details.qa").count()
        s = pg.locator("details.qa summary").first
        s.scroll_into_view_if_needed(); s.click(); pg.wait_for_timeout(400)
        log("FAQ answers open", n > 5 and pg.evaluate("document.querySelector('details.qa').open"), f"{n} questions")
    except Exception as e:
        log("FAQ", False, str(e)[:160])
    c.close()


def videos(b):
    for w, h in [(1366, 800), (390, 844)]:
        c = ctx_for(b, w, h)
        for path in ("/home", "/about-us", "/experience", "/services", "/panelists"):
            pg = c.new_page(); pg.goto(BASE + path, wait_until="load"); settle(pg)
            vids = pg.evaluate("[...document.querySelectorAll('.oyss-mount video')].map((v,i)=>({i, src: v.currentSrc || (v.querySelector('source')||{}).src || v.src, poster: v.poster}))")
            for v in vids:
                pg.evaluate(f"(()=>{{const v=document.querySelectorAll('.oyss-mount video')[{v['i']}]; v.scrollIntoView(); v.muted=true; return v.play().catch(()=>0)}})()")
                pg.wait_for_timeout(4000)
                st = pg.evaluate(f"(()=>{{const v=document.querySelectorAll('.oyss-mount video')[{v['i']}]; return {{rs: v.readyState, t: Math.round(v.currentTime*10)/10, err: v.error && v.error.code, dur: Math.round(v.duration)}}}})()")
                log(f"video {path} #{v['i']} @{w}", st["rs"] >= 2 and not st["err"], f"{(v['src'] or '')[-50:]} {st}")
            pg.close()
        c.close()


def pay_links():
    urls = sorted({h for h in links if "fastpaydirect" in h or "payment-link" in h})
    for u in urls:
        try:
            html = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30).read().decode("utf-8", "ignore")
            title = re.search(r"<title>(.*?)</title>", html, re.S)
            log(f"payment link {u[-24:]}", True, (title.group(1).strip() if title else "")[:80] + f" on {', '.join(sorted(links[u]))[:60]}")
        except Exception as e:
            log(f"payment link {u[-24:]}", False, str(e)[:100])
    return urls


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    collect_links(b)
    nav_desktop(b)
    for w, h in [(360, 740), (390, 844), (768, 1024), (1024, 768)]:
        mobile_menu(b, w, h)
    for w, h in [(390, 844), (1366, 800)]:
        assessment(b, w, h)
        stepped(b, w, h, "/apply", "host-application", "apply-done", "host application")
        stepped(b, w, h, "/panelist-application", "panelist-application", "pan-done", "panelist application")
        lets_talk(b, w, h)
        calendar(b, w, h)
    faq(b)
    videos(b)
    b.close()
check_links()
pay = pay_links()
json.dump({"results": results, "captured": captured, "links": {k: sorted(v) for k, v in links.items()}},
          open(os.path.join(OUT, "flows.json"), "w"), indent=1)
fails = [r for r in results if not r["ok"]]
print(f"\n{len(results) - len(fails)}/{len(results)} passed; intercepted posts {len(captured)}; payment links {len(pay)}")
