#!/usr/bin/env python3
"""
Own Your Stage Studio - agreement page generator.

The two agreements are the client's legal text. They are converted from the
source .docx rather than retyped, so the published wording stays byte-faithful
to what Annette's documents say, and regenerating after a legal edit is one
command instead of a proofreading exercise.

    python agreements_build.py && python build.py

Reads   ../Agreement Host.docx
        ../Agreement Featured Panelist.docx
Writes  _pages/agreements__host.html
        _pages/agreements__panelist.html
"""

import html
import pathlib
import re
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ROOT = pathlib.Path(__file__).parent
SRC = ROOT.parent
PAGES = ROOT / "_pages"


# A run of typed underscores is how the .docx draws a blank to fill in. Left
# as literal characters it is one unbreakable 42-character word, which on a
# phone forces the whole document column wider than the screen. Rendered as a
# rule it means the same thing and costs no minimum width.
FILL = re.compile(r'_{4,}')


def paragraphs(docx):
    """Yield (text, is_list_item, is_all_bold) for every non-empty paragraph.

    Bold matters: these documents use a fully bold paragraph as a sub-heading
    ("Entire Agreement", "Severability"), with no numbering to detect it by.
    """
    z = zipfile.ZipFile(docx)
    root = ET.fromstring(z.read("word/document.xml").decode("utf-8"))
    for p in root.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if not text:
            continue
        pPr = p.find(W + "pPr")
        listed = pPr is not None and pPr.find(W + "numPr") is not None

        runs = [r for r in p.findall(W + "r") if r.find(W + "t") is not None]
        bold = bool(runs) and all(
            (r.find(W + "rPr") is not None and r.find(W + "rPr").find(W + "b") is not None)
            for r in runs
        )
        yield text, listed, bold


SECTION = re.compile(r"^(\d{1,2})\.\s+(.{2,90})$")
SUBSECT = re.compile(r"^(\d{1,2}\.\d{1,2})\s+(.{2,90})$")


def convert(docx, stop_at, skip_leading=0):
    """Convert the legal body to HTML, stopping before the signature blocks.

    Returns (html_body, toc_entries).
    """
    out, toc = [], []
    open_list = False
    seen = 0
    stopped = False

    def close():
        nonlocal open_list
        if open_list:
            out.append("      </ul>")
            open_list = False

    for text, listed, bold in paragraphs(docx):
        if stopped:
            break
        if text.strip().upper() in stop_at:
            close()
            stopped = True
            break

        seen += 1
        if seen <= skip_leading:
            continue

        esc = FILL.sub(
            '<span class="fill" aria-hidden="true"></span>', html.escape(text))

        if listed:
            if not open_list:
                out.append("      <ul>")
                open_list = True
            out.append(f"        <li>{esc}</li>")
            continue

        close()

        m = SUBSECT.match(text)
        if m:
            out.append(f"      <h3>{html.escape(m.group(1))} &nbsp;{html.escape(m.group(2))}</h3>")
            continue

        m = SECTION.match(text)
        if m:
            n, title = m.group(1), m.group(2)
            sid = "s" + n
            toc.append((sid, n, title))
            out.append(f'      <h2 id="{sid}"><span class="doc__n">{n}</span>{html.escape(title)}</h2>')
            continue

        # Standalone all-caps blocks act as headings in these documents.
        if text.isupper() and len(text) < 70:
            sid = "b" + str(len(toc))
            toc.append((sid, "", text.title()))
            out.append(f'      <h2 id="{sid}">{html.escape(text)}</h2>')
            continue

        # A fully bold paragraph with no sentence punctuation is a sub-heading.
        if bold and len(text) < 60 and not text.endswith((".", ";", ":")):
            out.append(f"      <h3>{esc}</h3>")
            continue

        out.append(f"      <p>{esc}</p>")

    close()
    return "\n".join(out), toc


