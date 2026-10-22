"""Schemi della pagina "Architettura e workflow" (docs/advanced/architettura-e-workflow.md).

Disegna ogni schema come immagine SVG nello stile delle slide del corso: riquadri tinti nel
colore dell'argomento con glifo dell'Icon Pack (Phosphor duotone) o logo Microsoft, frecce
sottili colorate, ritorni tratteggiati. Le immagini vanno in docs/advanced/images/ e si vedono
uguali su GitHub e nel sito.

Uso, dalla cartella principale della repo:
    python tools/diagrams.py

Per cambiare uno schema si modifica la sua funzione qui sotto e si rilancia lo script.

Controlli di impaginazione: ogni testo viene misurato con le metriche di Segoe UI (Pillow +
segoeui.ttf / seguisb.ttf / segoeuib.ttf, cercati in C:/Windows/Fonts o nella cartella indicata
dalla variabile DIAGRAM_FONT_DIR). Lo script si ferma con l'elenco dei problemi se un testo
esce dal suo riquadro (serve un margine destro di almeno 12px), se un'etichetta di freccia non
sta sulla sua freccia o copre un riquadro, se una freccia attraversa un riquadro o se due
riquadri si sovrappongono. La cornice esterna si adatta al contenuto con margini uguali.
"""
import base64
import math
import os
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from PIL import ImageFont
except ImportError:  # pragma: no cover
    ImageFont = None

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

PAD = 12      # margine minimo fra la fine di un testo e il bordo destro del suo riquadro
MARGIN = 20   # margine fra il contenuto e la cornice esterna, uguale sui quattro lati
GAP = 4       # distanza minima fra un'etichetta di freccia e un riquadro
PILL_H = 18   # altezza delle etichette sulle frecce


class LayoutError(Exception):
    """Uno schema non rispetta i controlli di impaginazione."""

# --- misura dei testi -------------------------------------------------------------------
FONT_DIRS = [os.environ.get("DIAGRAM_FONT_DIR"), "C:/Windows/Fonts", str(Path.home() / ".fonts"),
             "/usr/share/fonts/truetype/msttcorefonts", "/Library/Fonts"]
FONT_FILES = {400: "segoeui.ttf", 600: "seguisb.ttf", 700: "segoeuib.ttf"}
_FONTS = {}


def _font(weight):
    # il browser usa Segoe UI Regular per i pesi fino a 500, Semibold per 600, Bold da 700
    key = 700 if weight >= 650 else 600 if weight >= 550 else 400
    if key not in _FONTS:
        if ImageFont is None:
            sys.exit("diagrams.py: serve Pillow per misurare i testi (pip install pillow)")
        name = FONT_FILES[key]
        path = next((Path(d) / name for d in FONT_DIRS if d and (Path(d) / name).exists()), None)
        if path is None:
            sys.exit(f"diagrams.py: font {name} non trovato; indica la cartella con DIAGRAM_FONT_DIR")
        _FONTS[key] = ImageFont.truetype(str(path), 1000)  # misura a 1000px: larghezze senza hinting
    return _FONTS[key]


def text_width(s, size, weight=400):
    return _font(weight).getlength(s) * size / 1000


def text_box(x, y, s, size, weight=400, anchor="start"):
    """Riquadro occupato da un testo con la linea di base in y."""
    w = text_width(s, size, weight)
    x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
    return (x0, y - 0.76 * size, x0 + w, y + 0.24 * size)


# --- geometria ----------------------------------------------------------------------------
def overlaps(a, b, gap=0.0):
    return a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap


def contains(outer, inner, pad=0.0):
    return (inner[0] >= outer[0] + pad and inner[1] >= outer[1] + pad
            and inner[2] <= outer[2] - pad and inner[3] <= outer[3] - pad)


def inset(r, d):
    return (r[0] + d, r[1] + d, r[2] - d, r[3] - d)


def seg_hits_rect(p, q, r):
    """True se il segmento p-q entra nell'interno del rettangolo r (Liang-Barsky)."""
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, x0 - r[0]), (dx, r[2] - x0), (-dy, y0 - r[1]), (dy, r[3] - y0)):
        if pp == 0:
            if qq <= 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    return t0 < t1


