# Own Your Stage Studio - website draft

A working draft of the company site.

---

## THE IDENTITY CHANGED (September 2026) - read this before the rest

The site was built to the **OYSS Brand Deck v3**: Authority Navy, Spotlight
Gold, Stage Crimson, Crimson Pro and Work Sans, with light as the only motif.
A new brand sheet has replaced all of it, and the site has been rebuilt to
the new one. **Everything below this section still describes the old deck's
reasoning.** It is kept because most of it explains WHY a component exists,
and that reasoning survived the recolor - but wherever it names a color or
a typeface, read this table instead.

| | Brand Deck v3 (old) | Brand sheet, Sep 2026 (current) |
|---|---|---|
| Identity color | Spotlight Gold `#DDAA52` | **Signature Red `#B91C1C`** |
| Accent on dark | gold | **Rose Red `#E05A5A`** - Signature Red measures 2.1:1 on the dark ground and cannot be used there |
| Tint field | one gold panel | **Soft Blush `#F9E9E7`** |
| Ground | Spotlight Ivory `#F7F2E8` | **Warm Neutral `#F8F5F2`** |
| Dark | Authority Navy `#101A31` | **Charcoal `#2E2E2E`**, taken to `#1F1E1D` as a surface so Rose Red clears 4.5:1 on it |
| Action | Stage Crimson `#C92E38` | **Signature Red `#B91C1C`** |
| Display type | Crimson Pro, a serif | **Montserrat**, 700 for headings and 800 for the wordmark |
| Reading type | Work Sans | **Lato** |
| Signature | gold italic serif | **Sacramento**, the brand sheet's own hand, used once (the agreement signature) |
| The mark | a navy disc carrying a gold beam and a pool | **the A of STAGE**: two strokes at a 2:1 rise, flat apex, an arch in the counter |
| The ornament | one flat gold pool | **a short red rule** - the sheet draws one under every label stack and draws no pool |
| The motif | light: beams, falloff, pools | **the silk**, a red chiffon ribbon. Light survives as what the silk is lit by. |

### What that meant in practice

- **317 color values migrated by RGB triple**, so a value moved whether it was
  written as a hex or inside an `rgba()`, and the alphas came through untouched.
  The old token NAMES are kept (`--navy`, `--gold`) and repointed, because
  renaming ninety-five call sites is how one gets missed. Section 1 of
  `oyss.css` maps the two sets against each other.
- **The mark is set inside live text**, not placed as a picture of a wordmark:
  the lockup is `Own Your St` + the mark + `ge`, so it stays selectable, scales
  with the type and needs no 2x file. `build.py` carries the measured geometry.
- **The silk runs in exactly three places** - the footer, the field a form
  sheet lands on, and the pull quote. `assets/silk.svg` is generated art: 17
  tapered ribbons over a left-to-right dissolve.
- **Every photograph was regraded warm.** Measured on the darkest 30% of each
  frame, blue ran 7 to 33 points ahead of red in every commission, which was
  right for a navy ground and wrong for a charcoal one. `_art/process.py` now
  carries a luminance-masked warm-shadow pass, and the two clips get the same
  move through ffmpeg's `colorbalance` so a poster frame and its clip stay one
  picture. Faces sit in the key light, so the grade warms the room, not the
  people in it.
- **The plates with the logo baked in are now rendered from the site's own
  stylesheet.** `python _art/plates.py` writes the holding slide and Annette's
  three Zoom backgrounds through Chrome, using the same CSS and the same
  lockup, so they cannot go stale again without the site going stale too.
  (Needs the site served on :8899 first.)
- **`_film/render_film.py` has NOT been rebranded.** It renders the 25 second
  brand film in Crimson Pro and Work Sans on navy and gold. That film is not
  shipped on the site, so nothing on the live pages is stale - but the file
  will render the old identity if anyone runs it.
- The rendered audit is back to **55 probes, 0 findings** at five widths.

---

## The idea

The brand has exactly one motif. The deck is unusually strict about it:

> Light is the only motif. Beams, falloff and pools. Never a lamp, a curtain,
> a microphone or a proscenium. *(deck p14)*

So the site has exactly one motion system, and it is not decoration. **Nothing
slides in, nothing bounces, nothing fades from nowhere. Things become visible
because they are lit** - which is the same sentence the business uses to describe
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
| **The red** | One stage-lit crimson field for the visibility ladder, and the same wash on the closing cue. | The red she picked, sampled off her own reference frame: #7A0011 in shadow to #EC2938 in the key light. Stage Crimson sits between them, so the deck's color is the middle of hers. |
| **The searchlight** | The film opens with the lamp coming up and hunting: it sweeps, misses twice, closes in, and lands on somebody who has been standing there the whole time. | The client's own reference, adjusted as she asked: "instead of a person falling I want the light to search for the person here and there and then find the person standing." |
| **The flood** | The closing block. Pointing at it brings the red up from the floor across the whole field. | The only moment on the site where the entire field goes red, which is what the deck's action color is for. |

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
| `assessment.html` | Readiness Assessment - **working**, scored, returns one of the four levels |
| `panelists.html` | Featured Panelist Program, $47 |
| `about.html` | The studio and the founder |
| `faq.html` | The questions worth asking before committing |
| `apply.html` | Host Package application - **working** |
| `contact.html` | Spotlight Call request - **working** |
| `apply-panelist.html` | Panelist application, built to your DRAFT form - **working** |
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
on the site - "Credible" being brand essence word 03.

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
API is read-only for funnels and pages - there is no page or funnel builder
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

## Open items - these need Annette

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
`.html` files at the root - they are overwritten.

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

---

# The human pass, 8 September 2026

Two reviews came in together. One asked how much the site reads as AI built and
answered "about 6 out of 10". The other said the page had twelve ideas and no
spine. They are the same complaint from two directions. Annette also supplied
two new spotlight clips for the header.

Nothing was redesigned. The brand system, the palette, the type ladder and the
light motif are untouched. What changed is the structure of the home page, the
footage it opens on, and the removal of a working note that was live in
production.

## The footage

She sent two clips, both 1080x1920, 8 seconds, 24fps, both from the same
generator.

**`erasio_Spotlight_illuminating_person`** is the one in the header. It renders a
stable, believable figure: a real suit silhouette, defined arms and legs, a
clean shadow in the pool.

**`erasio_Spotlight_searching_for_person`** is the better story, and it is not the
better clip. Its figure artefacts visibly: the jacket dissolves into the haze
around the torso, the shoulders go asymmetric, the head resolves as a featureless
blob. On a site whose entire brief this round is "stop looking machine made",
a visible generative artefact in the hero is disqualifying. It is used once, as
a frame rather than as motion.

**Both clips carry a watermark.** A four point sparkle at roughly x=900, y=1740
in the 1080x1920 frame, invisible at normal brightness and obvious under a two
stop lift. It is removed with an ffmpeg `delogo` box in the encode; the region is
smooth dark floor, so the patch does not show. Anything else that comes out of
that generator needs the same treatment. The recipe is in the commit and repeated
here:

    ffmpeg -ss 3.5 -to 8.04 -i <source> -an -movflags +faststart \
      -vf "delogo=x=843:y=1686:w=116:h=112" \
      -c:v libx264 -preset veryslow -crf 27 -pix_fmt yuv420p \
      -x264-params "aq-mode=3:aq-strength=1.15:deblock=-1,-1" \
      assets/media/hero-spotlight.mp4

**The cut.** The source spends its first 3.5 seconds igniting and then holding an
empty stage, and the figure does not appear until 5.2s. Nobody looks at a hero
for five seconds. Trimmed to start at 3.5s: the stage is already lit on load, the
figure resolves 1.4s in, and it holds. 4.5 seconds, 528KB, full 1080x1920.

**It plays once.** The light arrives and stays, which is the sentence the business
uses about itself, so it should not loop back to darkness. `data-once` in the
markup and `playOnce()` in `oyss.js` module 15: `play()` on an ended video seeks
to zero, so without the guard the room re-ignited every time a reader scrolled
back to the top.

**Why the hero is still a split and not full bleed.** A 9:16 frame is exactly the
shape the split composition was already right for. The media panel is about
0.77:1, so `cover` crops about a fifth of the height and the figure, the pool and
the beam all survive. Put the same clip behind a full-width hero and you get a
horizontal band across the subject's chest.

## Blending it with the masthead

