// Menu di navigazione: all'apertura di ogni pagina è aperto solo il modulo
// dell'esercizio corrente; tutti gli altri moduli sono chiusi.
(function () {
  function init() {
    document.querySelectorAll(".md-nav--primary .md-nav__toggle").forEach(function (t) {
      if (t.id === "__drawer" || t.id === "__toc") return;
      t.classList.remove("md-toggle--indeterminate");
      t.checked = t.parentElement.classList.contains("md-nav__item--active");
    });
  }
  // pulizia dello stato salvato dalla versione precedente dello script
  try { localStorage.removeItem("nav-open"); } catch (e) {}
  if (window.document$) document$.subscribe(init); else document.addEventListener("DOMContentLoaded", init);
})();
