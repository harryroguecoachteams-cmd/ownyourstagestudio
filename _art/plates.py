#!/usr/bin/env python3
"""
Render the branded plates: the holding slide the site shows, and Annette's
Zoom stage backgrounds.

These are the only pictures on the project with the LOGO baked into them, so
when the identity changed they were the only ones that went stale in a way no
color grade could fix. Rather than repaint them, they are rendered out of the
site's own stylesheet through Chrome: the lockup here is the same lockup, from
the same CSS, in the same fonts, so a plate cannot drift from the site again
without the site drifting too.

Two layouts, matching the ones the old set had:

  holding    centered lockup, the tagline, STARTING SHORTLY. Nobody is on
             camera yet, so the middle of the frame is free.
  corner     lockup (host) or the mark alone (panelist) top left, and a name
             plate bottom right. The middle is where the person sits, so it
             stays empty.

    python -m http.server 8899      # from the site root
    python _art/plates.py
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SERVE = "http://127.0.0.1:8899/"

MARK = ('<svg class="mark" viewBox="0 0 64 58" aria-hidden="true">'
        '<path class="mark__a" d="M29 0 H35 L64 58 H53 L32 16 L11 58 H0 Z"/>'
        '<path class="mark__arch" d="M27.5 46.4 Q26.5 46.4 26.5 45.4 V42.5 '
        'a5.5 5.5 0 0 1 11 0 V45.4 Q37.5 46.4 36.5 46.4 Z"/></svg>')


def lockup(scale=1.0):
    return (f'<span class="lockup" style="--k:{scale}"><span class="lockup__type">'
            f'<span class="lockup__name"><span class="lockup__own">Own Your</span>'
            f'<span class="lockup__stage">St{MARK}ge</span></span>'
            f'<span class="lockup__desc">Studio</span></span></span>')


# key, output, layout, role, name, title
PLATES = [
    ("holding-slide", "assets/media/stage-holding-slide.jpg", "holding", None, None, None),
    ("stage-holding", "assets/stage-holding.png", "holding", None, None, None),
    ("virtual-stage", "assets/virtual-stage.png", "holding", None, None, None),
    ("stage-host", "assets/stage-host.png", "corner", "Host",
     "Annette Knecht Seier", "Founder, Own Your Stage Studio"),
    ("stage-panelist", "assets/stage-panelist.png", "corner", "Panelist",
     "Your Name Here", "Your Title Here"),
]


def page_html(layout, role, name, title, w, h):
    if layout == "holding":
        body = f"""
  <div class="plate__mid">
    {lockup()}
    <span class="plate__rule"></span>
    <p class="plate__sub">We build the stage. You steal the show.</p>
  </div>
  <p class="plate__strip">Starting shortly</p>"""
    else:
        # The full lockup belongs to the host frame and the mark alone to a
        # panelist's. That was the old set's rule and it is still the right one:
        # one plate is the studio's, the others are guests standing on it.
        corner = (f'<span class="plate__corner">{lockup(.78)}</span>'
                  if role == "Host"
                  else f'<span class="plate__corner plate__corner--icon">{MARK}</span>')
        body = f"""
  {corner}
  <div class="plate__name">
    <p class="plate__role">{role}</p>
    <p class="plate__who">{name}</p>
    <p class="plate__title">{title}</p>
  </div>"""

    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{SERVE}assets/oyss.css">
<style>
  html,body {{ margin:0; padding:0; background:#121110; }}
  .plate {{
    position:relative; width:{w}px; height:{h}px; overflow:hidden;
    background: linear-gradient(176deg, #211F1E 0%, #191817 46%, #111010 100%);
  }}
  /* the beam. A light cone has no edge, so the polygon is only the shape the
     blur is given to work on, and the blur is SVG's because a CSS filter over
     a clip-path came back as a polygon with a soft hem. */
  .plate__beam {{ position:absolute; inset:0; z-index:0; width:100%; height:100%; }}
  .plate__pool {{
    position:absolute; left:50%; top:76%; z-index:0;
    width:{round(w * 0.52)}px; height:{round(h * 0.20)}px; transform:translate(-50%,-50%);
    border-radius:50%;
    background: radial-gradient(50% 50% at 50% 50%,
      rgba(255,232,206,.16) 0%, rgba(255,226,200,.06) 46%, transparent 74%);
  }}
  /* the brand's ribbon, laid along the floor and kept under the type */
  .plate__silk {{
    position:absolute; left:0; bottom:0; width:100%; height:17%; z-index:0;
    background:url('{SERVE}assets/silk.svg') left bottom / 100% 100% no-repeat;
    opacity:.15; mix-blend-mode:screen;
  }}
  /* the stage lip: the red rule along the floor of every frame */
  .plate__lip {{
    position:absolute; left:{round(w * 0.045)}px; right:{round(w * 0.045)}px;
    bottom:{round(h * 0.052)}px; height:2px; z-index:2; border-radius:2px;
    background:linear-gradient(90deg, rgba(224,90,90,0) 0%, rgba(224,90,90,.62) 18%,
                                      rgba(224,90,90,.62) 82%, rgba(224,90,90,0) 100%);
  }}
  .plate__mid {{
    position:absolute; inset:0; z-index:3;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
  }}
  .plate .lockup__type {{ text-align:center; }}
  .plate .lockup__name {{ font-size:calc({round(w * 0.0335)}px * var(--k,1)); color:#F8F5F2; }}
  .plate .lockup__desc {{ font-size:calc({round(w * 0.0148)}px * var(--k,1));
                          letter-spacing:.62em; text-indent:.62em;
                          margin-top:calc({round(w * 0.012)}px * var(--k,1)); }}
  .plate__rule {{ width:{round(w * 0.050)}px; height:3px; border-radius:2px;
                  background:#E05A5A; margin-top:{round(w * 0.024)}px; }}
  .plate__sub {{
    margin:{round(w * 0.019)}px 0 0;
    font-family:var(--sans); font-style:italic; font-weight:400;
    font-size:{round(w * 0.0165)}px; color:#F3B0AE; letter-spacing:.01em;
  }}
  .plate__strip {{
    position:absolute; left:0; right:0; bottom:{round(h * 0.086)}px; z-index:3; margin:0;
    text-align:center; font-family:var(--serif); font-weight:600;
    font-size:{round(w * 0.0095)}px; letter-spacing:.42em; text-transform:uppercase;
    color:rgba(248,245,242,.46);
  }}
  /* the corner set: identification, kept out of the way of a face */
  .plate__corner {{
    position:absolute; left:{round(w * 0.045)}px; top:{round(h * 0.062)}px; z-index:3;
    display:block;
  }}
  .plate__corner--icon svg {{ width:{round(w * 0.026)}px; height:auto; display:block; }}
  .plate__corner--icon .mark__a,
  .plate__corner--icon .mark__arch {{ fill:#E05A5A; }}
  .plate__name {{
    position:absolute; right:{round(w * 0.045)}px; bottom:{round(h * 0.098)}px;
    z-index:3; text-align:right;
  }}
  .plate__role {{
    margin:0 0 {round(h * 0.010)}px; font-family:var(--serif); font-weight:600;
    font-size:{round(w * 0.0088)}px; letter-spacing:.34em; text-transform:uppercase;
    color:#E05A5A;
  }}
  .plate__who {{
    margin:0; font-family:var(--serif); font-weight:700;
    font-size:{round(w * 0.0225)}px; letter-spacing:-.005em; color:#F8F5F2;
  }}
  .plate__title {{
    margin:{round(h * 0.008)}px 0 0; font-family:var(--sans); font-weight:400;
    font-size:{round(w * 0.0108)}px; color:rgba(248,245,242,.62);
  }}
</style></head><body><div class="oyss"><div class="plate">
  <svg class="plate__beam" viewBox="0 0 1600 900" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <linearGradient id="bm" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%"   stop-color="#FFEACE" stop-opacity=".34"/>
        <stop offset="32%"  stop-color="#FFE4C8" stop-opacity=".20"/>
        <stop offset="64%"  stop-color="#FFDEC4" stop-opacity=".08"/>
        <stop offset="100%" stop-color="#FFDCC0" stop-opacity="0"/>
      </linearGradient>
      <filter id="soft" x="-40%" y="-15%" width="180%" height="140%">
        <feGaussianBlur stdDeviation="38"/>
      </filter>
    </defs>
    <polygon points="726,-60 874,-60 1392,950 208,950" fill="url(#bm)" filter="url(#soft)"/>
  </svg>
  <span class="plate__pool"></span><span class="plate__silk"></span><span class="plate__lip"></span>
  {body}
</div></div></body></html>"""


def main():
    tmp = ROOT / "_art" / "_plate.html"
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        for key, out, layout, role, name, title in PLATES:
            w, h = (1600, 900) if key == "holding-slide" else (1920, 1080)
            tmp.write_text(page_html(layout, role, name, title, w, h), encoding="utf-8")
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            pg.goto(tmp.as_uri(), wait_until="networkidle")
            pg.wait_for_timeout(1200)          # webfonts
            dest = ROOT / out
            el = pg.query_selector(".plate")
            if dest.suffix == ".jpg":
                el.screenshot(path=str(dest), type="jpeg", quality=88)
            else:
                el.screenshot(path=str(dest))
            print("  %-14s %-34s %.0f KB" % (key, out, dest.stat().st_size / 1024))
            pg.close()
        b.close()
    tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
