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
        /* Feedback 9.0, note 1: the bar went clear over the hero's
           own words as soon as the page moved, so the menu and the
           headline were printed on top of each other. It is clear
           only at the very top now, where nothing is under it but
           the picture, and takes its ground back on the first
           scroll. */
        barEl.classList.toggle('masthead--over',
          window.scrollY < 8 && over.getBoundingClientRect().bottom > h + 8);
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
     AGREEMENT SIGNING  (rebuilt for feedback 11, 28 Sep 2026)
     Exposed as window.OYSS.signing so an agreement page wires
     itself up with one call.

     Three things happen when somebody signs:
       1. their signature is DRAWN, by them, on a pad. The typed
          legal name says whose it is; it is not the signature.
       2. a signed copy of the whole agreement is written as a PDF
          in the browser and saved to their device, and the same
          copy stays one button away on the page.
       3. the record goes to the GHL workflow carrying a link
          (signed_copy_url) that reopens this page as their signed
          copy, so the confirmation email and Annette's
          notification both carry the signed agreement.

     The signed copy link holds the record in the URL fragment,
     compressed. A fragment never reaches a server, so nothing is
     stored anywhere new.
     ========================================================== */
  window.OYSS = window.OYSS || {};

  var JSPDF_SRC = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
  var PAD_W = 1000;   /* signature strokes are stored on a 1000 unit wide grid */
  var INK = '#1F1E1D';

  /* ---- the pad ------------------------------------------------ */
  function SigPad(root, legalInput) {
    var canvas = root.querySelector('canvas');
    var clearBtn = root.querySelector('.sigpad__clear');
    var typeBtn = root.querySelector('.sigpad__typebtn');
    var value = root.querySelector('input[type="hidden"]');
    var ctx = canvas.getContext('2d');
    var strokes = [];          /* [[x,y],[x,y]...] in pad units */
    var typed = '';            /* set when the typed fallback is adopted */
    var cur = null, ratio = 1, padH = 300;

    function size() {
      var r = canvas.getBoundingClientRect();
      if (!r.width) return;
      var dpr = window.devicePixelRatio || 1;
      canvas.width = Math.round(r.width * dpr);
      canvas.height = Math.round(r.height * dpr);
      ratio = r.width / PAD_W;
      padH = Math.round(r.height / ratio);
      ctx.setTransform(dpr * ratio, 0, 0, dpr * ratio, 0, 0);
      draw();
    }

    function draw() {
      ctx.clearRect(0, 0, PAD_W, padH);
      if (typed) { script(ctx, typed, padH, 1); return; }
      paint(ctx, strokes, 1);
    }

    function point(e) {
      var r = canvas.getBoundingClientRect();
      return [Math.round((e.clientX - r.left) / ratio), Math.round((e.clientY - r.top) / ratio)];
    }

    function changed() {
      var ink = typed || strokes.length;
      root.classList.toggle('has-ink', !!ink);
      root.classList.remove('is-invalid');
      clearBtn.hidden = !ink;
      value.value = typed ? 'typed' : (strokes.length ? 'drawn' : '');
    }

    canvas.addEventListener('pointerdown', function (e) {
      if (e.button > 0) return;
      e.preventDefault();
      if (typed) { typed = ''; }
      try { canvas.setPointerCapture(e.pointerId); } catch (_) {}
      cur = [point(e)];
      strokes.push(cur);
      draw();
    });
    canvas.addEventListener('pointermove', function (e) {
      if (!cur) return;
      e.preventDefault();
      var evs = (e.getCoalescedEvents && e.getCoalescedEvents().length) ? e.getCoalescedEvents() : [e];
      evs.forEach(function (ev) {
        var p = point(ev), last = cur[cur.length - 1];
        if (Math.abs(p[0] - last[0]) + Math.abs(p[1] - last[1]) >= 2) cur.push(p);
      });
      draw();
    });
    function end() {
      if (!cur) return;
      if (cur.length === 1) cur.push([cur[0][0] + 1, cur[0][1]]);   /* a dot is a dot */
      cur = null;
      draw();
      changed();
    }
    canvas.addEventListener('pointerup', end);
    canvas.addEventListener('pointercancel', end);

    clearBtn.addEventListener('click', function () {
      strokes = []; typed = ''; draw(); changed(); canvas.focus();
    });
    if (typeBtn) typeBtn.addEventListener('click', function () {
      var n = (legalInput && legalInput.value.trim()) || '';
      if (!n) {
        if (legalInput) { legalInput.setAttribute('aria-invalid', 'true'); legalInput.focus(); }
        return;
      }
      strokes = []; typed = n;
      var go = function () { draw(); changed(); };
      if (document.fonts && document.fonts.load) {
        document.fonts.load('40px Sacramento').then(go, go);
      } else { go(); }
    });

    size();
    window.addEventListener('resize', function () { if (!cur) size(); });

    return {
      empty: function () { return !typed && !strokes.length; },
      invalid: function () { root.classList.add('is-invalid'); canvas.focus(); },
      data: function () {
        return { m: typed ? 'typed' : 'drawn', t: typed, h: padH, s: typed ? '' : encodePath(strokes) };
      }
    };
  }

  function script(c, name, h, scale) {
    c.fillStyle = INK;
    c.font = Math.round(h * 0.34 * scale) + 'px Sacramento, "Segoe Script", cursive';
    c.textBaseline = 'alphabetic';
    c.fillText(name, 70 * scale, h * 0.70 * scale);
  }

  function paint(c, strokes, scale) {
    c.lineCap = 'round'; c.lineJoin = 'round';
    c.strokeStyle = INK; c.lineWidth = 4.2 * scale;
    strokes.forEach(function (s) {
      c.beginPath();
      c.moveTo(s[0][0] * scale, s[0][1] * scale);
      for (var i = 1; i < s.length - 1; i++) {
        var mx = (s[i][0] + s[i + 1][0]) / 2, my = (s[i][1] + s[i + 1][1]) / 2;
        c.quadraticCurveTo(s[i][0] * scale, s[i][1] * scale, mx * scale, my * scale);
      }
      var l = s[s.length - 1];
      c.lineTo(l[0] * scale, l[1] * scale);
      c.stroke();
    });
  }

  /* strokes <-> "x,y dx,dy dx,dy;x,y ..." relative integers: small,
     and it deflates well. */
  function encodePath(strokes) {
    return strokes.map(function (s) {
      var out = [s[0][0] + ',' + s[0][1]];
      for (var i = 1; i < s.length; i++) out.push((s[i][0] - s[i - 1][0]) + ',' + (s[i][1] - s[i - 1][1]));
      return out.join(' ');
    }).join(';');
  }
  function decodePath(str) {
    if (!str) return [];
    return str.split(';').map(function (seg) {
      var pts = [], x = 0, y = 0;
      seg.split(' ').forEach(function (pair, i) {
        var v = pair.split(',').map(Number);
        if (i === 0) { x = v[0]; y = v[1]; } else { x += v[0]; y += v[1]; }
        pts.push([x, y]);
      });
      return pts;
    });
  }

  /* The signature as a PNG, cropped to the ink, dark on transparent. */
  function signaturePNG(sig) {
    var scale = 0.9, h = sig.h || 300;
    var c = document.createElement('canvas');
    c.width = Math.round(PAD_W * scale); c.height = Math.round(h * scale);
    var x = c.getContext('2d');
    if (sig.m === 'typed') script(x, sig.t, h, scale);
    else paint(x, decodePath(sig.s), scale);

    var d = x.getImageData(0, 0, c.width, c.height).data;
    var minX = c.width, minY = c.height, maxX = 0, maxY = 0;
    for (var yy = 0; yy < c.height; yy++) {
      for (var xx = 0; xx < c.width; xx++) {
        if (d[(yy * c.width + xx) * 4 + 3] > 8) {
          if (xx < minX) minX = xx;
          if (xx > maxX) maxX = xx;
          if (yy < minY) minY = yy;
          if (yy > maxY) maxY = yy;
        }
      }
    }
    if (maxX <= minX) return { url: c.toDataURL('image/png'), w: c.width, h: c.height };
    var m = 14;
    minX = Math.max(0, minX - m); minY = Math.max(0, minY - m);
    maxX = Math.min(c.width, maxX + m); maxY = Math.min(c.height, maxY + m);
    var o = document.createElement('canvas');
    o.width = maxX - minX; o.height = maxY - minY;
    o.getContext('2d').drawImage(c, minX, minY, o.width, o.height, 0, 0, o.width, o.height);
    return { url: o.toDataURL('image/png'), w: o.width, h: o.height };
  }

  /* ---- the signed copy link ------------------------------------ */
  function b64url(bytes) {
    var s = '';
    for (var i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
    return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
  function unb64url(str) {
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    while (str.length % 4) str += '=';
    var s = atob(str), b = new Uint8Array(s.length);
    for (var i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
    return b;
  }
  function pack(obj) {
    var raw = new TextEncoder().encode(JSON.stringify(obj));
    if (!window.CompressionStream) return Promise.resolve('j' + b64url(raw));
    try {
      var cs = new CompressionStream('deflate-raw');
      var w = cs.writable.getWriter(); w.write(raw); w.close();
      return new Response(cs.readable).arrayBuffer().then(function (buf) {
        return 'z' + b64url(new Uint8Array(buf));
      }, function () { return 'j' + b64url(raw); });
    } catch (_) { return Promise.resolve('j' + b64url(raw)); }
  }
  function unpack(str) {
    var kind = str.charAt(0), bytes = unb64url(str.slice(1));
    if (kind === 'j') return Promise.resolve(JSON.parse(new TextDecoder().decode(bytes)));
    var ds = new DecompressionStream('deflate-raw');
    var w = ds.writable.getWriter(); w.write(bytes); w.close();
    return new Response(ds.readable).text().then(JSON.parse);
  }

  /* ---- the PDF --------------------------------------------------- */
  function loadPdfLib() {
    if (window.jspdf && window.jspdf.jsPDF) return Promise.resolve(window.jspdf.jsPDF);
    return new Promise(function (res, rej) {
      var s = document.createElement('script');
      s.src = JSPDF_SRC; s.async = true;
      s.onload = function () { (window.jspdf && window.jspdf.jsPDF) ? res(window.jspdf.jsPDF) : rej(new Error('jsPDF')); };
      s.onerror = rej;
      document.head.appendChild(s);
    });
  }

  /* The standard PDF fonts speak WinAnsi only. */
  function ansi(t) {
    return String(t || '')
      .replace(/[‘’‚]/g, "'").replace(/[“”„]/g, '"')
      .replace(/[–—]/g, '-').replace(/…/g, '...').replace(/ /g, ' ')
      .replace(/™/g, '(TM)')
      .replace(/[^\x09\x0A\x0D\x20-\x7E¡-ÿ•]/g, '');
  }

  var LABELS = {
    legal_name: 'Legal name', business_name: 'Business name', email: 'Email address',
    phone: 'Telephone', event_title: 'Event title', event_theme: 'Event theme',
    event_date: 'Proposed event date', event_time: 'Time and time zone',
    event_audience: 'Intended audience', event_panelists: 'Target number of panelists',
    event_cta: 'Primary call to action'
  };

  function buildPdf(rec) {
    return loadPdfLib().then(function (JsPDF) {
      var doc = new JsPDF({ unit: 'pt', format: 'letter' });
      var W = doc.internal.pageSize.getWidth(), H = doc.internal.pageSize.getHeight();
      var M = 60, y = M, CW = W - M * 2;
      var title = rec.agreement;
      var BODY = [40, 38, 36], DARK = [31, 30, 29], MUTED = [110, 104, 100], RED = [185, 28, 28];

      function room(h) { if (y + h > H - M) { doc.addPage(); y = M; } }
      /* one wrapped block; `mark` hangs in the left margin of its first line */
      function text(str, size, style, gap, indent, color, mark) {
        indent = indent || 0;
        doc.setFont('helvetica', style || 'normal'); doc.setFontSize(size);
        doc.setTextColor(color ? color[0] : BODY[0], color ? color[1] : BODY[1], color ? color[2] : BODY[2]);
        var lines = doc.splitTextToSize(ansi(str), CW - indent), lh = size * 1.38;
        lines.forEach(function (ln, i) {
          room(lh);
          if (i === 0 && mark) doc.text(ansi(mark), M + (indent >= 20 ? 2 : indent - 12), y + size);
          doc.text(ln, M + indent, y + size);
          y += lh;
        });
        y += gap || 0;
      }

      /* the head */
      doc.setFont('helvetica', 'bold'); doc.setFontSize(9); doc.setTextColor(RED[0], RED[1], RED[2]);
      doc.text('OWN YOUR STAGE STUDIO, LLC', M, y + 9); y += 22;
      text(title, 19, 'bold', 4, 0, DARK);
      text('Signed copy', 11, 'normal', 14, 0, MUTED);

      /* the signing record */
      var top = y;
      y += 6;
      text('SIGNING RECORD', 8.5, 'bold', 4, 14, RED);
      Object.keys(LABELS).forEach(function (k) {
        if (rec.fields[k]) text(LABELS[k] + ':  ' + rec.fields[k], 9.5, 'normal', 1, 14);
      });
      text('Signed:  ' + rec.signedAtDisplay + '  (' + rec.signedAt + ')', 9.5, 'normal', 1, 14);
      text('Signature:  ' + (rec.sig.m === 'typed' ? 'typed legal name adopted as the signature' : 'drawn by the signer') +
           ', electronic, Fla. Stat. 668.50', 9.5, 'normal', 1, 14);
      text('Document:  ' + rec.url + (rec.version ? '  (text version ' + rec.version + ')' : ''), 9.5, 'normal', 6, 14);
      if (rec.changed) {
        text('The agreement text published at this address has changed since this signature. This copy ' +
             'shows the current text; the PDF saved at the moment of signing is the exact signed version.',
             9, 'bold', 6, 14, RED);
      }
      doc.setDrawColor(RED[0], RED[1], RED[2]); doc.setLineWidth(1.4);
      doc.line(M, top, M, y);
      y += 18;

      /* the agreement, as published on the page it was signed on */
      var body = document.getElementById('agreement-body');
      [].slice.call(body ? body.children : []).forEach(function (el) {
        var tag = el.tagName;
        var plain = el.textContent.replace(/\s+/g, ' ').trim();
        if (tag === 'H2') {
          var n = el.querySelector('.doc__n');
          var num = n ? n.textContent.trim() : '';
          var head = num ? num + '. ' + plain.slice(num.length).trim() : plain;
          y += 8; room(44);
          text(head, 11, 'bold', 4, 0, DARK);
        } else if (tag === 'H3') {
          y += 2; room(32);
          text(plain, 10, 'bold', 3, 0, DARK);
        } else if (tag === 'UL' || tag === 'OL') {
          [].slice.call(el.children).forEach(function (li, i) {
            text(li.textContent.replace(/\s+/g, ' ').trim(), 9.5, 'normal', 2, 16, null,
                 tag === 'OL' ? (i + 1) + '.' : '•');
          });
          y += 4;
        } else if (plain) {
          text(plain, 9.5, 'normal', 6);
        }
      });

      /* the signature page */
      doc.addPage(); y = M;
      text('EXECUTION', 8.5, 'bold', 6, 0, RED);
      text(title, 14, 'bold', 12, 0, DARK);
      text('Acknowledged by the signer before signing:', 9.5, 'bold', 6);
      (rec.acks || []).forEach(function (a) { text(a, 9.5, 'normal', 3, 22, null, '[X]'); });
      y += 22;

      var png = signaturePNG(rec.sig);
      var sw = Math.min(260, png.w * 0.5), sh = sw * png.h / png.w;
      if (sh > 90) { sh = 90; sw = sh * png.w / png.h; }
      room(sh + 110);
      doc.addImage(png.url, 'PNG', M, y, sw, sh);
      y += sh + 4;
      doc.setDrawColor(60, 58, 56); doc.setLineWidth(0.6); doc.line(M, y, M + 280, y);
      y += 6;
      text('Signature of ' + (rec.fields.legal_name || ''), 9, 'normal', 1, 0, MUTED);
      if (rec.fields.business_name) text('For ' + rec.fields.business_name, 9, 'normal', 1, 0, MUTED);
      text('Signed ' + rec.signedAtDisplay, 9, 'normal', 20, 0, MUTED);
      text('The other party to this Agreement is Own Your Stage Studio, LLC, a Florida limited ' +
           'liability company. This copy was generated at the moment of signing, from the ' +
           'Agreement as published at ' + rec.url + '.', 8.5, 'normal', 0, 0, MUTED);

      /* running foot */
      var pages = doc.getNumberOfPages();
      for (var i = 1; i <= pages; i++) {
        doc.setPage(i);
        doc.setFont('helvetica', 'normal'); doc.setFontSize(7.5); doc.setTextColor(140, 134, 130);
        doc.text(ansi(title + '  -  signed copy, ' + (rec.fields.legal_name || '')), M, H - 32);
        doc.text('Page ' + i + ' of ' + pages, W - M, H - 32, { align: 'right' });
      }
      return doc;
    });
  }

  function pdfName(rec) {
    var who = String(rec.fields.legal_name || 'signer').replace(/[^\w .-]+/g, '').trim();
    return 'Signed - ' + rec.agreement + ' - ' + who + ' - ' + String(rec.signedAt).slice(0, 10) + '.pdf';
  }

  function savePdf(rec, btn) {
    var label = btn && btn.textContent;
    if (btn) { btn.disabled = true; btn.textContent = 'Preparing your PDF'; }
    return buildPdf(rec).then(function (doc) {
      doc.save(pdfName(rec));
    }).catch(function () {
      /* The library could not load (offline, a blocker). The browser's
         own print to PDF still produces the signed page. */
      window.print();
    }).then(function () {
      if (btn) { btn.disabled = false; btn.textContent = label; }
    });
  }

  function ackTexts(form) {
    return [].slice.call(form.querySelectorAll('.check input[type="checkbox"]')).filter(function (b) {
      return b.checked;
    }).map(function (b) { return b.parentNode.textContent.replace(/\s+/g, ' ').trim(); });
  }

  function longDate(iso) {
    return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  }

  /* A fingerprint of the exact agreement text on the page (SHA-256, first
     12 hex). Stored with every signature, printed on the PDF, and checked
     when a signed copy link is opened: the link rebuilds the copy from the
     page, so if the wording has changed since, it has to say so. */
  function textVersion() {
    var body = document.getElementById('agreement-body');
    var t = body ? body.textContent.replace(/\s+/g, ' ').trim() : '';
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return Promise.resolve('');
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)).then(function (buf) {
      return [].slice.call(new Uint8Array(buf)).slice(0, 6).map(function (b) {
        return ('0' + b.toString(16)).slice(-2);
      }).join('');
    }, function () { return ''; });
  }

  /* ---- showing a signature that has been made ------------------- */
  function showSigned(rec, asCopy) {
    var panel = document.getElementById('sign-panel');
    var done = document.getElementById('signed-state');
    if (!done) return;
    if (panel) panel.hidden = true;
    done.hidden = false;
    /* The picture of the signature is made only once there is one, so
       the unsigned page carries no empty <img>. */
    var slot = document.getElementById('done-sig');
    if (slot) {
      var img = slot.tagName === 'IMG' ? slot : slot.querySelector('img');
      if (!img) { img = document.createElement('img'); slot.appendChild(img); }
      img.src = signaturePNG(rec.sig).url;
      img.alt = 'Signature of ' + (rec.fields.legal_name || 'the signer');
    }
    var nm = document.getElementById('done-name');
    var dt = document.getElementById('done-date');
    if (nm) nm.textContent = rec.fields.legal_name || '';
    if (dt) dt.textContent = rec.signedAtDisplay;
    var dl = document.getElementById('download-signed');
    if (dl) dl.onclick = function () { savePdf(rec, dl); };

    if (!asCopy) return;
    var lead = document.getElementById('done-lead');
    if (lead) lead.textContent = 'This is the signed copy of this agreement. Download it as a PDF ' +
      'with the full text, the signing record and the signature.';
    var after = document.getElementById('done-after');
    if (after) after.hidden = true;
    var gm = document.getElementById('gate-msg');
    if (gm) gm.remove();
    /* and say so at the top, where the reader lands */
    var head = document.querySelector('.docsheet .sheet__head');
    if (head && !document.querySelector('.signedcopy')) {
      var bar = document.createElement('div');
      bar.className = 'signedcopy no-print';
      bar.innerHTML = '<div><p class="signedcopy__k">Signed copy</p><p class="signedcopy__t"></p></div>' +
        '<button type="button" class="btn btn--primary">Download signed PDF</button>';
      bar.querySelector('.signedcopy__t').textContent = 'Signed by ' + (rec.fields.legal_name || '') +
        (rec.fields.business_name ? ', ' + rec.fields.business_name : '') + ', on ' + rec.signedAtDisplay + '.' +
        (rec.changed ? ' The agreement text on this page has changed since it was signed; the PDF saved at ' +
                       'signing is the exact signed version.' : '');
      var b = bar.querySelector('button');
      b.addEventListener('click', function () { savePdf(rec, b); });
      head.parentNode.insertBefore(bar, head.nextSibling);
    }
  }

  window.OYSS.signing = function (opts) {
    var cfg = opts || {};
    var form = document.getElementById(cfg.form || 'agreement-form');
    if (!form) return;
    var agreement = cfg.agreement || 'Agreement';
    var here = window.location.origin + window.location.pathname;

    /* Opened from a signed copy link: show that signature, nothing to sign. */
    var m = /[#&]signed=([^&]+)/.exec(window.location.hash);
    if (m) {
      var opened;
      try { opened = unpack(decodeURIComponent(m[1])); } catch (_) { opened = Promise.reject(_); }
      Promise.all([opened, textVersion()]).then(function (r) {
        var p = r[0];
        showSigned({
          agreement: agreement, fields: p.f || {}, acks: p.a || [], sig: p.g,
          signedAt: p.d, signedAtDisplay: longDate(p.d), url: here,
          version: p.k || '', changed: !!(p.k && r[1] && p.k !== r[1])
        }, true);
      }).catch(function () { /* a damaged link falls through to the unsigned page */ });
    }

    var gate = document.getElementById(cfg.gate || 'sign-gate');
    var body = document.getElementById(cfg.body || 'agreement-body');
    var legalIn = form.querySelector('[name="legal_name"]');
    var padEl = document.getElementById('sigpad');
    var pad = padEl ? SigPad(padEl, legalIn) : null;
    var dateOut = document.getElementById('sig-date');
    var submit = form.querySelector('[type="submit"]');

    /* The date is stamped, not typed. A party cannot backdate. */
    var now = new Date();
    var stamp = longDate(now.toISOString());
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
      /* the pad measured itself while locked; measure again now it is live */
      window.dispatchEvent(new Event('resize'));
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

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var missing = [];
      form.querySelectorAll('[required]').forEach(function (el) {
        if (el.type === 'hidden') return;
        var bad = (el.type === 'checkbox') ? !el.checked : !el.value.trim();
        el.setAttribute('aria-invalid', bad ? 'true' : 'false');
        if (bad) missing.push(el);
      });
      var noSig = !!pad && pad.empty();

      var err = document.getElementById('sign-error');
      if (missing.length || noSig) {
        if (err) {
          err.textContent = (noSig && !missing.length)
            ? 'Draw your signature in the box to sign.'
            : 'Complete every required field and acknowledgment' + (noSig ? ', and draw your signature,' : '') +
              ' before signing. ' + (missing.length + (noSig ? 1 : 0)) + ' remaining.';
          err.hidden = false;
        }
        if (missing.length) missing[0].focus(); else pad.invalid();
        return;
      }
      if (err) err.hidden = true;

      var fields = {};
      new FormData(form).forEach(function (v, k) {
        if (!/^ack_|^signature_drawn$/.test(k) && String(v).trim()) fields[k] = String(v).trim();
      });
      var sig = pad ? pad.data() : { m: 'typed', t: fields.legal_name || '', h: 300, s: '' };
      var signed = {
        agreement: agreement, fields: fields, acks: ackTexts(form), sig: sig,
        signedAt: now.toISOString(), signedAtDisplay: stamp, url: here
      };

      if (submit) { submit.disabled = true; submit.textContent = 'Recording signature'; }

      textVersion().then(function (ver) {
        signed.version = ver;
        return pack({ v: 1, f: fields, a: signed.acks, g: sig, d: signed.signedAt, k: ver });
      }).then(function (packed) {
        /* The same shape every other form posts, so the one workflow can
           create the contact, tag it and email both sides. */
        var record = {};
        new FormData(form).forEach(function (v, k) { record[k] = v; });
        record.agreement = agreement;
        record.signedAt = signed.signedAt;
        record.signedAtDisplay = stamp;
        record.tag = cfg.tag || 'agreement';
        record.signature = fields.legal_name || '';
        record.signature_method = sig.m === 'typed' ? 'typed name adopted' : 'drawn by hand';
        record.signed_copy_url = here + '#signed=' + packed;
        record.agreement_version = signed.version || '';
        var legal = String(fields.legal_name || '').trim().split(/\s+/);
        record.first_name = legal.shift() || '';
        record.last_name = legal.join(' ');
        record.business = fields.business_name || '';
        record.page = window.location.pathname;
        record.submittedAt = signed.signedAt;
        var endpoint = cfg.endpoint || (window.OYSS.endpoint && window.OYSS.endpoint());

        var finished = false;
        function finish() {
          if (finished) return;
          finished = true;
          showSigned(signed, false);
          var done = document.getElementById('signed-state');
          if (done) done.scrollIntoView({ behavior: CALM ? 'auto' : 'smooth', block: 'center' });
          try { window.sessionStorage.setItem('oyss:' + agreement, JSON.stringify(record)); } catch (_) {}
          /* their copy, straight away */
          savePdf(signed, document.getElementById('download-signed'));
          if (typeof cfg.onSigned === 'function') cfg.onSigned(record);
        }

        if (endpoint) {
          fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(record)
          }).then(finish, finish);
        } else {
          setTimeout(finish, 550);
        }
      });
    });
  };

  /* ==========================================================
     THE READINESS ASSESSMENT
     Scores Annette's own twelve questions across her six pillars:
     positioning, visibility, credibility, platform ownership,
     content leverage and authority conversion. Returns one of the
     four levels her GHL quiz uses.
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

  /* ==========================================================
     THE "WHAT WE DO" MENU (feedback 9.0, note 1)
     Opens on hover and on focus with a pointer that can hover,
     on click everywhere, closes on Escape and on an outside
     click. Inside the phone panel it is simply an open list.
     ========================================================== */
  (function () {
    var drop = document.querySelector('.navdrop');
    if (!drop) return;
    var btn = drop.querySelector('.navdrop__btn');
    var set = function (open) {
      drop.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      set(!drop.classList.contains('is-open'));
    });
    var hover = window.matchMedia('(hover: hover) and (min-width: 1041px)');
    drop.addEventListener('mouseenter', function () { if (hover.matches) set(true); });
    drop.addEventListener('mouseleave', function () { if (hover.matches) set(false); });
    document.addEventListener('click', function (e) { if (!drop.contains(e.target)) set(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drop.classList.contains('is-open')) { set(false); btn.focus(); }
    });
    drop.addEventListener('focusout', function (e) {
      if (!drop.contains(e.relatedTarget)) set(false);
    });
  })();

  window.OYSS.assessment = function () {
    var form = document.getElementById('assessment-form');
    if (!form) return;

    /* One question at a time. Falls back to the full form if the
       stepper cannot build itself, so a failure here costs the
       reader nothing. */
    var step = stepper(form);

    /* Feedback 7.0: Annette's own assessment, "Assessment 2.0" in
       her GHL account. Twelve questions, each answer worth 1 to 4 in
       order, so a total runs 12 to 48. Her tiers are entered in GHL as
       0-20, 21-29, 30-39 and 40+, which as POINTS on a 48 point scale
       make a sensible ladder; they are used here as points. (Entered
       as percentages, as they are in her quiz, nobody can score under
       25% and most people land on Visible. That is flagged to her.)

       Every sentence of every result is hers, from the quiz's own
       results page. */
    var LEVELS = [
      { key: 'hidden', name: 'Hidden Expert', min: 12,
        meaning: [
          'Your expertise is stronger than your visibility.',
          'You may be highly experienced, capable, and respected by the people who already know you. However, the broader market cannot yet see the full value of what you bring.',
          'You may depend heavily on referrals, direct outreach, networking, or individual conversations to explain your expertise. This means your authority is working privately rather than publicly.',
          'Your challenge is not a lack of expertise. Your challenge is that your market does not yet have enough opportunities to see, understand, and trust it.'],
        opportunity: [
          'Clarify what you want to be known for and begin placing that message consistently in front of a larger and more relevant audience.',
          'Your next stage of growth will not come from becoming more qualified. It will come from making your existing qualifications more visible.'],
        priorities: ['Clarify your authority message', 'Strengthen your public positioning',
          'Establish consistent visibility', 'Develop stronger credibility assets',
          'Create a clear next step for interested prospects'],
        step: [
          'Begin by defining one clear idea, problem, or transformation that you want people to associate with your name.',
          'Then create a visibility opportunity that allows you to demonstrate that expertise publicly.'],
        route: { label: 'Join a panel as a featured expert first', href: 'panelists.html' } },

      { key: 'emerging', name: 'Emerging Expert', min: 21,
        meaning: [
          'Your authority is beginning to take shape, but it is not yet working as a complete system.',
          'You have started building recognition through content, networking, speaking, collaborations, or professional relationships.',
          'However, your efforts may still feel fragmented, inconsistent, or dependent on continued personal effort.',
          'People may see pieces of your expertise without fully understanding the depth of your experience, the distinction of your perspective, or the value of working with you.'],
        opportunity: [
          'Connect your positioning, visibility, credibility, content, and offers into one deliberate authority strategy.',
          'You may not need to do more. You need your current efforts to work together more effectively.'],
        priorities: ['Strengthen your recognizable authority message', 'Increase strategic visibility',
          'Build more third-party credibility', 'Repurpose your strongest ideas and appearances',
          'Connect every visibility activity to a clear next step'],
        step: [
          'Choose one central authority theme and build your next month of content, collaborations, and visibility around it.',
          'Consistency around one strong message will create more recognition than frequently changing topics.'],
        route: { label: 'Join a panel as a featured expert', href: 'panelists.html' } },

      { key: 'established', name: 'Established Expert', min: 30,
        meaning: [
          'Your expertise and credibility are established, but your visibility may not yet reflect your full potential.',
          'You have a clear foundation, valuable content, and meaningful credibility. People recognize your work, and your visibility is beginning to produce opportunities.',
          'However, you may still rely heavily on platforms created by other people. Your next level will come from owning more of the stage, the audience, and the conversation.',
          'You are ready to move from being invited into authority-building opportunities to creating those opportunities yourself.'],
        opportunity: [
          'Build a platform that positions you as the host, convener, and central voice of an important professional conversation.',
          'Instead of waiting for invitations, create experiences that attract experts, audiences, prospects, and opportunities to you.'],
        priorities: ['Create an authority platform of your own', 'Build strategic expert collaborations',
          'Expand access to relevant audiences', 'Develop a repeatable visibility engine',
          'Turn every appearance into long-term content and credibility'],
        step: [
          'Identify one important conversation your audience needs and determine how you could host, lead, or convene it.',
          'This could become an expert interview series, a virtual panel, a roundtable, a live event, or another signature authority platform.'],
        route: { label: 'Host your own panel: Virtual Panel Events', href: 'experience.html' } },

      { key: 'visible', name: 'Visible Expert', min: 40,
        meaning: [
          'Your authority is no longer hidden.',
          'The right people can see your expertise, understand its value, and recognize you as a trusted voice in your field.',
          'Your positioning, visibility, credibility, content, platform, and conversion strategy are working together. You are increasingly able to attract recognition, opportunities, partnerships, invitations, and qualified prospects rather than constantly chasing them.',
          'You have built visible authority. Now it is time to expand its reach, influence, and commercial value.'],
        opportunity: [
          'Turn your visibility into an owned and scalable authority platform.',
          'Your next level will not come from simply appearing in more places. It will come from creating repeatable platforms that expand your reach, strengthen your professional associations, and position you at the center of valuable conversations.'],
        priorities: ['Expand the platforms you own', 'Host high-value expert conversations',
          'Build recurring authority events', 'Develop strategic partnerships',
          'Convert visibility into long-term brand equity'],
        step: [
          'Create a signature authority platform that can be repeated, expanded, and associated directly with your brand.',
          'The goal is to move beyond individual appearances and build an ecosystem that continues generating credibility, content, relationships, and opportunities.'],
        route: { label: 'See every stage we build', href: 'services.html' } }
    ];

    /* Paragraphs and list items are built as nodes, never as HTML
       strings: nothing here should ever be parsed as markup. */
    function paras(el, list) {
      if (!el) return;
      el.textContent = '';
      list.forEach(function (t) {
        var p = document.createElement('p'); p.textContent = t; el.appendChild(p);
      });
    }
    function items(el, list) {
      if (!el) return;
      el.textContent = '';
      list.forEach(function (t) {
        var li = document.createElement('li'); li.textContent = t; el.appendChild(li);
      });
    }

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

      document.getElementById('result-level').textContent = 'The ' + level.name;
      paras(document.getElementById('result-meaning'), level.meaning);
      paras(document.getElementById('result-opportunity'), level.opportunity);
      items(document.getElementById('result-priorities'), level.priorities);
      paras(document.getElementById('result-step'), level.step);
      var max = qs.length * 4;
      var score = document.getElementById('result-score');
      if (score) score.textContent = total + ' of ' + max;

      /* Feedback 8.0: the score, shown. Her GHL quiz reports a
         percentage of the maximum (39 of 48 is 81.25%), so the ring
         says the same number, rounded, and the points sit under it. */
      var pct = Math.round(total / max * 100);
      var arc = document.getElementById('result-arc');
      var pctEl = document.getElementById('result-pct');
      var pts = document.getElementById('result-points');
      if (pts) pts.textContent = total + ' of ' + max + ' points';
      if (arc) {
        var C = 326.73;
        arc.style.strokeDashoffset = C;
        var target = C * (1 - pct / 100);
        if (CALM) { arc.style.strokeDashoffset = target; if (pctEl) pctEl.textContent = pct; }
        else {
          var t0 = null;
          var tick = function (t) {
            if (t0 === null) t0 = t;
            var k = Math.min(1, (t - t0) / 1400), e = 1 - Math.pow(1 - k, 3);
            arc.style.strokeDashoffset = C - (C - target) * e;
            if (pctEl) pctEl.textContent = Math.round(pct * e);
            if (k < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      } else if (pctEl) pctEl.textContent = pct;

      /* The six pillars, two questions each, scored 2 to 8. The weakest
         pillar is where the Stop Hiding Strategy Call starts, so it says so. */
      var NAMES = ['Positioning', 'Visibility', 'Credibility', 'Platform ownership',
                   'Content leverage', 'Authority conversion'];
      var sums = [0, 0, 0, 0, 0, 0];
      qs.forEach(function (fs) {
        var q = parseInt(fs.getAttribute('data-q'), 10);
        var picked = fs.querySelector('input:checked');
        if (picked && q >= 1 && q <= 12) sums[Math.ceil(q / 2) - 1] += parseInt(picked.value, 10);
      });
      var low = Math.min.apply(null, sums);
      var list = document.getElementById('result-pillars');
      if (list) {
        list.textContent = '';
        sums.forEach(function (v, i) {
          var li = document.createElement('li');
          li.className = 'pillarscore__row' + (v === low && low < 8 ? ' is-low' : '');
          var name = document.createElement('span'); name.className = 'pillarscore__name';
          name.textContent = NAMES[i];
          if (v === low && low < 8) {
            var tag = document.createElement('b'); tag.textContent = 'Start here'; name.appendChild(tag);
          }
          var bar = document.createElement('span'); bar.className = 'pillarscore__bar';
          var fill = document.createElement('span'); fill.className = 'pillarscore__fill';
          fill.style.setProperty('--w', ((v - 2) / 6 * 100) + '%');
          bar.appendChild(fill);
          var val = document.createElement('span'); val.className = 'pillarscore__v';
          val.textContent = v + ' / 8';
          li.appendChild(name); li.appendChild(bar); li.appendChild(val);
          list.appendChild(li);
        });
        requestAnimationFrame(function () { requestAnimationFrame(function () {
          list.classList.add('is-in');
        }); });
      }
      var route = document.getElementById('result-route');
      if (route && level.route) { route.textContent = level.route.label; route.setAttribute('href', level.route.href); }

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
          JSON.stringify({ score: total, of: qs.length * 4, level: level.key }));
      } catch (_) {}

      /* Feedback 10.0: hand the finished result to the keep module
         (email it / download it). */
      var weakest = [];
      sums.forEach(function (v, i) { if (v === low && low < 8) weakest.push(NAMES[i]); });
      window.OYSS.keepResult({
        level: level, total: total, max: max, pct: pct,
        pillars: NAMES.map(function (n, i) { return { name: n, v: sums[i] }; }),
        weakest: weakest
      });
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
          /* two labels: the full one, and a short one for phones, where the
             full label on one line pushed the bar (and the page) wider than
             the screen (28 Sep 2026) */
          '<a class="btn btn--primary" href="' + (cfg.barHref || 'apply.html') + '">' +
            '<span class="prompt__cta-l">' + (cfg.barCta || 'Apply to host') + '</span>' +
            '<span class="prompt__cta-s">' + (cfg.barCtaShort || cfg.barCta || 'Apply to host') + '</span>' +
          '</a>' +
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

    /* ---------- exit intent ----------
       Feedback 14: it captures the lead. Somebody leaving is offered the
       assessment now, or the link by email for later; the email goes to
       the one site workflow tagged exit-intent (contact created, tagged,
       Annette notified, the link sent). Nobody who has already left
       their email is asked again. */
    if (recently('oyss:exit', 7) || store('oyss:lead')) return;

    var assessHref = cfg.exitHref || 'assessment.html';
    var exit = document.createElement('div');
    exit.className = 'exit';
    exit.hidden = true;
    exit.innerHTML =
      '<div class="exit__card" role="dialog" aria-modal="true" aria-labelledby="oyss-exit-t">' +
        '<button class="exit__x" type="button" aria-label="Close">&times;</button>' +
        '<div class="exit__ask">' +
          '<p class="exit__eyebrow">' + (cfg.exitEyebrow || 'Before you go') + '</p>' +
          '<p class="exit__t" id="oyss-exit-t">' + (cfg.exitTitle || 'How visible is your authority today?') + '</p>' +
          '<p class="exit__p">' + (cfg.exitBody || 'Twelve questions across six pillars, about five minutes. Take it now, or leave your email and we will send you the link for later.') + '</p>' +
          '<form class="exit__form" novalidate>' +
            '<label class="exit__field"><span>First name</span><input name="first_name" type="text" autocomplete="given-name"></label>' +
            '<label class="exit__field"><span>Email</span><input name="email" type="email" required autocomplete="email" inputmode="email"></label>' +
            '<button class="btn btn--primary exit__send" type="submit">Email me the link</button>' +
            '<p class="exit__err" role="alert" hidden></p>' +
          '</form>' +
          '<p class="exit__fine">We will email you the link. You can unsubscribe at any time. ' +
            '<a href="' + (cfg.privacyHref || 'privacy.html') + '" target="_blank" rel="noopener">Privacy policy</a></p>' +
          '<div class="exit__actions">' +
            '<a class="exit__now" href="' + assessHref + '">Take it now instead</a>' +
            '<button class="exit__no" type="button">No thanks</button>' +
          '</div>' +
        '</div>' +
        '<div class="exit__done" hidden>' +
          '<p class="exit__eyebrow">Sent</p>' +
          '<p class="exit__t">Check your inbox.</p>' +
          '<p class="exit__p">The link to the Readiness Assessment is on its way to <b class="exit__to"></b>. It takes about five minutes, whenever you are ready.</p>' +
          '<div class="exit__actions">' +
            '<a class="btn btn--primary" href="' + assessHref + '">Take it now</a>' +
            '<button class="exit__no" type="button">Close</button>' +
          '</div>' +
        '</div>' +
      '</div>';
    root.appendChild(exit);

    var exitForm = exit.querySelector('.exit__form');
    var exitErr = exit.querySelector('.exit__err');
    exitForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = exitForm.email.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
        exitErr.textContent = 'Enter a valid email address and we will send the link.';
        exitErr.hidden = false;
        exitForm.email.setAttribute('aria-invalid', 'true');
        exitForm.email.focus();
        return;
      }
      exitErr.hidden = true;
      exitForm.email.setAttribute('aria-invalid', 'false');
      var send = exitForm.querySelector('.exit__send');
      send.disabled = true; send.textContent = 'Sending';
      var first = exitForm.first_name.value.trim();
      var data = {
        tag: 'exit-intent',
        source: 'Exit intent pop-up',
        first_name: first,
        name: first,
        email: email,
        assessment_url: new URL(assessHref, window.location.href).href,
        page: window.location.pathname,
        submittedAt: new Date().toISOString()
      };
      var sent = false;
      function done() {
        if (sent) return;
        sent = true;
        store('oyss:lead', String(Date.now()));
        exit.querySelector('.exit__ask').hidden = true;
        var d = exit.querySelector('.exit__done');
        d.querySelector('.exit__to').textContent = email;
        d.hidden = false;
        var b = d.querySelector('.btn'); if (b) b.focus();
      }
      var endpoint = window.OYSS.endpoint && window.OYSS.endpoint();
      if (endpoint) {
        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        }).then(done, done);
      } else {
        setTimeout(done, 400);
      }
    });

    var lastFocus = null;
    var open = false;

    function typedSomething() {
      var any = false;
      document.querySelectorAll('input, textarea, select').forEach(function (el) {
        if (el.closest('.exit')) return;
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
      var first = exit.querySelector('.exit__form input[name="email"]') || exit.querySelector('.btn');
      if (first) first.focus();
    }

    exit.querySelector('.exit__x').addEventListener('click', closeExit);
    [].forEach.call(exit.querySelectorAll('.exit__no'), function (b) { b.addEventListener('click', closeExit); });
    exit.addEventListener('click', function (e) { if (e.target === exit) closeExit(); });
    document.addEventListener('keydown', function (e) {
      if (!open) return;
      if (e.key === 'Escape') { closeExit(); return; }
      /* Focus stays in the dialog while it is open. */
      if (e.key !== 'Tab') return;
      var f = [].filter.call(exit.querySelectorAll('button, a[href], input'), function (el) {
        return el.offsetParent !== null;
      });
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

      function play(at) {
        block.classList.add('is-playing');
        clip.controls = true;
        /* preload="none": before the first press there is no metadata to
           seek in, so the seek waits for it. play() is what starts the
           fetch, and loadedmetadata lands before the first frame does. */
        if (typeof at === 'number') {
          if (clip.readyState >= 1) { clip.currentTime = at; }
          else {
            clip.addEventListener('loadedmetadata', function () { clip.currentTime = at; }, { once: true });
          }
        }
        var p = clip.play();
        if (p && p.catch) p.catch(function () {});
        clip.focus({ preventScroll: true });
      }
      btn.addEventListener('click', function () { play(); });

      /* Feedback 6.0: the run order. Each cue under the picture is one of
         the film's own chapters and starts it there. The cue that is
         playing carries the marker, so the strip doubles as a progress
         bar in the film's own vocabulary. */
      var section = block.closest('section') || document;
      var cues = [].slice.call(section.querySelectorAll('.filmcue'));
      if (cues.length) {
        cues.forEach(function (cue) {
          cue.addEventListener('click', function () {
            play(parseFloat(cue.getAttribute('data-t')) || 0);
            block.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
          });
        });
        var mark = function () {
          var t = clip.currentTime, live = null;
          cues.forEach(function (cue) {
            if (t >= (parseFloat(cue.getAttribute('data-t')) || 0)) live = cue;
          });
          cues.forEach(function (cue) { cue.classList.toggle('on', cue === live && !clip.paused); });
        };
        clip.addEventListener('timeupdate', mark);
        clip.addEventListener('play', mark);
        clip.addEventListener('pause', mark);
      }

      /* If it is paused back to the very start, the poster is on
         screen again and the control belongs back with it. */
      clip.addEventListener('ended', function () {
        clip.currentTime = 0;
        clip.controls = false;
        block.classList.remove('is-playing');
        cues.forEach(function (cue) { cue.classList.remove('on'); });
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
        /* a radio group carries `required` on its first option only */
        if (el.type === 'radio') return !form.querySelector('input[name="' + el.name + '"]:checked');
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


  /* ==========================================================
     THE ONE ENDPOINT  (feedback 7.0)
     Every form used to carry its own `CONFIG.endpoint = null`, so
     connecting the site to GHL meant finding and editing five
     scripts, and one would always be missed. Now there is one
     switch for the whole site:

       <script>window.OYSS_ENDPOINT = 'https://services.leadconnectorhq.com/hooks/...';</script>

     placed before oyss.js loads. In GHL that is Settings > Tracking
     Code > Header, once for the whole funnel. The value is a GHL
     workflow's Inbound Webhook trigger URL; every form posts JSON to
     it with its own `tag`, so one workflow can branch on the tag.

     Never a private integration token and never the contacts API
     from the browser: anything in page source is public.
     ========================================================== */
  window.OYSS.endpoint = function () { return window.OYSS_ENDPOINT || null; };

  /* A short form: validate the required fields, collect everything,
     record both text message consents as an explicit yes or no, post
     it, and swap the form for its confirmation. */
  window.OYSS.simpleForm = function (formId, doneId, errId, tag) {
    var form = document.getElementById(formId);
    var done = document.getElementById(doneId);
    var err = document.getElementById(errId);
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var missing = [];
      form.querySelectorAll('[required]').forEach(function (el) {
        var bad = (el.type === 'checkbox') ? !el.checked : !String(el.value || '').trim();
        if (!bad && el.type === 'email') bad = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim());
        el.setAttribute('aria-invalid', bad ? 'true' : 'false');
        if (bad) missing.push(el);
      });
      if (missing.length) {
        if (err) {
          err.textContent = missing.length === 1
            ? 'One field still needs an answer.'
            : 'Complete the required fields. ' + missing.length + ' remaining.';
          err.hidden = false;
        }
        missing[0].focus();
        return;
      }
      if (err) err.hidden = true;

      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      ['sms_consent_transactional', 'sms_consent_marketing'].forEach(function (k) {
        var box = form.querySelector('input[name="' + k + '"]');
        if (box) data[k] = box.checked ? 'yes' : 'no';
      });
      data.tag = tag;
      data.page = window.location.pathname;
      data.submittedAt = new Date().toISOString();
      try {
        var a = window.sessionStorage.getItem('oyss:assessment');
        if (a) data.assessment = a;
      } catch (_) {}

      function finish() {
        form.hidden = true;
        if (done) { done.hidden = false; done.scrollIntoView({ block: 'center', behavior: CALM ? 'auto' : 'smooth' }); }
      }
      var url = window.OYSS.endpoint();
      if (url) {
        fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
          .then(finish).catch(finish);
      } else {
        setTimeout(finish, 400);
      }
    });
  };


  /* ==========================================================
     KEEP YOUR RESULT  (feedback 10.0)
     "When you show the result give option to send it to their
     email or download at the same time and don't show calendar,
     just give the button there."

     Email: posts the whole result to the GHL workflow (the same
     one endpoint as every form, tag `assessment-result`). The
     workflow creates or updates the contact and sends the report,
     so the email is built from fields in the payload:
       result_html   the full report as one block of email-safe HTML
       result_text   the same as plain text
       plus every piece on its own (level, score, pillars ...)
     Download: a PDF drawn in the browser with jsPDF (loaded only
     when the button is pressed), so nothing leaves the page.
     ========================================================== */
  var KEEP = null;

  function esc(t) {
    return String(t).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function siteUrl(path) {
    var a = document.createElement('a');
    a.href = path;
    return a.href;
  }
  function bookHref() {
    var b = document.querySelector('#assessment-result a.btn--primary');
    return siteUrl(b ? b.getAttribute('href') : 'contact.html');
  }

  function resultText(r) {
    var L = r.level, out = [];
    out.push('Your Authority Visibility Score: ' + r.pct + '% (' + r.total + ' of ' + r.max + ' points)');
    out.push('You are: The ' + L.name);
    out.push('');
    out.push('YOUR SIX PILLARS');
    r.pillars.forEach(function (p) {
      out.push(p.name + ': ' + p.v + ' / 8' + (r.weakest.indexOf(p.name) > -1 ? '  (start here)' : ''));
    });
    out.push('', 'WHAT THIS MEANS', L.meaning.join('\n\n'));
    out.push('', 'YOUR GREATEST OPPORTUNITY', L.opportunity.join('\n\n'));
    out.push('', 'YOUR PRIORITIES', L.priorities.map(function (p) { return '- ' + p; }).join('\n'));
    out.push('', 'YOUR RECOMMENDED NEXT STEP', L.step.join('\n\n'));
    out.push('', 'Book your complimentary Stop Hiding Strategy Call: ' + bookHref());
    return out.join('\n');
  }

  function resultHtml(r) {
    var L = r.level, RED = '#B91C1C', INK = '#2E2E2E', SL = '#5B5552';
    var h = function (t) {
      return '<p style="margin:28px 0 8px;font:700 12px/1.4 Arial,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:' + RED + '">' + esc(t) + '</p>';
    };
    var p = function (t) { return '<p style="margin:0 0 12px;font:16px/1.6 Georgia,serif;color:' + INK + '">' + esc(t) + '</p>'; };
    var rows = r.pillars.map(function (x) {
      var w = Math.round((x.v - 2) / 6 * 100), low = r.weakest.indexOf(x.name) > -1;
      return '<tr><td style="padding:6px 12px 6px 0;font:15px Arial,sans-serif;color:' + INK + ';white-space:nowrap">' + esc(x.name) +
        (low ? ' <b style="color:' + RED + ';font-size:11px;letter-spacing:.12em;text-transform:uppercase">Start here</b>' : '') +
        '</td><td style="width:100%;padding:6px 12px 6px 0"><div style="background:#F9E9E7;height:10px;border-radius:5px">' +
        '<div style="background:' + RED + ';height:10px;border-radius:5px;width:' + Math.max(w, 3) + '%"></div></div></td>' +
        '<td style="font:700 14px Arial,sans-serif;color:' + INK + ';white-space:nowrap">' + x.v + ' / 8</td></tr>';
    }).join('');
    return '<div style="max-width:600px">' +
      '<p style="margin:0;font:700 12px/1.4 Arial,sans-serif;letter-spacing:.18em;text-transform:uppercase;color:' + SL + '">Authority Visibility Score</p>' +
      '<p style="margin:6px 0 0;font:700 44px/1.1 Arial,sans-serif;color:' + RED + '">' + r.pct + '%</p>' +
      '<p style="margin:4px 0 0;font:700 22px/1.3 Arial,sans-serif;color:' + INK + '">You are the ' + esc(L.name) + '</p>' +
      '<p style="margin:4px 0 0;font:14px Arial,sans-serif;color:' + SL + '">' + r.total + ' of ' + r.max + ' points</p>' +
      h('Your six pillars') + '<table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse">' + rows + '</table>' +
      h('What this means') + L.meaning.map(p).join('') +
      h('Your greatest opportunity') + L.opportunity.map(p).join('') +
      h('Your priorities') + '<ul style="margin:0;padding-left:20px">' + L.priorities.map(function (x) {
        return '<li style="margin:0 0 6px;font:16px/1.5 Georgia,serif;color:' + INK + '">' + esc(x) + '</li>';
      }).join('') + '</ul>' +
      h('Your recommended next step') + L.step.map(p).join('') +
      '<p style="margin:28px 0 0"><a href="' + esc(bookHref()) + '" style="display:inline-block;background:' + RED +
      ';color:#fff;text-decoration:none;font:700 15px Arial,sans-serif;padding:14px 26px;border-radius:2px">Book your Stop Hiding Strategy Call</a></p>' +
      '</div>';
  }

  function sendResult(e) {
    e.preventDefault();
    var form = e.currentTarget, r = KEEP;
    var err = document.getElementById('result-mail-err');
    var done = document.getElementById('result-mail-done');
    var note = document.getElementById('result-mail-note');
    var btn = form.querySelector('button[type="submit"]');
    if (!r) return;
    var fn = form.elements.first_name, em = form.elements.email, bad = [];
    [fn, em].forEach(function (el) {
      var b = !String(el.value || '').trim();
      if (!b && el.type === 'email') b = !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim());
      el.setAttribute('aria-invalid', b ? 'true' : 'false');
      if (b) bad.push(el);
    });
    if (bad.length) {
      err.textContent = bad.length === 2 ? 'Add your first name and email.'
        : (bad[0] === em ? 'That email address does not look complete.' : 'Add your first name.');
      err.hidden = false; bad[0].focus(); return;
    }
    err.hidden = true;
    var url = window.OYSS.endpoint();
    if (!url) {
      err.textContent = 'Email delivery is not switched on yet. Download the PDF for now.';
      err.hidden = false; return;
    }
    var data = {
      tag: 'assessment-result',
      first_name: fn.value.trim(),
      email: em.value.trim(),
      assessment_level: r.level.name,
      assessment_level_key: r.level.key,
      assessment_percent: r.pct,
      assessment_points: r.total + ' of ' + r.max,
      assessment_start_here: r.weakest.join(', '),
      assessment_pillars: r.pillars.map(function (x) { return x.name + ' ' + x.v + '/8'; }).join('; '),
      result_meaning: r.level.meaning.join('\n\n'),
      result_opportunity: r.level.opportunity.join('\n\n'),
      result_priorities: r.level.priorities.join('\n'),
      result_step: r.level.step.join('\n\n'),
      result_text: resultText(r),
      result_html: resultHtml(r),
      booking_url: bookHref(),
      page: window.location.pathname,
      submittedAt: new Date().toISOString()
    };
    btn.disabled = true; btn.textContent = 'Sending...';
    fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (res) {
        if (!res.ok) throw new Error(res.status);
        form.querySelector('.keep__fields').hidden = true;
        btn.hidden = true; note.hidden = true;
        done.innerHTML = 'Sent to <b>' + esc(data.email) + '</b>. It should arrive in a minute or two; check your promotions folder if it does not.';
        done.hidden = false;
      })
      .catch(function () {
        btn.disabled = false; btn.textContent = 'Email my result';
        err.textContent = 'That did not go through. Try again, or download the PDF.';
        err.hidden = false;
      });
  }

  var JSPDF = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
  function loadJsPdf() {
    return new Promise(function (ok, no) {
      if (window.jspdf) return ok(window.jspdf);
      var s = document.createElement('script');
      s.src = JSPDF; s.async = true;
      s.onload = function () { if (window.jspdf) ok(window.jspdf); else no(); };
      s.onerror = no;
      document.head.appendChild(s);
    });
  }

  function drawPdf(lib, r) {
    var doc = new lib.jsPDF({ unit: 'pt', format: 'a4' });
    var W = doc.internal.pageSize.getWidth(), H = doc.internal.pageSize.getHeight();
    var M = 54, y = 0, RED = [185, 28, 28], INK = [46, 46, 46], SL = [91, 85, 82], BL = [249, 233, 231];
    function col(c) { doc.setTextColor(c[0], c[1], c[2]); }
    function need(h) { if (y + h > H - 60) { doc.addPage(); y = M; } }
    function eyebrow(t) {
      need(40); y += 22;
      doc.setFont('helvetica', 'bold'); doc.setFontSize(9); col(RED);
      doc.text(t.toUpperCase(), M, y, { charSpace: 1.4 }); y += 14;
    }
    function para(t, size) {
      doc.setFont('times', 'normal'); doc.setFontSize(size || 11.5); col(INK);
      doc.splitTextToSize(t, W - 2 * M).forEach(function (line) { need(16); doc.text(line, M, y); y += 15.5; });
      y += 5;
    }

    /* Letterhead band */
    doc.setFillColor(31, 30, 29); doc.rect(0, 0, W, 86, 'F');
    doc.setFillColor(RED[0], RED[1], RED[2]); doc.rect(M, 70, 36, 3, 'F');
    doc.setFont('helvetica', 'bold'); doc.setFontSize(15); doc.setTextColor(248, 245, 242);
    doc.text('OWN YOUR STAGE STUDIO', M, 44, { charSpace: 1.2 });
    doc.setFont('helvetica', 'normal'); doc.setFontSize(9); doc.setTextColor(215, 206, 192);
    doc.text('Authority Visibility Score', W - M, 44, { align: 'right' });
    doc.text(new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }), W - M, 58, { align: 'right' });

    /* Score */
    y = 140;
    doc.setFont('helvetica', 'bold'); doc.setFontSize(54); col(RED);
    doc.text(r.pct + '%', M, y);
    doc.setFontSize(20); col(INK);
    doc.text('You are the ' + r.level.name, M + 150, y - 22);
    doc.setFont('helvetica', 'normal'); doc.setFontSize(11); col(SL);
    doc.text(r.total + ' of ' + r.max + ' points, from twelve answers', M + 150, y - 4);

    /* Ladder */
    y += 26;
    var names = ['Hidden', 'Emerging', 'Established', 'Visible'], cw = (W - 2 * M - 12) / 4;
    var reached = ['hidden', 'emerging', 'established', 'visible'].indexOf(r.level.key);
    names.forEach(function (n, i) {
      var x = M + i * (cw + 4);
      if (i <= reached) doc.setFillColor(RED[0], RED[1], RED[2]); else doc.setFillColor(BL[0], BL[1], BL[2]);
      doc.rect(x, y, cw, 30, 'F');
      doc.setFont('helvetica', 'bold'); doc.setFontSize(9);
      if (i <= reached) doc.setTextColor(255, 255, 255); else col(SL);
      doc.text(n.toUpperCase(), x + 8, y + 19);
      if (i === reached) { doc.setFontSize(7); doc.text('YOU ARE HERE', x + cw - 8, y + 19, { align: 'right' }); }
    });
    y += 40;

    /* Pillars */
    eyebrow('Your six pillars');
    r.pillars.forEach(function (p) {
      need(20);
      var low = r.weakest.indexOf(p.name) > -1, bx = M + 150, bw = W - 2 * M - 150 - 44;
      doc.setFont('helvetica', low ? 'bold' : 'normal'); doc.setFontSize(10.5); col(INK);
      doc.text(p.name + (low ? '  (start here)' : ''), M, y + 8);
      doc.setFillColor(BL[0], BL[1], BL[2]); doc.rect(bx, y, bw, 9, 'F');
      doc.setFillColor(RED[0], RED[1], RED[2]); doc.rect(bx, y, Math.max(bw * (p.v - 2) / 6, 4), 9, 'F');
      doc.setFont('helvetica', 'bold'); col(INK);
      doc.text(p.v + ' / 8', W - M, y + 8, { align: 'right' });
      y += 19;
    });

    eyebrow('What this means');
    r.level.meaning.forEach(function (t) { para(t); });
    eyebrow('Your greatest opportunity');
    r.level.opportunity.forEach(function (t) { para(t); });
    eyebrow('Your priorities');
    r.level.priorities.forEach(function (t) { para('•  ' + t); y -= 5; });
    y += 5;
    eyebrow('Your recommended next step');
    r.level.step.forEach(function (t) { para(t); });

    /* Next step */
    need(70); y += 12;
    doc.setFillColor(BL[0], BL[1], BL[2]); doc.rect(M, y, W - 2 * M, 56, 'F');
    doc.setFont('helvetica', 'bold'); doc.setFontSize(12); col(INK);
    doc.text('Book your complimentary Stop Hiding Strategy Call', M + 16, y + 23);
    doc.setFont('helvetica', 'normal'); doc.setFontSize(10); col(RED);
    var link = bookHref();
    doc.textWithLink(link, M + 16, y + 40, { url: link });

    var pages = doc.getNumberOfPages();
    for (var i = 1; i <= pages; i++) {
      doc.setPage(i);
      doc.setFont('helvetica', 'normal'); doc.setFontSize(8); col(SL);
      doc.text('ownyourstagestudio.com', M, H - 30);
      doc.text(i + ' / ' + pages, W - M, H - 30, { align: 'right' });
    }
    doc.save('Authority-Visibility-Score-' + r.level.name.replace(/\s+/g, '-') + '.pdf');
  }

  function downloadResult() {
    var btn = document.getElementById('result-pdf'), note = document.getElementById('result-pdf-note');
    if (!KEEP) return;
    btn.disabled = true; btn.textContent = 'Preparing...';
    loadJsPdf().then(function (lib) {
      drawPdf(lib, KEEP);
      btn.disabled = false; btn.textContent = 'Download again';
      note.textContent = 'Saved to your downloads.'; note.hidden = false;
    }).catch(function () {
      btn.disabled = false; btn.textContent = 'Download PDF';
      note.textContent = 'The download could not start. Use your browser’s Print, then Save as PDF.';
      note.hidden = false;
    });
  }

  window.OYSS.keepResult = function (r) {
    var first = !KEEP;
    KEEP = r;
    if (!first) return;
    var mail = document.getElementById('result-mail');
    var pdf = document.getElementById('result-pdf');
    if (mail) mail.addEventListener('submit', sendResult);
    if (pdf) pdf.addEventListener('click', downloadResult);
  };


})();