def toc_html(toc):
    rows = []
    for sid, n, title in toc:
        label = f"{n}. {title}" if n else title
        rows.append(f'      <a href="#{sid}">{html.escape(label)}</a>')
    return "\n".join(rows)


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

HERO = """<!-- ============ HERO ============ -->
<section class="dark stage" style="padding:clamp(64px,8vh,96px) 0 clamp(92px,11vh,132px);overflow:hidden">
  <span class="beam" aria-hidden="true" style="width:min(40vw,480px)"></span>
  <span class="stage__pool" aria-hidden="true"></span>
  <div class="wrap">
    <div style="max-width:44rem" data-lit>
      <p class="eyebrow">{eyebrow}</p>
      <h1 class="display" style="font-size:clamp(1.9rem,1.4rem+2.2vw,3rem)">{title}</h1>
      <span class="pool" aria-hidden="true"></span>
      <p class="lead" style="margin-top:1.8rem;max-width:36rem">{blurb}</p>
      <p class="draft-flag" style="margin-top:1.8rem;border-color:var(--gold-40);color:var(--gold);background:rgba(221,170,82,.08)">
        Draft for review &middot; not yet legally executed
      </p>
    </div>
  </div>
</section>
"""

BODY = """
<!-- ============ THE DOCUMENT ============
     A contract is an object, so it is drawn as one: paper with an edge,
     lifted out of the dark hero. Section 22 of oyss.css. -->
<section class="sheetbay">
  <div class="wrap">
    <div class="sheet docsheet" data-lit>

      <div class="sheet__head">
        <div>
          <p class="sheet__kicker">Agreement &middot; draft for review</p>
          <p class="sheet__title">{title}</p>
        </div>
        <p class="sheet__meta">
          <b>{fee}</b>
          {feenote}<br>
          Florida law &middot; {sections} sections
        </p>
      </div>

      <!-- The parties block. A real agreement opens by saying who is bound
           and by what. This one now does too, before the first clause. -->
      <dl class="parties">
        <div><dt>Between</dt><dd>Own Your Stage Studio, LLC, a Florida limited liability company</dd></div>
        <div><dt>And</dt><dd>{party}</dd></div>
        <div><dt>Governed by</dt><dd>The laws of the State of Florida</dd></div>
        <div><dt>Signed</dt><dd>Electronically, at the end of this page</dd></div>
      </dl>

      <div class="notice" style="margin:2.2rem 0 2.6rem">
        {notice}
      </div>

      <!-- The rail is hidden under 900px, so on a phone this disclosure is
           the only way to reach section 12 without forty screens of thumbing. -->
      <details class="doctoc--mobile">
        <summary>Contents &middot; {sections} sections</summary>
        <div class="doctoc__list">
{toc}
        </div>
      </details>

      <div class="doclayout">

        <aside class="doctoc">
          <p class="eyebrow eyebrow--gold">Contents</p>
{toc}
          <div class="rule" style="margin:1.4rem 0"></div>
          <button type="button" class="cue no-print" onclick="window.print()" style="border:0;background:none;padding:0;cursor:pointer">Print or save as PDF</button>
        </aside>

        <article class="doc" id="agreement-body">
{body}
          <div id="agreement-end" style="height:1px"></div>
        </article>

      </div>
    </div>
  </div>
</section>
"""



