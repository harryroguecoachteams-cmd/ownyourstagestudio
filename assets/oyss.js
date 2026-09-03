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
       is read from the thing it is lighting: the optical centre
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
           its true weight sits left of the box centre. */
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
       15. THE REEL
       The home hero is footage now, not a CSS lamp, so it needs
       the three things a background video always needs and
       usually does not get.

       1. It must stop when it is not on screen. A looping video
          scrolled past is a decoded frame every 42ms for a
          picture nobody is looking at, and on a laptop that is
          the fan coming on while someone reads the pricing.
       2. It must dim out rather than be cut off. The section
          under it is the same ink, so as the hero leaves the
          doorway fades and pushes in fractionally and the join
          is invisible.
       3. It must not fire at all on a metered connection. The
          poster carries the same frame, so a reader on Save-Data
          loses the motion and nothing else.

       Autoplay can still be refused (low power mode is the usual
       reason). The catch is not decoration: without it the
       promise rejects, the poster stays, and that is already the
       correct outcome.
       -------------------------------------------------------- */
    var reel = document.querySelector('.reel');
    var clip = reel && reel.querySelector('video');

    if (clip) {
      var conn = navigator.connection || {};
      var metered = conn.saveData === true || /^(slow-)?2g$/.test(conn.effectiveType || '');

      if (CALM || metered) {
        clip.removeAttribute('autoplay');
        clip.pause();
        /* Leave the poster showing. The CSS already swaps to the
           still under prefers-reduced-motion; this covers the
           metered case, where the still is not in the cascade. */
        clip.style.display = 'none';
        var still = reel.querySelector('.reel__still');
        if (still) still.style.display = 'block';
      } else {
        var play = clip.play();
        if (play && play.catch) play.catch(function () {});

        if ('IntersectionObserver' in window) {
          new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
              if (e.isIntersecting) {
                var p = clip.play();
                if (p && p.catch) p.catch(function () {});
              } else {
                clip.pause();
              }
            });
          }, { threshold: 0.01 }).observe(reel);
        }

        /* The exit. One rAF-coalesced read, two custom properties
           written, no layout touched. */
        var pending = false;
        var dim = function () {
          pending = false;
          var h = reel.offsetHeight || 1;
          var travelled = Math.min(Math.max(-reel.getBoundingClientRect().top / h, 0), 1);
          reel.style.setProperty('--reel-o', (1 - travelled * 0.85).toFixed(3));
          reel.style.setProperty('--reel-s', (1 + travelled * 0.07).toFixed(3));
        };
        var onExit = function () {
          if (pending) return;
          pending = true;
          window.requestAnimationFrame(dim);
        };
        window.addEventListener('scroll', onExit, { passive: true });
        window.addEventListener('resize', onExit, { passive: true });
        dim();
      }
    }

    /* --------------------------------------------------------
       16. THE BAND
       The rails are pure CSS, but a rail that runs while the
       page is scrolled past it is work the compositor is doing
       for nobody. Same contract as the reel: on screen, running.
       -------------------------------------------------------- */
    var rails = document.querySelector('.rails');
    if (rails && !CALM && 'IntersectionObserver' in window) {
      /* A class, not an inline animation-play-state. Inline style
         would outrank the :hover rule that lets a reader stop a
         rail to actually read it. */
      new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          rails.classList.toggle('rails--off', !e.isIntersecting);
        });
      }, { threshold: 0 }).observe(rails);
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

      /* Light the ladder up to the level reached.
         Not with opacity: the cells are near-black and the result now sits
         on a white sheet, so a faded cell went pale grey and read as the
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

})();
