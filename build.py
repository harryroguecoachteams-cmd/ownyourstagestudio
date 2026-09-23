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
    # Feedback 8.0: no "Home" in the bar. With Services and Virtual Panel
    # Events added it no longer fit on one line at 1366, and the lockup is
    # already the way home on every page.
    ("index.html",             None,             "We build the stage. You steal the show.",    "Own Your Stage Studio builds done-for-you authority platforms for established experts: produced panel events, webinars, summits and interview series, turned into content that keeps working.",
     "home",      None,                       None),
    # Feedback 8.0, note 2: every service on one page, each one ending in
    # the booking calendar.
    ("services.html",          "Services",       "Services",                                   "Everything Own Your Stage Studio produces: virtual panel events, webinars and masterclasses, virtual summits, interview series, roundtables, podcast-style conversations, content and speaker preparation.",
     "guide",     "Services",                 None),
    # Feedback 8.0, note 4: the flagship is named for what it is. The file
    # keeps its name so every old link still lands.
    ("experience.html",        "Virtual Panel Events", "Virtual Panel Events",                 "The flagship: the Own Your Stage Experience, a three month done-for-you visibility and authority engagement built around one professionally produced virtual panel event.",
     "guide",     "Virtual Panel Events",          "Three months \u00b7 $2,997"),
    ("assessment.html",        "Assessment",     "Readiness Assessment",                       "Twelve questions across six pillars that show how visible your authority is today, and what to do next.",
     "form",      "Readiness Assessment",     "12 questions \u00b7 5 minutes"),
    ("panelists.html",         "Panelists",      "Featured Panelist Program",                  "Join a produced panel as a featured expert. A spotlight, professional footage and exposure to the combined audience.",
     "guide",     "Featured Panelists",       "$47 · by application"),
    ("about.html",             "About",          "About Own Your Stage Studio",                "A done-for-you authority building studio founded by Annette Knecht Seier.",
     "guide",     "About the Studio",         None),
    ("faq.html",               "FAQ",            "Frequently Asked Questions",                 "What Own Your Stage Studio produces, what the Experience includes, what it costs and what stays with you.",
     "guide",     "Questions",                "Tap a question to open it"),
    ("apply.html",             None,             "Apply for the Host Package",                 "Apply for the Own Your Stage Experience, a three month done-for-you authority engagement.",
     "form",      "Host Package",             "No payment at this step"),
    # Feedback 7.0: renamed from "Spotlight Call" to the name Annette's own
    # booking calendar and assessment already use, so the site, the calendar
    # invite and the results screen all call it the same thing.
    ("contact.html",           None,             "Book a Stop Hiding Strategy Call",           "Thirty minutes on Zoom, complimentary: where your authority stands today and which stage fits you next.",
     "form",      "Stop Hiding Strategy Call", "30 minutes · complimentary"),
    ("apply-panelist.html",    None,             "Panelist Application",                       "Apply to be considered as a featured panelist on an Own Your Stage Studio panel event.",
     "form",      "Panelist Application",     "Kept on file 12 months"),
    ("agreements/host.html",   None,             "Done-For-You Panel Host Services Agreement", "The agreement governing the Own Your Stage Experience host engagement.",
     "agreement", "Host Services",            "Draft · read then sign"),
    ("agreements/panelist.html", None,           "Featured Panelist Agreement",                "The agreement governing participation as a featured panelist.",
     "agreement", "Featured Panelist",        "Draft · read then sign"),
    # Feedback 7.0, note 10: the three legal pages Annette's own GHL site
    # links from its footer and from under every form's consent boxes.
    ("terms.html",             None,             "Terms and Conditions",                       "The terms governing use of the Own Your Stage Studio website.",
     "legal",     "Terms",                    None),
    ("privacy.html",           None,             "Privacy Policy",                             "How Own Your Stage Studio collects, uses and protects personal information, including text message consent.",
     "legal",     "Privacy",                  None),
    ("disclaimer.html",        None,             "Disclaimer",                                 "What Own Your Stage Studio does and does not promise.",
     "legal",     "Disclaimer",               None),
]

