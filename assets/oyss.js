/* ============================================================
   OWN YOUR STAGE STUDIO: The Light Engine
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
       0. FULL-BLEED SCROLLBAR MEASUREMENT
       Only relevant when the markup is pasted inside a page
       builder's centered container (see .oyss--bleed). `50vw`
       counts the scrollbar and `50%` does not, so without this
       the bleed overflows horizontally by the scrollbar width.
       -------------------------------------------------------- */
    if (document.querySelector('.oyss--bleed')) {
      var setSbw = function () {
        var sbw = window.innerWidth - document.documentElement.clientWidth;
        document.documentElement.style.setProperty('--oyss-sbw', sbw + 'px');
      };
      setSbw();
      window.addEventListener('resize', setSbw, { passive: true });
    }

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
      /* threshold 0.12 asks for 12% of the ELEMENT to be visible, which is a
         quiet trap: on the host agreement the lit container is 28,592px tall,
         so it wanted 3,431px in a 641px viewport and could never fire. The
         whole contract sat at opacity .1 forever and read as a rendering
         failure. A ratio of an element cannot be a threshold when the element
         may be taller than the screen. The trigger is a POSITION instead: an
         element lights once it crosses into the bottom 12% of the viewport,
         which behaves the same for a paragraph and for a contract. */
      var rig = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('lit');
          rig.unobserve(e.target);
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0 });

      for (var j = 0; j < lightable.length; j++) rig.observe(lightable[j]);
    }

    /* --------------------------------------------------------
       1b. STRIKING THE LAMP
       The spotlight cannot be ignited with CSS. A keyframe
       animation and a transition were both tried on `.spot` and
       both sat permanently pending: startTime null, currentTime 0,
       while every other animation on the page advanced normally.
       The element is 2000px wide and carries three blurred
       conic-gradient layers, blend modes and a mask, and the
       compositor never confirms the handoff that a CSS animation
       needs before it can start.

       A frame-driven ramp needs no such handshake: each step is an
       ordinary style write. The curve is the deck's own fader
       (the same cubic-bezier as --fade-up) and the duration is the
       1.1s the reference footage takes to reach full output.

       `.spot` rests LIT in the stylesheet, so this only ever takes
       the light DOWN and brings it back up. With JavaScript off,
       the stage is lit.
       -------------------------------------------------------- */
    function easeFade(t) {
      /* cubic-bezier(.22, .85, .3, 1), sampled. */
      return 1 - Math.pow(1 - t, 2.6);
    }

    function strike(spot) {
      if (CALM) return;
      var DUR = 1150;
      var floor = spot.querySelector('.spot__floor');
      spot.style.opacity = '0';
      if (floor) floor.style.opacity = '0';
      var t0 = null;
      function step(ts) {
        if (t0 === null) t0 = ts;
        var t = Math.min(1, (ts - t0) / DUR);
        var v = easeFade(t);
        spot.style.opacity = v.toFixed(3);
        /* The floor blooms late: light reaches the deck after it
           leaves the lamp. */
        if (floor) floor.style.opacity = Math.max(0, easeFade(Math.max(0, (t - 0.26) / 0.74))).toFixed(3);
        if (t < 1) {
          requestAnimationFrame(step);
        } else {
          /* Hand the element back to the stylesheet. */
          spot.style.opacity = '';
          if (floor) floor.style.opacity = '';
        }
      }
      requestAnimationFrame(step);
    }

    /* --------------------------------------------------------
       2. BEAM IGNITION
       The hero beam is the logo icon at architectural scale. It
       strikes once, on load, and the pool blooms where it lands.
       -------------------------------------------------------- */
    if (!CALM) {
      requestAnimationFrame(function () {
        setTimeout(function () {
          document.querySelectorAll('.spot').forEach(strike);
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

      /* 4b. THE RAIL IS A DIMMER TRACK.
         The old behavior was three generic scroll effects on one
         component: a drawn rail, a sliding bead, and a fade-up per
         row. What replaces it is one idea instead of three, and it
         is the brand's own: each cue is a LIGHTING STATE.

         The row the reader is level with goes to full, the rows
         behind it hold at a readable half, the rows ahead sit at a
         quarter. Passing a row hands the light on rather than
         merely revealing it, and the rail fills to wherever the
         light has reached.

         Driven from one scroll handler rather than an observer per
         row, because the states are relative to each other: which
         row is live depends on where every other row is, and an
         observer only ever knows about the row it fired for. */
      sheet.classList.add('cuesheet--dimmer');
      if (marker) marker.style.display = 'none';

      var raf = null;
      function cueScan() {
        raf = null;
        var mid = window.innerHeight * 0.42;
        var live = -1;
        for (var i = 0; i < rows.length; i++) {
          if (rows[i].getBoundingClientRect().top <= mid) live = i;
        }
        for (var j = 0; j < rows.length; j++) {
          rows[j].classList.add('lit');
          rows[j].classList.toggle('live', j === live);
          rows[j].classList.toggle('passed', j < live);
        }
        var pct = live < 0 ? 0 : ((live + 1) / rows.length) * 100;
        sheet.style.setProperty('--cue-fill', pct.toFixed(1) + '%');
      }
      function onCueScroll() { if (!raf) raf = requestAnimationFrame(cueScan); }

      window.addEventListener('scroll', onCueScroll, { passive: true });
      window.addEventListener('resize', onCueScroll, { passive: true });
      cueScan();
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

      /* 5b. THE POINTER TAKES THE DESK.
         "On hovering each panel section should light up."
         A producer at a vision mixer overrides the running order
         the moment they touch it, so hovering a frame lights that
         frame and holds the automatic cue until the pointer
         leaves. Delegated from the rig rather than bound per
         frame, and the timer is genuinely stopped rather than
         merely outvoted by CSS: two lights would otherwise be on
         at once, which is the one thing this component exists to
         say never happens. */
      if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
        var held = null;
        rigEl.addEventListener('pointerover', function (ev) {
          var f = ev.target.closest ? ev.target.closest('.frame') : null;
          if (!f || f === held || !rigEl.contains(f)) return;
          held = f;
          stop();
          rigEl.classList.add('rig--held');
          frames.forEach(function (x) { x.classList.remove('on'); });
          f.classList.add('on');
        });
        rigEl.addEventListener('pointerleave', function () {
          if (!held) return;
          held = null;
          rigEl.classList.remove('rig--held');
          /* resume from the frame that was lit, not from the top */
          idx = Array.prototype.indexOf.call(frames, frames[0]);
          start();
        });
      }

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
      var setNav = function (open) {
        nav.classList.toggle('open', open);
        burger.setAttribute('aria-expanded', open ? 'true' : 'false');
        burger.textContent = open ? 'Close' : 'Menu';
        /* The panel scrolls itself. Without this the page behind it
           scrolls instead the moment a thumb lands outside a link. */
        document.body.style.overflow = open ? 'hidden' : '';
      };

      burger.addEventListener('click', function (e) {
        e.stopPropagation();
        setNav(!nav.classList.contains('open'));
      });

      nav.addEventListener('click', function (e) {
        if (e.target.closest('a') && nav.classList.contains('open')) setNav(false);
      });

      /* Tapping the page behind an open menu should close it, which
         is what every phone user expects and no CSS can express. */
      document.addEventListener('click', function (e) {
        if (nav.classList.contains('open') && !nav.contains(e.target) && e.target !== burger) setNav(false);
      });

      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && nav.classList.contains('open')) { setNav(false); burger.focus(); }
      });

      /* Rotating a phone can cross the 1040px line with the panel
         still open, leaving the body locked and the nav laid out as
         a desktop row. Close it on the way past. */
      var mq = window.matchMedia('(min-width: 1041px)');
      var onWide = function (m) { if (m.matches && nav.classList.contains('open')) setNav(false); };
      if (mq.addEventListener) mq.addEventListener('change', onWide);
      else if (mq.addListener) mq.addListener(onWide);
    }

    /* --------------------------------------------------------
       7. READING PROGRESS: a beam that fills as you descend.
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


    /* --------------------------------------------------------
       13. HOW TALL THE MASTHEAD ACTUALLY IS
       The page mark sticks directly under the masthead and every
       in-page anchor has to clear both. Hard-coding 78px was
       already wrong on a phone, where the bar is shorter, so the
       strip stuck too high and the masthead painted over the page
       name it exists to show. Measured, published as --oyss-mh,
       and remeasured on resize.
       -------------------------------------------------------- */
    var bar = document.querySelector('.masthead');
    if (bar) {
      var publishBar = function () {
        document.documentElement.style.setProperty(
          '--oyss-mh', Math.round(bar.getBoundingClientRect().height) + 'px');
      };
      publishBar();
      window.addEventListener('resize', publishBar, { passive: true });
      if ('ResizeObserver' in window) new ResizeObserver(publishBar).observe(bar);
    }

    /* --------------------------------------------------------
       9. WHERE THE BEAM FALLS
       The review: "not in the middle".

       The beam was pinned at left:62%, a fixed number on a page
       whose headline column is not fixed. On a centered section
       it landed to the right of the words. On a phone, where the
       whole composition is one column, it landed off the text.

       A beam falls on the thing it is lighting, so its position
       is read from the thing it is lighting: the optical center
       of the section's own headline block, expressed back to the
       section as --beam-x. Recomputed on resize, because the
       block reflows and 62% was wrong for exactly that reason.
       -------------------------------------------------------- */
    var beamed = [];
    document.querySelectorAll('.spot').forEach(function (b) {
      var sec = b.closest('section');
      if (sec) beamed.push(sec);
    });

    function aimBeams() {
      var narrow = window.innerWidth <= 1040;
      beamed.forEach(function (sec) {
        /* A centered section is centered. Nothing to measure. */
        if (sec.querySelector('.center') || narrow) {
          sec.style.setProperty('--beam-x', '50%');
          return;
        }
        var head = sec.querySelector('h1, h2, .display');
        if (!head) { sec.style.setProperty('--beam-x', '50%'); return; }
        var s = sec.getBoundingClientRect();
        var h = head.getBoundingClientRect();
        if (!s.width || !h.width) return;
        /* Optical, not geometric: a headline is ragged right, so
           its true weight sits left of the box center. */
        var x = (h.left - s.left) + h.width * 0.46;
        sec.style.setProperty('--beam-x', ((x / s.width) * 100).toFixed(2) + '%');
      });
    }
    aimBeams();
    var aimTimer = null;
    window.addEventListener('resize', function () {
      clearTimeout(aimTimer);
      aimTimer = setTimeout(aimBeams, 120);
    }, { passive: true });

    /* --------------------------------------------------------
       10. THE DIMMER LADDER ON A TOUCH SCREEN
       The review: "missing scroll effect".

       The ladder's key light was bound to :hover, so on a phone
       the component was four dead cells and the idea it exists
       to carry, that visibility is a ladder you climb, never
       fired. On a device with no pointer the right trigger is
       the only input there is: scroll position. Each cell lights
       as it is reached and holds, so scrolling the ladder
       performs the ladder.
       -------------------------------------------------------- */
    /* Not gated on pointer type. A phone was where the complaint came
       from, but a desktop reader who never happens to hover the ladder
       sees the same dead component, and scroll is the one input every
       device has. Hover still moves the light on top of this. */
    if (!CALM && 'IntersectionObserver' in window) {
      document.querySelectorAll('.dimmer').forEach(function (ladder) {
        var cells = ladder.querySelectorAll('.dimmer__cell');
        if (!cells.length) return;
        var dimObs = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (!e.isIntersecting) return;
            e.target.classList.add('on');
            dimObs.unobserve(e.target);
          });
        }, { threshold: 0.55, rootMargin: '0px 0px -18% 0px' });
        cells.forEach(function (c, n) {
          /* Stagger by index so a four-across desktop-width
             ladder still climbs rather than lighting at once. */
          setTimeout(function () { dimObs.observe(c); }, n * 60);
        });
      });
    } else if (CALM) {
      document.querySelectorAll('.dimmer__cell').forEach(function (c) { c.classList.add('on'); });
    }

    /* --------------------------------------------------------
       11. THE MARK, LIT
       The review asked for a motion logo. The mark is a beam and
       a pool, so it does what a beam does: it strikes once when
       the page loads, and again on hover or keyboard focus. It
       never loops. A light cue that repeats forever is no longer
       a cue, it is a decoration, and the deck rules those out.
       -------------------------------------------------------- */

    /* --------------------------------------------------------
       12. REQUIRED MARKERS
       The sheets now state that required fields are marked. They
       have to actually be marked, and marking them by hand across
       four forms is how one gets missed when a field's `required`
       attribute later changes. The label is derived from the
       control, so the two can never disagree.
       -------------------------------------------------------- */
    document.querySelectorAll('.sheet [required]').forEach(function (el) {
      var wrap = el.closest('.field, .check');
      if (!wrap) return;
      var label = wrap.querySelector('.field__label');
      if (!label || label.querySelector('.req')) return;
      var star = document.createElement('span');
      star.className = 'req';
      star.setAttribute('aria-hidden', 'true');
      star.textContent = ' *';
      label.appendChild(star);
    });

    if (!CALM) {
      document.querySelectorAll('.lockup--motion').forEach(function (mark) {
        function strike() {
          mark.classList.remove('lockup--motion');
          /* Reading offsetWidth restarts the animation; without
             it the class comes straight back on in the same frame
             and nothing replays. */
          void mark.offsetWidth;
          mark.classList.add('lockup--motion');
        }
        var cooling = false;
        function restrike() {
          if (cooling) return;
          cooling = true;
          strike();
          setTimeout(function () { cooling = false; }, 1200);
        }
        mark.addEventListener('pointerenter', restrike);
        mark.addEventListener('focus', restrike);
      });
    }


    /* --------------------------------------------------------
       15. FOOTAGE
       Two clips on the home page and the same contract for both:
       play only while on screen, never on a metered connection,
       never under prefers-reduced-motion. A looping video that
       has been scrolled past is a decoded frame every 33ms for a
       picture nobody is looking at, and on a laptop that is the
       fan coming on while somebody reads the pricing.

       Autoplay can still be refused, usually by low power mode.
       The catch is not decoration: the promise rejects, the
       poster stays, and that is already the right outcome.
       -------------------------------------------------------- */
    var conn = navigator.connection || {};
    var METERED = conn.saveData === true || /^(slow-)?2g$/.test(conn.effectiveType || '');

    function playSafely(v) {
      var p = v.play();
      if (p && p.catch) p.catch(function () {});
    }

    function whileVisible(v, onChange) {
      if (!('IntersectionObserver' in window)) { playSafely(v); return; }
      new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) playSafely(v); else v.pause();
          if (onChange) onChange(e.isIntersecting);
        });
      }, { threshold: 0.12 }).observe(v);
    }

    /* The hero used to be marked data-once, because the clip was a
       title sequence: the stage lit, the figure resolved, and then
       it held, and play() on an ended video seeks to zero, so
       without a guard the room re-ignited every time somebody
       scrolled back to the top.

       Feedback 3.0 asked for it to loop instead, and the loop that
       replaced it closes on itself: the last frame dissolves into
       the first, so `loop` on the element is the whole mechanism
       and playOnce has nothing left to guard. whileVisible still
       pauses it off screen. */

    /* THE BAND CLIPS.
       These are ambient: haze moving behind a headline, with the poster
       carrying the same frame. So on a phone they must not load at all,
       and `preload="none"` cannot express that on its own, because the
       autoplay attribute overrides it: the browser fetches enough to
       start playing whatever preload says. Measured, not assumed - all
       three mp4s were being pulled on a 390px viewport.

       So the band clips carry no autoplay and no <source> until this
       decides. Under 760px, or under reduced motion, or on a metered
       connection, the src is never set and the CSS poster is the
       section. */
    document.querySelectorAll('.band__media video').forEach(function (clip) {
      var wide = window.matchMedia('(min-width: 761px)').matches;
      if (!wide || CALM || METERED) return;
      var src = clip.getAttribute('data-src');
      if (!src) return;
      var armed = false;
      var arm = function () {
        if (armed) return;
        armed = true;
        clip.src = src;
        clip.load();
        playSafely(clip);
      };
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es, obs) {
          if (es[0].isIntersecting) { arm(); obs.disconnect(); }
        }, { rootMargin: '200px 0px' }).observe(clip);
      } else { arm(); }
    });

    document.querySelectorAll('.reel__media video').forEach(function (clip) {
      if (CALM || METERED) {
        clip.removeAttribute('autoplay');
        clip.pause();
        clip.style.display = 'none';
        var still = clip.parentNode.querySelector('.reel__still');
        if (still) still.style.display = 'block';
        return;
      }
      whileVisible(clip);
    });

    /* --------------------------------------------------------
       16. THE MASTHEAD, OVER THE FILM
       On the home page the bar has nothing behind it while the
       hero film is under it, and takes its ground back the
       moment the film leaves. Driven from the hero's own
       position rather than from a scroll threshold, so it stays
       correct at any viewport height.
       -------------------------------------------------------- */
    var over = document.querySelector('[data-over]');
    var barEl = document.querySelector('.masthead');
    if (over && barEl) {
      var syncBar = function () {
        var h = barEl.getBoundingClientRect().height;
        barEl.classList.toggle('masthead--over',
          over.getBoundingClientRect().bottom > h + 8);
      };
      syncBar();
      window.addEventListener('scroll', syncBar, { passive: true });
      window.addEventListener('resize', syncBar, { passive: true });
    }

    /* --------------------------------------------------------
       17. THE FILM
       The brand film under the hero. It runs while it is on
       screen and stops when it is not, and the one control is a
       real toggle rather than a play badge, because by the time
       anybody looks at it the film is already running.

       Under reduced motion or on a metered connection it does
       not load at all: preload is "none" and the poster carries
       the frame. The five beats are written out under the
       picture either way, so nothing is only available to
       somebody who can watch a video.
       -------------------------------------------------------- */
    var film = document.getElementById('film');
    var filmBtn = document.querySelector('.film__toggle');
    if (film && filmBtn) {
      var wanted = !(CALM || METERED);   // what the reader has asked for
      var inView = false;

      var label = function () {
        var playing = !film.paused;
        filmBtn.textContent = playing ? 'Pause' : 'Play';
        filmBtn.dataset.state = playing ? 'playing' : 'paused';
        filmBtn.setAttribute('aria-label', playing ? 'Pause the film' : 'Play the film');
      };

      if (wanted) film.preload = 'metadata';

      whileVisible(film, function (visible) {
        inView = visible;
        if (!wanted) { film.pause(); return; }
        label();
      });
      /* whileVisible plays on entry; if the reader has asked for
         no motion we undo that immediately rather than never
         observing, because the observer is also what stops it. */
      if (!wanted) film.pause();

      film.addEventListener('play', label);
      film.addEventListener('pause', label);

      filmBtn.addEventListener('click', function () {
        wanted = film.paused;
        if (film.paused) playSafely(film); else film.pause();
        label();
      });
      label();
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
  /* ----------------------------------------------------------
     THE STEPPER
     "Do not create assessment as a long form, create it in a box
     once the person select question 1 question2 pops up and then
     next and back option."

     Applied ON TOP of the full form rather than replacing it.
     Every fieldset stays in the document, so with JS off the page
     is the eight question form it always was and nothing is lost.
     What this adds is: show one, advance on answer, allow back.

     It advances on a 420ms delay rather than instantly, because
     an instant jump reads as the page misbehaving; the delay is
     long enough for the reader to see their own choice register
     and short enough that it never feels like waiting.
     ---------------------------------------------------------- */
  function stepper(form) {
    var steps = [].slice.call(form.querySelectorAll('fieldset[data-q]'));
    var foot = form.querySelector('.sheet__foot');
    if (steps.length < 2 || !foot) return null;

    /* Each question and the section label above it move together. */
    steps.forEach(function (fs) {
      var wrap = document.createElement('div');
      wrap.className = 'qstep';
      var label = fs.previousElementSibling;
      fs.parentNode.insertBefore(wrap, label && label.classList.contains('sheet__sec') ? label : fs);
      if (label && label.classList.contains('sheet__sec')) wrap.appendChild(label);
      wrap.appendChild(fs);
    });
    var panes = [].slice.call(form.querySelectorAll('.qstep'));

    form.classList.add('quiz');
    var stage = document.createElement('div');
    stage.className = 'quiz__stage';
    panes[0].parentNode.insertBefore(stage, panes[0]);
    panes.forEach(function (pn) { stage.appendChild(pn); });

    var bar = document.createElement('div');
    bar.className = 'quiz__bar';
    bar.innerHTML = '<span class="quiz__count"></span><span class="quiz__pips"></span>';
    stage.parentNode.insertBefore(bar, stage);
    var count = bar.querySelector('.quiz__count');
    var pips = bar.querySelector('.quiz__pips');
    panes.forEach(function () {
      var d = document.createElement('span'); d.className = 'quiz__pip'; pips.appendChild(d);
    });
    var pipEls = [].slice.call(pips.children);

    var nav = document.createElement('div');
    nav.className = 'quiz__nav';
    var back = document.createElement('button');
    back.type = 'button'; back.className = 'quiz__back'; back.textContent = 'Back';
    var hint = document.createElement('span');
    hint.className = 'quiz__hint';
    hint.textContent = 'Choose an answer to continue.';
    nav.appendChild(back); nav.appendChild(hint);
    stage.parentNode.insertBefore(nav, foot);

    var at = 0;
    var submitBtn = foot.querySelector('button[type=submit]');

    function answered(i) { return !!panes[i].querySelector('input:checked'); }

    function render() {
      panes.forEach(function (pn, i) { pn.classList.toggle('is-current', i === at); });
      pipEls.forEach(function (d, i) {
        d.classList.toggle('done', answered(i));
        d.classList.toggle('now', i === at);
      });
      count.textContent = 'Question ' + (at + 1) + ' of ' + panes.length;
      back.disabled = at === 0;
      var last = at === panes.length - 1;
      /* The submit button only appears on the last question, so
         nobody can submit an unfinished form and meet an error. */
      foot.hidden = !last;
      nav.hidden = last && answered(at);
      hint.textContent = last ? 'That is the last one.' : 'Choose an answer to continue.';
      if (submitBtn) submitBtn.disabled = !answered(at);
    }

    function go(i) {
      at = Math.max(0, Math.min(panes.length - 1, i));
      render();
      var top = bar.getBoundingClientRect().top + window.pageYOffset - (window.innerHeight * 0.16);
      window.scrollTo({ top: top, behavior: CALM ? 'auto' : 'smooth' });
      var first = panes[at].querySelector('input');
      if (first && !CALM) setTimeout(function () { first.focus({ preventScroll: true }); }, 260);
    }

    back.addEventListener('click', function () { go(at - 1); });

    form.addEventListener('change', function (ev) {
      if (!ev.target.matches('input[type=radio]')) return;
      var pane = ev.target.closest('.qstep');
      if (!pane) return;
      pane.querySelectorAll('.choice').forEach(function (c) { c.classList.remove('is-picked'); });
      var lab = ev.target.closest('.choice');
      if (lab) lab.classList.add('is-picked');
      render();
      if (panes.indexOf(pane) === panes.length - 1) return;
      form.classList.add('quiz--advancing');
      setTimeout(function () {
        form.classList.remove('quiz--advancing');
        go(panes.indexOf(pane) + 1);
      }, 420);
    });

    render();
    return { go: go, reset: function () { go(0); } };
  }

  window.OYSS.assessment = function () {
    var form = document.getElementById('assessment-form');
    if (!form) return;

    /* One question at a time. Falls back to the full form if the
       stepper cannot build itself, so a failure here costs the
       reader nothing. */
    var step = stepper(form);

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
        /* In stepper mode the unanswered question is not on screen,
           so scrolling to it would scroll to a hidden element. Step
           the reader to it instead. */
        var firstMiss = form.querySelector('fieldset[aria-invalid="true"]');
        if (step && firstMiss) {
          var pane = firstMiss.closest('.qstep');
          var all = [].slice.call(form.querySelectorAll('.qstep'));
          if (pane) step.go(all.indexOf(pane));
        } else if (firstMiss) {
          firstMiss.scrollIntoView({ behavior: CALM ? 'auto' : 'smooth', block: 'center' });
        }
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

      /* Light the ladder up to the level reached.
         Not with opacity: the cells are near-black and the result now sits
         on a white sheet, so a faded cell went pale gray and read as the
         BRIGHTEST rung on a ladder whose whole point is that brighter means
         further along. The rungs that have been reached are lit; the rest
         stay at their own dark token, which is exactly what they mean. */
      var ladder = out.querySelector('.dimmer');
      if (ladder) ladder.classList.add('dimmer--result');
      var cells = out.querySelectorAll('.dimmer__cell');
      var reached = LEVELS.indexOf(level);
      cells.forEach(function (c, n) {
        c.classList.toggle('on', n <= reached);
        var tag = c.querySelector('.dimmer__here');
        if (n === reached && !tag) {
          tag = document.createElement('p');
          tag.className = 'dimmer__here';
          tag.textContent = 'You are here';
          c.appendChild(tag);
        } else if (n !== reached && tag) {
          tag.remove();
        }
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


  /* ==========================================================
     THE PROMPTS
     A sticky bar and an exit-intent modal, per the client's
     brief: bottom bar on desktop and tablet, top bar on a phone,
     exit intent on all three.

     The governing rule is that a prompt on a premium site has to
     be EARNED or it costs more than it makes. So:

       - the bar waits until the reader has passed the section
         that names the price, because before that they do not
         know what they would be applying for
       - a page whose own job IS the action (the forms, the
         agreements) never shows either, since the thing the
         prompt would offer is already on screen
       - exit intent fires once per visitor per week, and never
         while a form on the page has anything typed in it
       - both remember a dismissal for a week

     Storage is wrapped: a browser with site data blocked throws
     on the accessor itself rather than returning null, and an
     uncaught throw here would take the rest of the script with
     it.
     ========================================================== */
  function store(key, val) {
    try {
      if (val === undefined) return window.localStorage.getItem(key);
      window.localStorage.setItem(key, val);
    } catch (_) { return null; }
  }
  function recently(key, days) {
    var t = store(key);
    return !!t && (Date.now() - parseInt(t, 10)) < days * 864e5;
  }

  window.OYSS.prompts = function (opts) {
    var cfg = opts || {};
    if (cfg.off) return;

    var phone = window.matchMedia('(max-width: 760px)');
    var root = document.querySelector('.oyss');
    if (!root) return;

    /* ---------- the bar ---------- */
    var bar = null;
    if (!recently('oyss:bar', 7)) {
      bar = document.createElement('aside');
      bar.className = 'prompt';
      bar.setAttribute('role', 'complementary');
      bar.setAttribute('aria-label', 'Next step');
      bar.hidden = true;
      bar.innerHTML =
        '<div class="prompt__inner">' +
          '<span class="prompt__text">' +
            '<span class="prompt__t">' + (cfg.barTitle || 'Ready to host your own panel?') + '</span>' +
            '<span class="prompt__m">' + (cfg.barMeta || 'Eight minutes to apply. No payment at this step.') + '</span>' +
          '</span>' +
          '<a class="btn btn--primary" href="' + (cfg.barHref || 'apply.html') + '">' + (cfg.barCta || 'Apply to host') + '</a>' +
          '<button class="prompt__x" type="button" aria-label="Dismiss">&times;</button>' +
        '</div>';
      root.appendChild(bar);

      var placeBar = function () {
        bar.classList.toggle('prompt--top', phone.matches);
        bar.classList.toggle('prompt--bottom', !phone.matches);
      };
      placeBar();
      (phone.addEventListener ? phone.addEventListener('change', placeBar)
                              : phone.addListener(placeBar));

      bar.querySelector('.prompt__x').addEventListener('click', function () {
        bar.classList.remove('is-in');
        store('oyss:bar', String(Date.now()));
        setTimeout(function () { bar.hidden = true; }, 620);
      });

      /* Earned, not timed. The trigger is a real element on the
         page rather than a scroll percentage, so it fires at the
         same MOMENT IN THE ARGUMENT on a long page and a short
         one. Falls back to two thirds down when the page has no
         such element. */
      var gate = document.querySelector(cfg.after || '.figure__value, .flood, .sheet__foot');
      var shown = false;
      var showBar = function () {
        if (shown) return;
        shown = true;
        bar.hidden = false;
        requestAnimationFrame(function () {
          requestAnimationFrame(function () { bar.classList.add('is-in'); });
        });
      };
      if (gate && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (es, o) {
          if (es[0].isIntersecting) { showBar(); o.disconnect(); }
        }, { rootMargin: '0px 0px -20% 0px' }).observe(gate);
      } else {
        var onScroll = function () {
          var d = document.documentElement;
          if ((window.pageYOffset + window.innerHeight) / d.scrollHeight > 0.66) {
            showBar();
            window.removeEventListener('scroll', onScroll);
          }
        };
        window.addEventListener('scroll', onScroll, { passive: true });
      }
    }

    /* ---------- exit intent ---------- */
    if (recently('oyss:exit', 7)) return;

    var exit = document.createElement('div');
    exit.className = 'exit';
    exit.hidden = true;
    exit.innerHTML =
      '<div class="exit__card" role="dialog" aria-modal="true" aria-labelledby="oyss-exit-t">' +
        '<button class="exit__x" type="button" aria-label="Close">&times;</button>' +
        '<p class="exit__eyebrow">' + (cfg.exitEyebrow || 'Before you go') + '</p>' +
        '<p class="exit__t" id="oyss-exit-t">' + (cfg.exitTitle || 'Find out what the room already thinks you are known for.') + '</p>' +
        '<p class="exit__p">' + (cfg.exitBody || 'Eight questions, about three minutes, and the result appears on the screen. No email address, nothing sent anywhere.') + '</p>' +
        '<div class="exit__actions">' +
          '<a class="btn btn--primary" href="' + (cfg.exitHref || 'assessment.html') + '">' + (cfg.exitCta || 'Take the assessment') + '</a>' +
          '<button class="exit__no" type="button">No thanks</button>' +
        '</div>' +
      '</div>';
    root.appendChild(exit);

    var lastFocus = null;
    var open = false;

    function typedSomething() {
      var any = false;
      document.querySelectorAll('input, textarea, select').forEach(function (el) {
        if (el.type === 'radio' || el.type === 'checkbox') { if (el.checked) any = true; }
        else if (el.value && el.value.trim()) any = true;
      });
      return any;
    }

    function closeExit() {
      if (!open) return;
      open = false;
      exit.classList.remove('is-in');
      store('oyss:exit', String(Date.now()));
      setTimeout(function () { exit.hidden = true; }, 380);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    function openExit() {
      /* Never interrupt somebody who is mid-form. Whatever this
         modal offers is worth less than the application they are
         already filling in. */
      if (open || typedSomething() || recently('oyss:exit', 7)) return;
      open = true;
      lastFocus = document.activeElement;
      exit.hidden = false;
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { exit.classList.add('is-in'); });
      });
      var first = exit.querySelector('.btn');
      if (first) first.focus();
    }

    exit.querySelector('.exit__x').addEventListener('click', closeExit);
    exit.querySelector('.exit__no').addEventListener('click', closeExit);
    exit.addEventListener('click', function (e) { if (e.target === exit) closeExit(); });
    document.addEventListener('keydown', function (e) {
      if (!open) return;
      if (e.key === 'Escape') { closeExit(); return; }
      /* Focus stays in the dialog while it is open. */
      if (e.key !== 'Tab') return;
      var f = exit.querySelectorAll('button, a[href]');
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });

    /* POINTER: the mouse leaving through the TOP of the window,
       which is the only edge that means "going to the address bar
       or the tab strip" rather than "reaching for the scrollbar". */
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      var armed = false;
      setTimeout(function () { armed = true; }, 6000);
      document.addEventListener('mouseout', function (e) {
        if (!armed || e.relatedTarget || e.clientY > 8) return;
        openExit();
      });
    } else {
      /* TOUCH: there is no exit gesture, so the honest equivalent
         is a fast upward flick toward the address bar after the
         reader has actually read something. Both conditions
         matter: the flick alone is just scrolling. */
      var readEnough = false;
      var lastY = window.pageYOffset, lastT = Date.now();
      window.addEventListener('scroll', function () {
        var y = window.pageYOffset, t = Date.now();
        var d = document.documentElement;
        if ((y + window.innerHeight) / d.scrollHeight > 0.45) readEnough = true;
        var dt = t - lastT;
        if (readEnough && dt > 0 && dt < 260 && (lastY - y) / dt > 1.6 && y < 260) openExit();
        lastY = y; lastT = t;
      }, { passive: true });
    }
  };


  /* ==========================================================
     THE FRAME, ASSEMBLING
     "Create a video here how it looks."
     Four beats on the real component rather than a baked clip:
     light, frame and mark, name plate, on air. Runs once when
     scrolled to and replays on click or Enter. Rests ASSEMBLED,
     so with JS off or reduced motion on, the reader simply sees
     the finished frame, which is the useful state.
     ========================================================== */
  window.OYSS.buildFrame = function (id) {
    var el = document.getElementById(id || 'panelist-build');
    if (!el) return;
    var steps = [].slice.call(document.querySelectorAll('.build__step'));
    if (CALM) { steps.forEach(function (s) { s.classList.add('on'); }); return; }

    var timers = [];
    function clear() { timers.forEach(clearTimeout); timers = []; }
    function at(n) {
      el.setAttribute('data-build', String(n));
      steps.forEach(function (s) { s.classList.toggle('on', +s.dataset.step <= n); });
    }
    function run() {
      clear();
      at(0);
      [1, 2, 3, 4].forEach(function (n, i) {
        timers.push(setTimeout(function () { at(n); }, 620 + i * 720));
      });
      timers.push(setTimeout(function () { el.removeAttribute('data-build'); }, 620 + 4 * 720));
    }

    el.addEventListener('click', run);
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); run(); }
    });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es, o) {
        if (es[0].isIntersecting) { run(); o.disconnect(); }
      }, { threshold: 0.4 }).observe(el);
    } else { steps.forEach(function (s) { s.classList.add('on'); }); }
  };

  /* --------------------------------------------------------
     18. AN INDEX THAT ACTUALLY OPENS THE ANSWER
     The FAQ gained a standing index in feedback 3.0, and every
     entry in it points at a <details> that is closed. Recent
     Chrome opens a closed details when you navigate to it;
     Safari and Firefox scroll to a summary and leave it shut,
     which reads as a broken link rather than as a browser
     difference.

     So the page does it itself, on load and on every hash
     change, and it also un-shuts nothing else: only an element
     that is a details, or sits inside one, is touched.
     -------------------------------------------------------- */
  (function () {
    function openTarget() {
      var id = (location.hash || '').slice(1);
      if (!id) return;
      var el = document.getElementById(id);
      if (!el) return;
      var d = el.tagName === 'DETAILS' ? el : el.closest && el.closest('details');
      if (!d) return;
      d.open = true;
      /* Opening changes the layout under the anchor, so the
         scroll position has to be taken again afterwards. The
         masthead is sticky, so this uses the measured bar
         height rather than a number. */
      var bar = parseFloat(getComputedStyle(document.documentElement)
                  .getPropertyValue('--oyss-mh')) || 78;
      var y = d.getBoundingClientRect().top + window.pageYOffset - bar - 18;
      window.scrollTo({ top: y, behavior: 'auto' });
    }
    window.addEventListener('hashchange', openTarget);
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', openTarget);
    } else { openTarget(); }
  })();


  /* --------------------------------------------------------
     19. THE FILM
     Feedback 5.0, note 4. The explainer sits behind its own
     poster with a play control over the whole picture, because
     Chrome's native control on a poster frame is a small
     triangle in the bottom corner and the block reads as a
     still image.

     The button does three things and no more: load the film,
     play it, and get out of the way. `preload="none"` means the
     first press is also the first byte fetched, so nothing is
     downloaded for a reader who never presses it.
     -------------------------------------------------------- */
  (function () {
    document.querySelectorAll('.videoblock').forEach(function (block) {
      var clip = block.querySelector('video');
      var btn = block.querySelector('.videoblock__play');
      if (!clip || !btn) return;

      /* The element ships WITH controls, so a reader with no
         JavaScript gets a playable film. This takes them off
         once the overlay exists to replace them, which is the
         only state where the poster should be a clean picture
         rather than a picture with a scrubber under it. */
      clip.controls = false;

      btn.addEventListener('click', function () {
        block.classList.add('is-playing');
        clip.controls = true;
        var p = clip.play();
        if (p && p.catch) p.catch(function () {});
        clip.focus({ preventScroll: true });
      });

      /* If it is paused back to the very start, the poster is on
         screen again and the control belongs back with it. */
      clip.addEventListener('ended', function () {
        clip.currentTime = 0;
        clip.controls = false;
        block.classList.remove('is-playing');
      });
    });
  })();


  /* --------------------------------------------------------
     20. THE APPLICATION, ONE SECTION AT A TIME
     Feedback 5.0, note 2: "Make the apply.html form similar to
     the assessment.html form style."

     The assessment shows one question, a count, a row of pips
     and a Back control. The application was a single scroll of
     eighteen fields under four headings, which is a different
     object entirely on the same site.

     This gives it the same chrome, from the same classes, so
     the two forms are visibly one family. Three things differ,
     and each because the content differs:

       - it steps by SECTION, not by field. "About you" is four
         questions that belong together and splitting them would
         be eighteen screens.
       - it does not auto advance. The assessment advances on a
         radio because the answer IS the click; here somebody is
         typing and being moved mid sentence would be hostile.
       - it validates the current section before it will move on,
         so nobody reaches the end and meets a list of things
         they missed four screens ago.

     Progressive enhancement throughout: with JavaScript off the
     form is the long scroll it always was, every field on the
     page, one submit button, and nothing is lost.
     -------------------------------------------------------- */
  window.OYSS = window.OYSS || {};
  window.OYSS.formSteps = function (formId, opts) {
    var form = document.getElementById(formId);
    if (!form) return null;
    opts = opts || {};

    var foot = form.querySelector('.sheet__foot');
    var heads = [].slice.call(form.querySelectorAll('.sheet__sec'));
    if (heads.length < 2 || !foot) return null;

    /* Group each section heading with everything that follows it
       until the next heading. The markup has no per-section
       wrapper, and adding one to nine hundred lines of form by
       hand is how a required field goes missing. */
    heads.forEach(function (head) {
      var pane = document.createElement('div');
      pane.className = 'qstep';
      form.insertBefore(pane, head);
      var node = head;
      while (node && node !== foot &&
             !(node !== head && node.classList && node.classList.contains('sheet__sec'))) {
        var next = node.nextSibling;
        pane.appendChild(node);
        node = next;
        while (node && node.nodeType !== 1) { node = node.nextSibling; }
      }
    });

    var panes = [].slice.call(form.querySelectorAll('.qstep'));
    form.classList.add('quiz', 'quiz--form');

    var stage = document.createElement('div');
    stage.className = 'quiz__stage';
    panes[0].parentNode.insertBefore(stage, panes[0]);
    panes.forEach(function (pn) { stage.appendChild(pn); });

    var bar = document.createElement('div');
    bar.className = 'quiz__bar';
    bar.innerHTML = '<span class="quiz__count"></span><span class="quiz__pips"></span>';
    stage.parentNode.insertBefore(bar, stage);
    var count = bar.querySelector('.quiz__count');
    var pips = bar.querySelector('.quiz__pips');
    panes.forEach(function () {
      var d = document.createElement('span'); d.className = 'quiz__pip'; pips.appendChild(d);
    });
    var pipEls = [].slice.call(pips.children);

    var nav = document.createElement('div');
    nav.className = 'quiz__nav quiz__nav--form';
    var back = document.createElement('button');
    back.type = 'button'; back.className = 'quiz__back'; back.textContent = 'Back';
    var next = document.createElement('button');
    next.type = 'button'; next.className = 'btn btn--primary quiz__next';
    var hint = document.createElement('span');
    hint.className = 'quiz__hint';
    nav.appendChild(back); nav.appendChild(next); nav.appendChild(hint);
    stage.parentNode.insertBefore(nav, foot);

    var at = 0;

    function fieldsIn(i) {
      return [].slice.call(panes[i].querySelectorAll('[required]'));
    }
    function missingIn(i) {
      return fieldsIn(i).filter(function (el) {
        return el.type === 'checkbox' ? !el.checked : !el.value.trim();
      });
    }
    function done(i) { return missingIn(i).length === 0; }


    function render() {
      panes.forEach(function (pn, i) { pn.classList.toggle('is-current', i === at); });
      pipEls.forEach(function (d, i) {
        d.classList.toggle('done', done(i) && i < at);
        d.classList.toggle('now', i === at);
      });
      /* "Step 1 of 4", not "About you 1 of 4". The section
         heading two lines below already says About you, and the
         assessment shipped that exact duplication once. */
      count.textContent = 'Step ' + (at + 1) + ' of ' + panes.length;
      back.disabled = at === 0;
      var last = at === panes.length - 1;
      next.hidden = last;
      next.textContent = 'Continue';
      foot.hidden = !last;
      hint.textContent = '';
    }

    function go(i) {
      at = Math.max(0, Math.min(panes.length - 1, i));
      render();
      var top = bar.getBoundingClientRect().top + window.pageYOffset -
                (window.innerHeight * 0.14);
      window.scrollTo({ top: top, behavior: CALM ? 'auto' : 'smooth' });
      var first = panes[at].querySelector('input, textarea, select');
      if (first && !CALM) setTimeout(function () { first.focus({ preventScroll: true }); }, 260);
    }

    function advance() {
      var miss = missingIn(at);
      fieldsIn(at).forEach(function (el) {
        el.setAttribute('aria-invalid', miss.indexOf(el) > -1 ? 'true' : 'false');
      });
      if (miss.length) {
        hint.textContent = miss.length === 1
          ? 'One more field on this step.'
          : miss.length + ' fields still to fill on this step.';
        miss[0].focus();
        return;
      }
      hint.textContent = '';
      go(at + 1);
    }

    back.addEventListener('click', function () { go(at - 1); });
    next.addEventListener('click', advance);

    /* Enter moves on rather than submitting a form the reader is
       three sections away from finishing. Not in a textarea,
       where Enter is a newline and means it. */
    form.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Enter') return;
      if (ev.target.tagName === 'TEXTAREA') return;
      if (at === panes.length - 1) return;
      ev.preventDefault();
      advance();
    });

    form.addEventListener('input', function () {
      if (hint.textContent) hint.textContent = '';
      render();
    });
    form.addEventListener('change', render);

    render();
    return {
      go: go,
      /* The submit handler validates the whole form. When
         something is missing it is usually not on screen, so it
         hands the field back here and this finds its step. */
      reveal: function (el) {
        var pane = el.closest('.qstep');
        if (!pane) return false;
        go(panes.indexOf(pane));
        setTimeout(function () { el.focus({ preventScroll: true }); }, 300);
        return true;
      }
    };
  };

})();