The bar has always been transparent over the hero. That was fine over a dark
doorway and wrong over a beam, because the cone is the brightest thing in the
frame and it arrives exactly where the navigation sits. A `text-shadow` was doing
the work, which is a crutch, and it still left the bar looking stuck on top of a
picture.

Section 36.2 replaces it with a real scrim: Authority Navy rather than ink,
spanning the whole hero rather than just the media panel, so the two columns
share one ceiling and the beam appears to come from behind the bar.

It went on **every** hero, not only the home page. `_build/audit.py` measures
this from real pixels instead of walking DOM colors, and that turned up the same
failure on four interior pages against the light in their plates: "FAQ" at 3.8:1
and the Apply button at 3.6:1 on `apply.html`, where a color walk had reported
the page background and seen nothing wrong.

## What changed on the home page

Ten sections to eight. Eleven eyebrows to four. Eleven `01`-style numerals to
four. Six trademarked frameworks to three.

    was                              now
    hero (portal film)               hero (Annette's spotlight clip)
    the 25s explainer film           gone
    three cover cards                gone
    the dimmer ladder                gone, it lives on the assessment page
    six cue rail                     four stages
    the panel rig                    the same rig, on the real artwork
    the ledger                       folded into the price as .terms
    price                            price
    the panelist section             one line at the end
    the close                        the close, on real footage
    -                                the essay (new)
    -                                the stage, shown (new)
    -                                the manifest (new)
    -                                Annette (new)

Three sections are built deliberately wrong for the landing-page kit, because
the tell was never one element, it was that every section came out of the same
kit:

- **`.essay`** is one offset column of running prose. No eyebrow, no grid, no
  picture, nothing to hover. It is the quietest thing on the site on purpose.
- **`.showcase`** is plates rather than cards: unequal widths, unequal baselines,
  the big one running off the left edge of the page.
- **`.manifest`** is a delivery note. A quantity column, an item column, hairline
  rules, no boxes and no icons.

Headlines are now mostly plain ("What happens over three months", "What you keep
afterwards", "What it costs, and what we need from you"). Two clever lines
survive and they are both Annette's.

## The evidence

The single biggest note in both reviews was that a studio selling production was
showing no production. The branded stage frames existed and had never been on the
site. They are now the center of the page: the host frame carrying Annette's own
nameplate bleeding off the left edge, the holding slide beside it, and the six
frame rig rebuilt on a crop of the real panelist artwork instead of a CSS
gradient.

The four source PNGs were 3.9MB. They are now 132KB of JPEG in `assets/media/`,
with a whisper of noise added on conversion to break the gradient banding those
files carry. The PNGs stay in the repo as the masters.

**One thing to raise with Annette:** the stage frames carry the OLD lockup, the
navy disc with the lamp icon, which the site replaced in the September pass. The
site and the Zoom backgrounds now disagree. Re-rendering her Zoom frames is her
call, not ours, so nothing was touched.

## The deliverables were invisible

The Product doc specifies the content package in detail: full replay, registration
export, three host highlight videos, one for every panelist, about twenty edited
short-form videos, captions, a ninety day calendar. None of it was on any page of
the site. It is the most concrete thing in the whole offer, and no generic
template has "one featured highlight video for each panelist" in it. It is now
the manifest on the home page and again, itemized, on the Experience page.

## The About page

`Biography pending from Annette` was live in production, and under it a note
naming the site her portrait came from. Both are gone.

Nothing was invented to replace them. The quotation is **verbatim** from her
completed Brand Discovery Questionnaire, question 5, and the paragraphs under it
paraphrase the same source and question 7. **She should confirm she is happy to
have those words public**, and a real 80 to 120 word professional biography from
her would still be an upgrade on this.

Also on that page: the five brand words were a numbered cue stack, 01 to 05, on a
rail. The order of the five is not the content, so the numbers were decoration and
the rail was the third place on the site drawing the same picture. It is one
paragraph now. The three equal cards at the bottom are a plain two column
comparison, written to deliberately different lengths.

## Measuring instead of looking

`_build/audit.py` drives the system Chrome over the built site and probes 11
pages at 5 widths:

    python -m http.server 8899
    python _build/audit.py            probe
    python _build/audit.py --shots    probe and screenshot

It checks horizontal overflow, WCAG AA contrast on every rendered text node
against the color actually behind it, the masthead against **real pixels** where
the ground is a moving picture, tap target size, and where the hero's primary
action lands against the fold.

**55 probes, 0 findings** at the time of this commit.

Three real bugs it found, none of which were visible in the source:

1. The masthead over the footage, on four pages. See above.
2. The unlit cue numerals sat at 1.85:1 on ivory and 2.46:1 on navy. A number the
   light has not reached yet is still a number on the screen, and this is now the
   only numbered sequence on the site, so it is content. The resting alpha went to
   .80 and .60, measured at 3.30:1 and 3.91:1, and the row still visibly brightens
   when the light arrives.
3. `.draft-flag` at 3.31:1 on the two agreement heroes. `#84662A` is the darkest
   gold that passes on ivory and it does not pass on near black; on a dark ground
   the flag now takes the full Spotlight Gold, at 8.8:1.

And one build bug: `for_ghl()` rewrote `src` and `href` to absolute URLs but not
`poster`, so the hero's poster frame stayed relative inside a GHL funnel and
would have 404'd against the funnel's own domain.

## Small things done at the same time

- Every page now carries an `og:image`, the holding slide. Every link to this site
  previously rendered as a blank rectangle in WhatsApp, LinkedIn and iMessage.
- `panelists.html` was serving a 984KB PNG for one figure. It serves the 33KB
  JPEG now.
- The home page's total referenced weight is about 1.07MB, of which 528KB is the
  hero clip.

## What is NOT done

The plumbing is untouched, because this pass was about the design. Every form
still has `CONFIG.endpoint = null`, there is no payment path for either the
$2,997 or the $47, the assessment captures no lead, and the domain is not
connected. Those are the launch blockers and they are unchanged.

The 25 second brand film is still in the repo at `assets/media/oyss-how-it-works.mp4`
with its renderer in `_film/`. It is no longer on any page. Nothing else was
deleted.

---

# Art direction and the deck pass, 9 September 2026

Two notes came back on the human pass. The client's: the third section was
"very badly done", the previous version was better, and the fix is real
commissioned imagery rather than a flat 2D approximation. The partner's: the
site had drifted from the brand deck.

Both were right, and they turn out to be one problem. The third section was
showing the studio's branded stage frames **empty**, and deck page 22 says
in a single sentence why that could never work:

> The center two thirds of the frame stays empty. That is where the person
> sits, and it is the only reason this background exists.

An empty frame is not the product. It is the thing the product happens in
front of. At 700px wide it reads as a flat gradient with a banded edge,
because that is exactly what it is.

## The deck was handing over a shot list nobody had shot

Page 21 is not a mood board. It is a specification and a commission:

    PEOPLE & PANELS   Confident experts in warm, polished environments.
                      Shoulders up, shallow depth of field, one warm key at
                      45 degrees, eyes to camera. Virtual panels should look
                      like produced media, never a screen grab.
    ENVIRONMENT       Deep navy, soft amber light, clean negative space and
                      subtle texture. One light source, always from above or
                      behind. No props that turn the room into a set.
    ALWAYS AVOID      Curtains, microphones on stands, spotlights as objects,
                      applauding crowds, podiums, confetti, casual screen grabs.

    SHOT LIST TO COMMISSION OR LICENSE
    01 host portrait, shoulders up, warm key, navy background
    02 panel of four in conversation, mid shot, no podium
    03 attendee watching intently, screen light on the face
    04 empty lit room, negative space for headline overlay
    05 hands and notebook, shallow depth, warm desk lamp
    06 texture plate, dark surface with a single light shaft

None of the six existed. All six exist now, plus seven broadcast-framed
portraits for the panel rig and one product still, commissioned against that
brief with Azure `gpt-image-2`. Two Sora 2 clips carry the ambient bands.

**The pipeline is in the repo and re-runnable:**

    python _art/azure_art.py            everything not yet on disk
    python _art/azure_art.py panel      just the panel portraits
    python _art/azure_art.py --force    regenerate
    python _art/sora.py probe           does the deployment route today
    python _art/sora.py                 the ambient clips
    python _art/process.py              crop, grade, compress into assets/media

`_art/raw/` is gitignored: 26MB of masters that the processed assets are
derived from. Re-run `azure_art.py` to rebuild it. The Azure key is read out
of `E:\atreya\Azure AI keys.docx` at run time and is never written into any
file here.

**Sora note:** memory recorded the swedencentral `sora-2` deployment as a dead
end after it 404'd for over an hour in July. It routes now. `sora.py probe`
proves routing with a real 200 rather than assuming, because a 400 does not
prove it: body validation happens before deployment resolution.

**One prompt needed a second pass.** The "what you keep" still first came back
with sunsets and mountains on the phone screens, which is travel photography,
not panel footage. The fix was naming the subject explicitly rather than
describing it abstractly: "a vertical video still of a different person talking
to camera in a dark navy room". Prompt kept in the script with the note.

## The rig, with people in it

The six frame rig is the centerpiece and it now holds seven commissioned
portraits shot to one lighting setup: one host frame, five panelists, all in
deep navy with a warm key at 45 degrees, so the grid reads as one production
rather than seven stock photos.

Everything over the photography stays **live**:

- the horizontal lockup, top left of the host frame, icon only on a panelist
- the nameplate, bottom right, over a gold stage lip along the floor
- the ON AIR marker
- the key light, which still moves frame to frame the way a producer switches
  cameras

So a name is a text edit, not a re-render, and nothing is soft on a retina
screen. Unlit frames are dimmed to 52% brightness rather than hidden, because a
panel where five faces are invisible is not a panel: it is the light that
moves, not the people.

## Five things the site had drifted from

Every one of these is a sentence in the deck, not a matter of taste.

**1. The mark had lost its circle (p17, p19).** "The icon is always a complete
circle or a complete square. It is never bled off an edge or half shown." An
earlier pass deleted the disc because a navy circle on a navy bar is invisible.
The observation was right and the conclusion was wrong: the deck's own website
mock on page 24 solves it by **flipping the colorway**, an ivory disc carrying
a navy beam, not by deleting the shape. Both approved colorways are now in the
stylesheet; the geometry is measured off the page 19 lockup and normalised to a
64 unit circle. The beam carries the falloff, the pool never does: "The pool is
never a gradient. One flat gold is what makes the mark portable." (p16)

**2. The eyebrow was the wrong color (p11).** The type hierarchy sets the
eyebrow in Stage Crimson on light and Spotlight Gold on dark. The site had
slate: the one rung of a six rung ladder that was not being followed. #C92E38
on #F7F2E8 measures 5.19:1, so this is also the accessible choice.

**3. The gold field did not exist anywhere (p13).** "SPOTLIGHT HIGHLIGHT. Rare.
A single panel, a pull quote, a moment of emphasis." An approved surface in the
palette, unused on eleven pages. It is now the founder's pull quote on the home
page. Once, and nowhere else, which is what "rare" means. Navy on gold measures
8.9:1, and on that field everything goes navy including the pool (p19).

**4. The hero rule was a rectangle (p16).** "One flat gold ellipse. It is the
light the brand is named for, and the only ornament the identity is allowed."
It is the pool now, on every hero.

**5. The tagline was set in plain sans.** The deck closes on it in gold italic
serif with the pool beneath (p25). The footer now does the same.

## A pre-existing bug the new photography exposed

The `.sheet` component lifts out of the dark hero with a negative top margin of
up to 84px, and `.reel--short` sizes itself on min-height rather than on its
content. On `apply.html` the lead ran to three lines and the last of them sat
**40px underneath the sheet** at 1366 and 1440. The sentence "This application
tells us whether the timing is right" was simply not on the page.

Nothing overflowed and no contrast probe could see it, because the text was
present, painted, and covered. Found by measuring the lead's rect against the
sheet's, and confirmed pre-existing by stashing the day's work and re-measuring
against the previous commit: 35px there too.

Fixed with padding on the hero rather than a smaller lift, because the lift is
the component's whole idea. Verified across four form pages at eight
viewport sizes: worst case is now a 15px gap.

## Weight

The home page references about 2.3MB, and a phone loads far less than that:

- the two ambient band clips (730KB) do not load at all under 760px, or under
  reduced motion, or on a metered connection. The poster is the same frame.
- **`preload="none"` cannot express that on its own.** The `autoplay` attribute
  overrides it and the browser fetches enough to start playing regardless.
  Measured: all three mp4s were being pulled on a 390px viewport. The band
  clips now carry no `autoplay` and no `src` until `oyss.js` decides, which
  takes a phone down to one video, the hero.

## Still not done

Unchanged from the previous pass and still the launch blockers: every form has
`CONFIG.endpoint = null`, there is no payment path for either the $2,997 or the
$47, the assessment captures no lead, and the domain is not connected.

**And one thing for Annette:** her Zoom stage PNGs still carry the OLD lockup,
the navy disc with the lamp icon, which the site replaced. The site and her
Zoom backgrounds now disagree. Re-rendering those is her call.

---

# Reading size, real images and the studio's voice, 9 September 2026

Three notes: `notebook.jpg` was "giving full ai vibe" with "gibberish" text on
it, the layout still read as AI-designed, and the body copy was too small for an
audience of established coaches.

## The two things an image model always fails at

`notebook.jpg` had an open ruled page held in sharp focus under a hand. That is
the exact intersection of the two subjects this model cannot do: **writing** and
**hands**. The page carried gibberish squiggles and the second hand had a wrong
thumb. Both are hard to describe and unmistakable to look at.

The fix is not a better prompt for the same shot. It is a shot with no failure
surface:

- the notebook is **closed**, the pen rests on it, there are **no hands**, and
  the sharp point of the picture is the pen nib
- `HOUSE` now bans writing explicitly and by consequence: "no handwriting, no
  print, no signage, no labels, no numbers, no letters... any paper or screen
  surface is blank or too far out of focus to read"

**Rule for anything generated from here on: never frame legible text or hero
hands.** Frame them out; do not prompt them away.

`host-portrait` was re-shot for the same class of reason. The first version was
a retouched, symmetrical, eyes-to-camera corporate headshot, which is the single
most recognizable AI-stock look there is. Reprompted as reportage: caught mid
thought, looking off camera, not smiling, visible skin texture, unretouched, the
register of a broadsheet profile rather than a headshot. The difference is not
subtle.

## One new shot the deck could not have listed

`control.jpg`: a producer at a darkened desk facing a wall of monitors showing
the panel's speakers in their separate frames. The deck's shot list covers the
client's world; this one is **the studio's own workplace**, and it is the most
persuasive picture on the site because it is the only one showing the thing
being bought actually being done. No text, no hands, nothing to fail. It carries
stage four of the process, captioned in the studio's own voice.

## Reading size

The buyer this site describes is an established expert with years behind them,
so the median reader is somewhere between 45 and 65. 17px at 1.65 is a young
designer's number.

Deck page 11 is explicit that the ladder is a set of **ratios**: "Each step is
roughly 1.4 times the one below it. Sizes may scale, but never the
relationships." So every rung moved together and the ratios hold.

    body        17    -> 19px      (+12%)
    lead        18-21 -> 20-23px
    caption     14    -> 15.5px
    eyebrow     12    -> 12.5px, tracking eased from .26em to .2em
    essay prose 19    -> 19.5px at 1.78
    line-height 1.65  -> 1.7

The measure came **down**, from 34rem to 62ch. Bigger type on the same column
width means more characters per line, which is the thing that actually tires an
older reader. Form fields and labels moved with the body: a sixty year old
filling in a $2,997 application should not be squinting at the part that takes
their money.

## Where you are, and what happens next

**Orientation.** The masthead said OWN YOUR STAGE / STUDIO, from which a
stranger cannot tell whether this is a theater company, a design agency or a
recording studio. The descriptor line under the wordmark, which the deck already
specifies (p16, p19), now carries `Studio - Virtual panel events`. No bar and no
strip was added: the words went inside the lockup that was already there. Below
460px the descriptor drops back to `Studio` so the burger keeps its room.

**Action.** Every button named a destination and none said what happens after
the click. New `.donext` micro-copy sits under each primary action, and a four
step block on the home page says what actually occurs between applying and
standing on the stage.

### THE FOUR STEPS ARE PROPOSED, NOT CONFIRMED

This is the same method used for the run of show in the previous round: design
the answer, put it on the page, and let Annette correct by exception rather than
answering an open question. **These specific claims need her sign-off before
launch:**

- the application takes about eight minutes and Annette reads every one herself
- she replies within two working days, either way
- a no comes with what we would do instead
- a chosen date is held for five working days while the agreement is read
- nothing is charged until signature
- a Spotlight Call is thirty minutes, no charge, and she offers two or three
  times that week
- the panelist $47 is only asked for once a place on a specific panel is offered

Every one is plausible for a two person studio and none is contradicted by the
documents, but they are operations, not marketing, and only she can confirm them.

## Breaking the metronome

The last structural tell was rhythm in the literal sense: all eleven sections
used `--bay`, so the vertical beat between one idea and the next was identical
every time. No human lays out a long page that way. Padding is now set by hand
in three sizes by what the section is doing: `.bay--open` for the page's big
moments, `.bay` for the default, `.bay--tight` for a section that belongs to the
one above it.

And one device that is only this client's: `.marginal`, a short line hung in the
left margin in the serif, in **the studio's voice rather than the sales voice**,
the producer talking about the page while the page is running. Used once, on the
division of responsibilities: "The second column is the one clients argue with.
We put it on the sales page anyway, because finding it in the agreement three
weeks later is how engagements go wrong."

## Housekeeping

Removed: `notebook.jpg`, the four `plate-*.jpg` stills cut from the retired
brand film, `hero-portal-loop.mp4`, `stage-frame-host.jpg`, and the 25 second
brand film itself, which has not been on a page since the human pass.
`assets/media/` is 2.5MB total. `panel-f` is generated and kept in `_art/raw/`
as a spare face but not shipped: the rig is one host plus five panelists.

55 probes, 0 findings, at the new type size.

---

# Feedback 2.0, and the prompts, 9 September 2026

Twenty-one annotated screenshots plus a brief for pop-up surfaces. Every note
below is answered; the numbering follows the order in the document.

## The notes

**1, 17, 18, 20. "Remove this line."** The `.eyebrow--keyed` line above every
hero headline, boxed in red on four separate pages. Gone from all eleven. It was
labelling a section whose headline already said what it was, which is the first
tell on the AI-rhythm list.

**2. "Can the logo be continuous motion."** It runs now, on the brand's terms:
a lamp that is on does not flash, it breathes. Beam opacity and pool width drift
a few percent on a nine second cycle, out of phase with each other so the pair
never pulses together. Nothing moves position. At 34px what a reader perceives
is that the light is live rather than drawn. Held while the pointer is down, and
silent under reduced motion.

**3, 6. "This is an ai style, change it to something more humanize."** Twice, on
two components that were the same idea: small gray text beside a gold marker.
That is the generated-UI pattern. Both are now editorial footnotes rather than
UI callouts: serif, reading size, indented, marked by a small raised italic
numeral, the way a note sits in the margin of a printed proof.

**4. "Remove the highlighted part."** The pool ellipse under the band headline.
Gone.

**5. "On hovering each panel section should light up."** Done, and the timer
genuinely stops rather than being outvoted by CSS, because two lights on at once
is the one thing the component exists to say never happens. Hovering a frame
takes the desk the way a producer overrides a running order; leaving resumes the
cycle. Non-hovered frames dip below their resting state so the lit one reads.

**7. "This section is great but something feels missing here."** What was
missing was the specification: the reader had been told the room looks produced
and given nothing to check it against. Added `.spec`, four terms and their
consequences: 1920×1080 on every asset, two rehearsals, one operator on the
frames, a clean separate capture.

**8. "Video lacks clarity here."** Two causes, both fixed. CRF 29 on a dark,
fine-grained clip is false economy: h.264 spends its bits on grain and smears
the faces. Re-encoded at CRF 23 with a tuned deblock and psy-rd. And the scrim
was covering the whole picture at .74 alpha across 42% of the frame; it now hugs
the copy column instead of the image.

**9. "Keep this list style but innovate, try something new with animation."**
The cue sheet was three generic scroll effects layered on one component: a drawn
rail, a sliding bead, a fade per row. It is now one idea instead of three, and
it is the brand's own: each cue is a **lighting state**. The row you are level
with goes to full, rows behind hold at a readable half, rows ahead sit at a
quarter with their numbers unlit, and the rail fills like a dimmer track to
wherever the light has reached. Passing a row hands the light on rather than
revealing it.

**10. "Why image for stage 4... you have already explained 4 steps, now image
and then linking to page, this is not cool at all."** Right, it was the same
thing told three times. Both the picture and the link out are gone.

**11. "Do not use Annette names, it is Own Your Stage team who will reply."**
Every service promise now says the studio. Her name survives only on the founder
byline, which is attribution rather than an operations claim.

**12. "This is confusing section."** The `.marginal` I had added spoke in the
studio's voice while the section beside it spoke to the reader, and two voices
in one block is exactly what makes a block confusing. Removed.

**13. "Do not create assessment as a long form, create it in a box, once the
person selects question 1 question 2 pops up, and then next and back."** Built.
One question in a box, pips for progress, back button, and it advances on answer
after a 420ms beat so you see your own choice register first. The submit button
only appears on the last question, so nobody can submit an unfinished form and
meet an error. **The stepper is applied on top of the full form rather than
replacing it**, so with JS off the page is still the eight question form it
always was and no question is hidden from anybody.

**14. "Why panelist is having the same images as The Experience page."** New
photography commissioned for it: a panelist mid sentence, sharply lit, with the
other experts listening in the darkness either side of her. The distinction is
the point, since a panelist is one expert among several rather than the host.

**15. "Create a video here how it looks."** A video would be the wrong tool: the
thing being explained is how a frame gets dressed, and the dressing is live text
and vector. Baked into an mp4 it goes soft on a retina screen and a copy change
becomes a re-render. So it animates in the browser instead, as a four beat
sequence on the real frame: the light, the frame and mark, the name plate, the
on-air marker, each beat named underneath as it lands. Runs once on scroll,
replays on click or Enter, and **rests fully assembled**, so with JS off the
reader simply sees the finished frame.

**16. "Add a person here, the image is very good and lighting, just add a person
not very big, normal one."** Same room, same light, one figure standing in the
pool at a distance, about a fifth of the frame height, left third still clear
for the headline.

**19. "When you say to sign you should give option to sign at the end, it just
looks another form, nothing looks like an agreement."** The block was already at
the end; what was wrong is that it looked like a web form. It is an **execution
page** now: the witness clause, then two signature panels side by side, each
with a ruled signature line above a printed name and a date. The client's panel
is fillable, the studio's is shown as countersigned, so it reads as an agreement
between two parties rather than a form submitted into a void. The input itself
is invisible furniture: no box, no placeholder, just your name appearing in the
signature face on the rule.

**21. "Remove this line and add something very short motivation quote."** The
domain was sitting where a closing thought should be, and it was already in the
copyright line above. Replaced with: *The room is already looking for you.*

**22. "Lets use this big lines in the footer I really liked."** Taken from the
v2 build, and the right call: the tagline is the strongest thing the brand owns
and it was set in 19px sans halfway down a column. It is now at display scale
above the normal footer, split in the deck's own colors - the promise in ivory,
the payoff in gold.

## The prompts

*"two bottom bar for desktop and top bar for mobile and exit intent for all the
three types of layout."*

Three surfaces, one governing rule: on a premium site a prompt has to be
**earned** or it costs more than it makes.

- **The bar.** Bottom on desktop and tablet, top on a phone. The reason for the
  flip is the thumb: at the bottom of a phone it fights the browser chrome and
  the reader's own hand, and at the top it sits under a bar they are already
  ignoring.
- **It waits for the price.** The trigger is a real element (`.figure__value`),
  not a scroll percentage, so it fires at the same *moment in the argument* on a
  long page and a short one. Before the reader knows what it costs, an "apply"
  bar is asking them to commit to an unknown.
- **The second surface is per page kind, not per page.** `home` and `guide` are
  pages somebody is *reading*, so a prompt is the natural next step and the two
  kinds carry different offers (apply on the home page, the assessment on the
  guides). `form` and `agreement` are pages somebody is *doing*: both surfaces
  stay off, because the action is already on screen and an interruption there
  costs a conversion rather than earning one.
- **Exit intent, all three layouts.** On a pointer device it fires on the mouse
  leaving through the **top** of the window, the only edge that means "going to
  the address bar" rather than "reaching for the scrollbar", and only after six
  seconds. On touch there is no exit gesture, so the honest equivalent is a fast
  upward flick toward the address bar *after* the reader has passed 45% of the
  page. Both conditions matter: the flick alone is just scrolling.
- **It never interrupts somebody mid-form.** If anything on the page has been
  typed or ticked, the modal does not open. Whatever it offers is worth less
  than the application they are already filling in.
- **Everything remembers.** A dismissal is stored for seven days, and the
  storage accessor is wrapped, because a browser with site data blocked throws
  on the accessor itself rather than returning null.
- Real dialog semantics: focus moves in, Tab is trapped, Escape closes, focus
  returns to where it was.

## Verified

55 probes across 11 pages × 5 widths: **0 findings**. Every page loaded at 1440
and 390 with **no JavaScript errors and no failed requests**. The bar was
measured in place at 1440, 1024 and 390, exit intent fired and trapped focus on
both a pointer and a touch profile, and the assessment stepper was driven
through an answer to confirm it advances.

One bug worth recording because it is now the third time on this project: **a
`<span>` with no `display` is inline, whatever its class name implies.** The
prompt bar's title and meta ran together as one sentence, and the panelist name
plate set its three lines horizontally. Both invisible in source.

---

# Feedback 3.0, and the interior pages, 10 September 2026

Six notes in `new changes/feedback 3.0.docx`, plus Annette's covering message:

> Hi AJ, I do like it a lot. Love the color combination, the spotlight on the
> landing page is a cool feature (love it) but I absolutely dislike the
> artificial person stepping into the spotlight. Any chance your team could
> make him/her more natural and human looking? Also, some adjustments to
> various text will be needed down the road. We need to make sure we do not
> over promise on the website (USA!)

1. Use both header clips, looping one after the other, with a very smooth
   transition.
2. A random number 2 is showing up.
3. The artificial person stepping into the spotlight.
4. Remove number 3.
5. Only the home page is looking; the rest need an upgrade in design and copy.
6. Make sure the images look really genuine.

All six are done. Nothing on the home page was restructured - she likes it, and
notes 2 and 4 were the only two that touched it.

## The person in the spotlight

The figure in both of her clips is not disliked for being small. It is disliked
because it **materialises out of empty air** inside the beam, which is a thing
that cannot happen, and because at forty feet the generator gave it no
shoulders, no face and legs a head too long. Neither fault is fixable by
prompting the same shot again: both come from asking a generator for a
full-length human at that distance.

So the shot changed rather than the prompt. `_art/round8.py` commissions the
figure at the distance a photographer would actually stand at for a portrait in
a beam - knee up, weight on one leg, the key rimming the hair and shoulders,
eyes in soft shadow - which is the framing this model renders convincingly and
the framing the six panel portraits on the home page already proved it can.

**Then the clips are used for the thing they are genuinely good at, the light.**
`_art/hero_loop.py` builds one file with three beats:

| | source | what it is |
|---|---|---|
| A | `illuminating_person`, 1.1s to 4.8s | the beam ignites and blooms |
| B | `searching_person`, 1.2s to 4.4s | a narrower beam, different haze |
| C | `spot-figure.png`, 4.3s | a real person standing in it, slow push in |

Both clips are cut **before** their figure appears, so nothing in this loop
dissolves into existence. A joins B on a 0.85s cross fade - same composition, so
the eye reads it as the light changing rather than as a cut. B joins C on a
0.55s dissolve, and it is the one transition where the shot size changes: a wide
room becomes a portrait, so the beam appears to come toward the camera rather
than a person appearing inside it. **A white flash was tried there and thrown
out**; a hero that strobes is a hero somebody has to look away from.

The loop **closes on itself**: the tail of C dissolves into the head of A, so
the browser's own loop point is invisible. Measured, first frame against last:
mean absolute difference 3.76 of 255, which is the haze moving and nothing else.
`loop` on the element is now the whole mechanism, and `playOnce()` in oyss.js is
gone with the `data-once` attribute it guarded.

9.9 seconds, 1.54 MB, 1080x1920, CRF 26. It replaces a 4.5s 818 KB clip, so the
hero costs about 700 KB more than it did. That is the price of the note.

**Where the person sits in the frame** is not a taste decision. The panel is
`object-fit: cover` at `object-position: 50% 58%`, and its aspect runs from 0.48
at a 900px viewport to 1.44 on a phone, where the hero stacks into a band.
Solving cover at both ends leaves one strip that is on screen at every width,
y 740 to 1488 of 1920. The head goes just inside the top of it. Below the hip
the frame falls to black, which is also where the generator put a hand it could
not draw: **the hand is framed out, not prompted away**, same rule as the
notebook in round 6.

`room-figure.jpg` on the About page had the identical fault at an even smaller
scale and was re-shot the same way.

## The two random numbers

Notes 2 and 4, and they were the same bug. Three editorial asides carried a
raised numeral - `1` on the rig note, `2` on the essay note, `3` on the showcase
aside - and a footnote marker is only legible when something earlier in the text
carries the matching reference. Nothing did. They were numbered by where they
sat on the page.

The numerals are gone. What made those notes read as written by a person was
never the marker: it was the setting, the serif at reading size, held in from
the column it comments on, on a shorter measure than the prose above it. That is
what an aside looks like in print and it needs no marker at all.

While looking for the second one, a third turned up on the assessment: the
stepper builds its own "Question 1 of 8" bar and the section label it moves into
the pane said the same thing again, two lines apart. The label is the
no-JavaScript path, so it stays in the markup and is hidden once `.quiz` exists.

## "Only the homepage is looking"

The diagnosis was countable before it was aesthetic.

| | pictures | sections built from the shared kit |
|---|---|---|
| home | 12 | 0 |
| experience | 1 | 5 |
| panelists | 1 | 5 |
| about | 1 | 2 |

Every interior page repeated the same three objects in the same order: a row of
bordered cards with a numeral, a two-column tick list, and a pair of bordered
columns, then the same centerd close with the same two buttons. Three pages
built from the same kit in the same sequence read as one template however good
the words in them are - which is exactly the note.

Section 44 of `oyss.css` is mostly **subtraction**, plus one device per page
that belongs only to that page. Nothing in it introduces a color, a typeface or
a motion rule that was not already in the deck.

**Experience.** The three cards became `.premise`, one statement at display size
and the argument in two unequal columns. The sixteen-item tick grid and the
manifest under it became `.contents`, the same facts set as the contents page of
the schedule they actually belong to: item, leader, quantity. The division of
responsibilities became `.clause` (see below). The boxed price card is gone. Two
photographs at unequal widths (`.pair`) break the column once.

**Panelists.** Same cards, same treatment. Its own device is `.runorder`, the
running order of a produced panel with the reader's own ten minutes lit - it
answers the two questions that page kept being asked, how long am I on and what
happens either side of me, and neither was answered anywhere on the site. The
times are deliberately not clock times: the agreement gives the studio sole
discretion over the format, so the only fixed numbers in it are the three the
agreement states. The frame-assembly animation is unchanged and moved onto
paper, so two dark bands do not sit next to each other.

**About.** The prose was already right. It gained two photographs and lost one
outcome claim.

**FAQ.** Fourteen accordions in a column is a support page; the same fourteen
beside a standing index is a document, and the index is the only thing that
tells a reader how long the page is before they start opening things. Module 18
of `oyss.js` opens the target `<details>` on an anchor hit - recent Chrome does
this by itself, Safari and Firefox scroll to a closed summary and leave it shut,
which reads as a broken link rather than a browser difference.

**Every close is different now.** `.close` is a rule, one line naming what
happens next **on that page**, and one action. The right next step is not the
same on a page about panelists as it is on a page about a three thousand dollar
engagement. The home page keeps its flood; nothing else does.

## "We need to make sure we do not over promise (USA!)"

The substance of this was already written, in the agreements, and the site was
paraphrasing it into a sales object. The Experience page had two bordered
columns headed "We handle" and "We do not handle", which is a comparison table.

It is now `.clause`: an extract from the Host Services Agreement, carrying that
agreement's own clause numbers, in the agreement's own terms.

| clause | what it says |
|---|---|
| 5 | Scope of Services - what the studio provides |
| 6 | Excluded Services - no paid advertising, no guaranteed audience, registrations, attendance, leads, clients, revenue or media |
| 7 | Audience Generation - the room comes from your audience and your panelists, and the studio makes no representation about numbers |
| 8 | Client Responsibilities - intake, sessions, approvals, promotion on the agreed schedule |
| 21 | **No Business-Outcome Guarantee** |

Site and contract cannot now drift apart, because the site is quoting the
contract. **The one-line version of clause 21 is in the footer of every page**,
at caption size and full contrast, not collapsed and not set in gray fine print:
a no-guarantee statement in 10px gray is worse than none, because it reads as
something the studio hoped nobody would find.

Four outcome claims were rewritten in the body copy, each one a sentence that
predicted a result rather than describing the work:

- "which is also why they keep sharing it" - a prediction about what five other
  people will do with their own footage
- "the clips cut from it are still working ninety days later" - a caption cannot
  know that
- "someone else becomes known for the work you should be leading"
- "what they gain is visibility, credibility, professional connection"

Nothing was softened into vagueness. Where a number was real it stayed.

**Still needing Annette, unchanged from round 6:** the four process steps are
PROPOSED, not confirmed - "we reply within two working days", "we hold the date
five working days", "eight minutes to apply", the Spotlight Call being thirty
minutes. They are service promises she controls rather than results claims, so
they were left in place, but she has now been asked twice and they are the
obvious next thing to cut if she does not want to be held to them.

## The images

`_art/round8.py` commissions eight new shots. Every interior hero was a version
of the same picture, a group of people in a dark room talking, which is a large
part of why the pages read as one template. Each page now gets the shot that
belongs to its own subject: a late planning session for the Experience page, a
corridor before you go on for Panelists, one person deciding for the FAQ, a dark
house seen from the back for the Assessment, two people mid conversation for the
Spotlight Call. The notebook and pen on a dark desk is gone; it is the picture on
every consultancy site there has ever been.

**Three shots were re-rolled with hands framed out.** The first `prep-session`
put both of a man's hands in the middle of the frame gesturing and the generator
fused the fingers on one of them. The first `back-of-room` put a grand piano on
the stage, which is a concert hall and the wrong association entirely. Same rule
as always: reframe, never prompt it away.

## The working note that was live in production

`contact.html` carried a pale box reading **"Calendar embed goes here. Replace
this block with the GoHighLevel calendar iframe"**, visible to anybody who
opened the page. That is the third time a marked placeholder has shipped on this
site, so it was not replaced with another note. It is an HTML comment now, and
the form beside it already books the call and was always going to be the
calendar's no-JavaScript fallback.

## The three minute speech

`OYSS - 3-Minute Speech.docx` (new, in `own your studio/`). Read for consistency
against the site; nothing on the site was changed from it, because it is a stage
script and the site is not. Three things in it need Annette's decision:

1. **It calls the free call a "Stop Hiding Strategy Call". The site calls it a
   Spotlight Call.** Two names for one thing, and the speech sends people to the
   site. One of them has to go.
2. **"valued at $297"** and **"the first three to complete it"** are exactly the
   kind of claim her own note is about. A stated dollar value on a free call is
   a price representation, and a first-three scarcity claim has to be true every
   time it is said.
3. The speech says the assessment takes "less than five minutes"; the site says
   about three. Consistent, no action needed.

Otherwise the speech and the site agree closely, which is worth noting: the four
ladder rungs (Hidden, Emerging, Expanding, Visible), the title ("Stop getting
ready. Start getting recognized." is already the home page's close) and the
tagline are the same in both.

Her three shifts - decide what you want to be known for, stop waiting to be
invited onto someone else's stage, make your visibility last - are the cleanest
statement of the offer anywhere in the material, and they are not on the site.
That is a real copy upgrade and it belongs on the home page, which is the one
page she has just said she likes. **Not taken. Her call.**

## Verified

`python _build/audit.py` over 11 pages at 390, 768, 1024, 1366 and 1440:
**55 probes, 0 findings**. No horizontal overflow, no contrast failure, every
hero action above the fold at every width.

## Still not done

Unchanged, and every one of them is a launch blocker:

- Every form still has `CONFIG.endpoint = null`.
- No payment path for the $2,997 or the $47.
- The assessment captures no lead.
- **The domain is not connected.** There is no CNAME in the repo, so the site is
  on the Pages URL while every footer says ownyourstagestudio.com.
- The signature block on both agreements is a front-end demo. Real execution
  belongs in GHL Payments > Documents & Contracts.
- No testimonials, no Spotlight Call calendar embed, no legal review.
- Annette's Zoom PNGs are on the new brand but she still has to swap them into
  her Zoom account.
- `_film/render_film.py` still renders the OLD identity. Not shipped anywhere.

---

# Feedback 4.0, 10 September 2026

Ten notes in `new changes/feedback 4.0.docx`, plus the explainer video, which
arrived in the same folder as
`Own Your Stage Studio Explainer Video_1080p_caption.mp4`.

All ten are done. Nothing was changed that was not in the document.

| | note | where |
|---|---|---|
| 1 | Roll it back to the previous video style, make sure that video will play in loop | home hero |
| 2 | Recreate all these images and make it look more humanize | the six frames of the rig |
| 3 | Add the video here that I will be sharing it with you | home, the wide figure |
| 4 | Remove this from the footer, I feel like it is added uncessarly | the legal line |
| 5 | It is not going to be a real round table conference, it is going to be virtual | Experience, the pair |
| 6 | Not liking this at all | Experience, contents leaders |
| 7 | Same here | the second contents list |
| 8 | Start the form like this | Assessment |
| 9 | The image is not going with the page | FAQ hero |
| 10 | Make sure the form overlaps the black above the fold section, and change the image to a more humanize person | Apply |

## 1. The hero, rolled back

The three beat sequence from round 8 is gone and the earlier footage is back:
her `illuminating_person` clip, the same 3.5s to 8.04s cut, the same delogo box,
the same encode settings. It is in `_art/hero_loop.py`, which now builds the
rollback rather than the sequence. The round 8 version is at commit `59fd124`.

**One thing in that note could not be done literally.** That cut opens on a lit
but empty stage and ends with the figure standing in the beam, so putting
`loop` on it as it is makes him vanish every 4.5 seconds and resolve again out
of nothing. Measured, first frame against last: mean absolute difference 18.93
of 255, and the whole subject IS the difference.

So the tail dissolves back into the head. Nothing was added: the dissolve is
made only from this clip's own frames, and the result is the same shot with its
last 0.7 seconds cross faded onto its first 0.7. The seam measures 0.58 of 255
now, which is invisible. 3.8 seconds, 476 KB, down from 818 KB.

## 2 and 10. The rig, recreated

**What made those six faces read as generated was not the framing.** A video
call frame really is eyes to camera, head and shoulders, centered. It was
everything around it: the six were lit identically, retouched to the same flat
skin, shot against the same black void with nothing behind them, and all six
were sitting still with the same neutral expression. Six people cannot be that
alike. A real six up grid is six different rooms, six different cameras, six
people at slightly different distances, and at any moment one of them is mid
sentence.

`_art/round9.py` keeps the broadcast framing and changes the six things that
were identical: a real room behind each one instead of a void, a different
practical light in each, unretouched skin with visible texture, a different
moment caught in each, slightly different distances, and no two the same.

The host frame is also the Apply page hero, which is the face note 10 circled,
so notes 2 and 10 are answered by the same regeneration.

`panel-b` was rolled twice. "Brow furrowed in thought" came back as a scowl,
which is not what a panelist looks like while somebody else is talking.

## 3. The explainer video

`_art/explainer.py`. The file arrived at 1920x1080, 25fps, 2 minutes 22, stereo,
**106 MB**, with the captions burned into the picture.

- **720p, not 1080p.** The figure it sits in is at most 1180 CSS px wide, so
  720p is already above 1x. The burned-in captions are the one thing a
  downscale hurts, so the encode protects fine detail rather than chasing a
  number: CRF 26, no denoise, the same psy and deblock settings the site's other
  clips use. **11.5 MB.**
- **The audio stays.** It has a voice over. 128k AAC.
- **It does not autoplay and does not preload.** Two minutes with sound is
  something a reader chooses, so the page ships a poster frame and the browser
  fetches nothing until somebody presses play. Anyone who scrolls past pays for
  a 71 KB JPEG.
- **The caption sits under it, not over it.** `.figure-wide` lays its caption
  over the bottom of the picture on a gradient, which is exactly where a video's
  scrubber is. `.figure-wide--video` in section 45.2 drops the overlay.
- The poster is taken at 2 seconds, not 4. Four caught the opening title mid
  dissolve with half a sentence faded out, which looks like a broken render.

## 4. The footer line

The no-guarantee paragraph added in round 8 is removed, along with its rules in
the stylesheet so nothing dead is left behind. **The same statement is still on
the Experience page** as clause 21 of the extract from the Host Services
Agreement, in the agreement's own words, which is where the substance of it
lives.

## 5. The panel is virtual

The picture was four people in armchairs in one room, which is an in-person
panel and the wrong product. It is now the host at her desk watching five other
experts talking in separate video call frames on a screen, with the screen glow
as the only light. `panel-conversation.png` is out of `process.py`;
`panel-virtual.jpg` replaces `panel-room.jpg` on the page.

## 6 and 7. The leaders

Both contents lists on the Experience page had a dotted rule running from the
item across to its quantity. Gone. The spacer stays and still holds the column
of figures out at the right hand edge; there is simply nothing drawn across the
gap. The item description gets the width the leader used to take.

## 8 and 10. The form never actually overlapped

Both screenshots draw a box from inside the dark band down over the top of the
white form. **The form was already built to do exactly that:** `.sheet` carries
`margin-top: -84px` so it lifts out of whatever is above it. Measured on the
live page, it was not doing it, and the reason is margin collapse.

The sheet is the first in-flow child of `.sheetbay`, and neither the section nor
the `.wrap` between them establishes a block formatting context, so the negative
margin collapsed through both and moved THE SECTION up instead of lifting the
sheet out of it. On apply.html the section top and the sheet top measured
identical, at 463. The section carries the light background, so it painted Warm
Neutral over the bottom 82px of the dark hero and the overlap was invisible.
Every time, on all three form pages.

`display: flow-root` stops the collapse. The section now starts where the dark
band ends and keeps its background there, and the sheet lifts out over the dark
on its own. The lift went up to 56 to 118px so the overlap is unmistakable
rather than technically true.

**The hero above it has to give that height back**, or the sheet covers its last
line. That is the same bug round 5 fixed by hand on apply.html, and raising the
lift brings it straight back, so it is a rule now rather than one page's
padding. Measured at 1440, 1366, 1024 and 390: 95 to 114px of visible overlap on
desktop, and the sheet covers no hero text at any width.

## 9. The FAQ picture

It was a man alone at a desk at night, which reads brooding and lonely against a
bright premium studio brand. Same beat, somebody taking their time over it
before they commit, but in this brand's light and unhurried rather than
troubled. Cropped 16:9 and anchored high, because the generator left her hands
merging into a cuff at the bottom of the frame: **cropped out, not prompted
away**, same rule as always.

## Verified

`python _build/audit.py` over 11 pages at 390, 768, 1024, 1366 and 1440:
**55 probes, 0 findings**. All 11 pages at 1440 and 390 with no JavaScript
errors and no failed requests.

`assets/media` is 17 MB, of which the explainer is 12. Nothing on any page
preloads it.

## Still not done

Unchanged, and every one of them is a launch blocker:

- Every form still has `CONFIG.endpoint = null`.
- No payment path for the $2,997 or the $47.
- The assessment captures no lead.
- **The domain is not connected.** No CNAME in the repo, so the site is on the
  Pages URL while every footer says ownyourstagestudio.com.
- The signature block on both agreements is a front-end demo.
- No testimonials, no Spotlight Call calendar embed, no legal review.
- The three minute speech still calls the free call a "Stop Hiding Strategy
  Call" where the site says Spotlight Call, and still carries "valued at $297"
  and "the first three to complete it".

---

# Feedback 5.0, 10 September 2026

Eight notes in `new changes/feedback 5.0.docx`, four on desktop and four on a
phone, plus one from Harsh: "site feels a bit heavy on desktop please check
that too."

| | note | where |
|---|---|---|
| 1 | The form is overlapping the text | Assessment |
| 2 | Make the apply form similar to the assessment form style | Apply |
| 3 | These two images are not looking good can you change it | the rig, panel-c and panel-d |
| 4 | This one should be a proper section with headings and everything | the explainer video |
| 5 | The panelist section is not looking on mobile | the rig, on a phone |
| 6 | The text is cutting on mobile | the band copy |
| 7 | Both the images are looking same | the Experience pair |
| 8 | The text is very sticking to the screen | the band copy again |
| 9 | The image is cutting of the panelist one main image | mobile hero pictures |

## 1. The form was overlapping the text

Round 9 raised the sheet's lift and added a rule giving the section above it
the height back. **The assessment carried an inline `padding-bottom` that beat
that rule**, and the inline value happened to be smaller than the lift, so the
sheet landed on the last line of the paragraph above it. The round 9
verification missed it because it only measured text inside `.reel__copy`, and
on this page the covered line is in a `.bay--half.dark`.

Two changes. The inline style is gone. And the padding is now **derived from
the lift** rather than being a separate number that has to be remembered:

    .oyss { --sheet-lift: clamp(56px, 8vw, 118px); }
    .sheet          { margin-top: calc(-1 * var(--sheet-lift)); }
    :has(+ .sheetbay) { padding-bottom: calc(var(--sheet-lift) + clamp(28px, 4vw, 52px)); }

Re-measured on all three form pages at 1440, 1366, 1280, 1024, 820 and 390:
the gap between the lowest line above and the top of the sheet runs 39 to
163px and is never negative.

## 2. The application, stepped

The assessment shows one question, a count, a row of pips and a Back control.
The application was a single scroll of eighteen fields under four headings,
which is a different object on the same site.

Module 20 of `oyss.js` gives it the same chrome from the same classes. Three
things differ, each because the content differs:

- **it steps by section, not by field.** "About you" is four questions that
  belong together; splitting them would be eighteen screens.
- **it does not auto advance.** The assessment advances on a radio because the
  answer IS the click. Here somebody is typing, and being moved mid sentence
  would be hostile. There is a Continue button.
- **it validates the current section before it will move on**, so nobody
  reaches the end and meets a list of things they missed four screens ago. The
  submit handler still validates everything, and when something is missing it
  hands the field to the stepper, which goes and finds its step.

The count says "Step 1 of 4" rather than "About you 1 of 4", because the
section heading two lines below already says About you and that exact
duplication shipped once on the assessment.

With JavaScript off the form is the long scroll it always was, every field on
the page, one submit button. `formSteps` returns null and changes nothing if
the markup is not what it expects.

## 3. The two frames that stood out

Round 9 fixed six identical frames by making all six different and overshot on
these two: `panel-c` came back with a broad open laugh against the brightest
background in the grid, and `panel-d` came back near black and stern. Side by
side they read as one person having a great time next to one person having a
terrible one, which is what the box in the screenshot was around. Both are back
toward the middle: same rooms, same lighting idea, calmer expressions, matched
exposure.

## 4. The film has a section now

It was a bare figure at the tail of the delivery note above it, which made a
two minute film explaining the whole business read as an afterthought. It is
its own section with a heading, a standfirst and its own caption.

**The thumbnail.** Her own opening title card is the poster. The film has its
own design language and putting the site's furniture on the front of it would
only make the two disagree. What was added is the thing a poster frame actually
needs: **a play control you can see.** Chrome's native one on a poster is a
small triangle in the bottom corner, so the block read as a still image with a
toolbar. Now the whole picture is the button.

The element ships **with** `controls` so a reader with no JavaScript can play
it; the module takes them off once the overlay exists to replace them, and puts
them back the moment it starts. Still `preload="none"`, so a reader who never
presses play downloads a 71KB poster and nothing else.

## 5. The rig, on a phone

It was collapsing to two columns at 760 and to **one** at 420, so a phone got
six full width photographs stacked down the page. That is not the component:
the component is one host frame with five satellites, and the composition is
what says produced multi camera panel rather than six headshots.

The desktop grid is kept all the way down. What changes is everything that
cannot survive a 110px tile: the five satellites drop the nameplate to the role
line alone, the ON AIR marker and the mark shrink with it, and the host frame
keeps its full plate because it is the one tile with room. On the host, the
wordmark next to the mark is dropped too, because at 230px wide it ran under
the ON AIR badge.

## 6 and 8. The text was touching the screen edge

Both notes, one bug, and it is the padding shorthand:

    .band__copy { padding: clamp(56px, 9vw, 110px) 0 clamp(38px, 5.5vw, 66px); }

`.band__copy` is also a `.wrap`. That shorthand set left and right to **0** and
took the wrap's gutter with it. On a desktop the wrap is capped at 1180 and
centered, so there was room either side anyway and nothing showed. On a phone
the wrap is the full width and the gutter IS the padding, so the headline
started at x=0 and ran off the right edge. `padding-block` instead of the
shorthand. Measured after: 19.5px both sides, same as every other wrap.

## 7. The two pictures that were one picture

Both were a person shot from behind, in silhouette, facing a screen full of
faces. The subjects were different; the compositions were not. Same operator,
re-framed from the side at close range and cropped portrait, so the pair no
longer shares a shape at any width.

## 9. The mobile header pictures

The per-image framing list had gone stale. Rounds 8 and 9 replaced almost every
hero and **only two of the names in that list still existed**, so six pages were
falling through to the base `object-position: center 58%`, which anchors low and
takes the top of somebody's head off the moment the panel becomes a wide short
slot. That is exactly what the panelist application hero was doing.

Every current hero is named now, with a desktop value and a narrow value set
from where each subject's head actually sits. Re-rendered all eight at 390:
every head is complete with headroom.

## "A bit heavy on desktop"

Measured first, at 1440x900. The home page ran **12,303px, 13.7 screens**, with
about 2,000px of that in section padding.

The interesting number was not the total, it was the comparison. Below 1041px
the site already set `--bay: clamp(62px, 8vw, 104px)`. Above it, the same token
was `clamp(72px, 9vw, 132px)`. **A desktop was being given 27 percent more air
per section than a tablet**, on a viewport that is wider and therefore already
reads as roomier. That was never a decision, only two clamps written months
apart, and it is the asymmetry behind the note.

The whole ladder scales down and section 41's deliberate three step rhythm is
kept intact:

| | before (1440) | after | ratio to --bay |
|---|---|---|---|
| `.bay--open` | 190 | 152 | 1.51 to 1.51 |
| `.bay` | 130 | 104 | 1.00 to 1.00 |
| `.bay--tight` | 72 | 58 | .56 to .56 |
| `.essay` | 168 | 132 | 1.29 to 1.27 |

| page | before | after | saved |
|---|---|---|---|
| index | 12,303 | 11,901 | 402px |
| experience | 9,108 | 8,801 | 307px |
| panelists | 6,168 | 5,861 | 307px |
| about | 5,213 | 4,935 | 278px |

**That is a 3 percent trim and it will not on its own change how the page
feels.** Nothing was restructured, no section removed and no type moved, because
the home page is the one Annette has said she likes and "a bit heavy" is not a
brief to rebuild it. If the note is about something more specific, the two
candidates the measurements point at are the length itself (the home page is
still 13 screens, and this round added a section to it) and the fact that 47
percent of its height is near black. Both are structural and both need saying
out loud before anyone touches them.

## Verified

`python _build/audit.py` over 11 pages at 390, 768, 1024, 1366 and 1440:
**55 probes, 0 findings**. All 11 pages at 1440, 820 and 390 with no JavaScript
errors and no failed requests.

## Still not done

Unchanged, and every one of them is a launch blocker:

- Every form still has `CONFIG.endpoint = null`.
- No payment path for the $2,997 or the $47.
- The assessment captures no lead.
- **The domain is not connected.**
- The signature block on both agreements is a front-end demo.
- No testimonials, no Spotlight Call calendar embed, no legal review.


# Feedback 6.0, 13 September 2026

Five notes in a Google Doc, each with a screenshot from a second laptop: the
site looks "very contained" there and on every page, the panelist button "is
not looking nice", the "What the room looks like" text should sit further
left, and the film section is "lamely done", with no copy that sells, on "the
section which helps in converting majority of the people".

## The site stopped responding above 1440

The screenshots are 1920px wide and the browser chrome in them is a 125
percent Windows display, so the viewport that produced them is 1536 CSS
pixels. Measured there, and at 1920, before anything was touched:

| | 1440 (approved) | 1536 (that laptop) | 1920 |
|---|---|---|---|
| content width | 1180 | 1180 | 1180 |
| dark margin either side | 130 | 178 | 370 |
| hero headline column | 533px, 4 lines | 482px, 5 lines | 278px, 7 lines |

The headline column got **narrower as the screen got wider.** The copy block
was a fixed 48rem box whose left padding grows with the viewport to stay on the
wrap's edge, so the text inside it was being squeezed from the left while the
box could not grow on the right. Every page shares that component, which is
why "the same issue is with all the pages" is exactly right. Separately, the
content width was capped at 1180 and every display size is a clamp that stops
growing at about 1240px, so past that point a wider screen only added margin.

Three changes, all gated at 1441px so the approved 1440 layout is untouched:

1. **The content width grows with the screen**, 86 percent of the viewport up
   to 1640px. It is one token now (`--wrap`), and the five places that had
   1180 written into an expression all read it.
2. **The root type size eases from 100 percent at 1440 to 112.5 percent at
   1920.** Every rem measure on the site scales with it, so leads, columns,
   buttons and the sheets grow together and the page reads as the same design
   larger, not the same design with wider margins. It is a percentage, so a
   reader's own browser font setting still counts.
3. **The display sizes keep climbing** instead of stopping at their cap, and
   the hero copy column is the grid track it always should have been, with the
   measure set on the headline itself.

After:

| | 1440 | 1536 | 1920 |
|---|---|---|---|
| content width | 1180 | 1321 | 1640 |
| margin either side | 130 | 108 | 140 |
| hero headline | 573px, 3 lines at 67px | 647px, 3 lines at 70px | 780px, 3 lines at 82px |
| body / lead | 19 / 23 | 19.5 / 23.6 | 21.4 / 25.9 |

## Fifteen font sizes the browser had been throwing away

Every band headline, the About page's belief statement, the two prices on the
panelist page, the "Your application is in" and "Thank you for applying"
headings, the assessment head and the agreement execution headings carried an
inline `font-size: clamp(2rem,1.4rem+2.4vw,3.3rem)`. That is invalid CSS: the
`+` inside a clamp needs a space either side, or the whole declaration is
dropped. So those elements had been rendering at whatever their class gave
them. "What the room actually looks like" was written for 53px and had been
showing at 72. The About page's belief statement was written for 38px and had
been showing as 19px body text. The $997 was the same size as the $1,497 it is
meant to sit under.

All fifteen are valid now (and the two templates in `agreements_build.py`), so
each renders at the size it was written for and scales with the screen. This
is also most of the answer to "the text should be more on the left": at its
intended size the band headline is 575px wide instead of 782, sits on the
wider wrap's left edge, and clears the beam.

## The panelist button

The page close was a two column grid, statement and detail on the left, one
button on the right, aligned to the bottom. On a wide screen that put the
button alone at the far right with a hundred pixels of nothing above it,
anchored to no sentence. It is statement left, detail and action right, top
aligned, so the button sits under the sentence that explains it. Same fix on
the Experience and FAQ closes, which are the same component.

## The film section

It was presented as a labelled object: a neutral heading, a running time, a
note about captions. Nothing asked anyone to press play and nothing after it
asked anyone to do anything. Rebuilt as the section that sells:

- **Head:** "Two minutes, start to finish" / "Watch a stage get built around
  one expert." / "From the first conversation to the night the light comes up:
  the Authority Blueprint, the panel we cast, the launch kit your audience
  receives, the production itself, and what you are still holding ninety days
  later. Shown, not described." Every phase named is a title card in her film.
- **The control** says "Watch the film", with "Two minutes, captions on" under
  it (the caption note is gone; that is where the information belongs).
- **A run order** under the picture: the film's own six chapters, timed from
  its audio track sentence by sentence (0:00 Why good work stays unknown, 0:46
  The Authority Blueprint, 0:57 Casting the panel, 1:08 The launch kit, 1:24
  Showtime, 1:41 What you keep). Each one is a button that starts the film at
  that point, and the chapter that is playing carries the red marker, so a
  reader who will not sit through two minutes can go straight to the night, or
  to what they keep. Verified in Chrome: each cue seeks and plays, the marker
  follows.
- **A close** after the film, because the moment it ends is the warmest a
  reader gets on this page: "If that is the stage you want, the application
  takes about eight minutes." with the Apply button and the assessment as the
  second route, which is the call the film itself ends on.

Still no autoplay and still `preload="none"`.

## Verified

`python _build/audit.py`, now over seven widths with 1536x825 and 1920x1080
added: **77 probes, 0 findings.** All 11 pages at 390, 1440 and 1920 with no
JavaScript errors and no failed requests.

## Still not done

Unchanged, and every one of them is a launch blocker:

- Every form still has `CONFIG.endpoint = null`.
- No payment path for the $2,997 or the $47.
- The assessment captures no lead.
- **The domain is not connected.**
- The signature block on both agreements is a front-end demo.
- No testimonials, no Spotlight Call calendar embed, no legal review.
