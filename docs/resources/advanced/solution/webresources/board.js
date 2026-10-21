/* PMO Demand Hub: Proposal Board.
   Kanban of active proposals by Proposal Status. Moving a card updates csm_proposalstatus through the Dataverse Web API.
   Outside Dataverse the page runs on preview data and nothing is written. */
(function () {
  "use strict";

  var A = window.anime;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canAnimate = !!A && !reduceMotion;
  if (canAnimate) document.documentElement.classList.add("anim");

  var COLS = [
    { value: 770000000, label: "Received", color: "var(--c-warn)" },
    { value: 770000001, label: "Assessed", color: "var(--c-assessment)" },
    { value: 770000002, label: "Review Scheduled", color: "var(--c-brand)" }
  ];
  var RECO = { 770000000: { cls: "reco-1", label: "Recommended" }, 770000001: { cls: "reco-2", label: "Needs further review" }, 770000002: { cls: "reco-3", label: "Not recommended" } };

  /* ------------------------------------------------------------ backend */
  function xrm() {
    try { if (window.parent && window.parent !== window && window.parent.Xrm && window.parent.Xrm.Utility) return window.parent.Xrm; } catch (e) { /* cross-origin */ }
    return window.Xrm && window.Xrm.Utility ? window.Xrm : null;
  }
  var inDataverse = window.location.protocol.indexOf("http") === 0 && !!xrm();

  function live() {
    var base;
    try { base = xrm().Utility.getGlobalContext().getClientUrl(); } catch (e) { base = window.location.origin; }
    function req(method, path, body) {
      return fetch(base + "/api/data/v9.2/" + path, {
        method: method, credentials: "same-origin", body: body ? JSON.stringify(body) : undefined,
        headers: { "Accept": "application/json", "Content-Type": "application/json; charset=utf-8", "OData-MaxVersion": "4.0", "OData-Version": "4.0", "If-Match": "*", "Prefer": "odata.maxpagesize=5000" }
      }).then(function (r) {
        if (r.ok) return r.status === 204 ? null : r.json();
        return r.json().catch(function () { return {}; }).then(function (j) { throw new Error((j.error && j.error.message) || ("HTTP " + r.status)); });
      });
    }
    function all(path) { return req("GET", path).then(function (j) { return j.value || []; }); }
    return {
      preview: false,
      load: function () {
        return Promise.all([
          all("csm_proposals?$select=csm_proposalid,csm_title,csm_proposalcode,csm_proposalstatus,csm_requestedbudget,_csm_program_value,_csm_requester_value,createdon&$filter=statecode eq 0&$orderby=createdon desc"),
          all("csm_programs?$select=csm_programid,csm_name,csm_programcode,csm_availablebudget&$filter=statecode eq 0"),
          all("csm_requesters?$select=csm_requesterid,csm_name&$filter=statecode eq 0"),
          all("csm_assessments?$select=csm_score,csm_recommendation,_csm_proposal_value,createdon&$filter=statecode eq 0&$orderby=createdon desc")
        ]);
      },
      setStatus: function (id, value) { return req("PATCH", "csm_proposals(" + id + ")", { csm_proposalstatus: value }); }
    };
  }

  function preview() {
    var day = 86400000, now = Date.now();
    var programs = [["p1", "Digital Process Transformation", "PG-100", 600000], ["p2", "Security and Compliance", "PG-200", 450000], ["p3", "Data and Artificial Intelligence", "PG-300", 500000], ["p4", "Modern Workplace", "PG-400", 300000], ["p5", "Infrastructure and Cloud", "PG-500", 800000]]
      .map(function (p) { return { csm_programid: p[0], csm_name: p[1], csm_programcode: p[2], csm_availablebudget: p[3] }; });
    var requesters = [["r1", "Giulia Romano"], ["r2", "Marco Bianchi"], ["r3", "Sara Conti"]].map(function (r) { return { csm_requesterid: r[0], csm_name: r[1] }; });
    var proposals = [
      ["a", "Self-service supplier portal", "PP-1007", 0, 180000, "p1", "r1", 1],
      ["b", "Network segmentation and privileged access", "PP-1006", 1, 320000, "p2", "r2", 2],
      ["c", "AI assistant for customer service", "PP-1005", 2, 260000, "p3", "r3", 3],
      ["d", "Bologna data center migration to cloud", "PP-1004", 1, 690000, "p5", "r2", 5],
      ["e", "New intranet and employee hub", "PP-1003", 0, 340000, "p4", "r1", 7],
      ["f", "Real-time sales dashboard", "PP-1002", 0, 95000, null, "r3", 8],
      ["g", "Invoice OCR with AI Builder", "PP-1001", 2, 120000, "p1", "r1", 10]
    ].map(function (p) { return { csm_proposalid: p[0], csm_title: p[1], csm_proposalcode: p[2], csm_proposalstatus: COLS[p[3]].value, csm_requestedbudget: p[4], _csm_program_value: p[5], _csm_requester_value: p[6], createdon: new Date(now - p[7] * day).toISOString() }; });
    var assessments = [["b", 63, 770000001], ["c", 81.5, 770000000], ["d", 48.5, 770000002], ["g", 77, 770000000]]
      .map(function (a) { return { _csm_proposal_value: a[0], csm_score: a[1], csm_recommendation: a[2], createdon: new Date().toISOString() }; });
    return {
      preview: true,
      load: function () { return Promise.resolve([proposals, programs, requesters, assessments]); },
      setStatus: function (id, value) {
        if (window.__boardFail) return new Promise(function (r, j) { setTimeout(function () { j(new Error("Simulated save error")); }, 150); });
        proposals.forEach(function (p) { if (p.csm_proposalid === id) p.csm_proposalstatus = value; });
        return new Promise(function (r) { setTimeout(r, 150); });
      }
    };
  }

  var backend = inDataverse ? live() : preview();

  /* ------------------------------------------------------------ helpers */
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c]; }); }
  function money(n) {
    if (n >= 1000000) return "€" + (n / 1000000).toFixed(2).replace(/\.?0+$/, "") + "M";
    if (n >= 1000) return "€" + Math.round(n / 1000) + "k";
    return "€" + Math.round(n || 0);
  }
  function toast(msg, action) {
    var el = document.createElement("div");
    el.className = "toast"; el.setAttribute("role", "status");
    el.innerHTML = esc(msg) + (action ? ' <button type="button" class="toast-btn">' + esc(action.label) + "</button>" : "");
    if (action) el.querySelector("button").addEventListener("click", function () { action.run(); el.remove(); });
    document.body.appendChild(el);
    if (canAnimate) A.animate(el, { opacity: [0, 1], translateY: [20, 0], duration: 400, ease: "outExpo" });
    setTimeout(function () {
      if (!el.isConnected) return;
      if (canAnimate) A.animate(el, { opacity: 0, translateY: 10, duration: 300, ease: "inQuad", onComplete: function () { el.remove(); } }); else el.remove();
    }, 6000);
  }

  /* ------------------------------------------------------------ state + render */
  var state = { proposals: [], programs: {}, requesters: {}, latest: {}, search: "", program: "" };
  var board = document.getElementById("board");

  function load() {
    return backend.load().then(function (r) {
      state.proposals = r[0];
      state.programs = {}; r[1].forEach(function (p) { state.programs[p.csm_programid] = p; });
      state.requesters = {}; r[2].forEach(function (q) { state.requesters[q.csm_requesterid] = q; });
      state.latest = {}; r[3].forEach(function (a) { if (!state.latest[a._csm_proposal_value]) state.latest[a._csm_proposal_value] = a; });
      var sel = document.getElementById("programFilter");
      sel.innerHTML = '<option value="">All programs</option><option value="none">Program to be confirmed</option>' +
        r[1].sort(function (a, b) { return String(a.csm_programcode).localeCompare(String(b.csm_programcode)); })
          .map(function (p) { return '<option value="' + esc(p.csm_programid) + '">' + esc(p.csm_programcode + " " + p.csm_name) + "</option>"; }).join("");
      sel.value = state.program;
      document.getElementById("previewBadge").hidden = !backend.preview;
      render(true);
    }).catch(function (e) { toast("Could not read proposals: " + e.message); });
  }

  function visible(p) {
    if (state.program === "none" && p._csm_program_value) return false;
    if (state.program && state.program !== "none" && p._csm_program_value !== state.program) return false;
    if (!state.search) return true;
    var req = state.requesters[p._csm_requester_value];
    return [p.csm_title, p.csm_proposalcode, req && req.csm_name].join(" ").toLowerCase().indexOf(state.search) > -1;
  }

  function cardHtml(p) {
    var prog = state.programs[p._csm_program_value], req = state.requesters[p._csm_requester_value], a = state.latest[p.csm_proposalid];
    var over = prog && p.csm_requestedbudget > prog.csm_availablebudget;
    var score = "";
    if (a && typeof a.csm_score === "number") {
      var r = RECO[a.csm_recommendation] || { cls: "", label: "" };
      score = '<span class="score ' + r.cls + '" title="' + esc(r.label) + '"><span class="score-bar"><span data-w="' + Math.max(0, Math.min(100, a.csm_score)) + '" style="width:' + Math.max(0, Math.min(100, a.csm_score)) + '%"></span></span>' + a.csm_score.toFixed(1) + "</span>";
    }
    var opts = COLS.map(function (c) { return '<option value="' + c.value + '"' + (c.value === p.csm_proposalstatus ? " selected" : "") + ">" + esc(c.label) + "</option>"; }).join("");
    return '<div class="card-top"><span class="card-code">' + esc(p.csm_proposalcode || "New") + '</span><span class="card-budget' + (over ? " over" : "") + '" title="' + (over ? "Above the available budget of the program" : "Requested budget") + '">' + money(p.csm_requestedbudget) + "</span></div>" +
      '<button type="button" class="card-title" data-open="' + esc(p.csm_proposalid) + '">' + esc(p.csm_title) + "</button>" +
      '<div class="card-meta">' + (prog ? '<span class="tag" title="' + esc(prog.csm_name) + '">' + esc(prog.csm_programcode) + "</span>" : '<span class="tag tag-none">Program to be confirmed</span>') + score + "</div>" +
      '<div class="card-foot"><span class="card-req">' + esc(req ? req.csm_name : "No requester") + '</span>' +
      '<label class="sr-only" for="mv-' + esc(p.csm_proposalid) + '">Status of ' + esc(p.csm_title) + "</label>" +
      '<select class="card-move" id="mv-' + esc(p.csm_proposalid) + '" data-move="' + esc(p.csm_proposalid) + '">' + opts + "</select></div>";
  }

  function render(first) {
    board.innerHTML = "";
    COLS.forEach(function (c) {
      var items = state.proposals.filter(function (p) { return p.csm_proposalstatus === c.value && visible(p); });
      var none = state.proposals.filter(function (p) { return !p.csm_proposalstatus && c.value === COLS[0].value && visible(p); });
      items = items.concat(none);
      var col = document.createElement("div");
      col.className = "col"; col.dataset.status = c.value; col.style.setProperty("--accent", c.color);
      col.setAttribute("aria-label", c.label);
      col.innerHTML = '<div class="col-head"><span class="col-dot"></span><span class="col-name">' + esc(c.label) + '</span><span class="col-count">' + items.length + '</span><span class="col-sum">' + money(items.reduce(function (s, p) { return s + (p.csm_requestedbudget || 0); }, 0)) + "</span></div>" +
        '<div class="col-list"></div>';
      var list = col.querySelector(".col-list");
      items.forEach(function (p) {
        var el = document.createElement("article");
        el.className = "pcard"; el.draggable = true; el.dataset.id = p.csm_proposalid;
        el.style.setProperty("--accent", c.color);
        el.innerHTML = cardHtml(p);
        list.appendChild(el);
      });
      if (!items.length) list.innerHTML = '<p class="col-empty">' + (state.proposals.length ? "No proposals here. Drop a card to move it." : "No proposals yet.") + "</p>";
      board.appendChild(col);
    });
    if (!canAnimate) return;
    if (first) {
      A.animate(".board-head > div, .board-tools", { opacity: [0, 1], translateY: [10, 0], duration: 500, delay: A.stagger(80), ease: "outQuad" });
      A.animate(".col", { opacity: [0, 1], translateY: [16, 0], duration: 600, delay: A.stagger(90, { start: 150 }), ease: "outExpo" });
      A.animate(".pcard", { opacity: [0, 1], translateY: [14, 0], scale: [0.97, 1], duration: 550, delay: A.stagger(40, { start: 350 }), ease: "outExpo" });
      document.querySelectorAll(".score-bar span").forEach(function (el) { el.style.width = "0%"; });
      A.animate(".score-bar span", { width: function (el) { return el.dataset.w + "%"; }, duration: 900, delay: A.stagger(40, { start: 700 }), ease: "outExpo" });
    } else {
      document.querySelectorAll(".col").forEach(function (c) { c.style.opacity = 1; });
    }
  }

  /* ------------------------------------------------------------ move */
  function move(id, value, opts) {
    var p = state.proposals.filter(function (x) { return x.csm_proposalid === id; })[0];
    if (!p || p.csm_proposalstatus === value) return Promise.resolve();
    var before = p.csm_proposalstatus;
    p.csm_proposalstatus = value;
    render(false);
    var card = board.querySelector('.pcard[data-id="' + CSS.escape(id) + '"]');
    if (card) {
      card.classList.add("saving");
      if (canAnimate) A.animate(card, { scale: [0.92, 1], opacity: [0.4, 0.7], duration: 450, ease: "outBack(1.7)" });
    }
    return backend.setStatus(id, value).then(function () {
      var c = board.querySelector('.pcard[data-id="' + CSS.escape(id) + '"]');
      if (c) { c.classList.remove("saving"); if (canAnimate) A.animate(c, { opacity: [0.7, 1], duration: 250, ease: "outQuad" }); }
      var label = COLS.filter(function (x) { return x.value === value; })[0].label;
      if (!(opts && opts.silent)) toast((p.csm_proposalcode || p.csm_title) + " moved to " + label + ".", { label: "Undo", run: function () { move(id, before, { silent: true }); } });
    }).catch(function (e) {
      p.csm_proposalstatus = before;
      render(false);
      toast("Status not saved: " + e.message);
    });
  }

  board.addEventListener("dragstart", function (e) {
    var c = e.target.closest && e.target.closest(".pcard");
    if (!c) return;
    c.classList.add("dragging");
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", c.dataset.id);
  });
  board.addEventListener("dragend", function (e) {
    var c = e.target.closest && e.target.closest(".pcard");
    if (c) c.classList.remove("dragging");
    board.querySelectorAll(".col.over").forEach(function (x) { x.classList.remove("over"); });
  });
  board.addEventListener("dragover", function (e) {
    var col = e.target.closest(".col");
    if (!col) return;
    e.preventDefault();
    board.querySelectorAll(".col.over").forEach(function (x) { if (x !== col) x.classList.remove("over"); });
    col.classList.add("over");
  });
  board.addEventListener("dragleave", function (e) {
    var col = e.target.closest(".col");
    if (col && !col.contains(e.relatedTarget)) col.classList.remove("over");
  });
  board.addEventListener("drop", function (e) {
    var col = e.target.closest(".col");
    if (!col) return;
    e.preventDefault();
    col.classList.remove("over");
    move(e.dataTransfer.getData("text/plain"), parseInt(col.dataset.status, 10));
  });
  board.addEventListener("change", function (e) {
    if (e.target.dataset.move) move(e.target.dataset.move, parseInt(e.target.value, 10));
  });
  board.addEventListener("click", function (e) {
    var t = e.target.closest("[data-open]");
    if (!t) return;
    var x = xrm();
    if (x) x.Navigation.openForm({ entityName: "csm_proposal", entityId: t.dataset.open });
    else toast("The proposal form opens inside the PMO Demand Hub app.");
  });

  document.getElementById("search").addEventListener("input", function (e) { state.search = e.target.value.trim().toLowerCase(); render(false); });
  document.getElementById("programFilter").addEventListener("change", function (e) { state.program = e.target.value; render(false); });
  document.querySelector('[data-action="new"]').addEventListener("click", function () {
    var x = xrm();
    if (!x) { toast("The new proposal form opens inside the PMO Demand Hub app."); return; }
    x.Navigation.openForm({ entityName: "csm_proposal", useQuickCreateForm: true }).then(load);
  });

  if (backend.preview) window.__board = { move: move, state: state };
  load();
})();
