#!/usr/bin/env python3
"""
Own Your Stage Studio - rendered-page probe.

Contrast bugs and overflow bugs are invisible in source. This drives the
system Chrome over the built site and measures the things that have actually
broken on this project before:

  1. horizontal overflow  (documentElement.scrollWidth - clientWidth)
  2. WCAG AA contrast on every rendered text node, against the color that
     is really behind it, walking up through transparent ancestors
  3. where the hero's primary action lands against the fold
  4. tap-target size on the small widths

    python _build/audit.py              probe every page at every width
    python _build/audit.py --shots      also write screenshots to _build/shots

Serve the site first:  python -m http.server 8899
"""

import sys, json, pathlib
from playwright.sync_api import sync_playwright

ROOT = "http://127.0.0.1:8899/"
PAGES = ["index.html", "experience.html", "assessment.html", "panelists.html",
         "about.html", "faq.html", "apply.html", "contact.html",
         "apply-panelist.html", "agreements/host.html", "agreements/panelist.html"]
WIDTHS = [(390, 844), (768, 1024), (1024, 768), (1366, 768), (1440, 900), (1536, 825), (1920, 1080)]
SHOT_AT = [(390, 844), (1366, 768), (1440, 900)]

# The probe reads computed color, so it needs to know what "behind" means when
# an element is transparent. Everything else is measured, not assumed.
PROBE = r"""
(() => {
  const out = { overflow: 0, escapes: [], contrast: [], small: [] };
  const de = document.documentElement;
  out.overflow = de.scrollWidth - de.clientWidth;

  const parse = c => {
    const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(s => parseFloat(s));
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const over = (fg, bg) => ({          // fg composited onto bg
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1 });
  const lum = c => {
    const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); };
    return .2126 * f(c.r) + .7152 * f(c.g) + .0722 * f(c.b);
  };
  const ratio = (a, b) => {
    const l1 = lum(a), l2 = lum(b);
    return (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
  };
  const ground = el => {
    let bg = { r: 255, g: 255, b: 255, a: 1 }, stack = [], n = el;
    while (n && n.nodeType === 1) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0) { stack.push(c); if (c.a === 1) break; }
      n = n.parentElement;
    }
    for (let i = stack.length - 1; i >= 0; i--) bg = over(stack[i], bg);
    return bg;
  };

  const vw = innerWidth, vh = innerHeight;
  document.querySelectorAll('.oyss *').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < .12) return;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return;

    // does a non-decorative box leave the viewport sideways?
    // .skip is the keyboard skip link, parked off-screen on purpose.
    if ((r.right > vw + 1 || r.left < -1) && !el.classList.contains('skip')) {
      if (!el.hasAttribute('aria-hidden') && el.textContent.trim())
        out.escapes.push({ sel: el.className || el.tagName, left: Math.round(r.left), right: Math.round(r.right) });
    }

    // contrast, on text nodes only.
    // Type sitting on a transparent masthead over the hero footage has no
    // DOM color behind it, so a color walk reports the page ground and
    // lies. Those are measured from real pixels in mastheadContrast().
    const overFilm = el.closest && el.closest('.masthead--over');
    const own = !overFilm && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own) {
      const fg = parse(cs.color); if (!fg) return;
      const bg = ground(el);
      const cr = ratio(over(fg, bg), bg);
      const px = parseFloat(cs.fontSize);
      const bold = parseInt(cs.fontWeight, 10) >= 700;
      const large = px >= 24 || (px >= 18.66 && bold);
      const floor = large ? 3 : 4.5;
      if (cr < floor) out.contrast.push({
        sel: (el.className || el.tagName).toString().slice(0, 60),
        text: el.textContent.trim().slice(0, 46),
        ratio: Math.round(cr * 100) / 100, floor, px: Math.round(px * 10) / 10
      });
    }

    // Tap targets. WCAG 2.2 SC 2.5.8 exempts a target that is inline in a
    // sentence, so an inline <a> in running prose is not a finding.
    if (vw <= 768 && (el.tagName === 'A' || el.tagName === 'BUTTON' || el.tagName === 'INPUT')) {
      if (r.height > 0 && r.height < 24 && el.textContent.trim() && cs.display !== 'inline')
        out.small.push({ sel: (el.className || el.tagName).toString().slice(0, 40), h: Math.round(r.height) });
    }
  });

  const cta = document.querySelector('.reel__copy .btn--primary');
  if (cta) { const r = cta.getBoundingClientRect(); out.cta = { top: Math.round(r.top), bottom: Math.round(r.bottom), vh: Math.round(vh) }; }
  return out;
})()
"""

# The finished state of the page. [data-lit] is the reveal; .cuerow is lit by
# its own rail observer as the reader passes it, so both have to be forced or
# the probe measures a state no reader ever sits in.
LIGHT_ALL = ("document.querySelectorAll('[data-lit], .cuerow, .dimmer__cell')"
             ".forEach(e=>e.classList.add('lit'));")

