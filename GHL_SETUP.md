# Putting this site inside GoHighLevel

## First, the honest answer

**You cannot have this built into GHL programmatically.** GHL's public API v2 is
**read-only for funnels and pages** — there is no create-page or create-funnel
endpoint. The builder's own internal API is also out of reach: it runs in a
cross-origin iframe, it hangs if opened standalone because it waits on an auth
handshake from the parent frame, and its auth token lives in Firebase IndexedDB
rather than `localStorage`.

So it is a paste job. The work below reduces that to **one paste per page**,
because the blocks in `_ghl/` have already been rewritten for a funnel: internal
links point at funnel slugs, asset paths are absolute, and each block is a
complete page including the masthead and footer.

---

## Before you start

Decide one thing: **where do the two asset files live.**

`_ghl/` blocks currently point at the GitHub Pages copy:

```
https://harryroguecoachteams-cmd.github.io/ownyourstagestudio/assets/oyss.css
https://harryroguecoachteams-cmd.github.io/ownyourstagestudio/assets/oyss.js
```

That works today and needs no setup. For a client site you will probably want
them on Annette's own hosting — upload both to the GHL Media Library, take the
CDN URLs, and change `ASSET_HOST` at the top of `build.py`, then re-run
`python build.py`. Do not hand-edit the blocks.

The three images (`virtual-stage.png`, `stage-panelist.png`, `stage-host.png`)
follow the same `ASSET_HOST`.

---

## Build the funnel

### 1. Create the steps

**Sites → Funnels → New Funnel** (or **Websites → New Website** if you want a
site rather than a funnel). Create one step per page, with these **exact** path
names, because the links in the blocks already point at them:

| Step name | Path |
|---|---|
| Home | `/` |
| The Experience | `/experience` |
| Assessment | `/assessment` |
| Panelists | `/panelists` |
| About | `/about` |
| FAQ | `/faq` |
| Apply | `/apply` |
| Spotlight Call | `/spotlight-call` |
| Panelist Application | `/panelist-application` |
| Host Agreement | `/host-agreement` |
| Panelist Agreement | `/panelist-agreement` |

If you want different paths, change the `SLUGS` map in `build.py` and re-run it.
Do not rename them only in GHL — the links inside the blocks will break.

### 2. For each step

1. Open the step in the page builder.
2. Delete whatever GHL put there by default.
3. Add one **Section → Row → Column**.
4. Select the **Section** and set:
   - **Width: Full Width**
   - **Padding: 0** on all four sides
   - Background: leave transparent, the block paints its own
5. Select the **Row** and set padding to **0** as well. GHL puts padding on both.
6. Drag in a **Custom JS/HTML** element (Elements → "Custom JS/HTML", sometimes
   listed as "Code").
7. Open the corresponding file in `_ghl/`, copy **the entire file**, paste it in,
   save.

Repeat for all eleven steps. `_ghl/agreements__host.html` is the Host Agreement
step, `_ghl/agreements__panelist.html` is the Panelist Agreement step.

> **If you skip step 4 and 5**, the design still works — every block carries a
> `.oyss--bleed` class that breaks the full-width sections out of the builder's
> container on its own. Setting the section properly is still cleaner, and
> avoids GHL's padding showing as a white strip above the masthead.

### 3. Optional: load the assets once instead of per page

Every block includes its own `<link>` and `<script>`. That is harmless — the
browser caches both after the first page. If you would rather load them once:

- **Funnel Settings → Tracking Code → Header**: paste the `<link>` line
- **Funnel Settings → Tracking Code → Footer**: paste the `<script>` line
- Then delete those two lines from each of the eleven blocks

---

## Wiring the forms to the CRM

Three forms and two agreements currently validate and confirm on the page but
send nothing anywhere. Each has one line to change.

### The recommended route: inbound webhook

