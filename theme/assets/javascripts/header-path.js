// Header: "Copilot Studio Masterclass · Standard Harness · Lab 05", sempre visibile
// anche scorrendo la pagina. Sezione e lab vengono letti dalla voce attiva del menu.
(function () {
  function init() {
    var topic = document.querySelector(".md-header__title .md-header__topic .md-ellipsis");
    if (!topic) return;
    var site = topic.dataset.site || (topic.dataset.site = topic.textContent.trim());
    var parts = [site];
    var active = document.querySelectorAll(".md-nav--primary .md-nav__item--active > .md-nav__link");
    active.forEach(function (link, i) {
      var text = link.textContent.trim();
      if (i === 0) { if (text !== "Home") parts.push(text); return; }
      var lab = text.match(/^Lab \d+/);
      if (lab && parts.indexOf(lab[0]) < 0) parts.push(lab[0]);
    });
    topic.innerHTML = "";
    parts.forEach(function (p, i) {
      if (i) topic.appendChild(Object.assign(document.createElement("span"), { className: "header-path__sep", textContent: " · " }));
      topic.appendChild(Object.assign(document.createElement("span"), { className: i ? "header-path__part" : "", textContent: p }));
    });
  }
  if (window.document$) document$.subscribe(init); else document.addEventListener("DOMContentLoaded", init);
})();
