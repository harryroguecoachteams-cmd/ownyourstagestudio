#!/usr/bin/env python3
"""
Own Your Stage Studio - site builder.

Why a builder and not ten hand-copied files: the masthead and footer must be
byte-identical on every page, and each page body must also work as a standalone
block that pastes into a GoHighLevel Custom Code element. One template, one
source of truth for navigation, two outputs.

    python build.py

Reads   _pages/<name>.html   (body fragment only)
Writes  <name>.html          (full standalone page, for GitHub Pages)
        _ghl/<name>.html     (fragment + scoped CSS/JS, for GHL paste)
"""

import os
import re
import pathlib

ROOT = pathlib.Path(__file__).parent
PAGES = ROOT / "_pages"
GHL = ROOT / "_ghl"

# --------------------------------------------------------------------------
# Page register. Order here is the order in the footer "Explore" column.
# depth = how many directories down the file sits, so asset paths resolve.
# --------------------------------------------------------------------------
SITE = [
    # file,                    nav label,        title,                                        description
    ("index.html",             "Home",           "We build the stage. You steal the show.",    "Own Your Stage Studio helps hidden experts become recognized authorities through professionally produced virtual panel events."),
    ("experience.html",        "The Experience", "The Own Your Stage Experience",              "A three month done-for-you visibility and authority experience built around one professionally produced virtual panel event."),
    ("assessment.html",        "Assessment",     "Readiness Assessment",                       "Eight questions that place you on the visibility ladder and tell you what to do next."),
    ("panelists.html",         "Panelists",      "Featured Panelist Program",                  "Join a produced panel as a featured expert. A spotlight, professional footage and exposure to the combined audience."),
    ("about.html",             "About",          "About Own Your Stage Studio",                "A premium authority building studio founded by Annette Knecht Seier."),
    ("faq.html",               "FAQ",            "Frequently Asked Questions",                 "What the Own Your Stage Experience includes, what it costs and what stays with you."),
    ("apply.html",             None,             "Apply for the Host Package",                 "Apply for the Own Your Stage Experience, a three month done-for-you authority engagement."),
    ("contact.html",           None,             "Book a Spotlight Call",                      "A short conversation about the subject you should be known for."),
    ("apply-panelist.html",    None,             "Panelist Application",                       "Apply to be considered as a featured panelist on an Own Your Stage Studio panel event."),
    ("agreements/host.html",   None,             "Done-For-You Panel Host Services Agreement", "The agreement governing the Own Your Stage Experience host engagement."),
    ("agreements/panelist.html", None,           "Featured Panelist Agreement",                "The agreement governing participation as a featured panelist."),
]

NAV = [(f, label) for f, label, _, _ in SITE if label]

# The masthead and footer render the icon at 34px, which is below the 40px
# floor the deck sets for the gradient beam. Below that it specifies the
# single-ink variant: the beam drawn as two rays. That is not a downgrade here,
# it is the only version that still reads as light at this size. A solid
# trapezoid clipped by the circle domes at the top and turns into a lamp
# shade, which is precisely what the identity forbids.
LOGO_SVG = """<svg class="lockup__icon" viewBox="0 0 64 64" aria-hidden="true">
        <circle cx="32" cy="32" r="32" fill="#101A31"/>
        <path d="M27.5 13 H31 L26 42 H21 Z" fill="#DDAA52"/>
        <path d="M33 13 H36.5 L43 42 H38 Z" fill="#DDAA52"/>
        <ellipse cx="32" cy="47" rx="14.5" ry="3.2" fill="#DDAA52"/>
      </svg>"""


def lockup(gid, base):
    return f"""<a href="{base}index.html" class="lockup" aria-label="Own Your Stage Studio, home">
      {LOGO_SVG.format(gid=gid)}
      <span class="lockup__type">
        <span class="lockup__name">Own Your Stage</span>
        <span class="lockup__desc">Studio</span>
      </span>
    </a>"""


def masthead(current, base):
    links = []
    for f, label in NAV:
        cur = ' aria-current="page"' if f == current else ""
        links.append(f'      <a href="{base}{f}"{cur}>{label}</a>')
    links.append(f'      <a class="btn btn--primary" href="{base}apply.html">Apply</a>')
    return f"""<header class="masthead">
  <div class="wrap masthead__inner">
    {lockup("mb", base)}
    <button class="burger" aria-expanded="false" aria-controls="primary-nav">Menu</button>
    <nav id="primary-nav" aria-label="Primary">
{chr(10).join(links)}
    </nav>
  </div>
</header>"""


