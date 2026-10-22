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
AGENT_ICONS = ROOT / "docs" / "resources" / "advanced" / "agent-icon"

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
    """Glifo Phosphor (contorno scuro, strato duotone nel colore dell'argomento), logo o icona di un agente."""
    if spec.startswith(("logo:", "agent:")):
        kind, name = spec.split(":", 1)
        if kind == "agent":  # icona dell'agente caricata nei lab
            file = AGENT_ICONS / name
        else:
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
# Ogni schema riporta i nomi esatti dei componenti creati nei lab Advanced della Standard
# Harness (Lab 00, S01-S07). Se un lab cambia un nome, va cambiato anche qui.

DA = "agent:demand-it-agent-192.png"     # icona caricata in S01
COM = "agent:committee-agent-192.png"    # icona dell'Agente Comitato


def panoramica():
    """S01-S07: chi parla con chi."""
    d = Diagram(1015, 460)
    A, B, C, D = 20, 275, 530, 785
    u = d.node(A, 40, 200, "Proponenti e analisti", "users-three", "agents", "Teams e M365 Copilot (S07)")
    mail = d.node(A, 250, 200, "Casella del PMO", "logo:outlook", "tools", "oggetto Proposta progetto")
    kn = d.node(B, 140, 200, "PMO Knowledge", "logo:sharepoint", "knowledge", "conoscenza SharePoint")
    da = d.node(B, 40, 200, "Agente Demand IT", DA, "ai-engine", "orchestratore (S01)")
    trg = d.node(B, 250, 200, "Flow del trigger", "logo:power-automate", "triggers", "When a new email arrives (S05)")
    intk = d.node(C, 10, 200, "Intake Proposte", "robot", "agents", "child agent (S02-S05)")
    com = d.node(C, 100, 200, "Agente Comitato", COM, "agents", "agente connesso (S02)")
    dos = d.node(C, 190, 200, "Genera dossier", "logo:power-automate", "tools", "topic e agent flow (S06)")
    teams = d.node(D, 10, 200, "Canale del PMO", "logo:teams", "tools", "Notifica PMO in Teams")
    dv = d.node(D, 100, 200, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse (Lab 00)")
    od = d.node(D, 190, 200, "OneDrive", "logo:onedrive", "tools", "dossier Word e link")
    d.arrow([(u["r"], 70), (B, 70)], "ai-engine")
    d.arrow([(kn["cx"], kn["y"]), (kn["cx"], da["b"])], "knowledge", dashed=True)
    d.arrow([(mail["r"], 280), (B, 280)], "triggers")
    for ty in (40, 130, 220):
        d.arrow([(da["r"], 70), (505, 70), (505, ty), (C, ty)], "ai-engine")
    d.arrow([(trg["r"], 300), (497, 300), (497, 100), (da["r"], 100)], "triggers", label="Sends a prompt", at=(430, 335))
    d.arrow([(intk["r"], 40), (D, 40)], "tools")
    d.arrow([(intk["r"], 55), (757, 55), (757, 120), (D, 120)], "knowledge")
    d.arrow([(com["r"], 140), (D, 140)], "knowledge", dashed=True)
    d.arrow([(dos["r"], 220), (D, 220)], "tools")
    d.arrow([(trg["cx"], trg["b"]), (trg["cx"], 430), (1000, 430), (1000, 130), (dv["r"], 130)], "triggers", label="Registra proposta email", at=(700, 430))
    d.save("panoramica-sistema")


def architettura_standard():
    """S01-S06: i componenti dell'Agente Demand IT e dello specialista."""
    d = Diagram(1010, 620)
    d.lane(20, 20, 620, 470, "Agente Demand IT · csm_agentedemand_std", DA, "ai-engine")
    d.node(40, 62, 280, "Conoscenza PMO Knowledge", "logo:sharepoint", "knowledge", "Linee guida PMO, Piano Strategico IT", white=True)
    top = d.node(340, 62, 280, "Topic", "chats-circle", "topics", "Genera dossier di revisione", white=True)
    trg = d.node(340, 140, 280, "Trigger", "lightning", "triggers", "When a new email arrives (V3)", white=True)
    d.lane(40, 150, 280, 325, "Intake Proposte · child agent", "robot", "agents")
    tools = [("Carica business case", "crea proposta e carica il PDF"),
             ("Analizza business case", "prompt Estrai dati business case"),
             ("Crea valutazione", "prompt Valuta proposta,\nconferma dell'utente"),
             ("Notifica PMO in Teams", "adaptive card nel canale")]
    ys = [190, 255, 320, 401]
    for (label, sub), y in zip(tools, ys):
        d.node(55, y, 250, label, "logo:power-automate", "tools", sub, white=True, h=74 if "\n" in sub else 58)
    d.lane(680, 20, 310, 150, "Agente Comitato · connesso", COM, "agents")
    k2 = d.node(695, 62, 280, "Conoscenza Dataverse", "logo:dataverse", "knowledge", "Program, Evaluation Criterion,\nRequester, Proposal, Assessment", white=True)
    fd = d.node(680, 200, 310, "Agent flow Genera dossier", "logo:power-automate", "tools", "prompt Dossier di revisione")
    od = d.node(680, 285, 310, "OneDrive", "logo:onedrive", "tools", "Dossier_AS-####.docx, link")
    pa = d.node(680, 370, 310, "Flow del trigger", "logo:power-automate", "triggers", "prompt Classifica email PMO,\nRegistra proposta email")
    dv = d.node(340, 530, 300, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse, soluzione PMO Demand IT")
    d.arrow([(640, 45), (680, 45)], "agents")
    d.arrow([(top["r"], 87), (665, 87), (665, 225), (680, 225)], "topics")
    d.arrow([(fd["cx"], fd["b"]), (od["cx"], od["y"])], "tools")
    d.arrow([(trg["r"], 165), (655, 165), (655, 395), (680, 395)], "triggers")
    d.arrow([(180, 475), (180, 555), (dv["x"], 555)], "knowledge", label="scrivono", at=(180, 512))
    d.arrow([(pa["cx"], pa["b"]), (pa["cx"], 545), (dv["r"], 545)], "triggers")
    d.arrow([(k2["r"], 95), (1000, 95), (1000, 575), (dv["r"], 575)], "knowledge", dashed=True)
    d.save("architettura-standard")


def workflow_chat():
    """S02-S04: intake, analisi e valutazione in chat."""
    a = [("Utente", "user-circle", "agents"), ("Agente Demand IT", DA, "ai-engine"),
         ("Intake Proposte", "robot", "agents"), ("PMO Demand Hub", "logo:dataverse", "knowledge")]
    m = [(0, 1, "Allega il business case", "call"), (1, 2, "Delega l'intake", "call"),
         (2, 2, "Accetta solo PDF: un DOCX viene rifiutato", "note"),
         (2, 3, "Carica business case: proposta e PDF", "call"), (3, 2, "Codice PP-####", "reply"),
         (2, 3, "Analizza business case: Estrai dati, proponente RQ-####", "call"),
         (2, 0, "Riepilogo; programma PG-### da confermare se manca", "reply"),
         (0, 1, "Valuta la proposta", "call"), (1, 2, "Delega la valutazione", "call"),
         (2, 0, "Conferma richiesta prima di Crea valutazione", "reply"), (0, 2, "Conferma", "call"),
         (2, 3, "Crea valutazione: Valuta proposta, punteggio, AS-####", "call"),
         (2, 0, "Punteggio, indicazione e codice AS-####", "reply")]
    sequence("workflow-chat", a, m)


def workflow_email_standard():
    """S05: il flow del trigger in Power Automate."""
    d = Diagram(1000, 850)
    x, w = 200, 340
    t = d.node(x, 20, w, "When a new email arrives (V3)", "logo:outlook", "triggers", "Split On: una esecuzione per email")
    h = d.node(x, 104, w, "Html to text", "file-text", "tools")
    c = d.node(x, 180, w, "Classifica", "logo:ai-builder", "tools", "prompt Classifica email PMO")
    dec = d.node(x, 264, w, "Proposta rilevata", "git-branch", "system", "Classifica contiene Proposta?")
    lo = d.node(x, 348, w, "Per ogni allegato", "arrows-clockwise", "tools", "condizione Allegato PDF")
    r = d.node(x, 432, w, "Registra proposta email", "logo:dataverse", "knowledge", "riga in Proposals, canale Email")
    cd = d.node(x, 516, w, "Carica documento email", "logo:dataverse", "knowledge", "PDF in Business Case Document")
    ag = d.node(x, 600, w, "Sends a prompt to the specified copilot", DA, "ai-engine", "Agente Demand IT")
    an = d.node(x, 684, w, "Analizza business case", "robot", "agents", "strumento di Intake Proposte")
    nt = d.node(x, 768, w, "Notifica PMO in Teams", "logo:teams", "tools", "adaptive card")
    dv = d.node(650, 264, 320, "Da verificare", "git-branch", "system", "Classifica contiene Incerta?")
    man = d.node(650, 360, 320, "Avvisa verifica manuale", "logo:outlook", "tools", "Send an email (V2)")
    fine = d.node(650, 456, 320, "Fine senza azioni", "x-circle", "system", "RispostaAutomatica o NonPertinente")
    for a_, b_ in ((t, h), (h, c), (c, dec), (dec, lo), (lo, r), (r, cd), (cd, ag), (ag, an), (an, nt)):
        d.arrow([(a_["cx"], a_["b"]), (b_["cx"], b_["y"])], "instructions")
    d.text(dec["cx"] + 8, dec["b"] + 24, "Sì", 11, MUTED, 600)
    d.arrow([(dec["r"], dec["cy"]), (dv["x"], dv["cy"])], color=NEUTRAL_ARROW, label="No", at=(595, dec["cy"]))
    d.arrow([(dv["cx"], dv["b"]), (man["cx"], man["y"])], "platform", label="Sì", at=(dv["cx"] + 20, 338))
    d.arrow([(dv["r"], dv["cy"]), (985, dv["cy"]), (985, fine["cy"]), (fine["r"], fine["cy"])], color=NEUTRAL_ARROW, label="No", at=(985, 400))
    d.save("workflow-email-standard")


def workflow_dossier():
    """S06: dal topic al link del documento."""
    d = Diagram(1015, 330)
    u = d.node(20, 30, 210, "Utente", "user-circle", "agents", "Mi prepari il dossier\ndi AS-####?")
    top = d.node(270, 30, 230, "Topic", "chats-circle", "topics", "Genera dossier di revisione,\nchiede il codice se manca")
    d.lane(540, 15, 455, 300, "Agent flow · Genera dossier", "logo:power-automate", "tools")
    p = d.node(555, 55, 425, "Run a prompt", "logo:ai-builder", "tools", "prompt Dossier di revisione: output Document,\ntemplate Word, conoscenza Dataverse", white=True)
    f = d.node(555, 140, 425, "Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx", white=True, h=58)
    sl = d.node(555, 210, 425, "Create share link", "logo:onedrive", "tools", "View, Organization: output DossierURL", white=True, h=58)
    card = d.node(270, 210, 230, "Adaptive card", "cards", "topics", "link al dossier in chat")
    d.arrow([(u["r"], 64), (top["x"], 64)], "topics")
    d.arrow([(top["r"], 64), (p["x"], 64)], "topics", label="CodiceValutazione", at=(520, 92))
    d.arrow([(p["cx"], p["b"]), (f["cx"], f["y"])], "tools")
    d.arrow([(f["cx"], f["b"]), (sl["cx"], sl["y"])], "tools")
    d.arrow([(sl["x"], sl["cy"]), (card["r"], sl["cy"])], "tools", dashed=True)
    d.save("workflow-dossier")


def workflow_revisione():
    """S02: preparazione della revisione con l'agente connesso."""
    a = [("Utente", "user-circle", "agents"), ("Agente Demand IT", DA, "ai-engine"),
         ("Agente Comitato", COM, "agents"), ("PMO Demand Hub", "logo:dataverse", "knowledge")]
    m = [(0, 1, "Preparami alla revisione di PP-####", "call"), (1, 2, "Delega all'agente connesso", "call"),
         (2, 3, "Legge proposta, criteri e pesi", "call"),
         (2, 0, "Briefing e domande per sponsor e architetto", "reply"),
         (1, 0, "Al più una frase in aggiunta", "reply")]
    sequence("workflow-revisione", a, m)


if __name__ == "__main__":
    for old in OUT.glob("*.svg"):
        old.unlink()
    panoramica()
    architettura_standard()
    workflow_chat()
    workflow_email_standard()
    workflow_dossier()
    workflow_revisione()
