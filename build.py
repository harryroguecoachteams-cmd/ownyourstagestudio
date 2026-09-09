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
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).parent
PAGES = ROOT / "_pages"
GHL = ROOT / "_ghl"

# --------------------------------------------------------------------------
# Page register. Order here is the order in the footer "Explore" column.
# depth = how many directories down the file sits, so asset paths resolve.
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Asset versioning.
# GitHub Pages serves oyss.css and oyss.js with a long cache lifetime, so a
# stylesheet-only fix can ship and simply not arrive for anyone who loaded the
# page earlier. That is how a fixed bug gets reported a second time. The URLs
# carry a content hash, so a changed file is a changed URL and an unchanged
# file still comes from cache.
# --------------------------------------------------------------------------

def asset_v():
    h = hashlib.sha1()
    for name in ("assets/oyss.css", "assets/oyss.js"):
        f = ROOT / name
        if f.exists():
            h.update(f.read_bytes())
    return h.hexdigest()[:8]


ASSET_V = asset_v()


SITE = [
    # A page is not only a title. It is a KIND, and the kind decides the
    # silhouette: a guide is something you read, a form is something you fill
    # in, an agreement is something you sign. The review found every page
    # reading the same on a phone, which is what happens when kind is only
    # expressed in words. See section 22 of oyss.css.
    #
    # file, nav label, title, description, kind, page-mark name, page-mark meta
    ("index.html",             "Home",           "We build the stage. You steal the show.",    "Own Your Stage Studio helps hidden experts become recognized authorities through professionally produced virtual panel events.",
     "home",      None,                       None),
    ("experience.html",        "The Experience", "The Own Your Stage Experience",              "A three month done-for-you visibility and authority experience built around one professionally produced virtual panel event.",
     "guide",     "The Experience",           "Three months \u00b7 $2,997"),
    ("assessment.html",        "Assessment",     "Readiness Assessment",                       "Eight questions that place you on the visibility ladder and tell you what to do next.",
     "form",      "Readiness Assessment",     "8 questions \u00b7 3 minutes"),
    ("panelists.html",         "Panelists",      "Featured Panelist Program",                  "Join a produced panel as a featured expert. A spotlight, professional footage and exposure to the combined audience.",
     "guide",     "Featured Panelists",       "$47 · by application"),
    ("about.html",             "About",          "About Own Your Stage Studio",                "A premium authority building studio founded by Annette Knecht Seier.",
     "guide",     "About the Studio",         None),
    ("faq.html",               "FAQ",            "Frequently Asked Questions",                 "What the Own Your Stage Experience includes, what it costs and what stays with you.",
     "guide",     "Questions",                "Tap a question to open it"),
    ("apply.html",             None,             "Apply for the Host Package",                 "Apply for the Own Your Stage Experience, a three month done-for-you authority engagement.",
     "form",      "Host Package",             "No payment at this step"),
    ("contact.html",           None,             "Book a Spotlight Call",                      "A short conversation about the subject you should be known for.",
     "form",      "Spotlight Call",           "30 minutes · no charge"),
    ("apply-panelist.html",    None,             "Panelist Application",                       "Apply to be considered as a featured panelist on an Own Your Stage Studio panel event.",
     "form",      "Panelist Application",     "Kept on file 12 months"),
    ("agreements/host.html",   None,             "Done-For-You Panel Host Services Agreement", "The agreement governing the Own Your Stage Experience host engagement.",
     "agreement", "Host Services",            "Draft · read then sign"),
    ("agreements/panelist.html", None,           "Featured Panelist Agreement",                "The agreement governing participation as a featured panelist.",
     "agreement", "Featured Panelist",        "Draft · read then sign"),
]

# What the page-mark badge says for each kind. "Guide" would be jargon to a
# reader; "Read" and "Form" and "Agreement" are what the thing actually is.
KIND_BADGE = {"guide": "Read", "form": "Form", "agreement": "Agreement"}
PAGEKIND = {f: k for f, _, _, _, k, _, _ in SITE}

NAV = [(f, label) for f, label, _, _, _, _, _ in SITE if label]

# --------------------------------------------------------------------------
# GoHighLevel output
#
# GHL has no page or funnel builder API, so the site cannot be created inside
# it programmatically. What it does have is a Custom JS/HTML element, so each
# page body is emitted as a block that pastes straight into one.
#
# Two things have to change for a block to work inside a funnel:
#   1. Relative links (experience.html) must become GHL page slugs (/experience).
#   2. Relative asset paths must become absolute URLs.
# Both are rewritten here rather than left as a find-and-replace chore.
# --------------------------------------------------------------------------

ASSET_HOST = "https://harryroguecoachteams-cmd.github.io/ownyourstagestudio"

