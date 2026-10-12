// Animazioni del sito con anime.js (javascripts/vendor/anime.min.js).
// Per restare fluide animano solo transform e opacity (niente width/top/left, che
// ricalcolano il layout) e usano easing a molla. Disattivate se il sistema operativo
// chiede movimento ridotto.
(function () {
  if (!window.anime) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var SPRING = "spring(1, 180, 18, 0)";        // morbida, senza rimbalzo evidente
  var SPRING_SOFT = "spring(1, 120, 16, 0)";   // più lenta, per elementi grandi

  function hint(el, props) { el.style.willChange = props; }
  function done(el) { el.style.willChange = ""; }

  window.Anim = {
    // finestra della ricerca: sfondo in dissolvenza, riquadro che scende e si posa
    openModal: function (modal) {
      if (reduce) return;
      var bg = modal.querySelector(".sm-backdrop"), shell = modal.querySelector(".sm-shell");
      anime.remove([bg, shell]);
      hint(shell, "transform, opacity");
      anime({ targets: bg, opacity: [0, 1], duration: 260, easing: "easeOutQuad" });
      anime({ targets: shell, opacity: [0, 1], translateY: [-24, 0], scale: [.96, 1], easing: SPRING,
              complete: function () { done(shell); } });
    },
    closeModal: function (modal, cb) {
      if (reduce) return cb();
      var bg = modal.querySelector(".sm-backdrop"), shell = modal.querySelector(".sm-shell");
      anime.remove([bg, shell]);
      anime({ targets: bg, opacity: 0, duration: 180, easing: "easeInQuad" });
      anime({ targets: shell, opacity: 0, translateY: -10, scale: .98, duration: 180, easing: "easeInQuad", complete: cb });
    },
    // risultati della ricerca che scivolano dentro uno dopo l'altro
    results: function (items) {
      if (reduce || !items.length) return;
      anime.remove(items);
      anime({ targets: items, opacity: [0, 1], translateY: [10, 0], easing: SPRING,
              delay: anime.stagger(22, { start: 20 }) });
    },
    // barra di avanzamento: si anima la scala orizzontale, non la larghezza
    progress: function (fill, pct) {
      var to = pct / 100;
      fill.style.width = "100%";
      fill.style.transformOrigin = "left center";
      if (reduce) { fill.style.transform = "scaleX(" + to + ")"; return; }
      anime.remove(fill);
      anime({ targets: fill, scaleX: to, easing: SPRING_SOFT });
    },
    // interruttore chiaro/scuro: il pallino scorre
    toggle: function (knob, on) {
      if (reduce) { anime.set(knob, { translateX: on ? 21 : 0, rotate: on ? 180 : 0 }); return; }
      anime.remove(knob);
      anime({ targets: knob, translateX: on ? 21 : 0, rotate: on ? 180 : 0, easing: SPRING });
    }
  };

  // pulsanti: si abbassano alla pressione e tornano su con una molla al rilascio
  function pressable(el) {
    if (el.dataset.animPress) return;
    el.dataset.animPress = "1";
    el.addEventListener("pointerdown", function () {
      anime.remove(el);
      anime({ targets: el, scale: .94, duration: 120, easing: "easeOutQuad" });
    });
    ["pointerup", "pointerleave", "pointercancel"].forEach(function (ev) {
      el.addEventListener(ev, function () {
        anime.remove(el);
        anime({ targets: el, scale: 1, easing: "spring(1, 260, 12, 0)" });
      });
    });
  }

  function init() {
    if (!reduce) document.querySelectorAll(".sm-button, .checklist-reset, .md-clipboard, .md-button, .md-header__option > .md-header__button, .md-header__source, .md-nav__link, .md-footer__link")
      .forEach(pressable);
    // passi spuntati: la casella fa un piccolo "pop"
    if (!reduce) document.querySelectorAll(".md-content .task-list-control").forEach(function (el) {
      if (el.dataset.animPop) return;
      el.dataset.animPop = "1";
      el.addEventListener("change", function () {
        anime.remove(el);
        anime({ targets: el, scale: [.7, 1], easing: "spring(1, 300, 10, 0)" });
      });
    });
    // home: prima il titolo, poi card, voci e loghi, uno dopo l'altro
    var hero = document.querySelectorAll(".hero > *");
    if (hero.length && !reduce) {
      anime({ targets: hero, opacity: [0, 1], translateY: [12, 0], easing: SPRING_SOFT, delay: anime.stagger(70) });
    }
    var cards = document.querySelectorAll(".card-grid > .card, .feature-grid > .feature, .logo-row > span");
    if (cards.length && !reduce) {
      anime({ targets: cards, opacity: [0, 1], translateY: [16, 0], easing: SPRING_SOFT,
              delay: anime.stagger(60, { start: 180 }) });
    }
    // card cliccabili: si sollevano appena al passaggio del mouse
    if (!reduce) document.querySelectorAll(".card--link").forEach(function (el) {
      if (el.dataset.animLift) return;
      el.dataset.animLift = "1";
      el.addEventListener("pointerenter", function () { anime.remove(el); anime({ targets: el, translateY: -3, easing: SPRING }); });
      el.addEventListener("pointerleave", function () { anime.remove(el); anime({ targets: el, translateY: 0, easing: SPRING }); });
    });
    // contenuto della pagina: dissolvenza leggera all'apertura
    var inner = document.querySelector(".md-content__inner");
    if (inner && !hero.length && !reduce) anime({ targets: inner, opacity: [0, 1], translateY: [6, 0], easing: SPRING_SOFT });
    // menu: la freccia di una sezione ruota quando la si apre o chiude; a fine corsa lo
    // stile in linea viene tolto e torna a valere la posizione data dal CSS
    document.querySelectorAll(".md-nav--primary .md-nav__toggle").forEach(function (toggle) {
      if (toggle.dataset.animArrow || toggle.id === "__drawer" || toggle.id === "__toc") return;
      toggle.dataset.animArrow = "1";
      toggle.addEventListener("change", function () {
        var icon = toggle.parentElement.querySelector(":scope > .md-nav__link .md-nav__icon");
        if (!icon || reduce) return;
        anime.remove(icon);
        anime({ targets: icon, rotate: toggle.checked ? [0, 90] : [90, 0], easing: SPRING,
                complete: function () { icon.style.transform = ""; } });
      });
    });
    // interruttore chiaro/scuro: il pallino si posiziona sul tema attuale e scorre al cambio
    var dark = function () { return document.body.getAttribute("data-md-color-scheme") === "slate"; };
    var knobs = document.querySelectorAll(".md-header__option > .md-header__button svg");
    anime.set(knobs, { translateX: dark() ? 21 : 0, rotate: dark() ? 180 : 0 });
    document.querySelectorAll("input[name='__palette']").forEach(function (input) {
      if (input.dataset.animToggle) return;
      input.dataset.animToggle = "1";
      input.addEventListener("change", function () {
        // il tema cambia subito dopo l'evento: si parte dalla posizione opposta
        setTimeout(function () {
          var on = dark();
          var visible = document.querySelectorAll(".md-header__option > .md-header__button svg");
          anime.set(visible, { translateX: on ? 0 : 21, rotate: on ? 0 : 180 });
          visible.forEach(function (k) { window.Anim.toggle(k, on); });
        }, 0);
      });
    });
  }
  if (window.document$) document$.subscribe(init); else document.addEventListener("DOMContentLoaded", init);
})();
