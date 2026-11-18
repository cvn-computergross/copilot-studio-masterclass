/* PMO Demand Hub home page.
   - Manage data: one tile per table to view, add, download a CSV template and import rows.
   - CSV import: delimiter detection, preview, create or update by key, lookup and choice resolution.
   - Portfolio at a glance: live figures animated with anime.js.
   Outside Dataverse the page runs on an in-memory preview store, so everything can be tried safely. */
(function () {
  "use strict";

  var A = window.anime;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canAnimate = !!A && !reduceMotion;
  if (canAnimate) document.documentElement.classList.add("anim");

  /* ------------------------------------------------------------------ model */
  var CH = {
    channel: { "chat": 770000000, "email": 770000001 },
    status: { "received": 770000000, "assessed": 770000001, "review scheduled": 770000002 },
    reco: { "recommended": 770000000, "needs further review": 770000001, "not recommended": 770000002 }
  };
  var STATUS = { RECEIVED: 770000000, ASSESSED: 770000001, SCHEDULED: 770000002 };
  var STATUS_LABEL = {}; STATUS_LABEL[STATUS.RECEIVED] = "Received"; STATUS_LABEL[STATUS.ASSESSED] = "Assessed"; STATUS_LABEL[STATUS.SCHEDULED] = "Review scheduled";
  var RECO = [
    { value: 770000000, label: "Recommended", color: "var(--c-reco-1)" },
    { value: 770000001, label: "Needs further review", color: "var(--c-reco-2)" },
    { value: 770000002, label: "Not recommended", color: "var(--c-reco-3)" }
  ];

  /* t: text | int | dec | date | choice | lookup. aliases: other accepted header names (Italian lab files included). */
  var TABLES = [
    { key: "program", entity: "csm_program", set: "csm_programs", id: "csm_programid", label: "Programs", single: "program", icon: "program", color: "var(--c-program)",
      desc: "Investment programs, budget and scope.", keyCols: ["csm_programcode"], keyLabel: "Program Code",
      lookupBy: ["csm_programcode", "csm_name"],
      cols: [
        { h: "Name", a: "csm_name", t: "text", req: true, aliases: ["nome"] },
        { h: "Program Code", a: "csm_programcode", t: "text", req: true, aliases: ["codice programma", "code"] },
        { h: "Description", a: "csm_description", t: "text", aliases: ["descrizione"] },
        { h: "Available Budget (EUR)", a: "csm_availablebudget", t: "int", aliases: ["budget disponibile (eur)", "available budget", "budget"] }
      ] },
    { key: "criterion", entity: "csm_criterion", set: "csm_criterions", id: "csm_criterionid", label: "Evaluation Criteria", single: "criterion", icon: "criterion", color: "var(--c-criterion)",
      desc: "Weighted criteria per program, weights add up to 100.", keyCols: ["csm_name", "_csm_program_value"], keyLabel: "Name and Program",
      lookupBy: ["csm_name"],
      cols: [
        { h: "Name", a: "csm_name", t: "text", req: true, aliases: ["nome", "criterion"] },
        { h: "Description", a: "csm_description", t: "text", aliases: ["descrizione"] },
        { h: "Weight", a: "csm_weight", t: "int", aliases: ["peso"] },
        { h: "Program", a: "_csm_program_value", t: "lookup", nav: "csm_Program", target: "program", aliases: ["programma", "program code"] }
      ] },
    { key: "requester", entity: "csm_requester", set: "csm_requesters", id: "csm_requesterid", label: "Requesters", single: "requester", icon: "requester", color: "var(--c-requester)",
      desc: "People who submit proposals.", keyCols: ["csm_email"], keyLabel: "Email",
      lookupBy: ["csm_email", "csm_requestercode", "csm_name"],
      cols: [
        { h: "Name", a: "csm_name", t: "text", req: true, aliases: ["nome", "full name"] },
        { h: "Email", a: "csm_email", t: "text", aliases: ["e-mail", "mail"] },
        { h: "Role", a: "csm_role", t: "text", aliases: ["ruolo"] },
        { h: "Department", a: "csm_department", t: "text", aliases: ["funzione aziendale", "funzione", "business function"] }
      ] },
    { key: "proposal", entity: "csm_proposal", set: "csm_proposals", id: "csm_proposalid", label: "Proposals", single: "proposal", icon: "proposal", color: "var(--c-proposal)",
      desc: "Business cases with budget, status and document.", keyCols: ["csm_title"], keyLabel: "Title",
      lookupBy: ["csm_proposalcode", "csm_title"],
      cols: [
        { h: "Title", a: "csm_title", t: "text", req: true, aliases: ["titolo"] },
        { h: "Summary", a: "csm_summary", t: "text", aliases: ["sintesi"] },
        { h: "Cover Message", a: "csm_message", t: "text", aliases: ["messaggio", "message"] },
        { h: "Source Email", a: "csm_sourceemail", t: "text", aliases: ["email di origine"] },
        { h: "Requested Budget (EUR)", a: "csm_requestedbudget", t: "int", aliases: ["budget richiesto (eur)", "requested budget"] },
        { h: "Duration (Months)", a: "csm_durationmonths", t: "int", aliases: ["durata (mesi)", "duration"] },
        { h: "Channel", a: "csm_channel", t: "choice", choices: CH.channel, aliases: ["canale"] },
        { h: "Proposal Status", a: "csm_proposalstatus", t: "choice", choices: CH.status, aliases: ["stato proposta", "status"] },
        { h: "Submission Date", a: "csm_submissiondate", t: "date", aliases: ["data di presentazione"] },
        { h: "Requester", a: "_csm_requester_value", t: "lookup", nav: "csm_Requester", target: "requester", aliases: ["proponente", "requester email"] },
        { h: "Program", a: "_csm_program_value", t: "lookup", nav: "csm_Program", target: "program", aliases: ["programma", "program code"] }
      ] },
    { key: "assessment", entity: "csm_assessment", set: "csm_assessments", id: "csm_assessmentid", label: "Assessments", single: "assessment", icon: "assessment", color: "var(--c-assessment)",
      desc: "Scores, rationale and recommendation.", keyCols: ["csm_title"], keyLabel: "Title",
      lookupBy: ["csm_assessmentcode", "csm_title"],
      cols: [
        { h: "Title", a: "csm_title", t: "text", req: true, aliases: ["titolo"] },
        { h: "Proposal", a: "_csm_proposal_value", t: "lookup", nav: "csm_Proposal", target: "proposal", aliases: ["proposta", "proposal code"] },
        { h: "Program", a: "_csm_program_value", t: "lookup", nav: "csm_Program", target: "program", aliases: ["programma"] },
        { h: "Score", a: "csm_score", t: "dec", aliases: ["punteggio"] },
        { h: "Criteria Detail", a: "csm_criteriadetail", t: "text", aliases: ["dettaglio criteri"] },
        { h: "Rationale", a: "csm_rationale", t: "text", aliases: ["motivazione"] },
        { h: "Recommendation", a: "csm_recommendation", t: "choice", choices: CH.reco, aliases: ["raccomandazione"] },
        { h: "Assessment Date", a: "csm_assessmentdate", t: "date", aliases: ["data valutazione"] }
      ] }
  ];
  var BYKEY = {}; TABLES.forEach(function (t) { BYKEY[t.key] = t; });

  /* Starter data: the 5 programs and 25 criteria used by the labs (same content as the CSV files). */
  var STARTER = {
    program: [
      ["Digital Process Transformation", "PG-100", "Funds the digitalization of operational and administrative processes across business functions: removing manual steps, self-service portals, automation with Power Platform and integration with existing business systems.", "600000"],
      ["Security and Compliance", "PG-200", "Funds initiatives that reduce cyber risk and ensure compliance with NIS2, GDPR and internal policies: identity protection, network segmentation, monitoring and incident response.", "450000"],
      ["Data and Artificial Intelligence", "PG-300", "Funds data and AI use cases with measurable business value, provided that the data is available, of adequate quality and handled according to responsible AI principles.", "500000"],
      ["Modern Workplace", "PG-400", "Funds tools and services that improve the digital employee experience: collaboration, internal communication, intranet, workstations and adoption of Microsoft 365 tools.", "300000"],
      ["Infrastructure and Cloud", "PG-500", "Funds the modernization of IT infrastructure: cloud migrations, resilience and business continuity, lower infrastructure costs and less technical debt.", "800000"]
    ],
    criterion: [
      ["Strategic Alignment", "The proposal contributes directly to the goals of the IT Strategic Plan 2026-2028, in particular end-to-end process digitalization.", "25", "PG-100"],
      ["Measurable Financial Benefits", "Benefits expressed in euros or hours saved, with a stated baseline and a verifiable calculation method.", "25", "PG-100"],
      ["Process Impact", "Number of users, suppliers or cases involved and a concrete reduction in time, manual steps or errors.", "20", "PG-100"],
      ["Feasibility and Risk", "Realistic plan with phases and a pilot, identified dependencies, main risks described with their mitigations.", "15", "PG-100"],
      ["Platform Reuse", "Use of platforms the company already licenses (Power Platform, Dynamics 365, Microsoft 365) instead of new products.", "15", "PG-100"],
      ["Cyber Risk Reduction", "Measurable reduction of the attack surface or of the likelihood and impact of incidents, with reference to risks already on record.", "30", "PG-200"],
      ["Regulatory Compliance", "Explicit coverage of NIS2, GDPR or internal audit requirements, stating the gaps the proposal closes.", "25", "PG-200"],
      ["User Impact", "Effects on users' daily operations and measures to limit them (communication, maintenance windows, support).", "15", "PG-200"],
      ["Feasibility and Risk", "Realistic plan with phases, available skills, dependencies and project risks with mitigations.", "15", "PG-200"],
      ["Recurring Operating Costs", "Annual running costs (licenses, managed services, staff) stated and sustainable over time.", "15", "PG-200"],
      ["Business Value of the Use Case", "Clear business problem, identified target users and a quantified expected benefit.", "30", "PG-300"],
      ["Data Quality and Availability", "Identified data sources, data owner, and enough quality and history for the use case.", "25", "PG-300"],
      ["Responsible AI and Privacy", "Assessment of risks to people, legal basis for processing, human oversight and transparency toward users.", "20", "PG-300"],
      ["Feasibility and Risk", "Plan with a prototype or pilot, available skills, dependencies and main risks mitigated.", "15", "PG-300"],
      ["Measurable Outcomes", "KPIs defined with baseline and target, and how they will be measured after release.", "10", "PG-300"],
      ["Employee Experience", "Concrete improvement in employees' daily experience, backed by evidence (surveys, tickets, time spent).", "30", "PG-400"],
      ["Adoption and Change Management", "Communication, training and champions plan to ensure adoption after release.", "25", "PG-400"],
      ["Measurable Financial Benefits", "Savings or avoided costs expressed in euros, for example retiring existing tools or hours saved.", "20", "PG-400"],
      ["Security and Governance", "Content governance, permissions, lifecycle and compliance with company Microsoft 365 policies.", "15", "PG-400"],
      ["Feasibility and Risk", "Realistic plan with phases, dependencies and main risks with mitigations.", "10", "PG-400"],
      ["Resilience and Business Continuity", "Improved availability, disaster recovery, RPO and RTO compared with the current situation.", "30", "PG-500"],
      ["Infrastructure Cost Reduction", "Lower total cost of ownership (TCO) over at least three years, with stated assumptions.", "25", "PG-500"],
      ["Environmental Sustainability", "Lower energy use or emissions, with stated estimates and sources.", "15", "PG-500"],
      ["Feasibility and Risk", "Migration plan in waves, skills, dependencies and main risks with mitigations.", "20", "PG-500"],
      ["Reduced Technical Debt", "Retirement of obsolete or unsupported systems and a simpler architecture.", "10", "PG-500"]
    ]
  };
  var TEMPLATE_ROWS = {
    requester: [["Giulia Romano", "giulia.romano@zava.example", "Procurement Manager", "Procurement"]],
    proposal: [["Self-service supplier portal", "Portal where suppliers upload invoices and track payments.", "Please assess the attached business case.", "giulia.romano@zava.example", "180000", "9", "Email", "Received", "2026-10-15", "giulia.romano@zava.example", "PG-100"]],
    assessment: [["PP-1000 - Self-service supplier portal", "PP-1000", "PG-100", "78.5", "Strategic Alignment, 25, Strong, ..., 25", "Clear benefits and a realistic pilot.", "Recommended", "2026-10-16"]]
  };

  /* ------------------------------------------------------------------ backend */
  function xrm() {
    try { if (window.parent && window.parent !== window && window.parent.Xrm && window.parent.Xrm.Utility) return window.parent.Xrm; } catch (e) { /* cross-origin */ }
    return window.Xrm && window.Xrm.Utility ? window.Xrm : null;
  }

  function liveBackend() {
    var base;
    try { base = xrm().Utility.getGlobalContext().getClientUrl(); } catch (e) { base = window.location.origin; }
    var H = { "Accept": "application/json", "Content-Type": "application/json; charset=utf-8", "OData-MaxVersion": "4.0", "OData-Version": "4.0" };
    function req(method, path, body, extra) {
      var h = {}; Object.keys(H).forEach(function (k) { h[k] = H[k]; });
      if (extra) Object.keys(extra).forEach(function (k) { h[k] = extra[k]; });
      return fetch(base + "/api/data/v9.2/" + path, { method: method, credentials: "same-origin", headers: h, body: body ? JSON.stringify(body) : undefined })
        .then(function (r) {
          if (r.ok) return r;
          return r.json().catch(function () { return {}; }).then(function (j) {
            throw new Error((j.error && j.error.message) || ("HTTP " + r.status));
          });
        });
    }
    function listAll(path) {
      var out = [];
      function page(url, abs) {
        var p = abs ? fetch(url, { credentials: "same-origin", headers: { "Accept": "application/json", "Prefer": "odata.maxpagesize=5000" } }).then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r; })
          : req("GET", url, null, { "Prefer": "odata.maxpagesize=5000" });
        return p.then(function (r) { return r.json(); }).then(function (j) {
          out = out.concat(j.value || []);
          return j["@odata.nextLink"] ? page(j["@odata.nextLink"], true) : out;
        });
      }
      return page(path, false);
    }
    return {
      preview: false,
      list: function (t, select) { return listAll(t.set + "?$select=" + select.join(",") + "&$filter=statecode eq 0"); },
      create: function (t, body) {
        return req("POST", t.set, body, { "Prefer": "return=representation" }).then(function (r) { return r.json(); }).then(function (j) { return j[t.id]; });
      },
      update: function (t, id, body) { return req("PATCH", t.set + "(" + id + ")", body, { "If-Match": "*" }).then(function () { return id; }); }
    };
  }

  function previewBackend() {
    var db = {}, seq = 1;
    TABLES.forEach(function (t) { db[t.key] = []; });
    function uid() { var s = String(seq++); while (s.length < 12) s = "0" + s; return "00000000-0000-4000-8000-" + s; }
    function apply(t, rec, body) {
      Object.keys(body).forEach(function (k) {
        var m = /^(csm_\w+)@odata\.bind$/.exec(k);
        if (m) { rec["_" + m[1].toLowerCase() + "_value"] = /\(([^)]+)\)/.exec(body[k])[1]; return; }
        rec[k] = body[k];
      });
      return rec;
    }
    var be = {
      preview: true,
      list: function (t) { return Promise.resolve(db[t.key].map(function (r) { return Object.assign({}, r); })); },
      create: function (t, body) {
        var rec = { createdon: new Date().toISOString() }; rec[t.id] = uid();
        if (t.key === "proposal") rec.csm_proposalcode = "PP-" + (1000 + db.proposal.length);
        if (t.key === "requester") rec.csm_requestercode = "RQ-" + (1000 + db.requester.length);
        if (t.key === "assessment") rec.csm_assessmentcode = "AS-" + (1000 + db.assessment.length);
        db[t.key].push(apply(t, rec, body));
        return delay(40).then(function () { return rec[t.id]; });
      },
      update: function (t, id, body) {
        var rec = db[t.key].filter(function (r) { return r[t.id] === id; })[0];
        if (rec) apply(t, rec, body);
        return delay(40).then(function () { return id; });
      },
      _db: db
    };
    return be;
  }
  function delay(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  function seedPreview(be) {
    var db = be._db, now = Date.now(), day = 86400000;
    STARTER.program.forEach(function (r, i) { db.program.push({ csm_programid: "p" + i, csm_name: r[0], csm_programcode: r[1], csm_description: r[2], csm_availablebudget: +r[3] }); });
    STARTER.criterion.forEach(function (r, i) { db.criterion.push({ csm_criterionid: "c" + i, csm_name: r[0], csm_weight: +r[2], _csm_program_value: "p" + (+r[3].slice(3, 4) - 1) }); });
    db.requester.push({ csm_requesterid: "r0", csm_name: "Giulia Romano", csm_email: "giulia.romano@zava.example", csm_requestercode: "RQ-1000" });
    [["Self-service supplier portal", 0, 180000, 0, 1], ["Network segmentation and privileged access", 1, 320000, 1, 2], ["AI assistant for customer service", 2, 260000, 2, 4],
     ["Bologna data center migration to cloud", 1, 690000, 4, 6], ["New intranet and employee hub", 0, 340000, 3, 8], ["Real-time sales dashboard", 0, 95000, null, 9]]
      .forEach(function (p, i) {
        db.proposal.push({ csm_proposalid: "pp" + i, csm_title: p[0], csm_proposalcode: "PP-" + (1005 - i), csm_proposalstatus: [STATUS.RECEIVED, STATUS.ASSESSED, STATUS.SCHEDULED][p[1]],
          csm_requestedbudget: p[2], _csm_program_value: p[3] === null ? null : "p" + p[3], createdon: new Date(now - p[4] * day).toISOString() });
      });
    [[81.5, 770000000], [63, 770000001], [48.5, 770000002]].forEach(function (a, i) { db.assessment.push({ csm_assessmentid: "a" + i, csm_title: "Assessment " + i, csm_score: a[0], csm_recommendation: a[1] }); });
  }

  var inDataverse = window.location.protocol.indexOf("http") === 0 && !!xrm();
  var backend = inDataverse ? liveBackend() : previewBackend();
  if (backend.preview) seedPreview(backend);

  /* ------------------------------------------------------------------ helpers */
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c]; }); }
  function norm(s) { return String(s == null ? "" : s).toLowerCase().replace(/^﻿/, "").replace(/[^a-z0-9()]+/g, " ").trim(); }
  function money(n) {
    if (n >= 1000000) return "€" + (n / 1000000).toFixed(2).replace(/\.?0+$/, "") + "M";
    if (n >= 1000) return "€" + Math.round(n / 1000) + "k";
    return "€" + Math.round(n);
  }
  function fmt(el, v) {
    if (el.dataset.money) return money(v);
    return v.toFixed(parseInt(el.dataset.decimals || "0", 10));
  }
  function relDate(iso) {
    var d = (Date.now() - new Date(iso).getTime()) / 86400000;
    if (d < 1) return "today";
    if (d < 2) return "yesterday";
    if (d < 30) return Math.floor(d) + " days ago";
    return new Date(iso).toLocaleDateString();
  }
  function initials(t) { return (t || "?").split(/\s+/).filter(Boolean).slice(0, 2).map(function (w) { return w[0].toUpperCase(); }).join(""); }
  function countTo(el, value, delayMs) {
    if (!canAnimate) { el.textContent = fmt(el, value); return; }
    var o = { v: parseFloat(el.dataset.current || "0") };
    el.dataset.current = String(value);
    A.animate(o, { v: value, duration: 1200, delay: delayMs || 0, ease: "outExpo",
      onUpdate: function () { el.textContent = fmt(el, o.v); },
      onComplete: function () { el.textContent = fmt(el, value); } });
  }

  /* ------------------------------------------------------------------ CSV */
  function detectDelimiter(text) {
    var line = text.split(/\r?\n/)[0] || "";
    var counts = { ",": 0, ";": 0, "\t": 0 }, q = false;
    for (var i = 0; i < line.length; i++) { var c = line[i]; if (c === '"') q = !q; else if (!q && counts[c] !== undefined) counts[c]++; }
    return Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; })[0];
  }
  function parseCsv(text) {
    text = text.replace(/^﻿/, "");
    var d = detectDelimiter(text), rows = [], row = [], f = "", q = false;
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (q) {
        if (c === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; }
        else f += c;
      } else if (c === '"') q = true;
      else if (c === d) { row.push(f); f = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(f); f = "";
        if (row.some(function (x) { return x.trim() !== ""; })) rows.push(row);
        row = [];
      } else f += c;
    }
    row.push(f);
    if (row.some(function (x) { return x.trim() !== ""; })) rows.push(row);
    return { delimiter: d, header: rows[0] || [], rows: rows.slice(1) };
  }
  function toCsv(header, rows) {
    function q(v) { v = String(v == null ? "" : v); return /[",\n;]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
    return "﻿" + [header].concat(rows).map(function (r) { return r.map(q).join(","); }).join("\r\n") + "\r\n";
  }
  function download(name, text) {
    var blob = new Blob([text], { type: "text/csv;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  function parseNumber(raw, integer) {
    var s = String(raw).replace(/[\s €$]/g, "").replace(/eur$/i, "");
    if (s === "") return null;
    var lc = s.lastIndexOf(","), ld = s.lastIndexOf(".");
    if (lc > -1 && ld > -1) { s = lc > ld ? s.replace(/\./g, "").replace(",", ".") : s.replace(/,/g, ""); }
    else if (lc > -1) { s = (integer && /,\d{3}$/.test(s)) || /,\d{3},/.test(s) ? s.replace(/,/g, "") : s.replace(",", "."); }
    else if (ld > -1 && integer && /\.\d{3}$/.test(s)) { s = s.replace(/\./g, ""); }
    var n = Number(s);
    if (!isFinite(n)) throw new Error("\"" + raw + "\" is not a number");
    return integer ? Math.round(n) : n;
  }
  function parseDate(raw) {
    var s = String(raw).trim(), m;
    if (!s) return null;
    if ((m = /^(\d{4})-(\d{1,2})-(\d{1,2})/.exec(s))) return pad(m[1], m[2], m[3]);
    if ((m = /^(\d{1,2})[\/.\-](\d{1,2})[\/.\-](\d{4})$/.exec(s))) return pad(m[3], m[2], m[1]);
    throw new Error("\"" + raw + "\" is not a date (use YYYY-MM-DD or DD/MM/YYYY)");
  }
  function pad(y, mo, d) {
    mo = +mo; d = +d;
    var dt = new Date(Date.UTC(+y, mo - 1, d));
    if (mo < 1 || mo > 12 || dt.getUTCMonth() !== mo - 1 || dt.getUTCDate() !== d) throw new Error("\"" + y + "-" + mo + "-" + d + "\" is not a valid date");
    return y + "-" + (mo < 10 ? "0" : "") + mo + "-" + (d < 10 ? "0" : "") + d + "T12:00:00Z";
  }

  /* map CSV header to table columns */
  function mapHeader(t, header) {
    var map = [], used = {}, unknown = [];
    header.forEach(function (h, i) {
      var n = norm(h), col = null;
      t.cols.forEach(function (c) {
        if (col || used[c.a]) return;
        var names = [c.h, c.a.replace(/^_|_value$/g, "")].concat(c.aliases || []).map(norm);
        if (names.indexOf(n) > -1) col = c;
      });
      if (col) { used[col.a] = true; map.push({ index: i, col: col }); } else if (n) unknown.push(h);
    });
    var missing = t.cols.filter(function (c) { return c.req && !used[c.a]; }).map(function (c) { return c.h; });
    return { map: map, unknown: unknown, missing: missing };
  }

  /* lookup index for a target table: lower-case values of lookupBy columns -> id */
  function buildIndex(t, records) {
    var idx = {};
    records.forEach(function (r) {
      t.lookupBy.forEach(function (a) { if (r[a]) { var k = norm(r[a]); if (!(k in idx)) idx[k] = r[t.id]; } });
    });
    return idx;
  }
  function keyOf(t, obj) { return t.keyCols.map(function (a) { return norm(obj[a]); }).join("|"); }

  function runImport(t, rows, mapping, updateExisting, onProgress) {
    var targets = {}, result = { created: 0, updated: 0, failed: [], total: rows.length };
    mapping.map.forEach(function (m) { if (m.col.t === "lookup") targets[m.col.target] = true; });
    var loads = Object.keys(targets).map(function (k) {
      var tt = BYKEY[k];
      return backend.list(tt, [tt.id].concat(tt.lookupBy)).then(function (recs) { targets[k] = buildIndex(tt, recs); });
    });
    var select = [t.id].concat(t.keyCols);
    var existing = {};
    loads.push(backend.list(t, select).then(function (recs) { recs.forEach(function (r) { existing[keyOf(t, r)] = r[t.id]; }); }));

    return Promise.all(loads).then(function () {
      var i = 0;
      function next() {
        if (i >= rows.length) return Promise.resolve(result);
        var row = rows[i], line = i + 2; i++;
        var body = {}, keyObj = {};
        try {
          mapping.map.forEach(function (m) {
            var raw = (row[m.index] || "").trim(), c = m.col, v;
            if (raw === "") { if (c.req) throw new Error(c.h + " is required"); return; }
            if (c.t === "text") v = raw;
            else if (c.t === "int") v = parseNumber(raw, true);
            else if (c.t === "dec") v = parseNumber(raw, false);
            else if (c.t === "date") v = parseDate(raw);
            else if (c.t === "choice") {
              v = /^\d+$/.test(raw) ? +raw : c.choices[norm(raw)];
              if (v === undefined) throw new Error(c.h + " \"" + raw + "\" is not one of: " + Object.keys(c.choices).join(", "));
            } else if (c.t === "lookup") {
              var id = targets[c.target][norm(raw)];
              if (!id) throw new Error(c.h + " \"" + raw + "\" not found in " + BYKEY[c.target].label);
              body[c.nav + "@odata.bind"] = "/" + BYKEY[c.target].set + "(" + id + ")";
              keyObj[c.a] = id;
              return;
            }
            body[c.a] = v; keyObj[c.a] = v;
          });
        } catch (e) {
          result.failed.push({ line: line, message: e.message });
          onProgress(i, rows.length);
          return next();
        }
        var k = keyOf(t, keyObj), found = existing[k];
        var op = found && updateExisting ? backend.update(t, found, body).then(function () { result.updated++; })
          : backend.create(t, body).then(function (id) { existing[k] = id; result.created++; });
        return op.catch(function (e) { result.failed.push({ line: line, message: e.message }); })
          .then(function () { onProgress(i, rows.length); return next(); });
      }
      return next();
    });
  }

  /* ------------------------------------------------------------------ manage data UI */
  var counts = {};
  function renderTiles() {
    var host = document.getElementById("tiles");
    host.innerHTML = "";
    TABLES.forEach(function (t) {
      var el = document.createElement("article");
      el.className = "tile";
      el.style.setProperty("--accent", t.color);
      el.innerHTML =
        '<div class="tile-top"><span class="tile-icon" style="-webkit-mask-image:url(icons/' + t.icon + '.svg);mask-image:url(icons/' + t.icon + '.svg)"></span>' +
        '<span class="tile-count" data-tile="' + t.key + '">0</span></div>' +
        '<h3 class="tile-title">' + esc(t.label) + "</h3>" +
        '<p class="tile-desc">' + esc(t.desc) + "</p>" +
        '<div class="tile-actions">' +
        '<button class="chip chip-strong" type="button" data-action="list" data-entity="' + t.entity + '">View</button>' +
        '<button class="chip" type="button" data-action="new" data-entity="' + t.entity + '">New</button>' +
        '<button class="chip" type="button" data-action="import" data-table="' + t.key + '">Import</button>' +
        '<button class="chip chip-icon" type="button" data-action="template" data-table="' + t.key + '" title="Download CSV template" aria-label="Download ' + esc(t.label) + ' CSV template">CSV</button>' +
        "</div>";
      host.appendChild(el);
    });
  }
  function refreshCounts() {
    return Promise.all(TABLES.map(function (t) {
      return backend.list(t, [t.id]).then(function (r) { counts[t.key] = r.length; }).catch(function () { counts[t.key] = 0; });
    })).then(function () {
      document.querySelectorAll("[data-tile]").forEach(function (el, i) { countTo(el, counts[el.dataset.tile] || 0, 200 + i * 60); });
    });
  }

  function templateFor(key) {
    var t = BYKEY[key];
    var rows = STARTER[key] || TEMPLATE_ROWS[key] || [];
    download("pmo-" + t.set.replace("csm_", "") + "-template.csv", toCsv(t.cols.map(function (c) { return c.h; }), rows));
  }

  /* import panel */
  var state = { table: "program", parsed: null, mapping: null };
  var overlay = document.getElementById("overlay");
  var sel = document.getElementById("importTable");
  TABLES.forEach(function (t) { var o = document.createElement("option"); o.value = t.key; o.textContent = t.label; sel.appendChild(o); });

  function tableHint() {
    var t = BYKEY[state.table];
    var lookups = t.cols.filter(function (c) { return c.t === "lookup"; }).map(function (c) { return c.h + " (by " + BYKEY[c.target].lookupBy.map(function (a) { return labelOf(BYKEY[c.target], a); }).join(" or ") + ")"; });
    document.getElementById("tableHint").textContent = "Columns: " + t.cols.map(function (c) { return c.h + (c.req ? " *" : ""); }).join(", ") + "." +
      (lookups.length ? " Lookups are matched by name or code: " + lookups.join("; ") + "." : "") + " Import parent tables first (Programs, then Requesters, then Proposals).";
    document.getElementById("keyLabel").textContent = t.keyLabel;
  }
  function labelOf(t, a) {
    var c = t.cols.filter(function (x) { return x.a === a; })[0];
    if (c) return c.h;
    return { csm_requestercode: "Requester Code", csm_proposalcode: "Proposal Code", csm_assessmentcode: "Assessment Code" }[a] || a;
  }
  function openPanel(key) {
    state.table = key || state.table; sel.value = state.table;
    resetFile(); tableHint();
    overlay.hidden = false;
    document.body.classList.add("modal-open");
    if (canAnimate) {
      A.animate(overlay, { opacity: [0, 1], duration: 200, ease: "outQuad" });
      A.animate(".panel", { opacity: [0, 1], translateY: [24, 0], scale: [0.98, 1], duration: 450, ease: "outExpo" });
    }
    sel.focus();
  }
  function closePanel() {
    if (!canAnimate) { overlay.hidden = true; document.body.classList.remove("modal-open"); return; }
    A.animate(".panel", { opacity: 0, translateY: 16, duration: 220, ease: "inQuad" });
    A.animate(overlay, { opacity: 0, duration: 240, ease: "inQuad", onComplete: function () { overlay.hidden = true; document.body.classList.remove("modal-open"); } });
  }
  function resetFile() {
    state.parsed = null; state.mapping = null;
    document.getElementById("fileInput").value = "";
    document.getElementById("dropTitle").textContent = "Drop a CSV file here or select to browse";
    document.getElementById("previewStep").hidden = true;
    document.getElementById("progressWrap").hidden = true;
    document.getElementById("result").hidden = true;
    document.getElementById("runImport").disabled = true;
    document.getElementById("runImport").textContent = "Import rows";
  }
  function loadFile(file) {
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () { usePreparsed(file.name, parseCsv(String(reader.result))); };
    reader.readAsText(file, "utf-8");
  }
  function usePreparsed(name, parsed) {
    var t = BYKEY[state.table];
    state.parsed = parsed;
    state.mapping = mapHeader(t, parsed.header);
    document.getElementById("dropTitle").textContent = name + " · " + parsed.rows.length + " rows";
    var info = "Separator \"" + (parsed.delimiter === "\t" ? "tab" : parsed.delimiter) + "\". Matched " + state.mapping.map.length + " of " + t.cols.length + " columns.";
    if (state.mapping.unknown.length) info += " Ignored: " + state.mapping.unknown.join(", ") + ".";
    if (state.mapping.missing.length) info += " Missing required: " + state.mapping.missing.join(", ") + ".";
    document.getElementById("mappingInfo").textContent = info;
    var tbl = document.getElementById("previewTable");
    var head = "<thead><tr>" + state.mapping.map.map(function (m) { return "<th>" + esc(m.col.h) + "</th>"; }).join("") + "</tr></thead>";
    var body = "<tbody>" + parsed.rows.slice(0, 5).map(function (r) { return "<tr>" + state.mapping.map.map(function (m) { return "<td>" + esc(r[m.index]) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody>";
    tbl.innerHTML = head + body;
    document.getElementById("previewStep").hidden = false;
    var ok = !state.mapping.missing.length && parsed.rows.length > 0;
    var btn = document.getElementById("runImport");
    btn.disabled = !ok;
    btn.textContent = ok ? "Import " + parsed.rows.length + " rows" : "Import rows";
    if (canAnimate) A.animate("#previewStep", { opacity: [0, 1], translateY: [10, 0], duration: 400, ease: "outQuad" });
  }
  function doImport() {
    var t = BYKEY[state.table], btn = document.getElementById("runImport");
    btn.disabled = true;
    document.getElementById("progressWrap").hidden = false;
    var fill = document.getElementById("progressFill"), text = document.getElementById("progressText");
    fill.style.width = "0%";
    return runImport(t, state.parsed.rows, state.mapping, document.getElementById("updateExisting").checked, function (done, total) {
      var pct = Math.round(done / total * 100);
      if (canAnimate) A.animate(fill, { width: pct + "%", duration: 250, ease: "outQuad" }); else fill.style.width = pct + "%";
      text.textContent = "Processed " + done + " of " + total + " rows";
    }).then(function (r) {
      showResult(t, r);
      btn.textContent = "Done";
      return Promise.all([refreshCounts(), loadDashboard()]);
    }).catch(function (e) {
      showResult(t, { created: 0, updated: 0, total: state.parsed.rows.length, failed: [{ line: "-", message: e.message }] });
      btn.disabled = false;
    });
  }
  function showResult(t, r) {
    var el = document.getElementById("result");
    var cls = r.failed.length ? (r.created + r.updated ? "warn" : "error") : "ok";
    el.className = "result result-" + cls;
    el.innerHTML = "<strong>" + esc(t.label) + ":</strong> " + r.created + " created, " + r.updated + " updated, " + r.failed.length + " failed." +
      (r.failed.length ? "<ul>" + r.failed.slice(0, 20).map(function (f) { return "<li>Row " + esc(f.line) + ": " + esc(f.message) + "</li>"; }).join("") + "</ul>" +
        (r.failed.length > 20 ? "<p>" + (r.failed.length - 20) + " more rows failed.</p>" : "") : "") +
      (backend.preview ? "<p class=\"hint\">Preview mode: rows are kept in this page only. Open the page inside the app to write to Dataverse.</p>" : "");
    el.hidden = false;
    if (canAnimate) A.animate(el, { opacity: [0, 1], translateY: [8, 0], duration: 400, ease: "outQuad" });
  }
  function loadStarter() {
    var btn = document.querySelector('[data-action="starter"]');
    btn.disabled = true; btn.textContent = "Loading starter data...";
    var steps = ["program", "criterion"], log = [];
    function step(i) {
      if (i >= steps.length) return Promise.resolve();
      var t = BYKEY[steps[i]];
      var parsed = { header: t.cols.map(function (c) { return c.h; }), rows: STARTER[steps[i]] };
      return runImport(t, parsed.rows, mapHeader(t, parsed.header), true, function () {}).then(function (r) {
        log.push(t.label + ": " + r.created + " created, " + r.updated + " updated" + (r.failed.length ? ", " + r.failed.length + " failed" : ""));
        return step(i + 1);
      });
    }
    return step(0).then(function () {
      btn.textContent = "Starter data loaded";
      toast(log.join(" · "));
      return Promise.all([refreshCounts(), loadDashboard()]);
    }).catch(function (e) { toast("Could not load starter data: " + e.message); })
      .then(function () { setTimeout(function () { btn.disabled = false; btn.textContent = "Load starter data"; }, 2500); });
  }
  function toast(msg) {
    var el = document.createElement("div");
    el.className = "toast"; el.setAttribute("role", "status"); el.textContent = msg;
    document.body.appendChild(el);
    if (canAnimate) A.animate(el, { opacity: [0, 1], translateY: [20, 0], duration: 400, ease: "outExpo" });
    setTimeout(function () {
      if (canAnimate) A.animate(el, { opacity: 0, translateY: 10, duration: 300, ease: "inQuad", onComplete: function () { el.remove(); } }); else el.remove();
    }, 5000);
  }

  /* ------------------------------------------------------------------ dashboard */
  function loadDashboard() {
    return Promise.all([
      backend.list(BYKEY.program, ["csm_programid", "csm_name", "csm_programcode", "csm_availablebudget"]),
      backend.list(BYKEY.proposal, ["csm_proposalid", "csm_title", "csm_proposalcode", "csm_proposalstatus", "csm_requestedbudget", "_csm_program_value", "createdon"]),
      backend.list(BYKEY.assessment, ["csm_assessmentid", "csm_score", "csm_recommendation"]),
      backend.list(BYKEY.criterion, ["csm_criterionid", "_csm_program_value"])
    ]).then(function (r) {
      renderDashboard({
        programs: r[0].map(function (p) { return { id: p.csm_programid, name: p.csm_name, code: p.csm_programcode, available: p.csm_availablebudget || 0 }; })
          .sort(function (a, b) { return String(a.code).localeCompare(String(b.code)); }),
        proposals: r[1].map(function (p) { return { id: p.csm_proposalid, title: p.csm_title, code: p.csm_proposalcode, status: p.csm_proposalstatus, requested: p.csm_requestedbudget || 0, program: p._csm_program_value, created: p.createdon }; })
          .sort(function (a, b) { return String(b.created).localeCompare(String(a.created)); }),
        assessments: r[2].map(function (a) { return { score: a.csm_score, reco: a.csm_recommendation }; }),
        criteria: r[3].map(function (c) { return { program: c._csm_program_value }; })
      });
    }).catch(function (e) { toast("Could not read data: " + e.message); });
  }

  var firstRender = true;
  function renderDashboard(data) {
    document.getElementById("previewBadge").hidden = !backend.preview;
    var props = data.proposals;
    var totals = {
      proposals: props.length,
      received: props.filter(function (p) { return p.status === STATUS.RECEIVED; }).length,
      assessed: props.filter(function (p) { return p.status === STATUS.ASSESSED; }).length,
      scheduled: props.filter(function (p) { return p.status === STATUS.SCHEDULED; }).length,
      requested: props.reduce(function (s, p) { return s + p.requested; }, 0),
      available: data.programs.reduce(function (s, p) { return s + p.available; }, 0),
      assessments: data.assessments.length,
      avgScore: 0
    };
    var scored = data.assessments.filter(function (a) { return typeof a.score === "number"; });
    if (scored.length) totals.avgScore = scored.reduce(function (s, a) { return s + a.score; }, 0) / scored.length;

    var reqBy = {}, nBy = {}, critBy = {};
    props.forEach(function (x) { reqBy[x.program] = (reqBy[x.program] || 0) + x.requested; nBy[x.program] = (nBy[x.program] || 0) + 1; });
    data.criteria.forEach(function (c) { critBy[c.program] = (critBy[c.program] || 0) + 1; });
    var maxBudget = Math.max.apply(null, data.programs.map(function (p) { return Math.max(p.available, reqBy[p.id] || 0); }).concat([1]));
    var ul = document.getElementById("programs");
    ul.innerHTML = "";
    data.programs.forEach(function (p) {
      var req = reqBy[p.id] || 0;
      var li = document.createElement("li");
      li.className = "program"; li.tabIndex = 0; li.setAttribute("role", "button");
      li.innerHTML = '<span><span class="program-name">' + esc(p.name) + '</span><span class="program-code">' + esc(p.code) + "</span></span>" +
        '<span class="program-meta">' + money(req) + " of " + money(p.available) + " &middot; " + (nBy[p.id] || 0) + " proposals &middot; " + (critBy[p.id] || 0) + " criteria</span>" +
        '<span class="bar"><span class="bar-av" data-w="' + (p.available / maxBudget * 100) + '"></span><span class="bar-req' + (req > p.available ? " over" : "") + '" data-w="' + (req / maxBudget * 100) + '"></span></span>';
      li.addEventListener("click", function () { openRecord("csm_program", p.id); });
      li.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openRecord("csm_program", p.id); } });
      ul.appendChild(li);
    });
    if (!data.programs.length) ul.innerHTML = '<li class="empty">No programs yet. Select Load starter data or import programs.csv.</li>';

    var g = document.getElementById("donutSegments"), list = document.getElementById("recoList");
    g.innerHTML = ""; list.innerHTML = "";
    var C = 2 * Math.PI * 46, offset = 0, total = Math.max(totals.assessments, 1);
    RECO.forEach(function (r) {
      var count = data.assessments.filter(function (a) { return a.reco === r.value; }).length;
      var len = count / total * C;
      if (count > 0) {
        var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        c.setAttribute("class", "seg"); c.setAttribute("cx", "60"); c.setAttribute("cy", "60"); c.setAttribute("r", "46");
        c.style.stroke = r.color;
        c.setAttribute("stroke-dasharray", "0 " + C);
        c.setAttribute("stroke-dashoffset", String(-offset));
        c.dataset.len = String(Math.max(len - (len > 6 ? 4 : 0), 0.01)); c.dataset.c = String(C);
        g.appendChild(c);
      }
      offset += len;
      var li = document.createElement("li");
      li.innerHTML = '<span class="swatch" style="background:' + r.color + '"></span>' + esc(r.label) + '<span class="count" data-count="reco' + r.value + '">0</span>';
      list.appendChild(li);
      totals["reco" + r.value] = count;
    });

    var rec = document.getElementById("recent");
    rec.innerHTML = "";
    props.slice(0, 6).forEach(function (p) {
      var li = document.createElement("li");
      var cls = p.status === STATUS.ASSESSED ? 1 : p.status === STATUS.SCHEDULED ? 2 : 0;
      li.innerHTML = '<a href="#"><span class="avatar">' + esc(initials(p.title)) + "</span>" +
        '<span><span class="t">' + esc(p.title) + '</span><span class="s">' + esc(p.code || "") + " &middot; " + money(p.requested) + (p.created ? " &middot; " + relDate(p.created) : "") + "</span></span>" +
        '<span class="pill pill-' + cls + '">' + esc(STATUS_LABEL[p.status] || "Received") + "</span></a>";
      li.querySelector("a").addEventListener("click", function (e) { e.preventDefault(); openRecord("csm_proposal", p.id); });
      rec.appendChild(li);
    });
    document.getElementById("recentEmpty").hidden = props.length > 0;

    animateDashboard(totals);
  }

  function animateDashboard(totals) {
    var counters = document.querySelectorAll("[data-count]");
    var bars = document.querySelectorAll(".bar-av, .bar-req");
    var segs = document.querySelectorAll(".seg");
    if (!canAnimate) {
      counters.forEach(function (el) { el.textContent = fmt(el, totals[el.dataset.count] || 0); });
      bars.forEach(function (b) { b.style.width = b.dataset.w + "%"; });
      segs.forEach(function (s) { s.setAttribute("stroke-dasharray", s.dataset.len + " " + s.dataset.c); });
      return;
    }
    var base = firstRender ? 700 : 0;
    var i = 0;
    counters.forEach(function (el) { countTo(el, totals[el.dataset.count] || 0, base + 50 * i++); });
    A.animate(".bar-av", { width: function (el) { return el.dataset.w + "%"; }, duration: 1100, delay: A.stagger(70, { start: base }), ease: "outQuart" });
    A.animate(".bar-req", { width: function (el) { return el.dataset.w + "%"; }, duration: 1300, delay: A.stagger(70, { start: base + 150 }), ease: "outExpo" });
    segs.forEach(function (s, k) {
      var o = { l: 0 };
      A.animate(o, { l: parseFloat(s.dataset.len), duration: 1200, delay: base + 200 + k * 160, ease: "outExpo",
        onUpdate: function () { s.setAttribute("stroke-dasharray", o.l + " " + s.dataset.c); } });
    });
    A.animate(".recent li", { opacity: [0, 1], translateY: [10, 0], delay: A.stagger(50, { start: base }), duration: 500, ease: "outQuad" });
    firstRender = false;
  }

  function intro() {
    if (!canAnimate) return;
    var tl = A.createTimeline({ defaults: { ease: "outExpo", duration: 700 } });
    tl.add(".hero-icon", { opacity: [0, 1], scale: [0.6, 1], rotate: [-12, 0], duration: 800, ease: "outBack(1.6)" })
      .add(".eyebrow", { opacity: [0, 1], translateY: [8, 0] }, "-=550")
      .add(".title .word", { opacity: [0, 1], translateY: [22, 0], delay: A.stagger(80) }, "-=550")
      .add(".subtitle", { opacity: [0, 1], translateY: [10, 0] }, "-=500")
      .add(".hero-actions .btn", { opacity: [0, 1], translateX: [14, 0], delay: A.stagger(70) }, "-=550")
      .add(".manage .section-head", { opacity: [0, 1], translateY: [14, 0] }, "-=500")
      .add(".tile", { opacity: [0, 1], translateY: [24, 0], scale: [0.96, 1], delay: A.stagger(60) }, "-=550")
      .add(".section-title, .kpi", { opacity: [0, 1], translateY: [18, 0], delay: A.stagger(50) }, "-=500")
      .add(".card", { opacity: [0, 1], translateY: [22, 0], delay: A.stagger(70) }, "-=500");
    try { A.animate(A.svg.createDrawable(".hero-lines .line"), { draw: ["0 0", "0 1"], duration: 2000, delay: A.stagger(250), ease: "inOutQuad" }); } catch (e) { /* ignore */ }
    A.animate(".orb", { translateX: function () { return A.utils.random(-30, 30); }, translateY: function () { return A.utils.random(-20, 20); },
      scale: function () { return A.utils.random(90, 115) / 100; }, duration: function () { return A.utils.random(3500, 5500); }, alternate: true, loop: true, ease: "inOutSine" });
    A.animate(".flow li", { opacity: [0, 1], translateX: [-14, 0], delay: A.stagger(110, { start: 1300 }), duration: 600, ease: "outQuad" });
    A.animate(".step-dot", { scale: [0.4, 1], delay: A.stagger(110, { start: 1350 }), duration: 900, ease: "outElastic(1, .6)" });
    document.querySelectorAll(".kpi, .tile").forEach(function (k) {
      k.addEventListener("mouseenter", function () { A.animate(k, { translateY: -3, duration: 250, ease: "outQuad" }); });
      k.addEventListener("mouseleave", function () { A.animate(k, { translateY: 0, duration: 250, ease: "outQuad" }); });
    });
  }

  /* ------------------------------------------------------------------ navigation */
  function openRecord(entity, id) {
    var x = xrm();
    if (!x || !id || id.length < 30) return;
    x.Navigation.openForm({ entityName: entity, entityId: id });
  }
  function previewOnly(what) { toast(what + " opens inside the PMO Demand Hub app."); }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-action]");
    if (!b) return;
    var x = xrm(), a = b.dataset.action;
    if (a === "list") { if (x) x.Navigation.navigateTo({ pageType: "entitylist", entityName: b.dataset.entity }); else previewOnly("The table view"); }
    else if (a === "new") {
      if (!x) { previewOnly("The new record form"); return; }
      x.Navigation.openForm({ entityName: b.dataset.entity, useQuickCreateForm: true }).then(function () { refreshCounts(); loadDashboard(); });
    }
    else if (a === "board") {
      if (!x) { location.href = "board.html"; return; }
      x.Navigation.navigateTo({ pageType: "webresource", webresourceName: "csm_/pmo/board.html" }, { target: 1 })
        .then(null, function () { x.Navigation.navigateTo({ pageType: "entitylist", entityName: "csm_proposal" }); });
    }
    else if (a === "import") openPanel(b.dataset.table);
    else if (a === "template") templateFor(b.dataset.table || state.table);
    else if (a === "close") closePanel();
    else if (a === "run-import") doImport();
    else if (a === "starter") loadStarter();
  });
  sel.addEventListener("change", function () { state.table = sel.value; tableHint(); if (state.parsed) usePreparsed(document.getElementById("dropTitle").textContent.split(" · ")[0], state.parsed); });
  document.getElementById("fileInput").addEventListener("change", function (e) { loadFile(e.target.files[0]); });
  var drop = document.getElementById("drop");
  ["dragenter", "dragover"].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add("over"); }); });
  ["dragleave", "drop"].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove("over"); }); });
  drop.addEventListener("drop", function (e) { if (e.dataTransfer.files[0]) loadFile(e.dataTransfer.files[0]); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !overlay.hidden) closePanel(); });
  overlay.addEventListener("click", function (e) { if (e.target === overlay) closePanel(); });

  (function greet() {
    var x = xrm(), name = "";
    try { if (x) name = x.Utility.getGlobalContext().userSettings.userName.split(" ")[0]; } catch (e) { /* ignore */ }
    var h = new Date().getHours();
    document.getElementById("greeting").textContent = (h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening") + (name ? ", " + name : "") + " · Zava IT PMO";
  })();

  /* test hook for automated checks in preview mode */
  if (backend.preview) window.__pmo = { backend: backend, parseCsv: parseCsv, mapHeader: mapHeader, runImport: runImport, TABLES: BYKEY, usePreparsed: usePreparsed, openPanel: openPanel, doImport: doImport };

  renderTiles();
  intro();
  refreshCounts();
  loadDashboard();
})();
