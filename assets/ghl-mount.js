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
  var page = me.getAttribute('data-page') || 'index';
  var base = me.src.replace(/assets\/ghl-mount\.js.*$/, '');

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
  me.parentNode.insertBefore(host, me);

  var parents = [];
  for (var n = host.parentElement; n && n !== document.body; n = n.parentElement) parents.push(n);
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
