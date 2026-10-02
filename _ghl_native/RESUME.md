# OYSS on GHL - where the build stopped (23 Sep 2026, evening)

The website lives in GoHighLevel now (sub-account O1kebSJ9ZQAQPoaSv8lb, website
"Own Your Stage Studio" VxpsSqlLRJqrRH4qAFE0, domain ownyourstagestudio.com).
GitHub Pages is only a demo copy.

## Build chain

    python build.py        # site + _ghl/ blocks
    python build_ghl.py    # _ghl_native/ (GHL media ids, endpoint, loader)

- `_ghl_native/site_tracking_body.html` -> GHL website Settings > Tracking & scripts >
  **Body tracking code** (select all, paste, Save). Must stay in sync with every page.
- `_ghl_native/pages/<page>.html` -> the ONE Custom Code element on that GHL page.
- `_ghl_media.json` = filename -> GHL media id. New image: upload to Media Storage folder
  "Website - Own Your Stage Studio", add the id here, rebuild.
- `_ghl_endpoint.txt` = the workflow's Inbound Webhook URL (written into the tracking code).

## Done
- 15 pages built, SEO set, published, audited (`python _build/ghl_live_audit.py`).
- Website settings: favicon, **Optimize JavaScript OFF** (it lazy-loads custom code).

## Done 24 Sep 2026 (session 2)
- Body tracking code re-pasted: 190,980 chars saved = file minus CRLF; live pages carry the endpoint.
- Workflow "Website - all forms and the assessment" PUBLISHED. Steps:
  Inbound Webhook -> Create contact -> Tag `website, {{tag}}` -> Internal notification email to
  events@ownyourstagestudio.com (default sender) -> Update field **Last Website Form** (contact
  custom field MiwF8qRHokjYW8c4FPBv, `contact.last_website_form`) = `{{inboundWebhookRequest.tag}}`
  -> If/Else "Assessment or application?": Last Website Form is `assessment-result`
  - Assessment: 5 assessment fields -> Send email "Your Authority Visibility Score: N%"
    (body `workflow/assessment_result_email.html`; result_html arrives as real HTML, verified)
  - Application (none branch): Last name, Phone, Business Name, Website
    (`{{url}}{{website}}`: host form sends url, panelist form sends website)
- Tested with two webhook posts (TEST / example.com contacts jAWTzBp2xKc5E8V7688a and
  fYbUFE6NAvXVlZoO1Hf6, still in her CRM, tagged website): every step Executed, fields correct.

## Round 2 DONE (24 Sep 2026, ~5 AM IST)
LIVE on GHL: tracking code 191,693 chars (signing fix + photo/shift CSS); pages re-pasted and
published: Host Agreement, Panelist Agreement, Home, About, Virtual Panel Events (page ids in
page_ids.json). Photos in Media Storage (annette-stage-blue 6ab429b4c745ba551e3b693c,
annette-stage-warm 6ab429b418384d888bba9903). Products: new "Panelist Commitment &
Administrative Fee" 6ab429d8c31bafd11b6f1656 ($47 price 6ab429e35a60d0b801c0bdde), payment link
6ab42a504ae1d45672839331; plan description fixed to $3,100.
Workflows (all PUBLISHED):
- Website - all forms (5e574732): branches Assessment / Host agreement / Panelist agreement /
  Application(none -> save details -> If/Else host-application / panelist-application); every
  branch emails the person (workflow/confirm_*.html); Annette notification has agreement section.
- Website - Let's talk form (home page) 9b1d9b96: Form submitted (dvJo5tJIIPvpcprpSPcc) -> tag
  website+lets-talk -> notify events@ -> email confirm_lets_talk.
