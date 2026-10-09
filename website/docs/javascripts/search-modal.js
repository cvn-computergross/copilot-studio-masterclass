// Ricerca in stile Agent Academy: pulsante "Cerca  Ctrl K" sopra la barra di avanzamento
// (colonna di destra) e finestra centrata con risultati per pagina e sezione.
// Usa l'indice generato dal plugin "search" di MkDocs (search/search_index.json).
(function () {
  var index = null, modal, input, list, items = [], selected = 0;
  var base = document.querySelector("script[src*='javascripts/search-modal.js']").src.replace(/javascripts\/search-modal\.js.*$/, "");

  function load() {
    if (index) return Promise.resolve(index);
    return fetch(base + "search/search_index.json").then(function (r) { return r.json(); }).then(function (data) {
      // titolo della pagina per ogni sezione (location senza "#")
      var pages = {};
      data.docs.forEach(function (d) { if (d.location.indexOf("#") < 0) pages[d.location] = d.title; });
      index = data.docs.map(function (d) {
        var page = pages[d.location.split("#")[0]] || d.title;
        var text = d.text.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
        return { location: d.location, title: d.title, page: page, text: text,
                 hay: (d.title + " " + text).toLowerCase() };
      });
      return index;
    });
  }

  function escape(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function mark(s, terms) {
    var out = escape(s);
    terms.forEach(function (t) { out = out.replace(new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi"), "<mark>$1</mark>"); });
    return out;
  }
  function excerpt(text, term) {
    var i = text.toLowerCase().indexOf(term);
    if (i < 0) return text.slice(0, 140);
    var start = Math.max(0, i - 50);
    return (start ? "…" : "") + text.slice(start, start + 160) + (start + 160 < text.length ? "…" : "");
  }

  function search(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) return [];
    return index.map(function (d) {
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        if (d.hay.indexOf(terms[i]) < 0) return null;            // tutte le parole devono comparire
        if (d.title.toLowerCase().indexOf(terms[i]) >= 0) score += 10;
        score += d.hay.split(terms[i]).length - 1;
      }
      return { d: d, score: score, terms: terms };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 30);
  }

  function render() {
    var q = input.value.trim();
    if (!q) { list.innerHTML = ""; items = []; return; }
    load().then(function () {
      var res = search(q);
      if (!res.length) { list.innerHTML = '<div class="sm-empty">Nessun risultato per “' + escape(q) + '”</div>'; items = []; return; }
      list.innerHTML = res.map(function (r) {
        var path = r.d.title === r.d.page ? escape(r.d.page) : escape(r.d.page) + ' <span class="sm-sep">›</span> ' + mark(r.d.title, r.terms);
        return '<a class="sm-item" href="' + base + r.d.location + '"><div class="sm-path">' + path + '</div>' +
               '<div class="sm-text">' + mark(excerpt(r.d.text, r.terms[0]), r.terms) + "</div></a>";
      }).join("");
      items = [].slice.call(list.querySelectorAll(".sm-item"));
      select(0);
      if (window.Anim) window.Anim.results(items);
    });
  }
  function select(i) {
    if (!items.length) return;
    selected = (i + items.length) % items.length;
    items.forEach(function (el, j) { el.classList.toggle("sm-item--active", j === selected); });
    items[selected].scrollIntoView({ block: "nearest" });
  }

  function build() {
    modal = document.createElement("div");
    modal.className = "sm-modal";
    modal.innerHTML =
      '<div class="sm-backdrop"></div>' +
      '<div class="sm-shell" role="dialog" aria-label="Cerca">' +
        '<div class="sm-bar"><svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M9.5 3A6.5 6.5 0 0 1 16 9.5c0 1.61-.59 3.09-1.56 4.23l.27.27h.79l5 5-1.5 1.5-5-5v-.79l-.27-.27A6.52 6.52 0 0 1 9.5 16 6.5 6.5 0 0 1 3 9.5 6.5 6.5 0 0 1 9.5 3m0 2C7 5 5 7 5 9.5S7 14 9.5 14 14 12 14 9.5 12 5 9.5 5Z"/></svg>' +
          '<input type="search" placeholder="Cerca nei lab" autocomplete="off" spellcheck="false">' +
          '<button type="button" class="sm-clear" aria-label="Cancella">✕</button></div>' +
        '<div class="sm-results"></div>' +
        '<div class="sm-footer"><span><kbd>↑</kbd><kbd>↓</kbd> per navigare</span><span><kbd>↵</kbd> per aprire</span><span><kbd>esc</kbd> per chiudere</span></div>' +
      "</div>";
    document.body.appendChild(modal);
    input = modal.querySelector("input");
    list = modal.querySelector(".sm-results");
    modal.querySelector(".sm-backdrop").addEventListener("click", close);
    modal.querySelector(".sm-clear").addEventListener("click", function () { input.value = ""; render(); input.focus(); });
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); select(selected + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); select(selected - 1); }
      else if (e.key === "Enter" && items[selected]) { e.preventDefault(); items[selected].click(); }
    });
  }
  function open() {
    if (!modal) build();
    if (modal.classList.contains("sm-modal--open")) return;
    modal.classList.add("sm-modal--open");
    document.documentElement.style.overflow = "hidden";
    if (window.Anim) window.Anim.openModal(modal);
    load();
    setTimeout(function () { input.focus(); input.select(); }, 0);
  }
  function close() {
    if (!modal || !modal.classList.contains("sm-modal--open")) return;
    var hide = function () {
      modal.classList.remove("sm-modal--open");
      document.documentElement.style.overflow = "";
    };
    if (window.Anim) window.Anim.closeModal(modal, hide); else hide();
  }

  // pulsante nella colonna di destra, sopra la barra di avanzamento
  function placeButton() {
    var side = document.querySelector(".md-sidebar--secondary .md-sidebar__inner");
    if (!side || side.querySelector(".sm-button")) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sm-button";
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14"><path fill="currentColor" d="M9.5 3A6.5 6.5 0 0 1 16 9.5c0 1.61-.59 3.09-1.56 4.23l.27.27h.79l5 5-1.5 1.5-5-5v-.79l-.27-.27A6.52 6.52 0 0 1 9.5 16 6.5 6.5 0 0 1 3 9.5 6.5 6.5 0 0 1 9.5 3m0 2C7 5 5 7 5 9.5S7 14 9.5 14 14 12 14 9.5 12 5 9.5 5Z"/></svg>' +
                    '<span>Cerca</span><kbd>Ctrl K</kbd>';
    btn.addEventListener("click", open);
    side.insertAdjacentElement("afterbegin", btn);
    // schermi stretti (colonna di destra nascosta): stesso pulsante sotto il titolo
    var top = btn.cloneNode(true);
    top.classList.add("sm-button--top");
    top.addEventListener("click", open);
    var anchor = document.querySelector(".md-content .checklist-progress--top") || document.querySelector(".md-content h1");
    if (anchor) anchor.insertAdjacentElement("beforebegin", top);
  }

  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); open(); }
    else if (e.key === "Escape") close();
  });
  function init() { close(); placeButton(); }
  if (window.document$) document$.subscribe(init); else document.addEventListener("DOMContentLoaded", init);
})();