def footer(base):
    return f"""<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        {lockup("fb", base)}
        <p class="footer__promise">We build the stage. You steal the show.</p>
        <p class="caption" style="margin-top:1rem;max-width:34ch">
          A premium authority building studio for established experts ready to become
          more visible, more credible and easier to remember.
        </p>
      </div>
      <div>
        <h4>Explore</h4>
        <a href="{base}experience.html">The Experience</a>
        <a href="{base}assessment.html">Readiness Assessment</a>
        <a href="{base}panelists.html">Panelist Program</a>
        <a href="{base}about.html">About</a>
        <a href="{base}faq.html">Frequently Asked Questions</a>
      </div>
      <div>
        <h4>Next step</h4>
        <a href="{base}apply.html">Apply for the Host Package</a>
        <a href="{base}contact.html">Book a Spotlight Call</a>
        <a href="{base}apply-panelist.html">Panelist Application</a>
        <div style="margin-top:1.6rem">
          <h4>Agreements</h4>
          <a href="{base}agreements/host.html">Host Services Agreement</a>
          <a href="{base}agreements/panelist.html">Featured Panelist Agreement</a>
        </div>
      </div>
    </div>
    <div class="footer__base">
      <span>&copy; 2026 Own Your Stage Studio, LLC. Florida.</span>
      <span>ownyourstagestudio.com</span>
    </div>
  </div>
</footer>"""


SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Own Your Stage Studio</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title} | Own Your Stage Studio">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}assets/oyss.css">
</head>
<body>
<div class="oyss">

<a class="skip" href="#main">Skip to content</a>
{progress}
{masthead}

<main id="main">
{body}
</main>

{footer}

</div>
<script src="{base}assets/oyss.js"></script>
{inline}
</body>
</html>
"""


def build():
    GHL.mkdir(exist_ok=True)
    built = []

    for fname, label, title, desc in SITE:
        src = PAGES / (fname.replace("/", "__"))
        if not src.exists():
            print(f"  skip  {fname}  (no fragment at {src.name})")
            continue

        raw = src.read_text(encoding="utf-8")

        # A fragment may declare a page-scoped <script> after a %%INLINE%% marker.
        if "%%INLINE%%" in raw:
            body, inline = raw.split("%%INLINE%%", 1)
        else:
            body, inline = raw, ""

        depth = fname.count("/")
        base = "../" * depth
        progress = ('<div class="progress" aria-hidden="true"><div class="progress__fill"></div></div>'
                    if "agreements/" in fname else "")

        out = ROOT / fname
        out.parent.mkdir(parents=True, exist_ok=True)
        # Crimson Pro sets the trademark glyph at nearly full cap height, which
        # makes every "Own Your Stage Experience™" read as a typo. Wrapping it
        # once here beats hand-tagging it across nine pages.
        body = body.replace("&trade;", '<span class="tm">&trade;</span>')

        out.write_text(SHELL.format(
            title=title, desc=desc, base=base,
            progress=progress,
            masthead=masthead(fname, base),
            footer=footer(base),
            body=body.strip(),
            inline=inline.strip(),
        ), encoding="utf-8")

        # GHL block: the same body, wrapped so it stands alone inside a builder.
        ghl = GHL / fname.replace("/", "__")
        ghl.write_text(
            "<!-- ==========================================================\n"
            f"     OWN YOUR STAGE STUDIO - GHL BLOCK: {fname}\n"
            "     Paste into a GoHighLevel Custom Code / HTML element.\n"
            "     All CSS is scoped under .oyss so it cannot leak into the\n"
            "     builder chrome or the rest of the funnel.\n"
            "     Host oyss.css and oyss.js somewhere reachable and update\n"
            "     the two URLs below, or inline them if the site is one page.\n"
            "     ========================================================== -->\n"
            '<link rel="stylesheet" href="https://REPLACE-WITH-ASSET-HOST/oyss.css">\n'
            '<div class="oyss">\n'
            + body.strip() + "\n"
            "</div>\n"
            '<script src="https://REPLACE-WITH-ASSET-HOST/oyss.js"></script>\n'
            + inline.strip() + "\n",
            encoding="utf-8")

        built.append(fname)
        print(f"  built {fname}")

    print(f"\n{len(built)} pages built, {len(built)} GHL blocks written to _ghl/")


if __name__ == "__main__":
    build()