1. **Automation → Workflows → Create Workflow**
2. Trigger: **Inbound Webhook**. Copy the webhook URL it gives you.
3. Add action **Create/Update Contact**, mapping the payload fields.
4. Add action **Add Tag**, using the tag the form already sends.
5. In the block, find `CONFIG.endpoint` near the bottom and replace `null` with
   the webhook URL in quotes.

Field names are already keyed to match CRM fields, and each submission carries a
tag so a workflow can filter on it:

| Page | Tag it sends |
|---|---|
| `/apply` | `host-application` |
| `/spotlight-call` | `spotlight-call-request` |
| `/panelist-application` | `panelist-application` |

For the agreement pages the call is `OYSS.signing({ agreement: "..." })` —
add an `endpoint` key to that object:

```js
OYSS.signing({ agreement: "Featured Panelist Agreement",
               endpoint: "https://services.leadconnectorhq.com/hooks/..." });
```

The Spotlight Call form also forwards the visitor's assessment result if they
took it earlier in the session, so the contact record arrives with their level
already attached.

### What not to do

Do **not** POST straight to the LeadConnector contacts API with a Private
Integration Token. It works, but the token is readable by anyone who views
source. The webhook route has no such exposure.

### Or use native GHL forms

If Annette would rather manage fields herself in the GHL form builder, replace
the `<form>` in a block with a GHL Form element. You lose the styling and the
inline validation copy, and the Assessment cannot be rebuilt this way because it
is scored in JavaScript. For `/apply` and `/spotlight-call` it is a reasonable
trade.

---

## Signing and payment

**Use GHL's Documents & Contracts for the legally binding signature.** It is
under **Payments → Documents & Contracts**, and it gives you a real audit trail,
IP and timestamp logging, and a countersigned PDF. The signature block on the
agreement pages is a demonstration: it validates, renders the signature, stamps
an uneditable date and records the acknowledgments, but it is not an e-signature
platform and should not be treated as one.

The good structure is:

1. The public agreement page is where someone **reads** the contract. It builds
   trust precisely because it is readable before anyone asks for money.
2. Its signature block hands off to the real GHL document for signing.
3. Payment follows, or is collected on the document itself.

To wire that up, replace the form's submit handler target with the send-document
link, or simply change the button to link to the GHL document URL.

**Payments:** create two products under **Payments → Products** — $2,997 for the
Own Your Stage Experience and $47 for the Panelist Commitment fee — then either
add an Order Form step to the funnel or generate Payment Links and point the
post-signature step at them.

Note what both contracts actually say: a position is confirmed only after the
agreement is signed **and** the fee is paid. Signing and paying being two steps
is correct, not a gap.

---

## Things that will bite you

- **GHL's own styles do not leak in.** Every selector is scoped under `.oyss`
  and there is no global reset, which was tested against a simulated GHL page
  applying its own `h1`, `p`, `ul`, `a` and form styles. Nothing overrode.
- **The masthead is `position: sticky`.** If you ever wrap the block in a
  container with `overflow: hidden` or `overflow: clip`, sticky silently stops
  working. Do not add overflow rules to the section.
- **Do not paste a block into more than one element per step.** Each block
  contains its own masthead and footer.
- **Do not hand-edit files in `_ghl/`.** They are generated. Edit `_pages/` and
  re-run `python build.py`, or your change is lost on the next build.
- **The builder's code editor gets sluggish with large blocks.** The Host
  Agreement is the biggest at ~64KB because it is a 41-section contract. Paste
  it, save, and do not try to edit it in place inside GHL.
- **Test on mobile inside GHL specifically.** The design is responsive on its
  own, but GHL adds its own responsive controls that can fight it. If a section
  looks letterboxed on mobile, it is the GHL row padding, not the block.

---

## Regenerating after any change

```
cd oyss-site
python agreements_build.py     # only if a .docx contract changed
python build.py                # rewrites the 11 pages and the 11 GHL blocks
```

Then re-paste whichever blocks changed.