# --------------------------------------------------------------------------
# The masthead over the footage.
#
# On every page the bar starts transparent and the hero runs up underneath it,
# so what is behind the navigation is a moving picture, not a CSS color. A DOM
# color walk cannot see that and will happily report the page background.
#
# This measures it properly: screenshot the strip, hide the type, screenshot
# again, and take the WORST (brightest) background pixel inside each link box.
# Ivory on the brightest part of a beam is the failure case, and it is the one
# the scrim in section 36.2 exists to prevent.
# --------------------------------------------------------------------------

def _lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def masthead_contrast(page, tmp):
    from PIL import Image
    boxes = page.evaluate("""
      [...document.querySelectorAll('.masthead nav a, .masthead .lockup__name, .masthead .lockup__desc')]
        .map(el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
          return { t: el.textContent.trim().slice(0,24), x: r.left, y: r.top, w: r.width, h: r.height,
                   color: cs.color, px: parseFloat(cs.fontSize),
                   bold: parseInt(cs.fontWeight,10) >= 700 }; })
        .filter(b => b.w > 2 && b.h > 2)
    """)
    if not boxes:
        return []
    page.evaluate("document.querySelectorAll('.masthead nav a, .masthead .lockup__type').forEach(e=>e.style.visibility='hidden')")
    page.screenshot(path=str(tmp), clip={"x": 0, "y": 0, "width": page.viewport_size["width"],
                                         "height": min(200, page.viewport_size["height"])})
    page.evaluate("document.querySelectorAll('.masthead nav a, .masthead .lockup__type').forEach(e=>e.style.visibility='')")
    im = Image.open(tmp).convert("RGB")
    bad = []
    for b in boxes:
        x0, y0 = max(0, int(b["x"])), max(0, int(b["y"]))
        x1, y1 = min(im.width, int(b["x"] + b["w"])), min(im.height, int(b["y"] + b["h"]))
        if x1 <= x0 or y1 <= y0:
            continue
        px = list(im.crop((x0, y0, x1, y1)).getdata())
        worst = max(px, key=_lum)                       # brightest ground = worst case
        fg = [float(v) for v in __import__("re").findall(r"[\d.]+", b["color"])[:3]]
        l1, l2 = _lum(fg), _lum(worst)
        cr = (max(l1, l2) + .05) / (min(l1, l2) + .05)
        large = b["px"] >= 24 or (b["px"] >= 18.66 and b["bold"])
        floor = 3.0 if large else 4.5
        if cr < floor:
            bad.append({"t": b["t"], "ratio": round(cr, 2), "floor": floor,
                        "ground": worst, "px": b["px"]})
    return bad


def main():
    global shotdir_tmp
    shots = "--shots" in sys.argv
    shotdir = pathlib.Path(__file__).parent / "shots"
    shotdir.mkdir(exist_ok=True)
    shotdir_tmp = shotdir / "_mast.png"

    probes = fails = 0
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        for w, h in WIDTHS:
            page = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            for path in PAGES:
                page.goto(ROOT + path, wait_until="load")
                page.evaluate(LIGHT_ALL)
                page.wait_for_timeout(260)
                r = page.evaluate(PROBE)
                probes += 1
                mast = masthead_contrast(page, shotdir_tmp)
                bad = r["overflow"] > 1 or r["contrast"] or r["escapes"] or mast
                if mast:
                    print(f"\n  {path}  @{w}   MASTHEAD OVER FOOTAGE")
                    for m in mast:
                        print(f"     {m['ratio']}:1 (needs {m['floor']}) {m['px']}px  \"{m['t']}\"  worst ground rgb{tuple(m['ground'])}")
                if bad:
                    fails += 1
                    print(f"\n  {path}  @{w}")
                    if r["overflow"] > 1:
                        print(f"     OVERFLOW  {r['overflow']}px")
                    for c in r["contrast"][:8]:
                        print(f"     CONTRAST  {c['ratio']}:1 (needs {c['floor']}) {c['px']}px  .{c['sel']}  \"{c['text']}\"")
                    for e in r["escapes"][:4]:
                        print(f"     ESCAPES   .{e['sel']}  {e['left']}..{e['right']}")
                if r.get("small"):
                    for s in r["small"][:4]:
                        print(f"     small tap .{s['sel']} {s['h']}px  ({path} @{w})")
                if path == "index.html" and r.get("cta"):
                    c = r["cta"]
                    mark = "OK " if c["bottom"] <= c["vh"] else "BELOW FOLD"
                    print(f"  hero CTA @{w}x{h}: {c['top']}..{c['bottom']} of {c['vh']}  {mark}")
                if shots and (w, h) in SHOT_AT and path in ("index.html", "about.html"):
                    page.screenshot(path=str(shotdir / f"{path.replace('/','_')}-{w}.png"), full_page=True)
            page.close()
        b.close()
    print(f"\n{probes} probes, {fails} with findings")


if __name__ == "__main__":
    main()