# Annette's own "OWN YOUR STAGE" Strategy Session calendar in GHL, read from
# the LeadConnector API on 23 Sep 2026 (30 minutes, Zoom). The button inside
# her GHL quiz points at a TRUNCATED id, cNJmGXJ4ed9Yp, and 404s; this is the
# full one.
BOOKING_URL = "https://api.leadconnectorhq.com/widget/booking/cNJmGXJ4ed9YpmzNEElE"

# The calendar as an embeddable block (feedback 8.0, notes 3 and 9). One
# source, so the home page, the services page, the flagship page, the
# assessment result and the Strategy Session page all carry the same widget.
# No loading="lazy": a lazy iframe inside a revealed section was painting as
# an empty white box until something scrolled it, which is the blank calendar
# in the review screenshot. The explicit height is the calendar's own
# rendered height, so the box is right before form_embed.js resizes it.
BOOKING_HTML = """<div class="booking">
          <iframe src="%%BOOKING_URL%%" scrolling="no" id="{id}"
                  title="Book your Own Your Stage Strategy Session" height="740"></iframe>
        </div>
        <p class="caption booking__fallback">
          Calendar not showing?
          <a href="%%BOOKING_URL%%" target="_blank" rel="noopener">Open the calendar in a new tab</a>.
        </p>"""
# THE LEAD FORM (feedback 9.0, note 3): "bring back the form, but keep it
# short". The site's own forms still have no endpoint (see OYSS_ENDPOINT), so
# this one is Annette's own GHL form, embedded the way GHL's embed code does
# it: a submission is a real contact in her CRM with her own SMS consent
# wording. LEAD_FORM_ID is the short form built for the site in her GHL.
LEAD_FORM_ID = "dvJo5tJIIPvpcprpSPcc"   # "Website - Let's talk (short)", 23 Sep 2026
LEAD_FORM_HTML = """<div class="leadform">
            <iframe src="https://api.leadconnectorhq.com/widget/form/{fid}"
                    id="inline-{fid}" data-layout="{{'id':'INLINE'}}"
                    data-trigger-type="alwaysShow" data-trigger-value=""
                    data-activation-type="alwaysActivated" data-activation-value=""
                    data-deactivation-type="neverDeactivate" data-deactivation-value=""
                    data-form-name="Website - Let's talk (short)" data-height="700"
                    data-layout-iframe-id="inline-{fid}" data-form-id="{fid}"
                    title="Let's talk: Own Your Stage Studio" height="700"></iframe>
          </div>"""

BOOKING_SCRIPT = '<script src="https://link.msgsndr.com/js/form_embed.js" type="text/javascript"></script>'

# PAYMENT (feedback 8.0, note 4): pay in full, or in two. Both are Annette's
# own GHL products: "Own Your Stage Experience" at $2,997 one time, and
# "Own Your Stage Experience - Payment Plan" at $1,550 a month for two
# months (totalCycles 2, so it stops after the second). Both payment links
# already existed in her GHL (Payments > Payment Links, created 26 and 28
# Aug) and were checked on 23 Sep 2026: each renders a Stripe checkout for
# the right product and amount. Set either to None and its button books the
# Strategy Session instead.
PAY_FULL_URL = "https://link.fastpaydirect.com/payment-link/6a8f2bcbf9c8c807930ba334"
PAY_PLAN_URL = "https://link.fastpaydirect.com/payment-link/6a919448f9c8c807930ba92c"

# TEXT MESSAGE CONSENT (feedback 7.0, note 10).
# Every form Annette runs in GHL carries these two boxes, worded exactly like
# this, and it is the wording carriers look for when an A2P 10DLC texting
# campaign is reviewed. So every form here that asks for a phone number
# carries them too,
# from one source, so no page can drift. Both optional, both unchecked: consent
# to texts cannot be a condition of anything.
CONSENT_HTML = """<div class="consent">
              <label class="check consent__box">
                <input type="checkbox" name="sms_consent_transactional" value="yes">
                <span>By checking this box, I consent to receive non-marketing text messages from Own Your Stage Studio. Message frequency varies, message &amp; data rates may apply. Text HELP for assistance, reply STOP to opt out.</span>
              </label>
              <label class="check consent__box">
                <input type="checkbox" name="sms_consent_marketing" value="yes">
                <span>By checking this box, I consent to receive marketing and promotional messages including special offers, discounts, new product updates among others, from Own Your Stage Studio at the phone number provided. Frequency may vary. Message &amp; data rates may apply. Text HELP for assistance, reply STOP to opt out.</span>
              </label>
            </div>"""

