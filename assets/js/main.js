/* Restaurace a penzion U Slunce, interakce webu */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------- Hlavička */
  var header = document.querySelector('.header');
  var darkHero = document.querySelector('.hero');
  var progress = document.querySelector('.progress');
  var fab = document.querySelector('.call-fab');
  var ticking = false;

  function onScroll() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () {
      var y = window.scrollY;

      if (header) {
        var solid = y > 24;
        header.classList.toggle('is-solid', solid);
        /* svetle pismo jen dokud je hlavicka pruhledna, jinak bylo bile na bilem */
        if (darkHero) header.classList.toggle('is-over-dark', !solid);
      }
      if (fab) fab.classList.toggle('is-shown', y > window.innerHeight * 0.6);

      if (progress) {
        var max = document.documentElement.scrollHeight - window.innerHeight;
        progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(y / max, 1) : 0) + ')';
      }
      ticking = false;
    });
  }
  if (darkHero && header) header.classList.add('is-over-dark');
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
  function reveal(selector, options) {
    var els = document.querySelectorAll(selector);
    if (!els.length) return null;
    if (reduced || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-visible'); });
      return null;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-visible');
        io.unobserve(e.target);
      });
    }, options);
    els.forEach(function (el) { io.observe(el); });
    return io;
  }

  reveal('[data-reveal-img], .line-mask', { rootMargin: '0px 0px -6% 0px', threshold: 0.15 });

  document.querySelectorAll('[data-reveal-group] [data-reveal]').forEach(function (el) {
    var kids = Array.prototype.slice.call(
      el.closest('[data-reveal-group]').querySelectorAll('[data-reveal]'));
    el.style.setProperty('--d', Math.min(kids.indexOf(el), 5) * 90 + 'ms');
  });
  reveal('[data-reveal]', { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

  /* ---------------------------------------------------- Záložky */
  document.querySelectorAll('[data-tabs]').forEach(function (group) {
    var tabs = group.querySelectorAll('[role="tab"]');

    function select(active, focus) {
      tabs.forEach(function (t, i) {
        var on = i === active;
        t.setAttribute('aria-selected', String(on));
        t.setAttribute('tabindex', on ? '0' : '-1');
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
      if (focus && tabs[active]) tabs[active].focus();
    }

    tabs.forEach(function (tab, idx) {
      tab.addEventListener('click', function () { select(idx); });
      tab.addEventListener('keydown', function (e) {
        var dir = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!dir) return;
        e.preventDefault();
        select((idx + dir + tabs.length) % tabs.length, true);
      });
    });

    /* proklik z patičky a z úvodní stránky rovnou na nápoje */
    function fromHash() {
      var i = -1;
      tabs.forEach(function (t, idx) {
        if ('#' + t.dataset.hash === location.hash) i = idx;
      });
      if (i > -1) {
        select(i);
        group.scrollIntoView({ block: 'start', behavior: reduced ? 'auto' : 'smooth' });
      }
    }
    fromHash();
    window.addEventListener('hashchange', fromHash);
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
    var row = hoursList.querySelector(
      day === 5 || day === 6 ? '[data-days="fri-sat"]' : '[data-days="sun-thu"]');
    if (row) row.classList.add('is-now');
  }

  /* --------------------------------- Dnešní doba v liště pod hero */
  var openBox = document.querySelector('[data-open]');
  if (openBox) {
    var now = new Date();
    var wd = now.getDay();
    var closes = (wd === 5 || wd === 6) ? 23 : 22;   // pátek a sobota do 23
    var mins = now.getHours() * 60 + now.getMinutes();
    var isOpen = mins >= 10 * 60 && mins < closes * 60;
    var text = openBox.querySelector('[data-open-text]');
    var dot = openBox.querySelector('.hero__dot');
    var label = openBox.querySelector('b');

    if (text) text.textContent = isOpen
      ? 'otevřeno do ' + closes + '.00'
      : 'otevíráme v 10.00';
    if (label) label.textContent = isOpen ? 'Dnes' : 'Zavřeno';
    if (dot && !isOpen) dot.classList.add('is-shut');
  }
})();
