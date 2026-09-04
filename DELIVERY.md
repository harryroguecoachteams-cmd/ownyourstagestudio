# Own Your Stage Studio — website draft

A working draft of the company site, built to the approved **OYSS Brand Deck v3**.
Not a template with the colors swapped: every value traces to a page of that deck,
and the notes below say which.

---

## The idea

The brand has exactly one motif. The deck is unusually strict about it:

> Light is the only motif. Beams, falloff and pools. Never a lamp, a curtain,
> a microphone or a proscenium. *(deck p14)*

So the site has exactly one motion system, and it is not decoration. **Nothing
slides in, nothing bounces, nothing fades from nowhere. Things become visible
because they are lit** — which is the same sentence the business uses to describe
what it sells. The motion *is* the positioning:

| Element | What it is | Why it earns its place |
|---|---|---|
| **The beam** | The logo icon at architectural scale. Strikes once on load, pool blooms where it lands. | The mark and the hero are the same object at two sizes. |
| **The reveal** | Content enters dim and low-contrast, resolves to full when lit. | Hidden expert → recognized authority, performed on scroll. |
| **The dimmer ladder** | The four visibility levels as an intensity ladder. Each cell is *literally* brighter than the last; hover moves the light. | Turns an abstract diagnostic into something you read at a glance. |
| **The cue sheet** | The six-step client journey as a production cue stack, light travelling down the rail. | "Produced" is one of the five brand essence words. This is what produced looks like. |
| **The panel rig** | Six frames, one light, switching like a producer switching cameras. | Shows the deliverable working rather than describing it. |
| **The travelling pool** | A pool of light following the pointer on dark sections. Gold at 8%, desktop only. | The deck permits one pool of light and forbids flares. It stays a pool. |
| **The reel** | The home hero: type column left, and the film running full bleed to the right edge. A person standing at the base of a tall doorway of light, boomeranged into a seamless 20 second loop. | The client's brief for the header, and the composition all three of her reference sites open with. |
| **The film** | A 25 second brand film under the hero. Six beats on one stage: a hidden expert, the stage we build, the panel we cast, the live show, and the content that stays. | Two of her notes asked for the same thing, a motion graphic after the header and an animated explainer. This is one answer to both. |
| **The cover card** | Three cards. Point at one and a navy panel comes up and takes the whole card, carrying the list of what is actually included. | "The end CTA showing up to full screen when hovering." On her reference that is a card whose hidden panel covers it. |
| **The red** | One stage-lit crimson field for the visibility ladder, and the same wash on the closing cue. | The red she picked, sampled off her own reference frame: #7A0011 in shadow to #EC2938 in the key light. Stage Crimson sits between them, so the deck's colour is the middle of hers. |
| **The searchlight** | The film opens with the lamp coming up and hunting: it sweeps, misses twice, closes in, and lands on somebody who has been standing there the whole time. | The client's own reference, adjusted as she asked: "instead of a person falling I want the light to search for the person here and there and then find the person standing." |
| **The flood** | The closing block. Pointing at it brings the red up from the floor across the whole field. | The only moment on the site where the entire field goes red, which is what the deck's action colour is for. |

Everything switches itself off under `prefers-reduced-motion`, and the whole site
is fully readable with JavaScript blocked.

### The two clips

| File | What | Size |
|---|---|---|
| `assets/media/hero-portal-loop.mp4` | The hero. 1280x960, 20s, silent, boomeranged so the loop has no seam. | 1.05MB |
| `assets/media/oyss-how-it-works.mp4` | The brand film. 1600x900, 25s, silent. | 0.94MB |

Both are served from this repo rather than the tool that generated the source
footage, so nobody outside this project can delete the home page's main visual.
The unedited hero source is one folder up as `hero-portal-source.mp4`, and the
film is rendered by a script (Pillow into ffmpeg) so its copy and timing can be
changed and re-rendered rather than re-shot.

Both clips pause when scrolled off screen, are skipped entirely on a metered
connection and under `prefers-reduced-motion`, and the film's five beats are
also written out as text underneath it. Nothing on this page is only available
to somebody who can watch a video.

### The interior pages

All ten open with the same component as the home page: type column left, media
panel full bleed right. What changes is the size and what is in the panel.

The home page gets the doorway film. Every other page gets a still PLATE CUT
FROM THE BRAND FILM, so the picture at the top of a page is a frame of the same
stage the film is shot on rather than stock, and the whole site is lit by one
lamp.