def dist_to_polyline(pt, pts):
    best = math.inf
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, ((pt[0] - x0) * dx + (pt[1] - y0) * dy) / L))
        best = min(best, math.hypot(pt[0] - (x0 + t * dx), pt[1] - (y0 + t * dy)))
    return best


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
    """Raccoglie le parti dello schema e la loro geometria; save() controlla e adatta la cornice."""

    def __init__(self):
        self.parts, self.markers = [], set()
        self.nodes, self.lanes, self.pills, self.free, self.arrows, self.extent = [], [], [], [], [], []
        self.errors = []

    def _text(self, x, y, s, size=13, color=BODY, weight=400, anchor="start", italic=False):
        style = ' font-style="italic"' if italic else ""
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}"{style}>{escape(s)}</text>')
        return text_box(x, y, s, size, weight, anchor)

    def text(self, x, y, s, size=13, color=BODY, weight=400, anchor="start", italic=False):
        """Testo libero: non deve toccare riquadri, intestazioni di corsia o etichette."""
        box = self._text(x, y, s, size, color, weight, anchor, italic)
        self.free.append((s, box))
        return box

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
        rect = (x, y, x + w, y + h)
        boxes = [(label, self._text(x + 48, ty, label, 13.5, solid, 600))]
        for i, line in enumerate(lines):
            boxes.append((line, self._text(x + 48, ty + 17 + 16 * i, line, 12, MUTED)))
        for s, b in boxes:
            if b[2] > x + w - PAD:
                need = math.ceil(b[2] - x + PAD)
                self.errors.append(f"riquadro '{label}': il testo '{s}' supera il margine destro di "
                                   f"{b[2] - (x + w - PAD):.1f}px (larghezza {w}, ne servono almeno {need})")
            if b[1] < y + 4 or b[3] > y + h - 4:
                self.errors.append(f"riquadro '{label}': il testo '{s}' esce in verticale (altezza {h})")
        self.nodes.append((label, rect))
        return {"x": x, "y": y, "w": w, "h": h, "cx": x + w / 2, "cy": y + h / 2, "r": x + w, "b": y + h}

    def lane(self, x, y, w, h, title, icon, fam):
        solid, tint, fill = FAM[fam]
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{tint}" stroke="{fill}"/>')
        self.parts.append(icon_svg(icon, x + 14, y + 12, 22, fam))
        tb = self._text(x + 44, y + 28, title.upper(), 11.5, solid, 600)
        rect, ib = (x, y, x + w, y + h), (x + 14, y + 12, x + 36, y + 34)
        if not contains(rect, ib, 8):
            self.errors.append(f"corsia '{title}': l'icona non sta dentro la corsia")
        if tb[2] > x + w - PAD:
            self.errors.append(f"corsia '{title}': il titolo supera il margine destro di {tb[2] - (x + w - PAD):.1f}px")
        self.lanes.append((title, rect, [ib, tb]))
        return {"x": x, "y": y, "w": w, "h": h, "r": x + w, "b": y + h}

    def _marker(self, color):
        mid = "m" + color.strip("#")
        if mid not in self.markers:
            self.markers.add(mid)
            self.parts.insert(0, f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker></defs>')
        return mid

    def arrow(self, pts, fam="ai-engine", dashed=False, label=None, at=None, color=None):
        """Freccia a segmenti; l'etichetta (at = centro) deve stare su uno dei segmenti."""
        color = color or FAM[fam][0]
        mid = self._marker(color)
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6"{dash} marker-end="url(#{mid})"/>')
        self.arrows.append((label, pts))
        if label:
            lx, ly = at or ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
            wpx = text_width(label, 11, 500) + 20
            rect = (lx - wpx / 2, ly - PILL_H / 2, lx + wpx / 2, ly + PILL_H / 2)
            self.parts.append(f'<rect x="{rect[0]:.1f}" y="{rect[1]}" width="{wpx:.1f}" height="{PILL_H}" rx="9" fill="#FFFFFF" stroke="{RULE}"/>')
            self._text(lx, ly + 3.5, label, 11, color if color != NEUTRAL_ARROW else MUTED, 500, "middle")
            if dist_to_polyline((lx, ly), pts) > 0.75:
                self.errors.append(f"etichetta '{label}': il centro ({lx}, {ly}) non sta sulla sua freccia")
            self.pills.append((label, rect, pts))

    def badge(self, x, y, n, color="#0E2841"):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{color}"/>')
        self._text(x, y + 4, str(n), 11, "#FFFFFF", 600, "middle")
        self.extent.append((x - 10, y - 10, x + 10, y + 10))

    def note(self, x, y, lines, fam):
        """Passo interno di un diagramma di sequenza: etichetta tinta (una o due righe) che parte dalla linea x."""
        solid, tint, _ = FAM[fam]
        wpx = max(text_width(s, 12, 500) for s in lines) + 20
        ph = 24 + 15 * (len(lines) - 1)
        rect = (x - 8, y - ph / 2, x - 8 + wpx, y + ph / 2)
        self.parts.append(f'<rect x="{rect[0]}" y="{rect[1]}" width="{wpx:.1f}" height="{ph}" rx="12" fill="{tint}"/>')
        for k, s in enumerate(lines):
            self._text(x + 2, y + 4 - 7.5 * (len(lines) - 1) + 15 * k, s, 12, solid, 500)
        self.free.append((" ".join(lines), rect))
        return rect

    def vline(self, x, y0, y1):
        self.parts.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{RULE}" stroke-width="1.5" stroke-dasharray="4 4"/>')
        self.extent.append((x - 1, y0, x + 1, y1))

    def check(self):
        errs = list(self.errors)
        nodes = self.nodes
        for i, (a, ra) in enumerate(nodes):
            for b, rb in nodes[i + 1:]:
                if overlaps(ra, rb):
                    errs.append(f"i riquadri '{a}' e '{b}' si sovrappongono")
        headers = [(f"intestazione corsia '{t}'", hb) for t, _, hs in self.lanes for hb in hs]
        for t, _, hs in self.lanes:
            for hb in hs:
                for n, rn in nodes:
                    if overlaps(hb, rn, GAP):
                        errs.append(f"l'intestazione della corsia '{t}' tocca il riquadro '{n}'")
        for i, (p, rp, own) in enumerate(self.pills):
            for n, rn in nodes:
                if overlaps(rp, rn, GAP):
                    errs.append(f"l'etichetta '{p}' copre il riquadro '{n}'")
            for n, hb in headers:
                if overlaps(rp, hb, GAP):
                    errs.append(f"l'etichetta '{p}' copre l'{n}")
            for q, rq, _ in self.pills[i + 1:]:
                if overlaps(rp, rq, GAP):
                    errs.append(f"le etichette '{p}' e '{q}' si sovrappongono")
            for s, fb in self.free:
                if overlaps(rp, fb, GAP):
                    errs.append(f"l'etichetta '{p}' copre il testo '{s}'")
            for t, rl, _ in self.lanes:
                if overlaps(rp, rl) and not contains(rl, rp, GAP):
                    errs.append(f"l'etichetta '{p}' sta a cavallo del bordo della corsia '{t}'")
            for lab, pts in self.arrows:
                if pts is own:
                    continue
                if any(seg_hits_rect(a, b, rp) for a, b in zip(pts, pts[1:])):
                    errs.append(f"l'etichetta '{p}' sta sopra un'altra freccia ({lab or 'senza etichetta'})")
        for s, fb in self.free:
            for n, rn in nodes:
                if overlaps(fb, rn, 2):
                    errs.append(f"il testo '{s}' tocca il riquadro '{n}'")
            for n, hb in headers:
                if overlaps(fb, hb, 2):
                    errs.append(f"il testo '{s}' tocca l'{n}")
        for lab, pts in self.arrows:
            for a, b in zip(pts, pts[1:]):
                for n, rn in nodes:
                    if seg_hits_rect(a, b, inset(rn, 1)):
                        errs.append(f"la freccia {lab or pts[0]} attraversa il riquadro '{n}'")
                for n, hb in headers:
                    if seg_hits_rect(a, b, hb):
                        errs.append(f"la freccia {lab or pts[0]} attraversa l'{n}")
        return errs

    def bounds(self):
        boxes = [r for _, r in self.nodes] + [r for _, r, _ in self.lanes] + [r for _, r, _ in self.pills]
        boxes += [b for _, b in self.free] + [hb for _, _, hs in self.lanes for hb in hs] + self.extent
        for _, pts in self.arrows:  # punta della freccia e spessore della linea
            boxes += [(x - 6, y - 6, x + 6, y + 6) for x, y in pts]
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes))

    def save(self, name):
        errs = self.check()
        if errs:
            raise LayoutError(f"schema {name}: problemi di impaginazione\n  - " + "\n  - ".join(errs))
        x0, y0, x1, y1 = self.bounds()
        x0, y0, x1, y1 = math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1)
        w, h = x1 - x0 + 2 * MARGIN, y1 - y0 + 2 * MARGIN
        dx, dy = MARGIN - x0, MARGIN - y0
        OUT.mkdir(parents=True, exist_ok=True)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">'
               f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="#FFFFFF" stroke="{RULE}"/>'
               f'<g transform="translate({dx} {dy})">' + "".join(self.parts) + "</g></svg>")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"schema {name} ({w}x{h})")


