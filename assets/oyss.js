/* ============================================================
   OWN YOUR STAGE STUDIO — The Light Engine
   ------------------------------------------------------------
   The brand has exactly one motif: light. So the site has exactly
   one motion system. Nothing slides in. Nothing bounces. Things
   become visible because they are lit, which is the same sentence
   the business uses to describe what it sells.

   Everything here degrades to a fully readable static page if JS
   is blocked, and switches itself off under prefers-reduced-motion.
   No dependencies. Safe to paste into a GHL Custom Code element.
   ============================================================ */
(function () {
  'use strict';

  var CALM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FINE = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {

    /* --------------------------------------------------------
       1. THE REVEAL
       Light hits a section and its contents resolve. One observer
       for the whole page; elements are released as they are lit
       and never re-dimmed, because a light cue does not un-fire.
       -------------------------------------------------------- */
    var lightable = document.querySelectorAll('[data-lit]');

    if (CALM || !('IntersectionObserver' in window)) {
      for (var i = 0; i < lightable.length; i++) lightable[i].classList.add('lit');
    } else {
      var rig = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('lit');
          rig.unobserve(e.target);
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });

      for (var j = 0; j < lightable.length; j++) rig.observe(lightable[j]);
    }

    /* --------------------------------------------------------
       2. BEAM IGNITION
       The hero beam is the logo icon at architectural scale. It
       strikes once, on load, and the pool blooms where it lands.
       -------------------------------------------------------- */
    if (!CALM) {
      requestAnimationFrame(function () {
        setTimeout(function () {
          document.querySelectorAll('.beam').forEach(function (b) { b.classList.add('beam--lit'); });
          document.querySelectorAll('.landing').forEach(function (l) { l.classList.add('landing--lit'); });
        }, 120);
      });
    } else {
      document.querySelectorAll('.beam, .landing').forEach(function (n) { n.style.opacity = 1; });
    }

    /* --------------------------------------------------------
       3. THE TRAVELLING POOL
       A pool of light that follows the pointer across dark
       sections. Desktop only, and deliberately almost subliminal:
       gold at 8 percent. The deck permits one pool of light and
       forbids flares, so this stays a pool.
       -------------------------------------------------------- */
    if (FINE && !CALM) {
      document.querySelectorAll('.stage').forEach(function (stage) {
        var pool = stage.querySelector('.stage__pool');
        if (!pool) return;
        var raf = null, px = 0, py = 0;
        stage.addEventListener('pointermove', function (ev) {
          var r = stage.getBoundingClientRect();
          px = ev.clientX - r.left;
          py = ev.clientY - r.top;
          if (raf) return;
          raf = requestAnimationFrame(function () {
            pool.style.left = px + 'px';
            pool.style.top = py + 'px';
            raf = null;
          });
        });
      });
    }

    /* --------------------------------------------------------
       4. THE CUE SHEET
       The client journey runs like a production cue stack: a
       marker travels down the rail and each cue lights as the
       reader reaches it.
       -------------------------------------------------------- */
    document.querySelectorAll('.cuesheet').forEach(function (sheet) {
      var rows = sheet.querySelectorAll('.cuerow');
      var marker = sheet.querySelector('.cuesheet__marker');
      if (!rows.length) return;

      if (CALM || !('IntersectionObserver' in window)) {
        rows.forEach(function (r) { r.classList.add('lit'); });
        if (marker) marker.style.display = 'none';
        return;
      }

      var cueObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('lit');
          if (marker) {
            marker.style.top = (e.target.offsetTop + e.target.offsetHeight / 2 - 3) + 'px';
          }
        });
      }, { rootMargin: '-42% 0px -42% 0px' });

      rows.forEach(function (r) { cueObs.observe(r); });
    });

    /* --------------------------------------------------------
       5. THE PANEL RIG
       Six frames, one light. The producer switches between them.
       Runs only while the rig is on screen so it never burns
       cycles in a background tab.
       -------------------------------------------------------- */
    document.querySelectorAll('.rig').forEach(function (rigEl) {
      var frames = rigEl.querySelectorAll('.frame');
      if (frames.length < 2) return;

      if (CALM) { frames.forEach(function (f) { f.classList.add('on'); }); return; }

      var idx = 0, timer = null;
      function cue() {
        frames.forEach(function (f) { f.classList.remove('on'); });
        frames[idx].classList.add('on');
        idx = (idx + 1) % frames.length;
      }
      function start() { if (!timer) { cue(); timer = setInterval(cue, 2600); } }
      function stop() { clearInterval(timer); timer = null; }

      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (e) {
          e[0].isIntersecting ? start() : stop();
        }, { threshold: 0.25 }).observe(rigEl);
      } else { start(); }

      document.addEventListener('visibilitychange', function () {
        document.hidden ? stop() : start();
      });
    });

    /* --------------------------------------------------------
       6. MASTHEAD
       -------------------------------------------------------- */
    var burger = document.querySelector('.burger');
    var nav = document.querySelector('.masthead nav');
    if (burger && nav) {
      burger.addEventListener('click', function () {
        var open = nav.classList.toggle('open');
        burger.setAttribute('aria-expanded', open ? 'true' : 'false');
        burger.textContent = open ? 'Close' : 'Menu';
      });
      nav.addEventListener('click', function (e) {
        if (e.target.tagName === 'A' && nav.classList.contains('open')) {
          nav.classList.remove('open');
          burger.setAttribute('aria-expanded', 'false');
          burger.textContent = 'Menu';
        }
      });
    }

    /* --------------------------------------------------------
       7. READING PROGRESS — a beam that fills as you descend.
       -------------------------------------------------------- */
    var fill = document.querySelector('.progress__fill');
    if (fill) {
      var tick = false;
      function paint() {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        var p = h > 0 ? (window.scrollY / h) * 100 : 0;
        fill.style.width = Math.min(100, Math.max(0, p)) + '%';
        tick = false;
      }
      window.addEventListener('scroll', function () {
        if (!tick) { requestAnimationFrame(paint); tick = true; }
      }, { passive: true });
      paint();
    }

    /* --------------------------------------------------------
       8. DOCUMENT CONTENTS RAIL
       -------------------------------------------------------- */
    var toc = document.querySelector('.doctoc');
    if (toc && 'IntersectionObserver' in window) {
      var links = toc.querySelectorAll('a');
      var map = {};
      links.forEach(function (a) {
        var t = document.querySelector(a.getAttribute('href'));
        if (t) map[t.id] = a;
      });
      var tocObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          links.forEach(function (a) { a.classList.remove('here'); });
          if (map[e.target.id]) map[e.target.id].classList.add('here');
        });
      }, { rootMargin: '-15% 0px -70% 0px' });
      Object.keys(map).forEach(function (id) {
        var el = document.getElementById(id);
        if (el) tocObs.observe(el);
      });
    }
  });

  /* ==========================================================
     AGREEMENT SIGNING
     Exposed as window.OYSS.signing so an agreement page wires
     itself up with one call. Demo-functional by design: it
     validates, renders the signature, stamps the date and
     produces a signed record. CONFIG.endpoint is the single
     line to change when the live GHL / payment hook exists.
     ========================================================== */
  window.OYSS = window.OYSS || {};

  window.OYSS.signing = function (opts) {
    var cfg = opts || {};
    var form = document.getElementById(cfg.form || 'agreement-form');
    if (!form) return;

    var gate = document.getElementById(cfg.gate || 'sign-gate');
    var body = document.getElementById(cfg.body || 'agreement-body');
    var nameIn = form.querySelector('[name="signature"]');
    var preview = document.getElementById('sig-preview');
    var dateOut = document.getElementById('sig-date');
    var submit = form.querySelector('[type="submit"]');
    var done = document.getElementById('signed-state');

    /* The date is stamped, not typed. A party cannot backdate. */
    var now = new Date();
    var stamp = now.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    if (dateOut) dateOut.textContent = stamp;

    /* The signature block stays locked until the document has actually been
       scrolled to the end. Reading is the point.

       Two independent triggers, because a gate that fails closed means nobody
       can ever sign. The observer handles the normal case; the scroll fallback
       covers short documents, tall viewports and anything that keeps the end
       marker from ever intersecting on its own. */
    function unlock() {
      if (gate.classList.contains('unlocked')) return;
      gate.classList.add('unlocked');
      var msg = document.getElementById('gate-msg');
      if (msg) msg.remove();
      window.removeEventListener('scroll', onScroll);
    }

    function onScroll() {
      if (!body) return;
      var r = body.getBoundingClientRect();
      /* the end of the legal text has passed the fold */
      if (r.bottom - window.innerHeight < 120) unlock();
    }

    if (gate && body) {
      var end = document.getElementById('agreement-end');
      if ('IntersectionObserver' in window && end) {
        new IntersectionObserver(function (e) {
          if (e[0].isIntersecting) unlock();
        }, { threshold: 0 }).observe(end);
      }
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();   /* already at the bottom, e.g. a deep link */
    } else if (gate) {
      unlock();
    }

    /* Typed signature renders live in the brand serif. */
    if (nameIn && preview) {
      nameIn.addEventListener('input', function () {
        preview.textContent = nameIn.value.trim();
      });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var missing = [];
      form.querySelectorAll('[required]').forEach(function (el) {
        var bad = (el.type === 'checkbox') ? !el.checked : !el.value.trim();
        el.setAttribute('aria-invalid', bad ? 'true' : 'false');
        if (bad) missing.push(el);
      });

      var err = document.getElementById('sign-error');
      if (missing.length) {
        if (err) {
          err.textContent = 'Complete every required field and acknowledgment before signing. ' +
                            missing.length + ' remaining.';
          err.hidden = false;
        }
        missing[0].focus();
        return;
      }
      if (err) err.hidden = true;

      var record = {};
      new FormData(form).forEach(function (v, k) { record[k] = v; });
      record.agreement = cfg.agreement || 'Agreement';
      record.signedAt = now.toISOString();
      record.signedAtDisplay = stamp;

      if (submit) { submit.disabled = true; submit.textContent = 'Recording signature'; }

      function finish() {
        if (done) {
          document.getElementById('sign-panel').hidden = true;
          done.hidden = false;
          var nm = document.getElementById('done-name');
          var dt = document.getElementById('done-date');
          if (nm) nm.textContent = record.signature || '';
          if (dt) dt.textContent = stamp;
          done.scrollIntoView({ behavior: CALM ? 'auto' : 'smooth', block: 'center' });
        }
        try { window.sessionStorage.setItem('oyss:' + (cfg.agreement || 'doc'), JSON.stringify(record)); } catch (_) {}
        if (typeof cfg.onSigned === 'function') cfg.onSigned(record);
      }

      /* One line to go live. Until an endpoint is set this stays
         a local draft signature, which is what a demo should be. */
      if (cfg.endpoint) {
        fetch(cfg.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(record)
        }).then(finish).catch(finish);
      } else {
        setTimeout(finish, 550);
      }
    });
  };

  /* ==========================================================
     THE READINESS ASSESSMENT
     Scores eight questions across the five factors named in the
     brand discovery: positioning, recognition, consistency,
     audience reach and readiness. Returns one of the four levels.
     ========================================================== */
  window.OYSS.assessment = function () {
    var form = document.getElementById('assessment-form');
    if (!form) return;

    var LEVELS = [
      { key: 'hidden', name: 'Hidden Expert', min: 0,
        meaning: 'Your work is trusted by the people who already know you, and almost invisible to everyone else. Nothing here is a comment on your expertise. It is a comment on distribution.',
        opportunity: 'A single produced event that puts your name on one subject. You do not need a content system yet. You need one credible room.',
        step: 'Book a Spotlight Call and leave with the subject you should be known for.',
        route: 'Spotlight Call' },
      { key: 'emerging', name: 'Emerging Expert', min: 9,
        meaning: 'You are known for something, by some people, some of the time. The signal is real but it is inconsistent, so it does not compound.',
        opportunity: 'Association. Sharing a stage with other credible experts raises your standing faster than posting more will.',
        step: 'Join a panel as a featured expert and see the production from the inside.',
        route: 'Panelist Program' },
      { key: 'expanding', name: 'Expanding Expert', min: 17,
        meaning: 'The right people are starting to find you without an introduction. Your positioning is working. Your platform is not yet built to hold the attention it is earning.',
        opportunity: 'A stage of your own. You are past borrowing other people’s audiences and ready to convene one.',
        step: 'Apply for the Own Your Stage Experience and host the room instead of joining it.',
        route: 'Own Your Stage Experience' },
      { key: 'visible', name: 'Visible Expert', min: 25,
        meaning: 'You are recognized in your field and your name carries the subject. The risk at this level is not obscurity. It is a single good year that never became a platform.',
        opportunity: 'Repetition. One event creates visibility. A signature series builds lasting authority.',
        step: 'Talk to us about a signature event series rather than a single event.',
        route: 'Own Your Stage Experience' }
    ];

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var qs = form.querySelectorAll('fieldset[data-q]');
      var total = 0, answered = 0;
      var err = document.getElementById('assess-error');

      qs.forEach(function (fs) {
        var picked = fs.querySelector('input:checked');
        if (picked) { answered++; total += parseInt(picked.value, 10); }
        fs.setAttribute('aria-invalid', picked ? 'false' : 'true');
      });

      if (answered < qs.length) {
        if (err) {
          err.textContent = 'Answer all ' + qs.length + ' questions to see your level. ' +
                            (qs.length - answered) + ' remaining.';
          err.hidden = false;
        }
        var firstMiss = form.querySelector('fieldset[aria-invalid="true"]');
        if (firstMiss) firstMiss.scrollIntoView({ behavior: CALM ? 'auto' : 'smooth', block: 'center' });
        return;
      }
      if (err) err.hidden = true;

      var level = LEVELS[0];
      for (var i = LEVELS.length - 1; i >= 0; i--) {
        if (total >= LEVELS[i].min) { level = LEVELS[i]; break; }
      }

      var out = document.getElementById('assessment-result');
      if (!out) return;

      document.getElementById('result-level').textContent = level.name;
      document.getElementById('result-meaning').textContent = level.meaning;
      document.getElementById('result-opportunity').textContent = level.opportunity;
      document.getElementById('result-step').textContent = level.step;

      /* Light the ladder up to the level reached. */
      var cells = out.querySelectorAll('.dimmer__cell');
      var reached = LEVELS.indexOf(level);
      cells.forEach(function (c, n) {
        c.style.opacity = n <= reached ? '1' : '.32';
        c.style.borderTopColor = n === reached ? 'var(--gold)' : '';
      });

      form.hidden = true;
      out.hidden = false;
      out.scrollIntoView({ behavior: CALM ? 'auto' : 'smooth', block: 'start' });

      try {
        window.sessionStorage.setItem('oyss:assessment',
          JSON.stringify({ score: total, level: level.key, route: level.route }));
      } catch (_) {}
    });
  };

})();
