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

## Left to do
1. **Root domain** `ownyourstagestudio.com/` still serves her old `/home-8271`. The login we use
   has NO Settings > Domains (limited role). An admin must set the domain's default page to the
   new website's Home (/home).
2. Real browser test of each live form once (assessment email, host, panelist).
3. Optional: workflow for the home short form (GHL form dvJo5tJIIPvpcprpSPcc).
4. Optional: delete the two TEST contacts.

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