| Plate | What it shows | Pages |
|---|---|---|
| `plate-solo` | One figure in the beam | About, Assessment, Spotlight Call |
| `plate-rig`  | The host frame and the panel under it | The Experience, Apply |
| `plate-live` | The same rig, on air, audience filling in | Panelists, Panelist application |
| `plate-keep` | The content strip afterwards | FAQ, both agreements |

Two sizes: `reel--page` for the pages you read, `reel--short` for the ones that
carry a form or a contract, where the object below is the content and the head
should get out of the way.

Re-cut them with the commands in `_film/README.md` if the film changes.

### The mark

Simplified. It used to be a navy disc carrying two thin rays, a radial glow and
a pool; on a navy masthead the disc is invisible, so what was on screen at 34px
was two gold slivers and a dash with a haze behind them. It is now one flat
gold beam and the pool it lands in, which is what the identity actually is, and
it reads at 24px.

### Responsive

Three layouts, all built and checked:

- **Desktop (1041px and up)** Type column and film side by side. On a short
  screen, a 1366x768 laptop included, the air compresses so the primary action
  stays above the fold; the headline never shrinks to make room.
- **Tablet (621 to 1040px)** The film moves above the copy at its own aspect,
  the cards go to one column and print in full rather than hiding half of
  themselves behind a hover, and the ladder goes 2x2.
- **Phone (620px and down)** Same stack, tighter. Every hover-only reveal is
  printed open, because a detail that only exists on hover does not exist on a
  phone.

### The hero clip

`assets/media/hero-portal-loop.mp4`, 1.05MB, 1280x960, 20 seconds, no audio.

It is served from this repo, not from the generation tool's CloudFront bucket, so
nobody outside this project can delete the home page's main visual. The unedited
source is kept one folder up as `hero-portal-source.mp4`.

The clip pauses whenever it is scrolled off screen, is skipped entirely on a
metered connection or under `prefers-reduced-motion` (the poster frame carries the
same picture), and its vertical framing follows the viewport: the wider the screen,
the further down the frame the crop travels, so the figure and the floor stay in
shot on a 1366x768 laptop instead of falling off the bottom. On a phone the clip
takes the top of the screen at its own aspect and the headline stands on the ink
below it, because no scrim heavy enough to put type over a doorway of light leaves
a doorway worth showing.

---

## Pages

| Page | Purpose |
|---|---|
| `index.html` | Home |
| `experience.html` | The Own Your Stage Experience™, $2,997 |
| `assessment.html` | Readiness Assessment — **working**, scored, returns one of the four levels |
| `panelists.html` | Featured Panelist Program, $47 |
| `about.html` | The studio and the founder |
| `faq.html` | The questions worth asking before committing |
| `apply.html` | Host Package application — **working** |
| `contact.html` | Spotlight Call request — **working** |
| `apply-panelist.html` | Panelist application, built to your DRAFT form — **working** |
| `agreements/host.html` | Host Services Agreement, all 41 sections, **signable** |
| `agreements/panelist.html` | Featured Panelist Agreement, all 26 sections, **signable** |

### The agreements

Both are converted directly from your `.docx` files by `agreements_build.py`, so
the published wording is faithful to your legal text and a legal edit is one
command away, not a retyping job. Each page gives you:

- The full agreement, set as an editorial document rather than a wall of text
- A sticky contents rail that tracks where the reader is
- A reading-progress beam across the top
- **A signature block that stays locked until the reader reaches the end of the
  agreement.** Reading is the point.
- Typed signature rendered live in the brand serif, with an **auto-stamped date
  that cannot be edited or backdated**
- Acknowledgment checkboxes mapped to the acknowledgment section of each contract
- The fee stated plainly before signing ($2,997 / $47), with the non-refundable
  language in view
- Print / save-as-PDF that strips the navigation and prints the document clean

Putting the contracts on the public site is a deliberate choice, not an
oversight. Both pages say "read this before you pay" and point at the clauses
people most often miss. It costs nothing and it is the single most credible thing
on the site — "Credible" being brand essence word 03.

---

## What is real and what is a demo

**Real and working now:** all navigation, the scored assessment, every form's
validation and submission flow, the signature gate, signature capture, date
stamping, print output, responsive layout, reduced-motion, and the whole design
system.

**Stubbed, one line each:** every form has a `CONFIG.endpoint` set to `null` at
the top of its script. Point it at a GoHighLevel webhook (or the LeadConnector
contacts endpoint) and it goes live. Field names are already keyed to match CRM
fields, and each submission carries a `tag` for workflow triggers:

| Form | Tag |
|---|---|
| `apply.html` | `host-application` |
| `contact.html` | `spotlight-call-request` |
| `apply-panelist.html` | `panelist-application` |
| agreements | `OYSS.signing({ endpoint: ... })` |

**Not built, because it needs a payment account:** the $2,997 and $47 charges.
The signature step ends by handing off to payment; wire that to Stripe or the GHL
payment step. Signing and paying are deliberately two steps, which matches what
both agreements actually say ("confirmed only after this Agreement is signed
**and** the fee has been paid").

---

## Answering the GoHighLevel question

**The site cannot be created inside GHL programmatically.** GoHighLevel's public
API is read-only for funnels and pages — there is no page or funnel builder
endpoint, and the builder itself cannot be driven reliably. So it is a paste job,
and the work has been done to make it one paste per page.

`python build.py` writes `_ghl/`: one block per page, each **a complete page
including the masthead and footer**, with internal links already rewritten to
funnel slugs (`/experience`, `/host-agreement`) and every asset path made
absolute. Paste one into a Custom JS/HTML element and the step is done.

**See `GHL_SETUP.md`** for the step-by-step: the funnel step names to use, the
section settings, wiring the forms to an inbound webhook, and why the binding
signature belongs in GHL's Documents & Contracts rather than in the HTML.

Two things were built for this from the start:

- **Every selector is scoped under `.oyss`**, with no global reset and no bare
  element styling. Tested against a simulated GHL page that applied its own
  `h1`, `p`, `ul`, `a` and form styles: nothing leaked in either direction.
- **A full-bleed escape hatch.** A page builder wraps pasted markup in a
  centered, padded container, which letterboxes every full-width dark section.
  The blocks carry a `.oyss--bleed` class that breaks out of it, so the design
  survives even if someone forgets to set the GHL section to full width.

There is no ChatGPT connection available in this environment, so nothing was or
could be pushed there.

---

## Open items — these need Annette

1. **Founder biography and portrait.** The About page has a visibly marked
   placeholder. Nothing has been invented. Needs her background, the experience
   that led to the studio, and a portrait shot to the deck's spec (shoulders up,
   one warm key at 45°, navy background, eyes to camera).
2. **Testimonials.** None exist yet, so none are shown. When there are real ones,
   they belong on the Experience page above the investment block.
3. **Spotlight Call calendar.** `contact.html` has a marked slot for the GHL
   calendar iframe. The form beside it works as the fallback.
4. **Payment accounts** for the two amounts above.
5. **Content deliverables schedule.** Both the concept document and the
   agreements say the specific post-event deliverables are "to be specified in a
   separate document." The site says the same rather than inventing a list.
6. **Legal review of the two agreement pages** before anyone signs for real. They
   are marked "Draft for review · not yet legally executed" on the page.

---

## Accessibility

Measured on the rendered pages, not assumed from the stylesheet. **All 11 pages
pass WCAG AA contrast at both 1280px and 390px, with zero failures.** Getting
there caught four genuine bugs that were invisible in the source:

- The masthead's primary CTA was inheriting ivory-at-70% over crimson (3.03:1)
  because `.masthead nav a` outranks `.btn--primary` on specificity.
- Footer captions and signature-block field labels kept their light-context slate
  over near-black and navy (2.74:1 and 2.41:1) because those containers are dark
  but are not `.dark`.
- Gold text on ivory failed everywhere it appeared at small sizes (1.89:1). The
  deck already warns that gold on ivory fails; `#84662A` is the darkest step that
  still reads as gold and measures 4.81:1.
- Dark-section captions sat at 4.22:1, just under the floor.

Also: zero horizontal overflow at 390px, one `<h1>` per page, skip link, visible
focus rings, 20px checkbox targets, and form errors announced via `role="alert"`.
The audience skews 40+, so this is not a checkbox exercise.

---

## Rebuilding

```
cd oyss-site
python agreements_build.py     # regenerate agreements from the .docx sources
python build.py                # regenerate all pages + the _ghl/ blocks
```

Edit page bodies in `_pages/`. The masthead, footer and navigation live in
`build.py` so they stay byte-identical everywhere. Do not edit the generated
`.html` files at the root — they are overwritten.

```
oyss-site/
├── _pages/          page bodies (edit these)
├── _ghl/            paste-ready GHL blocks (generated)
├── assets/
│   ├── oyss.css     the design system, commented against the deck
│   ├── oyss.js      the light engine, the assessment, the signing flow
│   └── favicon.svg
├── build.py
├── agreements_build.py
└── *.html           generated (do not edit)
```