# file on disk -> the funnel step slug it becomes in GHL.
# Change the right-hand side to match whatever the steps are actually named.
SLUGS = {
    "index.html":               "/",
    "experience.html":          "/experience",
    "assessment.html":          "/assessment",
    "panelists.html":           "/panelists",
    "about.html":               "/about",
    "faq.html":                 "/faq",
    "apply.html":               "/apply",
    "contact.html":             "/spotlight-call",
    "apply-panelist.html":      "/panelist-application",
    "agreements/host.html":     "/host-agreement",
    "agreements/panelist.html": "/panelist-agreement",
}


def for_ghl(markup):
    """Rewrite a page body so it works pasted inside a GHL funnel step."""
    # assets -> absolute.
    # `poster` has to be in this list. It was not, so the hero's poster frame
    # stayed a relative path inside a GHL funnel, resolved against the funnel's
    # own domain and 404'd: a black rectangle until the video finished decoding.
    markup = re.sub(r'(src|href|poster)="(?:\.\./)*assets/', rf'\1="{ASSET_HOST}/assets/', markup)

    # internal page links -> funnel slugs. Longest paths first so
    # "agreements/host.html" is matched before "host.html" could be.
    for f in sorted(SLUGS, key=len, reverse=True):
        markup = markup.replace(f'href="{f}"', f'href="{SLUGS[f]}"')
        markup = markup.replace(f'href="../{f}"', f'href="{SLUGS[f]}"')
    return markup

# THE MARK.
#
# An earlier pass deleted the disc, on the reasoning that a navy circle on a
# navy masthead is invisible. The conclusion was that the mark had to keep
# its disc, because deck page 17 said "The icon is always a complete circle
# or a complete square."
#
# THE SEPTEMBER BRAND SHEET REPLACES ALL OF THAT. There is no disc, no beam
# and no pool. The mark is the A of STAGE: two parallel strokes at a 2:1
# rise with a flat apex, and an arch in the counter where an A has a
# crossbar. It has no field to reverse, which is why it survives being put
# on a dark bar by changing one fill rather than by flipping a colourway.
#
# Geometry measured off the sheet's ICON / MARK panel and normalised to a
# 64 x 58 box. Read off the artwork rather than eyeballed:
#   outer feet     x 0 and x 64, baseline y 58
#   stroke         11 wide measured horizontally, both edges at dx/dy .5
#   apex           cut flat 6 wide, where the extended edges would meet
#                  5.5 above the box
#   inner void     closes at y 16
#   the arch       11 wide on a 5.5 radius, sitting from y 37 to y 46.4,
#                  centred in a void 30 wide at that height
#
# The A is set as a mark inside live text rather than as a picture of the
# whole wordmark, so the lockup stays selectable, scales with the type and
# needs no second file at 2x.
MARK_SVG = """<svg class="mark" viewBox="0 0 64 58" aria-hidden="true" focusable="false">
          <path class="mark__a" d="M29 0 H35 L64 58 H53 L32 16 L11 58 H0 Z"/>
          <path class="mark__arch" d="M27.5 46.4 Q26.5 46.4 26.5 45.4 V42.5 a5.5 5.5 0 0 1 11 0 V45.4 Q37.5 46.4 36.5 46.4 Z"/>
        </svg>"""


def lockup(gid, base):  # gid kept: the callers name their instances
    # The anchor carries the accessible name, so the mark standing in for
    # the A never has to be read as "St ge" by anything.
    return f"""<a href="{base}index.html" class="lockup lockup--motion" aria-label="Own Your Stage Studio, home">
      <span class="lockup__type">
        <span class="lockup__name"><span class="lockup__own">Own Your</span><span class="lockup__stage">St{MARK_SVG}ge</span></span>
        <span class="lockup__desc">Studio<span class="lockup__what"> &middot; Virtual panel events</span></span>
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
    # THE BIG LINES.
    # Lifted from the v2 build the client flagged as the one thing he liked in
    # it, and it is the right call: the tagline is the strongest asset the brand
    # owns and it was being whispered in 19px sans halfway down a column. Set at
    # display scale it does what the deck's closing panel does on page 25, and
    # the split colour is the deck's own: the promise in ivory, what you get in
    # gold.
    return f"""<footer class="footer silked">
  <div class="wrap">
    <p class="footer__lines">
      <span>We build the stage.</span>
      <span class="footer__lines--gold">You steal the show.</span>
    </p>
  </div>
  <div class="wrap">
    <div class="footer__grid">
      <div>
        {lockup("fb", base)}
        <p class="caption" style="margin-top:1.1rem;max-width:34ch">
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
      <span class="footer__note">The room is already looking for you.</span>
    </div>
  </div>