def _splits(text):
    """Possibili divisioni su due righe: prima quelle dopo la punteggiatura, poi le altre."""
    words = text.split(" ")
    out = []
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wmax = max(text_width(a, 12), text_width(b, 12))
        out.append((a[-1] not in ":;,", wmax, [a, b]))
    return sorted(out, key=lambda c: (c[0], c[1]))


def sequence(name, actors, messages, col_min=230):
    """Schema a corsie: attori in alto, linee verticali, chiamate piene e risposte tratteggiate.

    Le colonne si allargano se un'etichetta non sta fra le due linee nemmeno su due righe;
    un'etichetta troppo lunga per una riga va a capo sopra la freccia."""
    n, side = len(actors), 14  # side: spazio fra etichetta e linee verticali
    col = col_min
    for label, _, _ in actors:
        col = max(col, 16 + 48 + text_width(label, 13.5, 600) + PAD)
    for a, b, text, kind in messages:
        two = min((c[1] for c in _splits(text)), default=math.inf)
        if a != b:
            col = max(col, (min(text_width(text, 12), two) + 2 * side) / abs(b - a))
        else:  # la nota non deve superare la linea successiva
            col = max(col, min(text_width(text, 12), two) + 20 + 8 + side)
    col = math.ceil(col)
    xs = [60 + col * i + col / 2 for i in range(n)]
    d = Diagram()
    for (label, icon, fam), cx in zip(actors, xs):
        d.node(cx - col / 2 + 8, 20, col - 16, label, icon, fam, white=True, h=56)
    y, step = 110, 46
    for i, (a, b, text, kind) in enumerate(messages):
        lines = [text]
        # spazio per il testo: fra le due linee, o (nota) dalla linea fino alla successiva
        room = abs(b - a) * col - 2 * side if a != b else col - 20 - 8 - side
        if text_width(text, 12) > room:
            lines = next(c[2] for c in _splits(text) if c[1] <= room)
        y += 15 * (len(lines) - 1) if a != b else 7.5 * (len(lines) - 1)
        d.badge(26, y, i + 1)
        if a == b:  # passo interno: etichetta tinta sulla corsia
            rect = d.note(xs[a], y, lines, actors[a][2])
            limit = xs[a + 1] - side if a + 1 < n else xs[a] + col / 2 - 8
            if rect[2] > limit + 0.5:
                d.errors.append(f"nota '{text}': supera la linea successiva")
            y += 7.5 * (len(lines) - 1)
        else:
            reply = kind == "reply"
            color = NEUTRAL_ARROW if reply else FAM["instructions"][0]
            x1, x2 = xs[a], xs[b]
            sign = 1 if x2 > x1 else -1
            d.arrow([(x1 + 4 * sign, y), (x2 - 4 * sign, y)], dashed=reply, color=color)
            for k, line in enumerate(reversed(lines)):
                box = d._text((x1 + x2) / 2, y - 7 - 15 * k, line, 12, MUTED if reply else BODY, 500, "middle")
                if box[0] < min(x1, x2) + side - 0.5 or box[2] > max(x1, x2) - side + 0.5:
                    d.errors.append(f"messaggio '{line}': esce dallo spazio fra le linee")
                d.extent.append(box)
        last = y
        y += step
    for cx in xs:
        d.vline(cx, 76, last + 30)
    d.save(name)


