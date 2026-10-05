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
import os
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
DOCS = "https://roguecoachteams.com/relay/oyss-docs.php"


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
    # Framing rules pick a picture by its filename ([src$="annette-close.jpg"]).
    # In GHL the file is served under its media id, so the rule has to name
    # the id or it silently stops matching (the About hero lost its face).
    # Names that are no longer in the media set are old pictures; left alone.
    css = re.sub(r'\[src\$="([\w.-]+\.(?:jpg|png|svg|mp4))"\]',
                 lambda m: f'[src$="{MEDIA[m.group(1)]}"]' if m.group(1) in MEDIA else m.group(0), css)
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
    var scripts;
    if (document.querySelector('.oyss-mount')) {
      // The page's own boot script (BOOT below) already painted it at parse
      // time; only the engine and the page's scripts are left to run.
      scripts = [].slice.call(t.content.querySelectorAll('script'));
    } else {
      var host = document.createElement('div');
      host.className = 'oyss-mount';
      var frag = t.content.cloneNode(true);
      scripts = [].slice.call(frag.querySelectorAll('script'));
      scripts.forEach(function (s) { s.parentNode.removeChild(s); });
      host.appendChild(frag);
      // The root domain still serves the old GHL page, so home links go to /home
      // until an admin sets /home as the domain's default page.
      [].forEach.call(host.querySelectorAll('a[href="/"]'), function (a) { a.setAttribute('href', '/home'); });
      document.body.insertBefore(host, document.body.firstChild);
      document.documentElement.classList.add('oyss-mounted');
    }
    window.__oyssEngine();
    run(scripts, 0);
    // The sticky bar and the exit pop-up, per page (feedback 14): the
    // demo builds them into each page's shell; here the loader adds them.
    var pc = window.__oyssPrompts && window.__oyssPrompts[t.getAttribute('data-page')];
    if (pc && window.OYSS && window.OYSS.prompts) { try { window.OYSS.prompts(pc); } catch (e) {} }
    return true;
  }
  function tick() {
    if (mount()) return;
    if (++tries < 300) setTimeout(tick, 50);
  }
  if (document.body) tick(); else document.addEventListener('DOMContentLoaded', tick);
})();
"""

# Page boot (5 Oct 2026). GHL changed how it serves the website's tracking
# code: with no cookie banner it now holds the head AND body code back until
# the visitor touches, scrolls or types, or 4 s pass (stcdn _preview chunk
# "HtmlPreview", defer -> listeners on pointerdown/keydown/touchstart/scroll/
# mousemove). On a phone that read as "every page opens blank white until I
# touch the screen". The page's own Custom Code element is still served as
# real markup, so this script, at the end of every page block, is the only
# code that runs at parse time. It does two things:
#   1. releases GHL's gate at once (it listens for scroll), so the engine
#      arrives as soon as GHL has hydrated, instead of on the first touch;
#   2. if the stylesheet is already on the page (the head code's <style>
#      blocks ARE served in <head>, and carry --oyss-boot), mounts the page
#      right now, so it paints with the HTML instead of after GHL's own JS.
# Kept small and stable on purpose: changing it means 15 builder pastes.
# Everything else stays in the tracking code.
BOOT = r"""
(function () {
  var w = window, d = document, de = d.documentElement;
  if (w.__oyssBoot) return;
  w.__oyssBoot = 1;
  var n = 0;
  (function kick() {
    if (w.__oyssLoader || ++n > 100) return;
    try { w.dispatchEvent(new Event('scroll')); } catch (e) {}
    setTimeout(kick, 60);
  })();
  var t = d.querySelector('template.oyss-page');
  if (!t || d.querySelector('.oyss-mount')) return;
  try { if (!getComputedStyle(de).getPropertyValue('--oyss-boot').trim()) return; } catch (e) { return; }
  var host = d.createElement('div');
  host.className = 'oyss-mount';
  var frag = t.content.cloneNode(true);
  [].forEach.call(frag.querySelectorAll('script'), function (s) { s.parentNode.removeChild(s); });
  host.appendChild(frag);
  [].forEach.call(host.querySelectorAll('a[href="/"]'), function (a) { a.setAttribute('href', '/home'); });
  d.body.insertBefore(host, d.body.firstChild);
  de.classList.add('oyss-mounted', 'oyss-booted');
  w.__oyssBootAt = Date.now();
  var bar = host.querySelector('.masthead');
  if (bar) de.style.setProperty('--oyss-mh', Math.round(bar.getBoundingClientRect().height) + 'px');
  de.style.setProperty('--oyss-sbw', (w.innerWidth - de.clientWidth) + 'px');
  [].forEach.call(host.querySelectorAll('.beam'), function (b) { b.classList.add('beam--lit'); });
  if (!('IntersectionObserver' in w)) return;
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('lit');
      io.unobserve(e.target);
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0 });
  [].forEach.call(host.querySelectorAll('[data-lit]'), function (el) { io.observe(el); });
})();
"""

HOST_CSS = (
    ":root{--oyss-boot:1}"
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

    # Prompts per GHL page: the same per-KIND config build.py writes into
    # each demo page's shell, with the demo's file links swapped for the
    # funnel slugs.
    import importlib.util
    spec = importlib.util.spec_from_file_location("oyss_build", ROOT / "build.py")
    B = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(B)
    cfgs = []
    for row in B.SITE:
        fname, kind = row[0], row[4]
        js = B.PROMPTS.get(kind)
        if not js:
            continue
        obj = re.search(r"OYSS\.prompts\((\{.*\})\);", js, re.S).group(1)
        for k, v in sorted(B.SLUGS.items(), key=lambda kv: -len(kv[0])):
            obj = obj.replace(f"'{k}'", f"'{v}'")
        if ".html'" in obj:
            raise SystemExit(f"prompts for {fname}: a link was not rewritten: {obj}")
        page = fname.replace("/", "__")[:-5]
        cfgs.append(f"{json.dumps(page)}:{obj}")
    prompts_js = "window.__oyssPrompts={" + ",".join(cfgs) + "};"

    endpoint = f"window.OYSS_ENDPOINT={json.dumps(ENDPOINT)};" if ENDPOINT else ""
    # the signed-PDF / receipts relay (28 Sep 2026): files each signed PDF in
    # Annette's GHL and emails it from events@. Live site only.
    endpoint += f"window.OYSS_DOCS={json.dumps(DOCS)};"
    # Hero preload (3 Oct 2026). Each page's largest paint is its hero image,
    # which the loader inserts late, so a mobile Lighthouse run only requested
    # it ~6 s in. This tiny script sits at the very top of the body code
    # (served as markup, unlike the head code, whose scripts GHL adds after
    # load) and starts the one hero image for the current path at parse time.
    slug_of = {k.replace("/", "__")[:-5]: ("/home" if v == "/" else v) for k, v in B.SLUGS.items()}
    heroes = {}
    for f in sorted(SRC.glob("*.html")):
        sec = re.search(r'<section class="reel[^"]*".*?</section>', rewrite_media(f.read_text(encoding="utf8")), re.S)
        if not sec:
            continue
        m = (re.search(r'<video[^>]*\bposter="([^"]+)"', sec.group(0))
             or re.search(r'<img[^>]*class="reel__plate"[^>]*\bsrc="([^"]+)"', sec.group(0)))
        if m and f.stem in slug_of:
            heroes[slug_of[f.stem]] = m.group(1)
    base = os.path.commonprefix(list(heroes.values())) if heroes else ""
    base = base[:base.rfind("/") + 1]
    hero_js = ("(function(){var M=" + json.dumps(base) + ",H=" +
               json.dumps({k: v[len(base):] for k, v in sorted(heroes.items())}, separators=(",", ":")) +
               ",p=location.pathname.replace(/\\/+$/,'').toLowerCase()||'/home',f=H[p];if(!f)return;"
               "var l=document.createElement('link');l.rel='preload';l.as='image';l.href=M+f;"
               "l.setAttribute('fetchpriority','high');document.head.appendChild(l);})();")
    # 5 Oct 2026: the stylesheet moved to the HEAD code. GHL serves the head
    # code's <style> blocks inside <head> (its parser keeps meta, JSON-LD and
    # style tags), while the body code is now held back until the visitor
    # interacts (see BOOT). The hero preload above is not emitted any more:
    # it relied on the body code running at parse time, which GHL stopped.
    del hero_js
    head = (
        (ROOT / "_ghl_head.html").read_text(encoding="utf8").rstrip() + "\n"
        "<!-- Own Your Stage Studio: site stylesheet (served in <head>, so pages paint "
        "with the HTML). Generated by build_ghl.py; paste the whole file, do not edit here. -->\n"
        f"<style>{HOST_CSS}</style>\n"
        f"<style>{css_for_ghl()}</style>\n"
    )
    (OUT / "site_tracking_head.html").write_text(head, encoding="utf8")
    tracking = (
        "<!-- Own Your Stage Studio: light engine and page loader (the stylesheet is in the "
        "head code). Generated by build_ghl.py; paste the whole file, do not edit here. -->\n"
        f'<link rel="icon" href="{media_url("favicon.svg")}" type="image/svg+xml">\n'
        f"<script>{endpoint}{prompts_js}{engine_min}</script>\n"
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
            f"<script>{BOOT.strip()}</script>\n"
        )
        (OUT / "pages" / f.name).write_text(block, encoding="utf8")

    sizes = {p.name: p.stat().st_size for p in [OUT / "site_tracking_head.html", OUT / "site_tracking_body.html",
                                                *sorted((OUT / "pages").glob("*.html"))]}
    for k, v in sizes.items():
        print(f"{v/1024:8.1f} KB  {k}")
    print("endpoint:", ENDPOINT or "(none yet)")


if __name__ == "__main__":
    main()
