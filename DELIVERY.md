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
this from real pixels instead of walking DOM colours, and that turned up the same
failure on four interior pages against the light in their plates: "FAQ" at 3.8:1
and the Apply button at 3.6:1 on `apply.html`, where a colour walk had reported
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
site. They are now the centre of the page: the host frame carrying Annette's own
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
the manifest on the home page and again, itemised, on the Experience page.

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
against the colour actually behind it, the masthead against **real pixels** where
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

The six frame rig is the centrepiece and it now holds seven commissioned
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
mock on page 24 solves it by **flipping the colourway**, an ivory disc carrying
a navy beam, not by deleting the shape. Both approved colourways are now in the
stylesheet; the geometry is measured off the page 19 lockup and normalised to a
64 unit circle. The beam carries the falloff, the pool never does: "The pool is
never a gradient. One flat gold is what makes the mark portable." (p16)

**2. The eyebrow was the wrong colour (p11).** The type hierarchy sets the
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