def sign_section(kind):
    """The signature experience. Locked until the document has been read."""

    fee = ""
    if kind == "panelist":
        fee = """
          <div class="fee" style="margin:2.2rem 0">
            <span class="fee__amt">$47.00</span>
            <div>
              <p class="caption" style="color:var(--ivory-70);margin:0">
                Panelist Commitment &amp; Administrative Fee. One time, non-refundable.
                Not a speaking fee.
              </p>
            </div>
          </div>
          <p class="caption" style="color:var(--ivory-46);margin-bottom:2rem">
            Your speaking position is confirmed only after this agreement is signed and
            the fee has been paid. Payment is collected on the next step through the
            secure payment processor.
          </p>"""
        acks = [
            ("ack_read", "I have carefully read this Agreement in its entirety and understand all of its terms and conditions."),
            ("ack_counsel", "I have had the opportunity to seek independent legal advice before signing."),
            ("ack_fee", "I understand that the $47 Panelist Commitment &amp; Administrative Fee is non-refundable, and that it is not a speaking fee."),
            ("ack_live", "I understand that I must appear live, on camera, and that prerecorded, AI generated or substitute presentations are not permitted."),
            ("ack_promo", "I agree to promote the Event a minimum of three times before the Event."),
            ("ack_bind", "I voluntarily agree to be legally bound by this Agreement and I have the legal authority to enter into it."),
        ]
        cta = "Sign and continue to payment"
        confirm = ("Your signature has been recorded. The next step is the $47 Panelist "
                   "Commitment and Administrative Fee, which confirms your speaking position.")
    else:
        fee = """
          <div class="fee" style="margin:2.2rem 0">
            <span class="fee__amt">$2,997.00</span>
            <div>
              <p class="caption" style="color:var(--ivory-70);margin:0">
                Total package price. Due on signature. Non-refundable and non-transferable
                except where required by applicable law.
              </p>
            </div>
          </div>
          <p class="caption" style="color:var(--ivory-46);margin-bottom:2rem">
            No event date is reserved and no work begins until this Agreement is signed,
            payment has processed and the intake questionnaire is complete.
          </p>"""
        acks = [
            ("ack_read", "I have read and understand this Agreement, and I have had an opportunity to ask questions."),
            ("ack_counsel", "I have had an opportunity to consult independent legal counsel."),
            ("ack_refund", "I understand that the $2,997 package price is non-refundable and that the engagement lasts three months."),
            ("ack_intake", "I understand that I must complete the intake process within 48 hours of signing."),
            ("ack_promo", "I understand that I am responsible for promoting the event, and that Own Your Stage Studio does not guarantee audience size, registrations, leads, sales or revenue."),
            ("ack_ip", "I accept the recording and intellectual property provisions, and Florida law with Martin County venue."),
        ]
        cta = "Sign and continue to payment"
        confirm = ("Your signature has been recorded. The next step is the $2,997 package "
                   "payment, after which your event date can be reserved.")

    ack_html = "\n".join(
        f'            <label class="check"><input type="checkbox" name="{n}" required><span>{t}</span></label>'
        for n, t in acks
    )

    specs = ""
    if kind == "host":
        specs = """
          <p class="eyebrow" style="color:var(--gold);margin-top:3rem">Event specifications</p>
          <div class="rule" style="margin:.9rem 0 1.8rem;background:rgba(215,206,192,.2)"></div>
          <p class="caption" style="color:var(--ivory-46);margin-bottom:1.6rem">
            Completed together on the Authority Blueprint call. Leave blank if not yet decided.
          </p>
          <div class="cols-2" style="gap:1.5rem">
            <label class="field" style="margin:0">
              <span class="field__label">Event title</span>
              <input class="field__input" type="text" name="event_title">
            </label>
            <label class="field" style="margin:0">
              <span class="field__label">Event theme</span>
              <input class="field__input" type="text" name="event_theme">
            </label>
            <label class="field" style="margin:0">
              <span class="field__label">Proposed event date</span>
              <input class="field__input" type="date" name="event_date">
            </label>
            <label class="field" style="margin:0">
              <span class="field__label">Time and time zone</span>
              <input class="field__input" type="text" name="event_time" placeholder="6:00 PM Eastern">
            </label>
            <label class="field" style="margin:0">
              <span class="field__label">Intended audience</span>
              <input class="field__input" type="text" name="event_audience">
            </label>
            <label class="field" style="margin:0">
              <span class="field__label">Target number of panelists</span>
              <input class="field__input" type="text" name="event_panelists" placeholder="Up to 5">
            </label>
          </div>
          <label class="field">
            <span class="field__label">Primary call to action</span>
            <input class="field__input" type="text" name="event_cta">
          </label>"""

    extra_id = ""
    if kind == "panelist":
        extra_id = """
          <label class="field">
            <span class="field__label">Event title</span>
            <input class="field__input" type="text" name="event_title" placeholder="As provided in your invitation">
          </label>"""

    return f"""
<!-- ============ SIGNATURE ============ -->
<section class="bay--half paper no-print">
  <div class="wrap">
    <div class="signblock" style="max-width:50rem;margin:0 auto">
      <span class="beam" aria-hidden="true" style="width:60%;top:-30%;opacity:1"></span>

      <div id="sign-panel">
        <p class="eyebrow" style="color:var(--gold)">Electronic signature</p>
        <h2 style="color:var(--ivory);font-size:clamp(1.5rem,1.2rem+1.2vw,2rem)">Sign this agreement</h2>
        <p class="caption" style="color:var(--ivory-70);margin-top:1rem;max-width:36rem">
          Electronic signatures have the same legal force as handwritten ones under
          Florida&rsquo;s Uniform Electronic Transaction Act, Fla. Stat. &sect; 668.50.
        </p>

        <p id="gate-msg" class="notice" style="margin-top:2rem;background:rgba(221,170,82,.09);border-left-color:var(--gold);color:var(--ivory-70)">
          Read to the end of the agreement above to unlock the signature block.
        </p>

        <div class="locked" id="sign-gate" style="margin-top:2rem">
          <form id="agreement-form" novalidate>
{fee}
            <p class="eyebrow" style="color:var(--gold)">Your details</p>
            <div class="rule" style="margin:.9rem 0 1.8rem;background:rgba(215,206,192,.2)"></div>

            <div class="cols-2" style="gap:1.5rem">
              <label class="field" style="margin:0">
                <span class="field__label">Legal name</span>
                <input class="field__input" type="text" name="legal_name" required autocomplete="name">
              </label>
              <label class="field" style="margin:0">
                <span class="field__label">Business name <span style="text-transform:none;letter-spacing:0;font-weight:400">(if applicable)</span></span>
                <input class="field__input" type="text" name="business_name" autocomplete="organization">
              </label>
              <label class="field" style="margin:0">
                <span class="field__label">Email address</span>
                <input class="field__input" type="email" name="email" required autocomplete="email">
              </label>
              <label class="field" style="margin:0">
                <span class="field__label">Telephone</span>
                <input class="field__input" type="tel" name="phone" autocomplete="tel">
              </label>
            </div>
{extra_id}{specs}

            <p class="eyebrow" style="color:var(--gold);margin-top:3rem">Acknowledgments</p>
            <div class="rule" style="margin:.9rem 0 1.8rem;background:rgba(215,206,192,.2)"></div>
{ack_html}

            <p class="eyebrow" style="color:var(--gold);margin-top:3rem">Signature</p>
            <div class="rule" style="margin:.9rem 0 1.8rem;background:rgba(215,206,192,.2)"></div>

            <label class="field" style="margin:0">
              <span class="field__label">Type your full legal name to sign</span>
              <input class="field__input" type="text" name="signature" required autocomplete="off" placeholder="Your full legal name">
            </label>
            <div class="sig-preview" style="margin-top:1.2rem">
              <span class="sig" id="sig-preview"></span>
            </div>
            <p class="caption" style="color:var(--ivory-46);margin-top:.8rem">
              Signed on <span id="sig-date" style="color:var(--gold)"></span>. The date is
              stamped automatically and cannot be edited.
            </p>

            <p id="sign-error" hidden class="notice notice--action" style="margin-top:1.6rem;color:var(--ivory)" role="alert"></p>

            <button type="submit" class="btn btn--primary" style="margin-top:2rem">{cta}</button>
          </form>
        </div>
      </div>

      <div id="signed-state" hidden>
        <p class="eyebrow" style="color:var(--gold)">Signed</p>
        <h2 style="color:var(--ivory);font-size:clamp(1.5rem,1.2rem+1.2vw,2rem)">
          Agreement executed
        </h2>
        <div class="sig-preview" style="margin-top:1.8rem">
          <span class="sig" id="done-name"></span>
        </div>
        <p class="caption" style="color:var(--ivory-70);margin-top:1rem">
          Signed <span id="done-date" style="color:var(--gold)"></span>
        </p>
        <p class="lead" style="color:var(--ivory-70);margin-top:1.8rem">{confirm}</p>
        <div class="notice" style="margin-top:2rem;background:rgba(221,170,82,.09);border-left-color:var(--gold);color:var(--ivory-70)">
          <strong style="color:var(--ivory)">Demonstration build.</strong>
          This signature is recorded in the browser only. Before launch, connect the
          signing endpoint and the payment processor, or replace this block with the
          GoHighLevel document and payment step. See DELIVERY.md.
        </div>
        <div class="actions no-print" style="margin-top:2rem">
          <button type="button" class="btn btn--ghost" onclick="window.print()">Save a copy as PDF</button>
        </div>
      </div>

    </div>
  </div>
</section>
"""


