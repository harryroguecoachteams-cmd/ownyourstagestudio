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

## Left to do, in order
1. **Re-paste the Body tracking code** from `_ghl_native/site_tracking_body.html`
   (the live copy predates the endpoint and the `[src$=]` framing fix; the About hero is
   cropped until this is done). Verify the saved length equals the file length.
2. **Finish the workflow** "Website - all forms and the assessment (ownyourstagestudio.com)",
   id 5e574732-ce29-4627-9636-b97e889b1018 (Automation > Workflows):
   - Existing: Inbound Webhook -> Create contact (first name, email) -> Tag (dynamic:
     `website, {{inboundWebhookRequest.tag}}`).
   - Step 4 may be lost (was unsaved): **Send internal notification**, Email, From name
     "Own Your Stage Studio website", To: Custom email events@ownyourstagestudio.com,
     Subject `Website: {{inboundWebhookRequest.tag}} from {{inboundWebhookRequest.first_name}} {{inboundWebhookRequest.last_name}}`,
     body = `workflow/notify_annette_email.html` pasted through the editor's **Source code (</>)**
     view (a rich paste auto-links .page/.email/.phone/.video as domains).
   - Step 5: **If/Else** on `{{inboundWebhookRequest.tag}}` equals `assessment-result`:
     - Yes: **Update contact field** Assessment Level / Assessment Score Percent / Assessment
       Points / Assessment Start Here / Assessment Pillars from
       `{{inboundWebhookRequest.assessment_level}}`, `..._percent`, `..._points`,
       `..._start_here`, `..._pillars`; then **Send email** to the contact, subject
       `Your Authority Visibility Score: {{inboundWebhookRequest.assessment_percent}}%`,
       body = `workflow/assessment_result_email.html` via Source code view.
     - No (applications): **Update contact field** Last name, Phone, Company name, Website
       from last_name / phone / business / url.
   - **Publish** the workflow (toggle top right).
3. **Test** each form on the live site (assessment email, host application, panelist
   application); check Execution logs and the contact record. Check the result email renders
   `result_html` as HTML (if GHL escapes it, switch the body to the individual fields).
4. **Point the root domain** `ownyourstagestudio.com/` at the new Home (/home). Today `/`
   serves Annette's old GHL page. Settings > Domains (or the website's domain settings).
5. Optional: workflow for the home short form (GHL form dvJo5tJIIPvpcprpSPcc, no workflow yet).

## Builder traps (cost real time)
- Chrome must be visible. If `document.visibilityState` is "hidden" the builder never
  loads and screenshots time out. Restore without stealing focus:
  user32 ShowWindow(h, 4) + SetWindowPos(h, HWND_TOPMOST, ..., 0x13); undo with HWND_NOTOPMOST.
- Code element: **drag** "Code" from Quick Add onto the canvas; clicking does nothing.
- Paste large code: PowerShell `Set-Clipboard` then ctrl+a / ctrl+v in the code editor.
- Never type unless the field is focused (zoom to check): stray keys fire builder shortcuts.
- Workflow field dropdowns render in a ~40px strip: scroll inside it to reach the result.