LEGAL_HTML = ('<p class="legalline"><a href="{base}privacy.html">Privacy Policy</a>'
              '<span aria-hidden="true">|</span><a href="{base}terms.html">Terms of Service</a></p>')


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
    "services.html":            "/services",
    "experience.html":          "/experience",
    "assessment.html":          "/assessment",
    "panelists.html":           "/panelists",
    "about.html":               "/about",
    "faq.html":                 "/faq",
    "apply.html":               "/apply",
    "contact.html":             "/strategy-session",
    "apply-panelist.html":      "/panelist-application",
    "agreements/host.html":     "/host-agreement",
    "agreements/panelist.html": "/panelist-agreement",
    "terms.html":               "/terms-conditions",
    "privacy.html":             "/privacy-policy",
    "disclaimer.html":          "/disclaimer",
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
        # and the same link with an anchor on it (index.html#formats)
        markup = re.sub(rf'href="(?:\.\./)*{re.escape(f)}#', f'href="{SLUGS[f]}#', markup)
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
# on a dark bar by changing one fill rather than by flipping a colorway.
#
# Geometry measured off the sheet's ICON / MARK panel and normalised to a
# 64 x 58 box. Read off the artwork rather than eyeballed:
#   outer feet     x 0 and x 64, baseline y 58
#   stroke         11 wide measured horizontally, both edges at dx/dy .5
#   apex           cut flat 6 wide, where the extended edges would meet
#                  5.5 above the box
#   inner void     closes at y 16
#   the arch       11 wide on a 5.5 radius, sitting from y 37 to y 46.4,
#                  centered in a void 30 wide at that height
#
# The A is set as a mark inside live text rather than as a picture of the
# whole wordmark, so the lockup stays selectable, scales with the type and
# needs no second file at 2x.
# Feedback 7.0, note 3: "make sure the logo looks exactly like that". The
# reference Annette sent is the stacked lockup: OWN YOUR light and wide, STAGE
# bold with the red A, STUDIO red and tracked out, centered under it, and the
# line "Speak. Be Seen. Create Impact." beneath. The apex of the A in that
# artwork comes to a point, so the flat cut is narrowed from 6 units to 3.
MARK_SVG = """<svg class="mark" viewBox="0 0 64 58" aria-hidden="true" focusable="false">
          <path class="mark__a" d="M30.5 0 H33.5 L64 58 H53 L32 16 L11 58 H0 Z"/>
          <path class="mark__arch" d="M27.5 46.4 Q26.5 46.4 26.5 45.4 V42.5 a5.5 5.5 0 0 1 11 0 V45.4 Q37.5 46.4 36.5 46.4 Z"/>
        </svg>"""


def lockup(gid, base, tagline=False, tone=""):  # gid kept: the callers name their instances
    # The anchor carries the accessible name, so the mark standing in for
    # the A never has to be read as "St ge" by anything.
    #
    # "Virtual panel events" is gone from under the wordmark: the studio is
    # not a virtual-event-only company (feedback 7.0, notes 1 and 3). STUDIO
    # takes the middle, as the reference draws it.
    #
    # The tagline is a call we were asked to take. It is IN wherever the
    # lockup is large enough to read it (the footer), and OUT of the header,
    # where at 30px of wordmark the line would set at about seven pixels and
    # read as a smudge under the logo rather than as a promise.
    tag = ('\n        <span class="lockup__tag">Speak. Be Seen. Create Impact.</span>'
           if tagline else "")
    cls = "lockup lockup--stack lockup--motion" + (f" lockup--{tone}" if tone else "")
    return f"""<a href="{base}index.html" class="{cls}" aria-label="Own Your Stage Studio, home">
      <span class="lockup__type">
        <span class="lockup__row lockup__row--own">Own Your</span>
        <span class="lockup__row lockup__row--stage">St{MARK_SVG}ge</span>
        <span class="lockup__row lockup__row--studio">Studio</span>{tag}
      </span>
    </a>"""


