"""Fill each site form with sample values, submit it against a mocked endpoint,
and save the exact JSON the site sends. These become the GHL webhook samples."""
import json, os
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(__file__)
FILL = r"""
(() => {
  const f = document.querySelector('form');
  const sample = {
    name: 'Sample Applicant', first_name: 'Sample', last_name: 'Applicant',
    email: 'sample.applicant@example.com', phone: '+1 561 555 0100',
    business: 'Sample Consulting LLC', url: 'https://example.com', website: 'https://example.com',
    linkedin: 'https://www.linkedin.com/in/sample', video: 'https://example.com/video',
    title: 'Founder', referrer: 'A colleague'
  };
  f.querySelectorAll('input, select, textarea').forEach(el => {
    if (el.type === 'hidden' || el.disabled) return;
    if (el.type === 'checkbox') { el.checked = true; }
    else if (el.type === 'radio') {
      const first = f.querySelector('input[type=radio][name="' + el.name + '"]');
      if (first) first.checked = true;
    } else if (el.tagName === 'SELECT') {
      const opt = [...el.options].find(o => o.value);
      if (opt) el.value = opt.value;
    } else if (el.type === 'email') { el.value = sample.email; }
    else if (el.type === 'tel') { el.value = sample.phone; }
    else if (el.type === 'url') { el.value = sample[el.name] || 'https://example.com'; }
    else if (el.tagName === 'TEXTAREA') { el.value = 'Sample answer for ' + el.name.replace(/_/g, ' ') + '.'; }
    else { el.value = sample[el.name] || ('Sample ' + el.name.replace(/_/g, ' ')); }
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  });
  f.requestSubmit();
})()
"""
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for page, key in [("apply.html", "host-application"), ("apply-panelist.html", "panelist-application")]:
        pg = b.new_page()
        got = []
        pg.route("https://hook.test/**", lambda r: (got.append(r.request.post_data), r.fulfill(status=200, body="{}")))
        pg.add_init_script("window.OYSS_ENDPOINT='https://hook.test/x';")
        pg.goto("http://localhost:8899/" + page, wait_until="load")
        pg.wait_for_timeout(1500)
        pg.evaluate(FILL)
        pg.wait_for_timeout(1500)
        print(page, "captured" if got else "NOT SENT")
        if got:
            res[key] = json.loads(got[-1])
        pg.close()
    b.close()
json.dump(res, open(os.path.join(OUT, "payloads.json"), "w"), indent=1)
for k, v in res.items():
    print(k, sorted(v.keys()))