- Stop Hiding Strategy Call - booked a834a089: Customer booked appointment -> tag
  strategy-call-booked -> notify events@ (calendar's own emails handle the contact).
- Own Your Stage Experience - payment received 3e05c1b4: Payment received, product is NOT the
  panelist fee -> notify events@ -> welcome email (confirm_payment).
- Panelist fee - payment received d378ade6: product IS panelist fee -> notify -> confirm_panelist_fee.
Webhook tests 24 Sep: all 10 emails sent and rendered (5 to person, 5 to events@).
"Save the application details" errored only because the TEST phone was a duplicate.

## Round 3 DONE (24 Sep 2026, ~5:40 AM IST)
- User test finished (_build/user_test.py + _build/user_test_retry.py): every flow passes on
  desktop and mobile. The earlier fails were test-script issues: assessment auto-advances
  (click label.choice, wait 1.2s); host application is a 4-step form (.quiz__next); the GHL
  "Let's talk" form has Cloudflare Turnstile, so headless Playwright can never submit it.
  Verified by hand in real Chrome instead: contact created, first_name kept, tags applied.
- Real bug fixed: the "Host Services Agreement" link inside the host-application checkbox and
  the form's Privacy/Terms links opened in the SAME tab, wiping the half-filled application.
  Now target=_blank (apply.html + LEGAL_HTML in build.py, forms only; footer untouched).
  Apply + Panelist Application pages re-pasted and PUBLISHED.
- All 20 TEST contacts (oyss-test*@example.com) DELETED from the CRM.

## 25 Sep 2026 (evening)
- Home links: 30 `href="/"` links (logo + footer) led to the OLD root page. The loader in build_ghl.py now rewrites a[href="/"] to /home at mount (8b30fa8).
  - Tracking code: 193,512 chars LF, handed to Harsh on the clipboard to paste.
  - Remove the rewrite once the root domain serves /home.
- Booking workflow a834a089 TESTED via an API appointment (the widget has Turnstile). Results:
  - tag strategy-call-booked applied
  - the "New Stop Hiding Strategy Call booked" email reached events@
  - the calendar confirmation reached the booker
  - the test event and contact were deleted afterwards
- Payments: Stripe is LIVE (pk_live), 0 transactions ever. Both payment workflows are still untested; that needs a real card payment + refund.

- ROOT DOMAIN FIXED 25 Sep: GHL URL redirect `/` -> https://ownyourstagestudio.com/home (301), created through the LeadConnector API `create-redirect` (id mRzUYGgWIxUaGBw3yOzk). The Domains screen was not needed.
  - Verified: apex, www and http all land on /home; the other pages are unaffected.
  - To undo: `delete-redirect-by-id`.
- Old-site redirects (25 Sep, all 301, verified). These old pages were already 404; the redirects catch old links.

  | Old path | New page | Redirect id |
  |---|---|---|
  | /home-8271 | /home | Yad7MQSqS57v5n1lSB62 |
  | /welcome-791727 | /home | gC8wGa9NDePO3EkAslSs |
  | /about | /about-us | NWzDNBxnsc9OoZ7crssE |
  | /courses | /services | FU7ZsIsG1SrE8Gff9ds8 |
  | /trainings | /services | YPVbzjkirP5nNBbS3vRY |
  | /coaching | /services | Fw3uzDOFBKW4u095CWpT |
  | /terms-conditions | /terms | Z0H0nNLX0CB5CSxQvccq |
  | /privacy-policy | /privacy | EcmBqtTDNrM0K1P0Cq7p |
  - The loader home-link rewrite (8b30fa8) is now optional; it saves one redirect hop.

## Left to do
1. (done 25 Sep) Root domain -> /home, via the redirect above.
2. Security Deposit product would also trigger the Experience welcome email (filter can only
   exclude one product); not sold on the site.
3. Known GHL behaviour: "Save the application details" fails when the phone already belongs
   to another contact (same person, new email). Rare; the email still goes out.

## Workflow builder traps (24 Sep)
- If/Else cannot read `inboundWebhookRequest.*`; copy the value into a contact field first.
- Only ONE Inbound Webhook trigger per workflow (second is greyed out).
- Number / phone fields reject a pasted `{{...}}`: use the tag icon picker > Inbound Webhook Trigger.
- Internal notification: a From Name without a From Email fails validation; leave both empty.

## Builder traps (cost real time)
- Chrome must be visible. If `document.visibilityState` is "hidden" the builder never
  loads and screenshots time out. Restore without stealing focus:
  user32 ShowWindow(h, 4) + SetWindowPos(h, HWND_TOPMOST, ..., 0x13); undo with HWND_NOTOPMOST.
- Code element: **drag** "Code" from Quick Add onto the canvas; clicking does nothing.
- Paste large code: PowerShell `Set-Clipboard` then ctrl+a / ctrl+v in the code editor.
- Never type unless the field is focused (zoom to check): stray keys fire builder shortcuts.
- Workflow field dropdowns render in a ~40px strip: scroll inside it to reach the result.

## Feedback 10 (25 Sep 2026) - built + pushed (ab8c25b), LIVE on GHL (all done)
Doc tab "feedback 10" (t.a8e0n1k9sygc). Home page re-ordered to one ask; see commit message.
New photo already in GHL Media Storage (root folder): annette-stage-blue-sharp.jpg
6ab64b53974a9da6eeb9c872, mapped in _ghl_media.json. Two pastes left, nothing else:
1. DONE 25 Sep: Body tracking code saved (193,259 chars LF, verified after reload).
2. DONE 25 Sep: Home page (builder id 1IZ74onJJMQakHYBuTJF) Custom Code element = `_ghl_native/pages/index.html`, published.
   Harsh pasted it from the clipboard (LF, 36,748 chars). Verified live: 91/91 text snippets match, and the old "See all services" and "Let's talk" are gone.
   Also verified: no overflow at 1440/390, and the sharp story photo loads (1280 wide).
   NOTE: a HeadlessChrome UA renders the GHL page blank. Use a normal Chrome UA in Playwright.
Other pages' GHL code is unchanged. Blocked on 25 Sep: Chrome's active tab was Harsh's Sheets tab,
so the GHL tab stayed hidden, and forcing the window/tab switch was refused by the permission classifier.

## Go-live, feedback 11-16 (28 Sep 2026, ~3:15-3:30 PM IST). ALL LIVE.
Order was deliberate: the workflow first, so the exit pop-up could never post before its branch existed.
1. Workflow 5e574732 "Website - all forms and the assessment" (saved, still published):
   - New If/Else branch "Exit intent" (Last Website Form is exit-intent) -> "Email the assessment link"
     (workflow/confirm_exit_intent.html, subject "Your Readiness Assessment link"; greeting "Hello," because
     first name is optional in the pop-up). Without it an exit lead would run "Save the application details".
   - Both agreement confirmations: signed_copy_url button "View and download your signed agreement".
   - Annette's notification: signed-copy link + EXIT INTENT section.
   - Note: If/Else now offers "Inbound webhook trigger" fields too; branches still use Last Website Form.
2. Body tracking code: 223,410 chars (557d504), verified after reload. The FIRST scripted Save did not persist;
   a real click on the Save button (find -> ref) did. Always verify after reload.
3. Pages pasted (LF, line counts checked in the editor) and published: Home, About, Panelist Application,
   Host Agreement, Panelist Agreement. No other page block changed since its last paste.
4. Live test _build/live_test_0928.py: 37/37 PASS (15 pages x 2 widths: mounted, no errors, no overflow, bar +
   exit only on the 6 reading pages; exit lead; both agreements signed with a drawn signature + PDF; both
   stepped applications; assessment). 6 webhooks 200; 6 contacts with the right tags/fields (exit lead got no
   phone/business writes); 12 emails "sent" (6 to events@, 6 to the leads, all 6 read back in the RCT inbox);
   the tracked "View and download" link 302s to /panelist-agreement#signed=... (fragment kept) and the signed
   copy + PDF render on the live site. All 6 TEST contacts deleted afterwards.

## Signed agreements + receipts relay (28 Sep 2026, evening). Built + deployed, WAITING FOR THE GHL TOKEN.
Harsh: "add a automation to send the signed agreement and payment recipt to the person email when they done with it".
Code in `_relay/` (deploy: `python _relay/deploy.py`; status only: `--check`).
- Public endpoint `https://roguecoachteams.com/relay/oyss-docs.php`. Private code + state in `/home/rogucmxm/oyss_private`, outside the web root.
- Signing: the agreement page posts the PDF it just saved (`fileCopy` in oyss.js; `window.OYSS_DOCS` is set in the GHL tracking code only, never on the demo).
  - The relay checks it: origin, the PDF's running foot names the agreement, the signing record holds the same email, and rate limits.
  - Then, in Annette's GHL, via her token:
    - upsert the contact
    - upload the PDF to Media Storage > Signed agreements (6aba4580b5e520ac173482ac)
    - set the contact field Signed Panelist Agreement (PDF) 3Q7VzuoEGmOPlUMRbeE9 or Signed Host Agreement (PDF) MtwZ8bIBvgKwg5lpjExo
    - email the signer from events@ (Conversations API) with the PDF attached, Bcc events@
    - add a note and the tag signed-agreement-sent
  - If they paid first, the receipt goes along.
- Receipts: cron `*/5 * * * * /usr/local/bin/php -q /home/rogucmxm/oyss_private/receipts.php` (cPanel linekey 3341189030).
  - Every succeeded live payment after RECEIPTS_FROM gets a receipt PDF (`receipt_pdf`, own tiny PDF writer).
  - The PDF goes to Media Storage > Payment receipts (6aba45817ef452865a1cf081) and to the field Payment Receipt (PDF) JM7IfUflED93E5R08NVH, with a note and the tag receipt-sent.
  - It is emailed from events@ with Bcc events@. The first receipt for a line also attaches that line's signed agreement.
- The workflow's own emails are unchanged. The relay's emails are the document deliveries: "Your signed ... (PDF)" and "Your receipt ...".
- **BLOCKER:** Annette's GHL Private Integration token.
  - Where: sub-account Settings > Private Integrations > Create new integration, named "Website documents".
  - Scopes: contacts.readonly, contacts.write, medias.readonly, medias.write, conversations.readonly, conversations.write, conversations/message.readonly, conversations/message.write, payments/transactions.readonly.
  - Save the token as one line in `E:/_shared/secrets/oyss_ghl_pit.txt`, then run `python _relay/deploy.py`. Until then the relay answers 503 not_configured and the cron exits.
- Tests: `scratchpad/relay_local_test.py [url]` 14/14 local + live (dry). `scratchpad/sim_signed.py` 11/11: signed-copy view, the relay payload is the same bytes as the download.
- After the token: one live signing per agreement with events+oyss-test@ownyourstagestudio.com, the $47 test payment, then delete the TEST contacts.

## 29 Sep 2026 (00:00-01:00 IST): tracking code LIVE, read-only live check
- Body tracking code saved twice, both verified after a reload by SHA-256:
  - a995101: 227,038 chars LF. Mobile fixes, the signed-copy header, and the relay hook `window.OYSS_DOCS`.
  - then **ee64e46: 227,165 chars LF**. pdfName now uses the signer's local day. It used the UTC day, so a Florida signing after 8 PM got the next day's date in the filename.
  - The GHL page blocks (`_ghl_native/pages/`) did not change, so no page pastes were needed.
- **Hidden-tab save method (works; Harsh's tab stays in front):**
  1. Open website Settings: `app.gohighlevel.com/v2/location/O1kebSJ9ZQAQPoaSv8lb/funnels-websites/websites/VxpsSqlLRJqrRH4qAFE0/settings`.
  2. Poll until the Name input AND the Body textarea are filled (~10-20 s). Never write earlier.
  3. `fetch` raw.githubusercontent at the commit SHA, CRLF->LF, and compare the SHA-256 with `git show <sha>:_ghl_native/site_tracking_body.html`.
  4. Set the value with the native setter + focus + `InputEvent('input', {inputType: 'insertFromPaste'})` + change + blur.
  5. Hook `XMLHttpRequest.send` and click Save **from script** (pointer/mouse events + `.click()`).
  6. Expect POST `backend.leadconnectorhq.com/funnels/funnel/update-settings` -> 201, with the body containing your marker.
  7. Reload and re-hash.
  - In a hidden tab the extension's ref click on Save sends NOTHING (no request, no error).
- `python _build/live_check_readonly.py [pages] [exit] [sign]`: live check that creates NO contacts and sends NO email.
  - It intercepts the webhook + relay, then posts the captured relay payload to the live relay in dry mode (test key).
  - 29 Sep result: pages 45/45 (1366/390/360), exit pop-up 3/3 (mouse leave + phone flick), signing + signed copy + relay dry 20/20.
  - Output goes to `_build/livecheck/` (gitignored).
- Relay (`deploy.py --check`): endpoint up, `configured: false`.
- **Still blocked:**
  1. RCT's GHL user is not an admin. Harsh, 29 Sep: "we need to get access to the full settings from annettes first".
     - The Private Integrations page opens, but do not try to create one until Annette grants full access.
     - Then: token -> `E:/_shared/secrets/oyss_ghl_pit.txt` -> `python _relay/deploy.py`.
  2. Then the $47 payment test. It needs a real card, so Harsh or Annette pays and refunds in GHL; I verify the workflows + receipt.

## 2 Oct 2026: access check
- RCT's GHL user is now agency admin on this sub-account (changed 1 Oct). Settings shows Users + Billing; Private Integrations offers "Create new integration" (none exist yet).
- Creating the integration was refused by Claude Code's permission classifier (credential creation), so **Harsh creates it himself**: Settings > Private Integrations > Create new integration, name "Website documents", the scopes listed in the relay section above, copy the token once, save it as one line in `E:/_shared/secrets/oyss_ghl_pit.txt`. Then `python _relay/deploy.py` and the live tests.
- Relay `--check`: up, `configured: false`. No payments since 27 Sep and no new contacts since 28 Sep, so nothing to back-fill.
- `_build/live_check_readonly.py`: 68/68 (pages 45, exit pop-up 3, both agreements incl. live relay dry 200).
- **Later 2 Oct: RELAY LIVE.** Harsh created the Private Integration and sent the token. It is saved to `oyss_ghl_pit.txt`, and the read checks (location, media, payments, conversations, contacts) all return 200 on Own Your Stage Studio. `deploy.py` -> `configured: true`.
  - `python _build/live_sign_real.py`: a REAL signing of both agreements with events+oyss-test@ownyourstagestudio.com. Both webhooks 200, and the relay log shows `agreement.sent` for panelist and host.
  - Checked in GHL: tags panelist-agreement, host-agreement, signed-agreement-sent; both contact fields point at Media files that are byte-identical to the downloaded PDFs; both files in Signed agreements; notes added.
  - Emails: "Your signed ... (PDF)" from events@mail.ownyourstagestudio.com with the PDF attached and Bcc events@, plus the workflow's "Your ... Agreement is signed". All four delivered.
  - Receipt cron runs with the token (state `last` updates; `?do=receipts` dry: 0 payments since RECEIPTS_FROM 28 Sep).
  - Cleaned up: TEST contact and both test PDFs deleted.
  - The page's fetch to the relay is not reported to Playwright's response event, so `live_sign_real.py` proves the relay from its log (test key) instead.
- **Left:** the $47 card test (Harsh or Annette pays and refunds; then check the receipt email, `amount` units, card fields, workflows d378ade6 / 3e05c1b4).
- **2 Oct, Harsh: "drop the workflow email".** The workflow's signer email ("Your ... Agreement is signed") was the only place with the payment step ($47 link; host $2,997 / 2 x $1,550 links). Those links, plus the "next" line, moved into the relay's PDF email (`agreements()` pay_intro / pay / next in lib.php). If a receipt is already on the contact, it says "Your payment is received" instead of showing the buttons. Deployed; a live dry run shows the links.
  - DONE in the builder (version 13, 2 Oct 17:59 UTC, still published): deleted "Email the signed host their next step" and the panelist one. Both agreement branches now go straight to END. "Email Annette the submission" sits in the main path above the If/Else and is unchanged.
    - The builder is the cross-origin iframe client-app-automation-workflows.leadconnectorhq.com. It needs a VISIBLE tab, and Chrome reports a window covered by another app as hidden, so Harsh had to keep Chrome uncovered.
  - Re-test with `live_sign_real.py`: 6/6. The signer got ONE email per agreement ("Your signed ... (PDF)", pay links + "The last step"); Annette's "Website: <tag> from <name>" notification still went out. Test contact + PDFs deleted.
  - The payment workflows' emails (confirm_payment / confirm_panelist_fee) carry the welcome + next steps, not a receipt, so they stay next to the relay's receipt.
- Also deleted on Harsh's OK: the RCT test contacts "ainsley" (exit-intent, 28 Sep) and "rcrt coach" (assessment, 18 Sep).

## 2-3 Oct 2026: pre-handoff sweep (before Annette's own test round)
- `_build/final_sweep.py <widths> [--shots]`: 15 pages x 11 widths (320-1920). Checks:
  - overflow
  - contrast (audit.py probe) and the masthead over footage
  - broken images, clipped or wrapped buttons, tiny text, tap targets, missing alt text
  - template tokens, JS and console errors, failed requests, meta
  - Result: 0 overflow, 0 broken images, 0 JS errors at every width, and one h1 per page.
- `_build/final_flows.py` (read-only, posts intercepted):
  - desktop nav + dropdown, menu at 360/390/768/1024
  - assessment (result, PDF, email-me), both stepped applications (empty step is stopped, submitted through 8 steps)
  - calendar, FAQ, videos, every link, the 3 payment links
  - Result: 64/66. The 2 "fails" are the retired home Let's talk GHL form, which no page embeds since 25 Sep.
- Fixed:
  - Head tracking code (`_ghl_native/site_tracking_head.html`, 1,563 chars): og:image share card (`assets/media/share-card.jpg`, 1200x630, `_art/plates.py share-card`, in her GHL Media) + twitter card. GHL serves the meta tags in the HTML but DROPS `<link>` tags from the head code, so the PNG icons (32, 192, apple-touch 180) are added by a small script.
  - Body tracking code b6ec99e (227,220 chars; SHA-256 LF 0ffbdd7c...), exactly 4 CSS edits:
    - orbit "You are here" #EE8A85 (6.4:1)
    - signature-line cross .68 (5.3:1)
    - "Sign here" hint .52 (3.3:1)
    - `.btn` centred + `text-wrap: balance` (wrapped phone labels)
  - XML sitemap was EMPTY: generated in Settings > Domains > ownyourstagestudio.com > row menu > XML Sitemap (all 15 pages). Live sitemap.xml lists 15 URLs.
  - Redirects /contact and /book -> /strategy-session (ids KhVlSrjNDuALLOgJvtct, QC1xghUmjAEq9bwv46xH).
  - `_art/plates.py`: `.oyss .plate p` specificity fix (the site's `.oyss p` had turned the plate text dark). It needs `python _build/serve.py . 8899` running.
- Checked OK:
  - http/www/root redirects, SSL (Google Trust, to 18 Dec, auto)
  - payment links: $47 / $2,997 / $1,550 x 2 (`totalCycles: 2`)
  - services anchors, calendar slots
- Noted for Harsh: ownthestagestudio.com auto-renew is OFF (expires 22 Jul 2027). Domain card still says "Set Default Page", which the `/` redirect covers.
- Body code 0e0f907 (227,999 chars LF, SHA-256 24c85b20...): `build_ghl.py` now writes a tiny script at the top that preloads the current page's hero image.
  - LIVE on all 15 pages.
  - Result: the hero image now loads in ~30 ms, but mobile LCP did NOT move. The bottleneck is first paint (FCP 5.5-6.2 s under Lighthouse's slow-4G + 4x CPU): GHL's own JS plus our 228 KB inline bundle.
  - Lighthouse: mobile performance 31-37, desktop 69 (LCP 2.0 s); accessibility 94, best practices 79, SEO 100. Real unthrottled loads: 0.5-1.7 s.
  - A real mobile gain needs a structural pass (per-page CSS, deferred engine). Not done before Annette's test.
- Lighthouse a11y leftovers, all known and left on purpose:
  - contrast flags = scroll-reveal text caught mid-fade
  - footer column titles are h4 after h2 (all 15 page blocks; would need builder pastes)
  - logo link aria-label vs its "St[mark]ge" text
- GHL head tracking code: meta tags are served in the HTML; `<link>` tags are dropped; `<script>` runs only after load (injected client-side). Body tracking code IS served as markup.