# --- schemi -----------------------------------------------------------------------------
# Ogni schema riporta i nomi esatti dei componenti creati nei lab Advanced della Standard
# Harness (Lab 00, S01-S07). Se un lab cambia un nome, va cambiato anche qui.

DA = "agent:demand-it-agent-192.png"     # icona caricata in S01
COM = "agent:committee-agent-192.png"    # icona dell'Agente Comitato


def panoramica():
    """S01-S07: chi parla con chi."""
    d = Diagram()
    A, B, C, D = 20, 285, 570, 825          # colonne: 210, 230, 200, 200 px con 55 px fra l'una e l'altra
    u = d.node(A, 40, 210, "Proponenti e analisti", "users-three", "agents", "Teams e M365 Copilot (S07)")
    kn = d.node(A, 140, 210, "PMO Knowledge", "logo:sharepoint", "knowledge", "conoscenza SharePoint")
    mail = d.node(A, 250, 210, "Casella del PMO", "logo:outlook", "tools", "oggetto Proposta progetto")
    da = d.node(B, 40, 230, "Agente Demand IT", DA, "ai-engine", "orchestratore (S01)")
    trg = d.node(B, 250, 230, "Flow del trigger", "logo:power-automate", "triggers", "When a new email arrives (S05)")
    intk = d.node(C, 10, 200, "Intake Proposte", "robot", "agents", "child agent (S02-S05)")
    com = d.node(C, 100, 200, "Agente Comitato", COM, "agents", "agente connesso (S02)")
    dos = d.node(C, 190, 200, "Genera dossier", "logo:power-automate", "tools", "topic e agent flow (S06)")
    teams = d.node(D, 10, 200, "Canale del PMO", "logo:teams", "tools", "Notifica PMO in Teams")
    dv = d.node(D, 100, 200, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse (Lab 00)")
    od = d.node(D, 190, 200, "OneDrive", "logo:onedrive", "tools", "dossier Word e link")
    d.arrow([(u["r"], u["cy"]), (B, u["cy"])], "ai-engine")
    d.arrow([(kn["r"], kn["cy"]), (B + 40, kn["cy"]), (B + 40, da["b"])], "knowledge", dashed=True)
    d.arrow([(mail["r"], mail["cy"]), (B, mail["cy"])], "triggers")
    bus = da["r"] + 30
    for t in (intk, com, dos):
        d.arrow([(da["r"], da["cy"]), (bus, da["cy"]), (bus, t["cy"]), (C, t["cy"])], "ai-engine")
    d.arrow([(da["cx"], trg["y"]), (da["cx"], da["b"])], "triggers", label="Sends a prompt", at=(da["cx"], (da["b"] + trg["y"]) / 2))
    d.arrow([(intk["r"], teams["cy"]), (D, teams["cy"])], "tools")
    bus2 = intk["r"] + 27
    d.arrow([(intk["r"], intk["cy"] + 15), (bus2, intk["cy"] + 15), (bus2, dv["cy"] - 10), (D, dv["cy"] - 10)], "knowledge")
    d.arrow([(com["r"], dv["cy"] + 10), (D, dv["cy"] + 10)], "knowledge", dashed=True)
    d.arrow([(dos["r"], od["cy"]), (D, od["cy"])], "tools")
    right = dv["r"] + 25
    d.arrow([(trg["r"], trg["cy"]), (right, trg["cy"]), (right, dv["cy"]), (dv["r"], dv["cy"])], "triggers",
            label="Registra proposta email", at=(dos["cx"], trg["cy"]))
    d.save("panoramica-sistema")


def architettura_standard():
    """S01-S06: i componenti dell'Agente Demand IT e dello specialista."""
    d = Diagram()
    d.lane(20, 20, 620, 382, "Agente Demand IT · csm_agentedemand_std", DA, "ai-engine")
    top = d.node(340, 62, 280, "Topic", "chats-circle", "topics", "Genera dossier di revisione", white=True)
    trg = d.node(340, 140, 280, "Trigger", "lightning", "triggers", "When a new email arrives (V3)", white=True)
    d.node(340, 218, 280, "Conoscenza PMO Knowledge", "logo:sharepoint", "knowledge", "Linee guida PMO, Piano Strategico IT", white=True)
    intake = d.lane(40, 62, 280, 325, "Intake Proposte · child agent", "robot", "agents")
    tools = [("Carica business case", "crea proposta e carica il PDF"),
             ("Analizza business case", "prompt Estrai dati business case"),
             ("Crea valutazione", "prompt Valuta proposta,\nconferma dell'utente"),
             ("Notifica PMO in Teams", "adaptive card nel canale")]
    ys = [102, 167, 232, 313]
    for (label, sub), y in zip(tools, ys):
        d.node(55, y, 250, label, "logo:power-automate", "tools", sub, white=True, h=74 if "\n" in sub else 58)
    d.lane(680, 20, 310, 150, "Agente Comitato · connesso", COM, "agents")
    k2 = d.node(695, 62, 280, "Conoscenza Dataverse", "logo:dataverse", "knowledge", "Program, Evaluation Criterion,\nRequester, Proposal, Assessment", white=True)
    fd = d.node(680, 200, 310, "Agent flow Genera dossier", "logo:power-automate", "tools", "prompt Dossier di revisione")
    od = d.node(680, 285, 310, "OneDrive", "logo:onedrive", "tools", "Dossier_AS-####.docx, link")
    pa = d.node(680, 370, 310, "Flow del trigger", "logo:power-automate", "triggers", "prompt Classifica email PMO,\nRegistra proposta email")
    dv = d.node(340, 490, 300, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse, soluzione PMO Demand IT")
    d.arrow([(640, 45), (680, 45)], "agents")
    d.arrow([(top["r"], top["cy"]), (665, top["cy"]), (665, fd["cy"]), (680, fd["cy"])], "topics")
    d.arrow([(fd["cx"], fd["b"]), (od["cx"], od["y"])], "tools")
    d.arrow([(trg["r"], trg["cy"]), (655, trg["cy"]), (655, pa["cy"]), (680, pa["cy"])], "triggers")
    d.arrow([(180, intake["b"]), (180, dv["cy"]), (dv["x"], dv["cy"])], "knowledge", label="scrivono", at=(180, (402 + dv["y"]) / 2))
    d.arrow([(pa["cx"], pa["b"]), (pa["cx"], dv["y"] + 15), (dv["r"], dv["y"] + 15)], "triggers")
    d.arrow([(k2["r"], k2["cy"]), (1005, k2["cy"]), (1005, dv["b"] - 15), (dv["r"], dv["b"] - 15)], "knowledge", dashed=True)
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
    d = Diagram()
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
    d.text(dec["cx"] + 8, (dec["b"] + lo["y"]) / 2 + 4, "Sì", 11, MUTED, 600)
    d.arrow([(dec["r"], dec["cy"]), (dv["x"], dv["cy"])], color=NEUTRAL_ARROW, label="No", at=((dec["r"] + dv["x"]) / 2, dec["cy"]))
    d.arrow([(dv["cx"], dv["b"]), (man["cx"], man["y"])], "platform", label="Sì", at=(dv["cx"], (dv["b"] + man["y"]) / 2))
    loop = dv["r"] + 30
    d.arrow([(dv["r"], dv["cy"]), (loop, dv["cy"]), (loop, fine["cy"]), (fine["r"], fine["cy"])], color=NEUTRAL_ARROW,
            label="No", at=(loop, man["cy"]))
    d.save("workflow-email-standard")


def workflow_dossier():
    """S06: dal topic al link del documento."""
    d = Diagram()
    lane_x, lane_y = 605, 20               # spazio fra Topic e corsia per l'etichetta CodiceValutazione
    row = lane_y + 40
    p_h, f_h, sl_h = 76, 58, 58            # altezze di Run a prompt, Create file, Create share link
    f_y = row + p_h + 9
    sl_y = f_y + f_h + 12
    d.lane(lane_x, lane_y, 370, sl_y + sl_h + 15 - lane_y, "Agent flow · Genera dossier", "logo:power-automate", "tools")
    u = d.node(20, row, 190, "Utente", "user-circle", "agents", "Mi prepari il dossier\ndi AS-####?")
    top = d.node(250, row, 220, "Topic", "chats-circle", "topics", "Genera dossier di revisione,\nchiede il codice se manca")
    p = d.node(lane_x + 15, row, 340, "Run a prompt", "logo:ai-builder", "tools", "prompt Dossier di revisione: output Document,\ntemplate Word, conoscenza Dataverse", white=True, h=p_h)
    f = d.node(lane_x + 15, f_y, 340, "Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx", white=True, h=f_h)
    sl = d.node(lane_x + 15, sl_y, 340, "Create share link", "logo:onedrive", "tools", "View, Organization: output DossierURL", white=True, h=sl_h)
    card = d.node(250, sl["cy"] - 30, 220, "Adaptive card", "cards", "topics", "link al dossier in chat")
    d.arrow([(u["r"], u["cy"]), (top["x"], u["cy"])], "topics")
    d.arrow([(top["r"], top["cy"]), (p["x"], top["cy"])], "topics", label="CodiceValutazione", at=((top["r"] + lane_x) / 2, top["cy"]))
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
    failed = []
    for build in (panoramica, architettura_standard, workflow_chat, workflow_email_standard,
                  workflow_dossier, workflow_revisione):
        try:
            build()
        except LayoutError as e:
            failed.append(str(e))
    if failed:
        sys.exit("\n".join(failed))
