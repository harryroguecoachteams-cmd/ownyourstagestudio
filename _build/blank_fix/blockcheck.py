"""Check that each live page serves the new page block (SSR) byte-for-byte.
usage: python blockcheck.py <page> [<page> ...]   (page = file stem in _ghl_native/pages)"""
import sys, time, urllib.request
from pathlib import Path

PAGES = Path(r"F:\Annette\own your studio\oyss-site\_ghl_native\pages")
PATH = {'index': '/home', 'services': '/services', 'experience': '/experience', 'assessment': '/assessment',
        'panelists': '/panelists', 'about': '/about-us', 'faq': '/faq', 'apply': '/apply',
        'contact': '/strategy-session', 'apply-panelist': '/panelist-application',
        'agreements__host': '/host-agreement', 'agreements__panelist': '/panelist-agreement',
        'terms': '/terms', 'privacy': '/privacy', 'disclaimer': '/disclaimer'}

for page in sys.argv[1:]:
    want = (PAGES / f"{page}.html").read_text(encoding="utf8").replace('\r\n', '\n').strip()
    url = f"https://ownyourstagestudio.com{PATH[page]}?cb={int(time.time() * 1000)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf8')
    a = html.find('<!-- OYSS page:')
    ssr = html[a:a + len(want)] if a >= 0 else ''
    boot = '__oyssBootAt' in html[a:html.find('</body>')] if a >= 0 else False
    print(f"{page:22} {PATH[page]:22} ssr-block {'MATCH' if ssr == want else 'DIFF'}  boot-script {boot}  len {len(want)}")
