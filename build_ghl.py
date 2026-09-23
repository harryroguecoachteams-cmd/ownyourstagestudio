"""
GHL-native build (feedback 10.0: "GHL is the real deal, GitHub was just
for demo"). Nothing on the live site loads from GitHub any more.

Run AFTER `python build.py` (which writes the _ghl/ blocks):

    python build_ghl.py

Writes _ghl_native/:

  site_tracking_body.html   ONE paste, GHL website Settings > Tracking
                            code > Body. Holds the whole stylesheet, the
                            light engine (oyss.js) and the mount loader.
  pages/<page>.html         ONE paste per GHL page, into a single Custom
                            Code element. It is the page's markup inside a
                            <template>, so GHL renders nothing by itself.

Why a template plus a loader: GHL renders page content client side
(Nuxt), after DOMContentLoaded, and its builder wraps custom code in a
padded column. The loader waits for the template, mounts the page as the
first child of <body> (full bleed, outside the builder's column), hides
the builder's empty sections, starts the engine, then runs the page's own
scripts in order. The same behaviour as the tested GitHub mount, with
every byte now in GHL.

Media comes from GHL Media Storage (folder "Website - Own Your Stage
Studio"); the filename -> CDN id map is _ghl_media.json.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "_ghl"
OUT = ROOT / "_ghl_native"
MEDIA = json.loads((ROOT / "_ghl_media.json").read_text(encoding="utf8"))
BASE = MEDIA.pop("_base")
MEDIA.pop("_note", None)
GH = "https://harryroguecoachteams-cmd.github.io/ownyourstagestudio/"

# The one switch for every form on the site: the GHL workflow's Inbound
# Webhook URL. Empty = forms show their "not switched on" state.
ENDPOINT = (ROOT / "_ghl_endpoint.txt").read_text().strip() if (ROOT / "_ghl_endpoint.txt").exists() else ""


def media_url(name):
    if name not in MEDIA:
        raise SystemExit(f"not in GHL media: {name}")
    return BASE + MEDIA[name]


def rewrite_media(text):
    # absolute GitHub asset URLs (block markup)
    def gh(m):
        return media_url(m.group(1).split("/")[-1])
    text = re.sub(re.escape(GH) + r"assets/(?:media/)?([\w.-]+\.(?:jpg|jpeg|png|svg|mp4|webm))(?:\?v=\w+)?", gh, text)
    return text


def minify(path, loader):
    r = subprocess.run(f"npx --yes esbuild --loader={loader} --minify",
                       input=path.read_text(encoding="utf8"), capture_output=True,
                       text=True, encoding="utf8", shell=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    return r.stdout


def css_for_ghl():
    css = minify(ROOT / "assets" / "oyss.css", "css")
    # relative url()s in the stylesheet: media/x.jpg and silk.svg
    css = re.sub(r"url\((['\"]?)(?:media/)?([\w.-]+\.(?:jpg|png|svg))\1\)",
                 lambda m: f"url({media_url(m.group(2))})", css)
    assert "github.io" not in css
    return css


LOADER = r"""
(function () {
  if (window.__oyssLoader) return;
  window.__oyssLoader = true;
  var tries = 0;
  function run(list, i) {
    if (i >= list.length) return;
    var old = list[i], s = document.createElement('script');
    if (old.src) {
      s.src = old.src;
      s.onload = s.onerror = function () { run(list, i + 1); };
      document.body.appendChild(s);
    } else {
      s.textContent = old.textContent;
      document.body.appendChild(s);
      run(list, i + 1);
    }
  }
  function mount() {
    var t = document.querySelector('template.oyss-page');
    if (!t) return false;
    var host = document.createElement('div');
    host.className = 'oyss-mount';
    var frag = t.content.cloneNode(true);
    var scripts = [].slice.call(frag.querySelectorAll('script'));
    scripts.forEach(function (s) { s.parentNode.removeChild(s); });
    host.appendChild(frag);
    document.body.insertBefore(host, document.body.firstChild);
    document.documentElement.classList.add('oyss-mounted');
    window.__oyssEngine();
    run(scripts, 0);
    return true;
  }
  function tick() {
    if (mount()) return;
    if (++tries < 300) setTimeout(tick, 50);
  }
  if (document.body) tick(); else document.addEventListener('DOMContentLoaded', tick);
})();
"""

HOST_CSS = (
    "html,body{margin:0;background:#F8F5F2}"
    "html{font-size:clamp(100%,62.5% + .4167vw,112.5%)}"
    ".oyss-mount{width:100%}"
    "html.oyss-mounted body>*:not(.oyss-mount):not(script):not(style):not(link):not(#teleports){display:none!important}"
)


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "pages").mkdir(exist_ok=True)

    js = (ROOT / "assets" / "oyss.js").read_text(encoding="utf8")
    engine = "window.__oyssEngine=function(){\n" + js + "\n};"
    engine_min_src = OUT / "_engine.js"
    engine_min_src.write_text(engine, encoding="utf8")
    engine_min = minify(engine_min_src, "js")
    engine_min_src.unlink()
    loader_min = LOADER  # small, left readable

    endpoint = f"window.OYSS_ENDPOINT={json.dumps(ENDPOINT)};" if ENDPOINT else ""
    tracking = (
        "<!-- Own Your Stage Studio: site stylesheet, light engine and page loader. "
        "Generated by build_ghl.py; paste the whole file, do not edit here. -->\n"
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="icon" href="{media_url("favicon.svg")}" type="image/svg+xml">\n'
        f"<style>{HOST_CSS}</style>\n"
        f"<style>{css_for_ghl()}</style>\n"
        f"<script>{endpoint}{engine_min}</script>\n"
        f"<script>{loader_min}</script>\n"
    )
    (OUT / "site_tracking_body.html").write_text(tracking, encoding="utf8")

    for f in sorted(SRC.glob("*.html")):
        s = f.read_text(encoding="utf8")
        s = re.sub(r"^<!--.*?-->\s*", "", s, count=1, flags=re.S)       # paste instructions
        s = re.sub(r'<link rel="stylesheet" href="[^"]*oyss\.css[^"]*">\s*', "", s)
        s = re.sub(r'<script src="[^"]*oyss\.js[^"]*"></script>\s*', "", s)
        s = rewrite_media(s)
        if "github.io" in s:
            left = sorted(set(re.findall(r"https://harryroguecoachteams[^\"' )]+", s)))
            raise SystemExit(f"{f.name}: GitHub URLs left: {left}")
        page = f.stem
        block = (
            f"<!-- OYSS page: {page}. Generated by build_ghl.py. -->\n"
            f'<template class="oyss-page" data-page="{page}">\n{s.strip()}\n</template>\n'
        )
        (OUT / "pages" / f.name).write_text(block, encoding="utf8")

    sizes = {p.name: p.stat().st_size for p in [OUT / "site_tracking_body.html", *sorted((OUT / "pages").glob("*.html"))]}
    for k, v in sizes.items():
        print(f"{v/1024:8.1f} KB  {k}")
    print("endpoint:", ENDPOINT or "(none yet)")


if __name__ == "__main__":
    main()