</footer>"""


# The share card. Every link to this site rendered as a blank rectangle in
# WhatsApp, LinkedIn and iMessage because no page carried an og:image, and the
# obvious asset was sitting unused: the holding slide is the studio's own most
# seen artwork and it is already 16:9.
# Per-kind prompt configuration. `home` and `guide` are pages somebody is
# READING, so a prompt is the natural next step. `form` and `agreement` are
# pages somebody is DOING, so both surfaces stay off: the action is already
# in front of them and an interruption there costs a conversion rather than
# earning one.
PROMPTS = {
    "home": """<script>OYSS.prompts({
  after: '.figure__value',
  barTitle: 'Ready to host your own panel?',
  barMeta: 'Eight minutes to apply. No payment at this step.',
  barCta: 'Apply to host', barHref: 'apply.html'
});</script>""",
    "guide": """<script>OYSS.prompts({
  after: '.flood, .figure__value, .bay--half',
  barTitle: 'Find out where you stand first.',
  barMeta: 'Eight questions, three minutes, no email required.',
  barCta: 'Take the assessment', barHref: 'assessment.html',
  exitTitle: 'One question before you go.',
  exitBody: 'Would the people in your industry name a subject when they describe you? Eight questions tells you, in about three minutes.'
});</script>""",
}


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
<meta property="og:image" content="https://harryroguecoachteams-cmd.github.io/ownyourstagestudio/assets/media/stage-holding-slide.jpg">
<meta property="og:image:width" content="1600">
<meta property="og:image:height" content="900">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}assets/oyss.css?v={v}">
<style>
/* PAGE SHELL RESET.
   oyss.css carries no global reset on purpose: every selector is scoped
   under .oyss so the same file can be pasted into a GoHighLevel Custom Code
   element without touching the builder chrome. The cost is that on a
   standalone page the browser's own 8px body margin survives, and it was
   drawing a pale frame around every dark section on every page. It is the
   page shell's job to remove it, not the brand system's, so it lives here
   and never reaches the GHL block. */
html, body {{ margin: 0; padding: 0; }}
body {{ background: #F8F5F2; }}
</style>
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
<script src="{base}assets/oyss.js?v={v}"></script>
{prompts}
{inline}
</body>
</html>
"""


def build():
    GHL.mkdir(exist_ok=True)
    built = []

    for fname, label, title, desc, kind, markname, markmeta in SITE:
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

        # THE PROMPTS.
        # A page whose own job IS the action never gets a bar or an exit
        # modal: a form page already has the thing on screen, and a contract
        # is not a place to be interrupted. So the surfaces are declared per
        # KIND rather than switched on globally, and there is exactly one
        # place to change that.
        prompts = PROMPTS.get(kind, "")

        out.write_text(SHELL.format(
            title=title, desc=desc, base=base, v=ASSET_V,
            progress=progress, prompts=prompts,
            masthead=masthead(fname, base),
            footer=footer(base),
            body=body.strip(),
            inline=inline.strip(),
        ), encoding="utf-8")

        # GHL block: the same body, links and assets rewritten for a funnel.
        ghl = GHL / fname.replace("/", "__")
        slug = SLUGS.get(fname, "/")
        ghl.write_text(
            "<!-- ==========================================================\n"
            f"     OWN YOUR STAGE STUDIO - GHL BLOCK\n"
            f"     Page:  {title}\n"
            f"     Step:  {slug}\n"
            "\n"
            "     Paste ALL of this into one Custom JS/HTML element on that\n"
            "     funnel step. Set the surrounding GHL section to full width\n"
            "     with 0 padding, or its container will letterbox the design.\n"
            "\n"
            "     The <link> and <script> below are safe to leave on every\n"
            "     page: the browser caches both after the first one. If you\n"
            "     would rather load them once for the whole funnel, move them\n"
            "     to Funnel Settings > Tracking Code (Header / Footer) and\n"
            "     delete them from each block.\n"
            "\n"
            "     All CSS is scoped under .oyss, so nothing here can leak into\n"
            "     the builder chrome or the rest of the funnel.\n"
            "     ========================================================== -->\n"
            f'<link rel="stylesheet" href="{ASSET_HOST}/assets/oyss.css?v={ASSET_V}">\n'
            '<div class="oyss oyss--bleed">\n\n'
            "<!-- ---------- masthead ---------- -->\n"
            + for_ghl(masthead(fname, "")) + "\n"
            "<!-- ---------- page ---------- -->\n"
            "<main>\n"
            + for_ghl(body.strip()) + "\n"
            "</main>\n\n"
            "<!-- ---------- footer ---------- -->\n"
            + for_ghl(footer("")) + "\n\n"
            "</div>\n"
            f'<script src="{ASSET_HOST}/assets/oyss.js?v={ASSET_V}"></script>\n'
            + for_ghl(inline.strip()) + "\n",
            encoding="utf-8")

        built.append(fname)
        print(f"  built {fname}")

    print(f"\n{len(built)} pages built, {len(built)} GHL blocks written to _ghl/")


if __name__ == "__main__":
    build()