def build():
    PAGES.mkdir(exist_ok=True)

    jobs = [
        dict(
            docx=SRC / "Agreement Host.docx",
            out="agreements__host.html",
            kind="host",
            fee="$2,997.00",
            feenote="Due on signature, non-refundable",
            party="The Client, named in the signature block below",
            eyebrow="Own Your Stage Experience™ · $2,997",
            title="Done-For-You Panel Host Services Agreement",
            blurb=("The full agreement, published before you commit rather than sent "
                   "after. Read it, then sign at the bottom of the page."),
            notice=("<strong style='color:var(--navy)'>Read this before you pay.</strong> "
                    "The whole agreement is on this page. The parts most people miss are "
                    "section 4, which makes payment non-refundable, section 7, which puts "
                    "audience promotion on you, and section 9, which gives you 48 hours to "
                    "complete intake once you sign."),
            stop=("EVENT SPECIFICATIONS AND SCOPE OF SERVICES",),
            skip=5,
        ),
        dict(
            docx=SRC / "Agreement Featured Panelist.docx",
            out="agreements__panelist.html",
            kind="panelist",
            fee="$47.00",
            feenote="Administrative fee, non-refundable",
            party="The Featured Panelist, named in the signature block below",
            eyebrow="Featured Panelist Program · $47",
            title="Featured Panelist Agreement",
            blurb=("The full agreement for featured panelists. Read it, then sign at the "
                   "bottom of the page."),
            notice=("<strong style='color:var(--navy)'>Read this before you pay.</strong> "
                    "The parts most people miss are section 9, which forbids selling from "
                    "the stage, section 10, which commits you to promoting three times, "
                    "section 11, which requires you to appear live, and section 12, which "
                    "makes the $47 fee non-refundable."),
            stop=("COMPANY",),   # the paper signature block, replaced by the live one
            skip=6,
        ),
    ]

    for j in jobs:
        if not j["docx"].exists():
            print(f"  MISSING {j['docx'].name}")
            continue

        body, toc = convert(j["docx"], j["stop"], j["skip"])

        page = (
            HERO.format(eyebrow=j["eyebrow"], title=j["title"], blurb=j["blurb"])
            + BODY.format(toc=toc_html(toc), body=body, notice=j["notice"],
                          title=j["title"], fee=j["fee"], feenote=j["feenote"],
                          party=j["party"], sections=len(toc))
            + sign_section(j["kind"])
            + "%%INLINE%%\n"
            + f'<script>OYSS.signing({{ agreement: "{j["title"]}" }});</script>\n'
        )

        (PAGES / j["out"]).write_text(page, encoding="utf-8")
        print(f"  built {j['out']}  ({len(toc)} sections, {len(body):,} chars)")


if __name__ == "__main__":
    build()
