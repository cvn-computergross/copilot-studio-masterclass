"""Schemi della pagina "Architettura e workflow" (docs/advanced/architettura-e-workflow.md).

Disegna ogni schema come immagine SVG nello stile delle slide del corso: riquadri tinti nel
colore dell'argomento con glifo dell'Icon Pack (Phosphor duotone) o logo Microsoft, frecce
sottili colorate, ritorni tratteggiati. Le immagini vanno in docs/advanced/images/ e si vedono
uguali su GitHub e nel sito.

Uso, dalla cartella principale della repo:
    python tools/diagrams.py

Per cambiare uno schema si modifica la sua funzione qui sotto e si rilancia lo script.
"""
import base64
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
GLYPHS = ROOT / "docs" / ".vitepress" / "theme" / "icons"
LOGOS = ROOT / "docs" / "public" / "logos"
OUT = ROOT / "docs" / "advanced" / "images"

FONT = "Segoe UI, Inter, Helvetica, Arial, sans-serif"
INK, BODY, MUTED, RULE, ICON = "#1B1B1B", "#363B42", "#6B7480", "#E2E5E9", "#1F2937"
NEUTRAL_ARROW = "#B4BAC2"
# argomento -> (colore pieno, tinta, riempimento dell'icona), come nelle slide
FAM = {
    "instructions": ("#0F6CBD", "#EDF4FB", "#5AA9F0"),
    "ai-engine": ("#0E2841", "#E3E8EF", "#7AB3E0"),
    "knowledge": ("#0B7A3E", "#E6F4EC", "#5CC689"),
    "tools": ("#B4540A", "#FDEEE0", "#FFA94D"),
    "topics": ("#5B5FC7", "#EEEEFB", "#9B9CF2"),
    "agents": ("#0E7C86", "#E3F3F4", "#4FC3C7"),
    "triggers": ("#646800", "#F2F5DA", "#B3C94A"),
    "lifecycle": ("#A02B93", "#F8EDF6", "#D98BCB"),
    "platform": ("#9A6700", "#FDF3DC", "#FFC83D"),
    "system": ("#4A5563", "#EDEFF2", "#C9CED6"),
    "risk": ("#C4314B", "#FBE9EC", "#F06A6A"),
    "standard": ("#A02B93", "#F8EDF6", "#D98BCB"),
    "github": ("#0F6CBD", "#EDF4FB", "#5AA9F0"),
}


def icon_svg(spec, x, y, size, fam):
    """Glifo Phosphor (contorno scuro, strato duotone nel colore dell'argomento) o logo."""
    if spec.startswith("logo:"):
        name = spec[5:]
        file = next(f for f in (LOGOS / f"{name}.svg", LOGOS / f"{name}.png") if f.exists())
        mime = "image/svg+xml" if file.suffix == ".svg" else "image/png"
        data = base64.b64encode(file.read_bytes()).decode()
        return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:{mime};base64,{data}" preserveAspectRatio="xMidYMid meet"/>'
    src = (GLYPHS / f"{spec}.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path[^>]*/>", src)
    fill = FAM[fam][2]
    out = []
    for p in paths:
        if 'opacity="0.2"' in p:
            out.append(p.replace('opacity="0.2"', f'fill="{fill}"'))
        else:
            out.append(p.replace("<path", f'<path fill="{ICON}"'))
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 256 256">{"".join(out)}</svg>'


