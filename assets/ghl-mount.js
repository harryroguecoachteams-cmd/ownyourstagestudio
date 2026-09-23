/* ==========================================================
   OWN YOUR STAGE STUDIO - GHL PAGE MOUNT
   Feedback 9.0, note 8: the site lives in GoHighLevel, in the
   website "Own Your Stage Studio". Each GHL page carries ONE
   Custom JS/HTML element with one line:

     <script src="https://harryroguecoachteams-cmd.github.io/ownyourstagestudio/assets/ghl-mount.js" data-page="index"></script>

   and this script fetches that page's block (assets/ghl/<page>.html,
   written by build.py with links already rewritten to the GHL
   slugs), puts it where the script sits, loads the stylesheet and
   runs the page's scripts in order. So a change to the site is a
   push to GitHub, and every GHL page has it on the next load, with
   no re-pasting.
   ========================================================== */
(function () {
  var me = document.currentScript;
  if (!me) return;
  var base = me.src.replace(/assets\/ghl-mount\.js.*$/, '');

  /* One snippet for the whole website: put it in the GHL website's
     Settings > Body tracking code and every page works out which block
     it is from its own path. data-page still overrides, for a single
     page placed by hand. */
  var PATHS = {
    '': 'index', 'home': 'index', 'services': 'services', 'experience': 'experience',
    'assessment': 'assessment', 'panelists': 'panelists', 'about': 'about', 'faq': 'faq',
    'apply': 'apply', 'strategy-session': 'contact', 'panelist-application': 'apply-panelist',
    'host-agreement': 'agreements__host', 'panelist-agreement': 'agreements__panelist',
    'terms-conditions': 'terms', 'privacy-policy': 'privacy', 'disclaimer': 'disclaimer',
    /* GHL's preview links end in the page id rather than the path */
    '1iz74onjjmqakhybutjf': 'index', 'ltoy0agqxqh7d1ekzoz0': 'services',
    'ny4qv9tuq4uvy0tkhgb8': 'experience', 'ssfhgjmm35kvkmg5fehb': 'assessment',
    'm6wij1vlrt3s2hpqzohb': 'panelists', 'l9dgzyg1hyqsxtnnfci8': 'about',
    'oa8b1owhlb9h0docifr6': 'faq', 'kwc1l4mnmr5cexpk0tq5': 'apply',
    'clpwh4u35kfg34f5vwie': 'contact', 'xsaarow6ptqsfzmnhw7x': 'apply-panelist',
    'igbkl674r7nm7zrqag0r': 'agreements__host', 'yft7dckyim0rbojsxrgz': 'agreements__panelist',
    '21ygqleftzsyeldmkebe': 'terms', 'esdoqdzqr1s95sn7fxme': 'privacy',
    'cyei0n2mazbxrddekt6y': 'disclaimer'
  };
  var slug = location.pathname.replace(/^\/+|\/+$/g, '').split('/').pop().toLowerCase();
  var page = me.getAttribute('data-page') || PATHS[slug];
  if (!page) return;            /* a page this site does not own: leave it alone */

  /* The GHL builder wraps custom code in its own padded, centered
     column; the block is full bleed, so that column is opened up. */
  var css = document.createElement('style');
  css.textContent =
    'html,body{margin:0;background:#F8F5F2}' +
    '.oyss-mount{width:100%}' +
    'html{font-size:clamp(100%,62.5% + .4167vw,112.5%)}';
  document.head.appendChild(css);

  var host = document.createElement('div');
  host.className = 'oyss-mount';
  var inBody = me.parentNode && me.parentNode !== document.head && document.body && document.body.contains(me);
  var tracking = !me.getAttribute('data-page');
  if (inBody && !tracking) me.parentNode.insertBefore(host, me);
  else {
    /* From tracking code the script sits in the head or at the end of
       the body: the site goes first in the body, and the builder's own
       (empty) page sections are hidden. */
    var place = function () {
      document.body.insertBefore(host, document.body.firstChild);
      var hide = document.createElement('style');
      hide.textContent = 'body > *:not(.oyss-mount):not(script):not(style):not(link){display:none!important}';
      document.head.appendChild(hide);
    };
    if (document.body) place(); else document.addEventListener('DOMContentLoaded', place);
  }

  var parents = [];
  for (var n = host.parentElement; n && n !== document.body && n !== document.documentElement; n = n.parentElement) parents.push(n);
  parents.forEach(function (el) {
    el.style.maxWidth = 'none'; el.style.padding = '0'; el.style.margin = '0';
    el.style.width = '100%';
  });

  function run(scripts, i) {
    if (i >= scripts.length) return;
    var old = scripts[i], s = document.createElement('script');
    if (old.src) {
      s.src = old.src;
      s.onload = s.onerror = function () { run(scripts, i + 1); };
      document.body.appendChild(s);
    } else {
      s.textContent = old.textContent;
      document.body.appendChild(s);
      run(scripts, i + 1);
    }
  }

  fetch(base + 'assets/ghl/' + page + '.html', { cache: 'no-cache' })
    .then(function (r) { return r.text(); })
    .then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      doc.querySelectorAll('link[rel="stylesheet"]').forEach(function (l) {
        var k = document.createElement('link'); k.rel = 'stylesheet'; k.href = l.href;
        document.head.appendChild(k);
      });
      var scripts = [].slice.call(doc.querySelectorAll('script'));
      scripts.forEach(function (s) { s.parentNode.removeChild(s); });
      var root = doc.querySelector('.oyss');
      if (root) host.appendChild(document.importNode(root, true));
      run(scripts, 0);
    });
})();
