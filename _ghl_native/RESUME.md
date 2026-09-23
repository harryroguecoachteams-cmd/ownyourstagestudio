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

## Left to do (24 Sep, round 2; code is committed, GHL side pending)
Code: agreements now post to the webhook (tag host-agreement / panelist-agreement, first/last
name split from legal_name, business = business_name); "Demonstration build" notice replaced by
the payment step; Annette's keynote lines + 2 stage photos added. Tracking code WITH the signing
fix is already LIVE (191,253 chars saved). Email bodies: workflow/confirm_*.html, subjects in
workflow/subjects.json.
1. Media Storage folder "Website - Own Your Stage Studio": upload assets/media/annette-stage-blue.jpg
   and annette-stage-warm.jpg, add ids to _ghl_media.json, run build.py + build_ghl.py.
2. Re-paste page code (one Custom Code element each): Host Agreement (page-builder
   igBKL674r7nm7ZrQAg0R), Panelist Agreement, Home, About, Virtual Panel Events; publish each.
   DO NOT paste via clipboard while another process uses it; verify length before Save.
3. Website workflow (5e574732): replace internal notification body (agreement section added);
   If/Else add branch "Agreement" (Last Website Form is any of host-agreement,panelist-agreement)
   -> Update Last name/Phone/Business Name -> If/Else host vs panelist -> Send email
   confirm_host_agreement / confirm_panelist_agreement. Application branch: after "Save the
   application details" add If/Else host-application / panelist-application -> Send email
   confirm_host_application / confirm_panelist_application.
4. New workflow "Website - Let's talk form": Form Submitted (dvJo5tJIIPvpcprpSPcc) -> tag
   website, lets-talk -> internal notification to events@ -> Send email confirm_lets_talk.
5. New workflow "Stop Hiding Strategy Call booked": Customer Booked Appointment (calendar
   cNJmGXJ4ed9YpmzNEElE) -> tag strategy-call-booked -> internal notification to events@.
   Contact emails are NOT needed: the calendar's own notifications (auto-confirm on) already
   send confirmation, 24h/1h/10m reminders, reschedule and cancel to the contact and Annette.
6. New workflow "Own Your Stage Experience - payment received": Payment Received (products
   6a8f2ab7ddec25df2d4e9da4 $2,997 and 6a9193ac469e8f2385c54aa4 plan) -> tag experience-client
   -> internal notification -> Send email confirm_payment. Leave re-entry OFF (plan pays twice).
7. Test each with TEST contacts, then DELETE all TEST contacts (Harsh asked): jAWTzBp2xKc5E8V7688a,
   fYbUFE6NAvXVlZoO1Hf6 + new ones.
8. Root domain -> /home (admin, waiting on Annette).
Open questions for Annette: no $47 panelist fee product/payment link exists; payment plan
product says $3,110 vs site $1,550 x 2 = $3,100; keynote says "Expanding", quiz says "Established".

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
