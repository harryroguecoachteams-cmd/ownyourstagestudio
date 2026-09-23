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

## Left to do
1. Fix/finish user test (_build/user_test.py, results in _build/usertest/): 27 PASS, 6 FAIL,
   likely test-script issues, not verified yet: assessment radios "outside viewport" (styled
   inputs: click the label instead), host application submit button not found (check its
   markup / multi-step), home Let's talk GHL iframe (timeout / crash). All 15 pages x 2 viewports
   PASS, mobile menu PASS, panelist app PASS, both agreements PASS (pay buttons, no demo text),
   calendar widget PASS.
2. DELETE all TEST contacts (Harsh asked): emails oyss-test*@example.com (search contacts).
3. Root domain -> /home (admin; Harsh waiting on Annette).
4. Security Deposit product would also trigger the Experience welcome email (filter can only
   exclude one product); not sold on the site.

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