class Diagram:
    def __init__(self, w, h):
        self.w, self.h, self.parts, self.markers = w, h, [], set()

    def text(self, x, y, s, size=13, color=BODY, weight=400, anchor="start", italic=False):
        style = ' font-style="italic"' if italic else ""
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}"{style}>{escape(s)}</text>')

    def node(self, x, y, w, label, icon, fam, sub=None, white=False, h=None):
        """Riquadro con icona ed etichetta; white=True dentro un'area tinta."""
        solid, tint, _ = FAM[fam]
        lines = sub.split("\n") if sub else []
        h = h or (44 + 16 * len(lines) if lines else 48)
        if white:
            self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FFFFFF" stroke="{RULE}"/>')
        else:
            self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{tint}"/>')
        self.parts.append(icon_svg(icon, x + 12, y + h / 2 - 13, 26, fam))
        ty = y + h / 2 - 8 * len(lines) + 5
        self.text(x + 48, ty, label, 13.5, solid, 600)
        for i, line in enumerate(lines):
            self.text(x + 48, ty + 17 + 16 * i, line, 12, MUTED)
        return {"x": x, "y": y, "w": w, "h": h, "cx": x + w / 2, "cy": y + h / 2, "r": x + w, "b": y + h}

    def lane(self, x, y, w, h, title, icon, fam):
        solid, tint, fill = FAM[fam]
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{tint}" stroke="{fill}"/>')
        self.parts.append(icon_svg(icon, x + 14, y + 12, 22, fam))
        self.text(x + 44, y + 28, title.upper(), 11.5, solid, 600)

    def _marker(self, color):
        mid = "m" + color.strip("#")
        if mid not in self.markers:
            self.markers.add(mid)
            self.parts.insert(0, f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker></defs>')
        return mid

    def arrow(self, pts, fam="ai-engine", dashed=False, label=None, at=None, color=None):
        color = color or FAM[fam][0]
        mid = self._marker(color)
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6"{dash} marker-end="url(#{mid})"/>')
        if label:
            lx, ly = at or ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
            wpx = 6.6 * len(label) + 10
            self.parts.append(f'<rect x="{lx - wpx / 2}" y="{ly - 10}" width="{wpx}" height="18" rx="9" fill="#FFFFFF" stroke="{RULE}"/>')
            self.text(lx, ly + 3.5, label, 11, color if color != NEUTRAL_ARROW else MUTED, 500, "middle")

    def badge(self, x, y, n, color="#0E2841"):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{color}"/>')
        self.text(x, y + 4, str(n), 11, "#FFFFFF", 600, "middle")

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" font-family="{FONT}">'
               f'<rect x="0.5" y="0.5" width="{self.w - 1}" height="{self.h - 1}" rx="14" fill="#FFFFFF" stroke="{RULE}"/>'
               + "".join(self.parts) + "</svg>")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print("schema", name)


def sequence(name, actors, messages, width=1000):
    """Schema a corsie: attori in alto, linee verticali, chiamate piene e risposte tratteggiate."""
    n = len(actors)
    col = (width - 80) / n
    xs = [60 + col * i + col / 2 for i in range(n)]
    step, top = 46, 110
    d = Diagram(width, top + step * len(messages) + 30)
    for (label, icon, fam), cx in zip(actors, xs):
        d.node(cx - col / 2 + 8, 20, col - 16, label, icon, fam, white=True, h=56)
        d.parts.append(f'<line x1="{cx}" y1="76" x2="{cx}" y2="{d.h - 20}" stroke="{RULE}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    for i, (a, b, text, kind) in enumerate(messages):
        y = top + step * i
        d.badge(26, y, i + 1)
        if a == b:  # passo interno: etichetta tinta sulla corsia
            solid, tint, _ = FAM[actors[a][2]]
            wpx = 6.6 * len(text) + 20
            d.parts.append(f'<rect x="{xs[a] - 8}" y="{y - 12}" width="{wpx}" height="24" rx="12" fill="{tint}"/>')
            d.text(xs[a] + 2, y + 4, text, 12, solid, 500)
            continue
        reply = kind == "reply"
        color = NEUTRAL_ARROW if reply else FAM["instructions"][0]
        x1, x2 = xs[a], xs[b]
        sign = 1 if x2 > x1 else -1
        d.arrow([(x1 + 4 * sign, y), (x2 - 4 * sign, y)], dashed=reply, color=color)
        d.text((x1 + x2) / 2, y - 7, text, 12, MUTED if reply else BODY, 500, "middle")
    d.save(name)


# --- schemi -----------------------------------------------------------------------------

def panoramica():
    d = Diagram(1015, 440)
    A, B, C, D = 20, 275, 530, 785
    u = d.node(A, 40, 200, "Proponenti e analisti", "users-three", "agents", "Teams, Microsoft 365 Copilot")
    mail = d.node(A, 210, 200, "Casella del PMO", "logo:outlook", "tools", "oggetto Proposta progetto")
    p = d.node(A, 360, 200, "Analista PMO", "user-check", "agents", "decide e conferma")
    da = d.node(B, 40, 200, "Agente Demand IT", "cpu", "ai-engine", "orchestratore")
    auto = d.node(B, 210, 200, "Automazione email", "lightning", "triggers", "flow o workflow")
    intk = d.node(C, 10, 200, "Intake e valutazione", "robot", "agents", "child agent o skill")
    doc = d.node(C, 95, 200, "Dossier di revisione", "logo:word", "lifecycle", "documento Word")
    ac = d.node(C, 180, 200, "Agente Comitato", "link", "agents", "agente connesso")
    teams = d.node(C, 300, 200, "Scheda Teams", "logo:teams", "tools", "per il PMO")
    dv = d.node(D, 10, 200, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse")
    cal = d.node(D, 180, 200, "Calendari interni", "calendar-dots", "platform", "Outlook o Work IQ")
    d.arrow([(u["r"], 70), (B, 70)], "ai-engine")
    d.arrow([(mail["r"], 240), (B, 240)], "triggers")
    d.arrow([(auto["cx"], 210), (auto["cx"], da["b"])], "triggers")
    for target, ty in ((intk, 40), (doc, 125), (ac, 210)):
        d.arrow([(da["r"], 70), (505, 70), (505, ty), (C, ty)], "ai-engine")
    d.text(510, 202, "delega", 11, MUTED, 500)
    d.arrow([(intk["r"], 40), (D, 40)], "knowledge")
    d.arrow([(ac["r"], 195), (757, 195), (757, 60), (D, 60)], "knowledge")
    d.arrow([(ac["r"], 225), (D, 225)], "platform")
    d.arrow([(auto["r"], 262), (1000, 262), (1000, 40), (dv["r"], 40)], "triggers")
    d.arrow([(auto["r"], 252), (500, 252), (500, 330), (C, 330)], "triggers")
    d.arrow([(p["r"], 385), (248, 385), (248, 90), (B, 90)], dashed=True, color=NEUTRAL_ARROW, label="conferma", at=(248, 315))
    d.arrow([(p["r"], 400), (auto["cx"], 400), (auto["cx"], auto["b"])], dashed=True, color=NEUTRAL_ARROW, label="revisione umana", at=(330, 400))
    d.save("panoramica-sistema")


def architettura_standard():
    d = Diagram(1010, 560)
    d.lane(20, 20, 620, 420, "Agente Demand IT · csm_agentedemand_std", "cpu", "ai-engine")
    d.node(40, 60, 280, "Conoscenza", "books", "knowledge", "Linee guida PMO, Piano strategico", white=True)
    top = d.node(340, 60, 280, "Topic Genera dossier", "chats-circle", "topics", "di revisione", white=True)
    trg = d.node(340, 140, 280, "Trigger Nuova proposta", "lightning", "triggers", "via email", white=True)
    d.lane(40, 150, 280, 275, "Child agent · Intake proposte", "robot", "agents")
    steps = [("Carica business case", None), ("Analizza business case", "prompt Estrai dati"),
             ("Crea valutazione", "prompt Valuta, conferma utente"), ("Notifica PMO in Teams", None)]
    for i, (label, sub) in enumerate(steps):
        d.node(55, 190 + 58 * i, 250, label, "logo:power-automate", "tools", sub, white=True, h=50)
    d.lane(680, 20, 310, 130, "Agente Comitato · std", "link", "agents")
    k2 = d.node(695, 60, 280, "Conoscenza Dataverse", "logo:dataverse", "knowledge", "5 tabelle csm_", white=True)
    fd = d.node(680, 180, 310, "Flow Genera dossier", "logo:power-automate", "tools", "prompt Dossier, OneDrive e link")
    pa = d.node(680, 270, 310, "Power Automate", "logo:power-automate", "tools", "Classifica email PMO, ciclo PDF")
    dv = d.node(340, 480, 300, "Dataverse", "logo:dataverse", "knowledge", "tabelle csm_ del PMO Demand Hub")
    d.arrow([(640, 40), (680, 40)], "agents", label="agente connesso", at=(660, 160 - 120))
    d.arrow([(top["r"], 85), (665, 85), (665, 205), (680, 205)], "topics")
    d.arrow([(trg["r"], 165), (655, 165), (655, 295), (680, 295)], "triggers")
    d.arrow([(180, 425), (180, 505), (dv["x"], 505)], "knowledge", label="scrive", at=(180, 465))
    d.arrow([(pa["cx"], pa["b"]), (pa["cx"], 495), (dv["r"], 495)], "knowledge")
    d.arrow([(k2["r"], 88), (1000, 88), (1000, 520), (dv["r"], 520)], "knowledge", dashed=True)
    d.save("architettura-standard")


def architettura_github():
    d = Diagram(1010, 540)
    d.lane(20, 20, 620, 330, "Agente Demand IT - GH · csm_agentedemand_gh", "cpu", "ai-engine")
    d.node(40, 60, 280, "Conoscenza", "books", "knowledge", "Linee guida PMO, Piano strategico", white=True)
    mcp1 = d.node(40, 140, 280, "Dataverse MCP Server", "hard-drives", "tools",
                  "modalità User\nsearch, describe, read_query,\ncreate_record, update_record", white=True)
    skills = [("proposal-intake", None, "puzzle-piece"), ("proposal-scoring", "sola lettura, rubrica", "puzzle-piece"),
              ("evaluation-recording", "dopo conferma", "puzzle-piece"), ("review-dossier-document", "Python, python-docx", "code")]
    for i, (label, sub, icon) in enumerate(skills):
        d.node(340, 60 + 68 * i, 280, label, icon, "github", sub, white=True, h=56)
    d.lane(680, 20, 310, 250, "Agente Comitato - GH", "link", "agents")
    mcp2 = d.node(695, 60, 280, "Dataverse MCP Server", "hard-drives", "tools", "modalità Maker\nsearch, describe, read_query", white=True)
    d.node(695, 160, 280, "Work IQ (Preview)", "calendar-dots", "platform", "persone e calendari interni", white=True)
    d.lane(20, 380, 620, 130, "Workflow · Intake proposte via email", "tree-view", "github")
    cl = d.node(40, 425, 170, "Classify", "arrows-split", "github", white=True, h=56)
    ai = d.node(240, 425, 180, "Agente inline", "robot", "agents", "Conferma programma", white=True, h=56)
    ap = d.node(450, 425, 170, "Nodo Agent", "cpu", "ai-engine", "orchestratore", white=True, h=56)
    dv = d.node(680, 425, 310, "Dataverse", "logo:dataverse", "knowledge", "tabelle e note")
    d.arrow([(cl["r"], 453), (ai["x"], 453)], "github")
    d.arrow([(ai["r"], 453), (ap["x"], 453)], "github")
    d.arrow([(640, 40), (680, 40)], "agents", label="agente connesso", at=(660, 40))
    d.arrow([(ap["cx"], ap["y"]), (ap["cx"], 350)], "ai-engine", label="chiama", at=(ap["cx"], 400))
    d.arrow([(180, mcp1["b"]), (180, 365), (660, 365), (660, 445), (dv["x"], 445)], "knowledge")
    d.arrow([(mcp2["r"], 90), (1000, 90), (1000, 450), (dv["r"], 450)], "knowledge")
    d.arrow([(640, 480), (dv["x"], 480)], "github")
    d.save("architettura-github")


def workflow_chat():
    a = [("Analista o proponente", "user-circle", "agents"), ("Agente Demand IT", "cpu", "ai-engine"),
         ("Intake: child agent o skill", "robot", "agents"), ("Dataverse", "logo:dataverse", "knowledge")]
    m = [(0, 1, "Allega il business case PDF o DOCX", "call"), (1, 2, "Delega o carica la skill", "call"),
         (2, 2, "Controlli: formato, dimensione, testo", "note"), (2, 3, "Cerca il proponente per email", "call"),
         (2, 3, "Crea o riusa proponente, crea proposta", "call"), (3, 2, "Codici SP-xxxxx e PP-xxxxx", "reply"),
         (2, 0, "Riepilogo; programma da confermare se ambiguo", "reply"), (0, 1, "Valuta la proposta", "call"),
         (1, 3, "Legge programma e criteri pesati", "call"), (1, 0, "Tabella criteri, punteggio, indicazione", "reply"),
         (0, 1, "Conferma la registrazione", "call"), (1, 3, "Crea valutazione AS-xxxxx, stato Assessed", "call"),
         (1, 0, "Codice della valutazione", "reply")]
    sequence("workflow-chat", a, m)


def workflow_email_standard():
    d = Diagram(1000, 760)
    x, w = 220, 330
    t = d.node(x, 20, w, "When a new email arrives (V3)", "logo:outlook", "triggers", "oggetto Proposta progetto, con allegati")
    h = d.node(x, 104, w, "Html to text", "file-text", "tools")
    c = d.node(x, 180, w, "Run a prompt", "logo:ai-builder", "tools", "Classifica email PMO")
    dec = d.node(x, 264, w, "Proposta rilevata?", "git-branch", "system")
    lo = d.node(x, 350, w, "Per ogni allegato PDF", "arrows-clockwise", "tools")
    r = d.node(x, 426, w, "Crea la proposta in Dataverse", "logo:dataverse", "knowledge", "e carica il documento")
    ag = d.node(x, 510, w, "Sends a prompt to the specified copilot", "cpu", "ai-engine", "Agente Demand IT")
    an = d.node(x, 594, w, "Analizza business case", "sparkle", "agents")
    nt = d.node(x, 670, w, "Notifica PMO in Teams", "logo:teams", "tools")
    fine = d.node(650, 264, 300, "Fine senza azioni", "x-circle", "system")
    man = d.node(650, 350, 300, "Email al PMO", "logo:outlook", "tools", "da verificare manualmente")
    for a, b in ((t, h), (h, c), (c, dec), (dec, lo), (lo, r), (r, ag), (ag, an), (an, nt)):
        d.arrow([(a["cx"], a["b"]), (b["cx"], b["y"])], "instructions")
    d.text(dec["cx"] + 8, dec["b"] + 24, "Sì", 11, MUTED, 600)
    d.arrow([(dec["r"], dec["cy"]), (fine["x"], fine["cy"])], color=NEUTRAL_ARROW, label="No: risposta automatica o non pertinente", at=(600, dec["cy"] - 18))
    d.arrow([(dec["r"], dec["cy"] + 10), (600, dec["cy"] + 10), (600, man["cy"]), (man["x"], man["cy"])], "platform", label="Incerta", at=(600, 335))
    d.save("workflow-email-standard")


def workflow_email_github():
    d = Diagram(1000, 760)
    x, w = 250, 300
    t = d.node(x, 20, w, "When a new email arrives", "logo:outlook", "triggers", "Proposta progetto, solo con allegati")
    v = d.node(x, 104, w, "Avvia elenco proposte", "stack", "system", "variabile ProposteRegistrate")
    cl = d.node(x, 188, w, "Classifica email", "arrows-split", "github", "nodo Classify")
    e1 = d.node(680, 188, 300, "Fine, Succeeded", "check-circle", "system", "RispostaAutomatica o NonPertinente")
    hr = d.node(680, 290, 300, "Human review", "user-check", "agents", "Verifica email non chiara")
    iff = d.node(680, 384, 300, "Il revisore conferma?", "git-branch", "system")
    e3 = d.node(680, 470, 300, "Fine, Succeeded", "check-circle", "system")
    ge = d.node(680, 600, 300, "Scope Gestisci errore", "warning-circle", "risk", "avviso in Teams, End Failed")
    d.lane(180, 272, 440, 470, "Scope · Elabora proposta", "tree-structure", "github")
    rows = [("Per ogni allegato", "formato ammesso: PDF o DOCX", "arrows-clockwise", "tools"),
            ("Registra proposta", "documento come nota, ricorda la proposta", "logo:dataverse", "knowledge"),
            ("Agente inline Conferma programma", "Request for information se ambiguo", "robot", "agents"),
            ("Completa con Agente Demand IT", "proposal-intake e proposal-scoring", "cpu", "ai-engine"),
            ("Notifica PMO in Teams", "scheda adattiva", "logo:teams", "tools")]
    nodes = [d.node(200, 312 + 84 * i, 400, l, ic, f, s, white=True, h=60) for i, (l, s, ic, f) in enumerate(rows)]
    for a, b in zip(nodes, nodes[1:]):
        d.arrow([(a["cx"], a["b"]), (b["cx"], b["y"])], "github")
    d.arrow([(t["cx"], t["b"]), (v["cx"], v["y"])], "github")
    d.arrow([(v["cx"], v["b"]), (cl["cx"], cl["y"])], "github")
    d.arrow([(cl["cx"], cl["b"]), (cl["cx"], 272)], "github", label="Proposta", at=(cl["cx"] + 48, 258))
    d.arrow([(cl["r"], cl["cy"]), (e1["x"], e1["cy"])], color=NEUTRAL_ARROW)
    d.arrow([(cl["r"], cl["cy"] + 12), (650, cl["cy"] + 12), (650, hr["cy"]), (hr["x"], hr["cy"])], "agents", label="Other", at=(650, 268))
    d.arrow([(hr["cx"], hr["b"]), (iff["cx"], iff["y"])], "agents")
    d.arrow([(iff["cx"], iff["b"]), (e3["cx"], e3["y"])], color=NEUTRAL_ARROW, label="No", at=(iff["cx"] + 22, 452))
    d.arrow([(iff["x"], iff["cy"]), (620, iff["cy"])], "agents", label="Yes", at=(648, iff["cy"] - 14))
    d.arrow([(620, 700), (650, 700), (650, ge["cy"]), (ge["x"], ge["cy"])], "risk", label="Failed o TimedOut", at=(800, 680))
    d.save("workflow-email-github")


def workflow_dossier():
    d = Diagram(1015, 400)
    r = d.node(20, 168, 190, "Richiesta", "user-circle", "agents", "dossier per AS-xxxxx")
    s = d.node(240, 168, 140, "Harness", "git-branch", "system")
    d.lane(415, 10, 585, 180, "Standard harness", "logo:copilot-studio", "standard")
    t1 = d.node(430, 50, 170, "Topic", "chats-circle", "standard", "Genera dossier", white=True)
    f = d.node(615, 50, 165, "Agent flow", "logo:power-automate", "tools", white=True, h=60)
    p = d.node(795, 50, 190, "Prompt Dossier", "logo:ai-builder", "tools", "output Document,\nmodello Word", white=True)
    o = d.node(795, 128, 190, "OneDrive /PMO Dossier", "logo:onedrive", "tools", "link di condivisione", white=True, h=50)
    d.lane(415, 205, 585, 185, "GitHub Copilot harness", "logo:github", "github")
    k = d.node(430, 245, 170, "Skill", "puzzle-piece", "github", "review-dossier-document", white=True)
    m = d.node(615, 245, 165, "Dataverse MCP", "logo:dataverse", "knowledge", "valutazione e criteri", white=True)
    j = d.node(795, 245, 190, "dossier_input.json", "code", "github", white=True, h=60)
    py = d.node(795, 322, 190, "generate_dossier.py", "code", "github", "validazione e punteggio", white=True, h=56)
    w = d.node(615, 322, 165, "dossier_revisione", "logo:word", "lifecycle", ".docx allegato in chat", white=True, h=56)
    d.arrow([(r["r"], r["cy"]), (s["x"], s["cy"])], "instructions")
    d.arrow([(s["cx"], s["y"]), (s["cx"], 80), (t1["x"], 80)], "standard", label="Standard", at=(s["cx"], 125))
    d.arrow([(s["cx"], s["b"]), (s["cx"], 275), (k["x"], 275)], "github", label="GitHub Copilot", at=(s["cx"], 240))
    d.arrow([(t1["r"], 80), (f["x"], 80)], "standard")
    d.arrow([(f["r"], 80), (p["x"], 80)], "standard")
    d.arrow([(p["cx"], p["b"]), (o["cx"], o["y"])], "standard")
    d.arrow([(k["r"], 275), (m["x"], 275)], "github")
    d.arrow([(m["r"], 275), (j["x"], 275)], "github")
    d.arrow([(j["cx"], j["b"]), (py["cx"], py["y"])], "github")
    d.arrow([(py["x"], py["cy"]), (w["r"], w["cy"])], "github")
    d.save("workflow-dossier")


def workflow_revisione():
    a = [("Analista PMO", "user-circle", "agents"), ("Agente Demand IT", "cpu", "ai-engine"),
         ("Agente Comitato", "link", "agents"), ("Dataverse", "logo:dataverse", "knowledge"),
         ("Calendari interni", "calendar-dots", "platform")]
    m = [(0, 1, "Preparami alla revisione di PP-xxxxx", "call"), (1, 2, "Delega come agente connesso", "call"),
         (2, 3, "Legge proposta, criteri, valutazione", "call"), (2, 0, "Briefing e domande per sponsor e architetto", "reply"),
         (2, 0, "Offre di prenotare 30 minuti", "reply"), (0, 2, "Sì, con il collega, la prossima settimana", "call"),
         (2, 4, "Risolve la persona e cerca orari liberi", "call"), (2, 0, "Al massimo tre opzioni", "reply"),
         (0, 2, "Confermo l'orario scelto", "call"), (2, 4, "Crea l'evento e invia l'invito", "call"),
         (2, 0, "Evento riletto e confermato", "reply")]
    sequence("workflow-revisione", a, m)


if __name__ == "__main__":
    panoramica()
    architettura_standard()
    architettura_github()
    workflow_chat()
    workflow_email_standard()
    workflow_email_github()
    workflow_dossier()
    workflow_revisione()
