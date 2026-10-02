"""REAL signing of both agreements on the live site (first run 2 Oct 2026, relay go-live).

Usage: python _build/live_sign_real.py [panelist] [host]   (default: both)

Unlike live_check_readonly.py nothing is intercepted: the GHL inbound webhook
runs the workflow, and the documents relay files the PDF in Annette's GHL and
emails it from events@. The signer is events+oyss-test@ownyourstagestudio.com,
so every email lands in her own inbox. Delete the TEST contact afterwards.
"""
import datetime, json, math, os, sys, time, urllib.request
from playwright.sync_api import sync_playwright

BASE = "https://ownyourstagestudio.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "livecheck", "real")
os.makedirs(OUT, exist_ok=True)
EMAIL = "events+oyss-test@ownyourstagestudio.com"
AGREEMENTS = {"panelist": "/panelist-agreement", "host": "/host-agreement"}
results = []


def relay_log():
    """The relay's own log (test key). The page's fetch to the relay is not
    reliably reported to Playwright, so the log line is the proof."""
    tk = open("E:/_shared/secrets/oyss_docs_test.txt").read().strip()
    req = urllib.request.Request("https://roguecoachteams.com/relay/oyss-docs.php",
                                 headers={"X-OYSS-Test": tk, "User-Agent": "Mozilla/5.0 oyss-live-check"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode()).get("log", [])


def log(name, ok, note=""):
    results.append({"name": name, "ok": bool(ok), "note": note})
    print(("PASS " if ok else "FAIL ") + name + (f"  ({note})" if note else ""), flush=True)


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
    else if (el.tagName === 'TEXTAREA') el.value = 'TEST signing by the web team. Please ignore.';
    else if (/first/i.test(n)) el.value = 'TEST';
    else if (/last/i.test(n)) el.value = 'QA';
    else if (/legal/i.test(n)) el.value = 'TEST QA Signer';
    else el.value = 'TEST QA';
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
  });
  return 'ok';
}"""


def sign(b, key, path):
    ctx = b.new_context(user_agent=UA, viewport={"width": 1366, "height": 800}, accept_downloads=True)
    pg = ctx.new_page()
    seen = {"hook": [], "relay": []}

    def on_resp(r):
        if r.request.method != "POST":
            return
        kind = "hook" if "/hooks/" in r.url else "relay" if "/relay/" in r.url else None
        if kind:
            try:
                body = r.text()[:300]
            except Exception:
                body = ""
            seen[kind].append((r.status, body))
    pg.on("response", on_resp)

    started = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    pg.goto(BASE + path, wait_until="load")
    pg.wait_for_selector(".oyss-mount .oyss", timeout=25000); pg.wait_for_timeout(1500)
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
    line = None
    for _ in range(18):  # the relay uploads + emails before it logs
        pg.wait_for_timeout(5000)
        new = [l for l in relay_log() if l[:25] >= started and l.split("\t")[1].startswith("agreement.")]
        line = next((l for l in new if l.split("\t")[2].startswith(key + " ") or "error" in l), None)
        if line:
            break
    pdf = open(os.path.join(OUT, name), "rb").read()
    log(f"{key}: signed on the live page, PDF downloaded", pdf[:5] == b"%PDF-", f"{name}, {len(pdf):,} bytes")
    log(f"{key}: workflow webhook", bool(seen["hook"]) and seen["hook"][-1][0] == 200, json.dumps(seen["hook"]))
    log(f"{key}: documents relay filed + emailed the PDF", bool(line) and "\tagreement.sent\t" in line, line or "no log line")
    pg.screenshot(path=os.path.join(OUT, f"{key}_signed.png"))
    ctx.close()
    return name


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    files = {}
    for key in (sys.argv[1:] or list(AGREEMENTS)):
        try:
            files[key] = sign(b, key, AGREEMENTS[key])
        except Exception as e:
            log(f"{key} signing", False, str(e)[:200])
    b.close()
    json.dump({"results": results, "files": files}, open(os.path.join(OUT, "result.json"), "w"), indent=1)
    print(f"\n{sum(r['ok'] for r in results)}/{len(results)} passed; files in {OUT}")