# FEEDBACK 9.0, NOTE 1: "the menu bar looks very cluttered ... add things
# you do in a dropdown". Seven items and a button became four and a button:
# everything the studio SELLS sits under one "What we do" menu, flagship
# first, so the bar itself reads as a sentence rather than a site map.
WHAT_WE_DO = [
    ("experience.html", "Virtual Panel Events", "The flagship: host your own produced panel"),
    ("services.html",   "All services",         "Webinars, summits, series, podcasts and more"),
    ("panelists.html",  "Panelist Program",     "Join a panel as a featured expert"),
]
NAV_REST = [("assessment.html", "Assessment"), ("about.html", "About"), ("faq.html", "FAQ")]


def masthead(current, base):
    in_menu = any(f == current for f, _, _ in WHAT_WE_DO)
    items = []
    for f, label, sub in WHAT_WE_DO:
        cur = ' aria-current="page"' if f == current else ""
        items.append(f'          <a href="{base}{f}"{cur}><b>{label}</b><span>{sub}</span></a>')
    links = [f"""      <div class="navdrop{' is-current' if in_menu else ''}">
        <button class="navdrop__btn" type="button" aria-expanded="false" aria-controls="navdrop-menu">What we do</button>
        <div class="navdrop__menu" id="navdrop-menu">
{chr(10).join(items)}
        </div>
      </div>"""]
    for f, label in NAV_REST:
        cur = ' aria-current="page"' if f == current else ""
        links.append(f'      <a href="{base}{f}"{cur}>{label}</a>')
    # Feedback 8.0: every service ends in a conversation, so the one action
    # in the bar is the call, not the flagship's application.
    links.append(f'      <a class="btn btn--primary" href="{base}contact.html">Book a Call</a>')
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
    # FEEDBACK 7.0, NOTE 5 gave the footer Annette's silk banner: the stacked
    # lockup and its tagline top left, REAL / EXPERTISE / BIGGER /
    # OPPORTUNITIES over a short red rule top right, red silk sweeping across.
    #
    # FEEDBACK 8.0, NOTE 8 rearranged it, drawn on a screenshot:
    #   - the links move UP, into the empty warm ground between the lockup
    #     and the silk, where the banner had nothing to say;
    #   - the big old sign-off comes back at display size, "We build the
    #     stage. You steal the show.", the one line of the old dark footer
    #     Harsh ever liked;
    #   - Your Voice Matters moves DOWN, to the base line, where the small
    #     version of the sign-off used to sit.
    # The silk is now a band of its own under the type, so no word, link or
    # line sits on the fabric and every contrast is measured on the ground.
    return f"""<footer class="footer footer--silk">
  <div class="wrap footer__hero">
    <div class="footer__brand">
      {lockup("fb", base, tagline=True, tone="light")}
    </div>
    <div class="footer__words">
      <p class="footer__claims"><span>Real</span><span>Expertise</span><span>Bigger</span><span>Opportunities</span></p>
      <span class="footer__rule" aria-hidden="true"></span>
    </div>
  </div>
  <div class="wrap footer__nav">
    <div class="footer__grid">
      <div>
        <h4>Explore</h4>
        <a href="{base}services.html">Services</a>
        <a href="{base}experience.html">Virtual Panel Events</a>
        <a href="{base}panelists.html">Panelist Program</a>
        <a href="{base}about.html">About Annette</a>
        <a href="{base}faq.html">Questions</a>
      </div>
      <div>
        <h4>Next step</h4>
        <a href="{base}contact.html">Book a Stop Hiding Strategy Call</a>
        <a href="{base}assessment.html">Take the Readiness Assessment</a>
        <a href="{base}apply.html">Apply for the Host Package</a>
        <a href="{base}apply-panelist.html">Panelist Application</a>
      </div>
      <div>
        <h4>Agreements</h4>
        <a href="{base}agreements/host.html">Host Services Agreement</a>
        <a href="{base}agreements/panelist.html">Featured Panelist Agreement</a>
      </div>
      <div>
        <h4>Legal</h4>
        <a href="{base}terms.html">Terms and Conditions</a>
        <a href="{base}privacy.html">Privacy Policy</a>
        <a href="{base}disclaimer.html">Disclaimer</a>
      </div>
    </div>
  </div>
  <div class="footer__stage">
    <span class="footer__silk" aria-hidden="true"></span>
    <p class="wrap footer__tagline"><span>We build the stage.</span><span>You steal the show.</span></p>
  </div>
  <div class="wrap footer__base">
    <span>&copy; 2026 Own Your Stage Studio, LLC. Florida.</span>
    <p class="footer__voice"><span>Your</span><span>Voice</span><span>Matters</span></p>
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
  after: '#formats',
  barTitle: 'Talk to us about your stage.',
  barMeta: 'Thirty minutes on Zoom, complimentary.',
  barCta: 'Book a Stop Hiding Strategy Call', barHref: 'contact.html'
});</script>""",
    "guide": """<script>OYSS.prompts({
  after: '.flood, .figure__value, .bay--half',
  barTitle: 'Find out how visible your authority is first.',
  barMeta: 'Twelve questions, about five minutes, no email required.',
  barCta: 'Take the assessment', barHref: 'assessment.html',
  exitTitle: 'One question before you go.',
  exitBody: 'How visible is your authority today? Twelve questions across six pillars tell you, in about five minutes, and the result appears on the screen.'
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
/* THE WIDE SCREEN (feedback 6.0). The site was approved at 1440 and stopped
   responding above it. From 1440 to 1920 the root eases 100% -> 112.5%, so
   every rem measure in oyss.css (type, leads, columns, buttons) grows with
   the screen; the content width grows with it via --wrap (oyss.css section
   47). Percentages, not px, so a reader's own browser font size still
   counts. It is the html element, so it lives in the shell, not the brand
   file, which may style nothing outside .oyss. */
html {{ font-size: clamp(100%, 62.5% + .4167vw, 112.5%); }}
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
        body = (body.replace("%%CONSENT%%", CONSENT_HTML)
                    .replace("%%LEGAL%%", LEGAL_HTML.format(base=base))
                    .replace("%%PAY_FULL%%", PAY_FULL_URL or base + "contact.html")
                    .replace("%%PAY_PLAN%%", PAY_PLAN_URL or base + "contact.html")
                    .replace("%%PAY_LIVE%%", "live" if (PAY_FULL_URL and PAY_PLAN_URL) else "pending"))
        n = 0
        if "%%LEADFORM%%" in body:
            n += 1
            body = body.replace("%%LEADFORM%%", LEAD_FORM_HTML.format(fid=LEAD_FORM_ID))
        while "%%BOOKING%%" in body:
            n += 1
            body = body.replace("%%BOOKING%%", BOOKING_HTML.format(id=f"oyss-booking-{n}"), 1)
        body = body.replace("%%BOOKING_URL%%", BOOKING_URL)
        if n and BOOKING_SCRIPT not in inline:
            inline = BOOKING_SCRIPT + "\n" + inline
        inline = inline.replace("%%BOOKING_URL%%", BOOKING_URL)

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

        # Feedback 9.0, note 8: the same block, published, for the GHL
        # website's one-line mount (assets/ghl-mount.js). _ghl/ itself is
        # not served: GitHub Pages skips folders that start with "_".
        pub = ROOT / "assets" / "ghl" / fname.replace("/", "__")
        pub.parent.mkdir(parents=True, exist_ok=True)
        pub.write_text(ghl.read_text(encoding="utf-8"), encoding="utf-8")

        built.append(fname)
        print(f"  built {fname}")

    print(f"\n{len(built)} pages built, {len(built)} GHL blocks written to _ghl/")


if __name__ == "__main__":
    build()
