/* Restaurace a penzion U Slunce, interakce webu */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------- Hlavička */
  var header = document.querySelector('.header');
  var hasDarkHero = !!document.querySelector('.page-hero, .hero');

  var progress = document.querySelector('.progress');
  var fab = document.querySelector('.call-fab');
  var band = document.querySelector('.band__bg');
  var ticking = false;

  function onScroll() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () {
      var y = window.scrollY;

      if (header) {
        header.classList.toggle('is-solid', y > 24);
        if (hasDarkHero) header.classList.toggle('is-over-dark', y <= 90);
      }

      if (fab) fab.classList.toggle('is-shown', y > window.innerHeight * 0.6);

      if (progress) {
        var max = document.documentElement.scrollHeight - window.innerHeight;
        progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(y / max, 1) : 0) + ')';
      }

      if (band && !reduced) {
        var r = band.parentElement.getBoundingClientRect();
        if (r.bottom > 0 && r.top < window.innerHeight) {
          var p = (r.top + r.height / 2 - window.innerHeight / 2) / window.innerHeight;
          band.style.transform = 'translate3d(0,' + (p * 9).toFixed(2) + '%,0)';
        }
      }
      ticking = false;
    });
  }
  if (hasDarkHero && header) header.classList.add('is-over-dark');
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ------------------------------------------------ Mobilní menu */
  var burger = document.querySelector('.burger');
  var mnav = document.querySelector('.mobile-nav');

  function closeMenu() {
    if (!burger || !mnav) return;
    burger.setAttribute('aria-expanded', 'false');
    mnav.classList.remove('is-open');
    document.body.classList.remove('is-locked');
  }

  if (burger && mnav) {
    burger.addEventListener('click', function () {
      var open = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', String(!open));
      mnav.classList.toggle('is-open', !open);
      document.body.classList.toggle('is-locked', !open);
    });
    mnav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeMenu);
    });
  }

  /* --------------------------------------- Odhalování při scrollu */
  var imgReveals = document.querySelectorAll('[data-reveal-img], .line-mask');
  if (imgReveals.length) {
    if (reduced || !('IntersectionObserver' in window)) {
      imgReveals.forEach(function (el) { el.classList.add('is-visible'); });
    } else {
      var ioImg = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('is-visible');
          ioImg.unobserve(e.target);
        });
      }, { rootMargin: '0px 0px -6% 0px', threshold: 0.15 });
      imgReveals.forEach(function (el) { ioImg.observe(el); });
    }
  }

  var revealables = document.querySelectorAll('[data-reveal]');
  if (revealables.length) {
    if (reduced || !('IntersectionObserver' in window)) {
      revealables.forEach(function (el) { el.classList.add('is-visible'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

      revealables.forEach(function (el, i) {
        var group = el.closest('[data-reveal-group]');
        if (group) {
          var kids = Array.prototype.slice.call(group.querySelectorAll('[data-reveal]'));
          el.style.setProperty('--d', Math.min(kids.indexOf(el), 5) * 90 + 'ms');
        }
        io.observe(el);
      });
    }
  }

  /* ---------------------------------------------------- Záložky */
  document.querySelectorAll('[data-tabs]').forEach(function (group) {
    var tabs = group.querySelectorAll('[role="tab"]');
    tabs.forEach(function (tab, idx) {
      tab.addEventListener('click', function () { select(idx); });
      tab.addEventListener('keydown', function (e) {
        var dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!dir) return;
        e.preventDefault();
        var next = (idx + dir + tabs.length) % tabs.length;
        select(next);
        tabs[next].focus();
      });
    });

    if (location.hash === '#napoje' && tabs.length > 1) {
      window.setTimeout(function () { select(1); }, 0);
    }

    function select(active) {
      tabs.forEach(function (t, i) {
        var on = i === active;
        t.setAttribute('aria-selected', String(on));
        t.setAttribute('tabindex', on ? '0' : '-1');
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
    }
  });

  /* ------------------------------------------ Přepínač sezóny */
  var seasonSwitch = document.querySelector('[data-season]');
  if (seasonSwitch) {
    var rooms = document.querySelectorAll('[data-price-main]');
    seasonSwitch.querySelectorAll('button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var season = btn.dataset.value;
        seasonSwitch.querySelectorAll('button').forEach(function (b) {
          b.setAttribute('aria-selected', String(b === btn));
        });
        rooms.forEach(function (room) {
          var out = room.querySelector('.room__amount');
          var value = season === 'off' ? room.dataset.priceOff : room.dataset.priceMain;
          if (!out || out.textContent === value) return;
          room.classList.add('is-swapping');
          window.setTimeout(function () {
            out.textContent = value;
            room.classList.remove('is-swapping');
          }, reduced ? 0 : 200);
        });
      });
    });
  }

  /* ---------------------------------------------- Filtr galerie */
  var filterBar = document.querySelector('[data-filter]');
  if (filterBar) {
    var items = document.querySelectorAll('[data-cat]');
    filterBar.querySelectorAll('button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var cat = btn.dataset.value;
        filterBar.querySelectorAll('button').forEach(function (b) {
          b.setAttribute('aria-pressed', String(b === btn));
        });
        items.forEach(function (it) {
          it.hidden = !(cat === 'all' || it.dataset.cat === cat);
        });
        if (window.buildList) window.buildList();
      });
    });
  }

  /* ------------------------------------------------ Světelný rám */
  var lb = document.querySelector('.lightbox');
  if (lb) {
    var lbImg = lb.querySelector('img');
    var lbCap = lb.querySelector('.lightbox__caption span');
    var lbCount = lb.querySelector('.lightbox__count');
    var list = [];
    var current = 0;
    var lastFocus = null;

    function buildList() {
      list = Array.prototype.slice
        .call(document.querySelectorAll('[data-lightbox]'))
        .filter(function (el) { return !el.hidden; });
    }
    window.buildList = buildList;
    buildList();

    function show(i) {
      if (!list.length) return;
      current = (i + list.length) % list.length;
      var el = list[current];
      var img = el.querySelector('img');
      lbImg.src = el.dataset.full || img.src;
      lbImg.alt = img.alt;
      if (lbCap) lbCap.textContent = img.alt;
      if (lbCount) lbCount.textContent = (current + 1) + ' z ' + list.length;
    }

    function open(i) {
      lastFocus = document.activeElement;
      buildList();
      show(i);
      lb.classList.add('is-open');
      document.body.classList.add('is-locked');
      lb.querySelector('.lightbox__close').focus();
    }

    function close() {
      lb.classList.remove('is-open');
      document.body.classList.remove('is-locked');
      if (lastFocus) lastFocus.focus();
    }

    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('[data-lightbox]');
      if (!trigger) return;
      e.preventDefault();
      buildList();
      open(list.indexOf(trigger));
    });

    document.querySelectorAll('[data-lightbox]').forEach(function (el) {
      el.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        e.preventDefault();
        buildList();
        open(list.indexOf(el));
      });
    });

    lb.querySelector('.lightbox__close').addEventListener('click', close);
    lb.querySelector('.lightbox__prev').addEventListener('click', function () { show(current - 1); });
    lb.querySelector('.lightbox__next').addEventListener('click', function () { show(current + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });

    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(current - 1);
      if (e.key === 'ArrowRight') show(current + 1);
    });
  }

  /* ------------------------------- Zvýraznění dnešní otevírací doby */
  var hoursList = document.querySelector('[data-hours]');
  if (hoursList) {
    var day = new Date().getDay(); // 0 neděle
    var isWeekendEve = day === 5 || day === 6;
    var row = hoursList.querySelector(isWeekendEve ? '[data-days="fri-sat"]' : '[data-days="sun-thu"]');
    if (row) row.classList.add('is-now');
  }
})();
