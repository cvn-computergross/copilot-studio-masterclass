"""Schemi dei lab della Standard Harness: Advanced (S01, S02, S04-S08) e Fundamentals (Lab 01-05).

Disegna ogni schema come file SVG, nello stile delle slide del corso: riquadri tinti nel colore
dell'argomento con glifo dell'Icon Pack (Phosphor duotone), logo Microsoft o icona dell'agente,
frecce sottili colorate, ritorni tratteggiati. Gli schemi dell'Advanced vanno in
docs/advanced/images/, quelli dei Fundamentals in docs/fondamentali/images/ (parametro out).

Tipi di schema:
  - Diagram: riquadri (node), corsie (lane), frecce con etichetta (arrow), numeri dei passi (badge);
  - sequence(): attori in alto e messaggi numerati fra le loro linee verticali;
  - Flow: un topic come nel canvas di Copilot Studio, dentro una corsia con il nome del topic:
    nodi in colonna (step) con frecce dritte, rami di una Condition affiancati (branch) con
    l'etichetta del ramo sulla freccia, che si riuniscono nel nodo successivo, e schede laterali
    (side) per le variabili di input e output.

Uso, dalla cartella principale della repo (servono Pillow e `npm install` già fatto):
    python tools/diagrams.py

Per cambiare uno schema si modifica la sua funzione qui sotto e si rilancia lo script: vengono
rigenerati tutti gli schemi, Advanced e Fundamentals.

Colori e tema scuro: i colori non sono scritti negli elementi ma in classi (dg-box, dg-label,
dg-arrow...) e nelle classi di argomento f-... (le stesse del sito). Lo sfondo è trasparente.
  - Il file SVG da solo (GitHub, anteprima del file) porta un <style> con i colori chiari e una
    @media (prefers-color-scheme: dark) con quelli scuri: segue il tema del sistema operativo.
  - Nel sito markdown.ts inserisce l'SVG direttamente nella pagina (non come <img>), toglie il
    suo <style> e i colori vengono da theme/style.css ("Schemi"), che usa la classe .dark di
    VitePress: decide l'interruttore del tema del sito. Se si aggiunge una classe qui, va
    aggiunta anche lì.
Glifi: contorno (dg-ol) scuro, bianco nel tema scuro; strato duotone (dg-dt) nel colore
dell'argomento. Loghi e icone degli agenti sono immagini incorporate, mai ricolorate.

Controlli di impaginazione: ogni testo viene misurato con Inter, il carattere del sito (il file
woff2 variabile che VitePress porta in node_modules, o quello indicato da DIAGRAM_FONT), con
un margine di sicurezza del 4%. Lo script si ferma con l'elenco dei problemi se un testo esce
dal suo riquadro (serve un margine destro di almeno 12px), se un'etichetta di freccia non sta
sulla sua freccia o copre un riquadro, se una freccia attraversa un riquadro o se due riquadri
si sovrappongono. Il disegno si adatta al contenuto con margini uguali.
"""
import base64
import json
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
ADVANCED = ROOT / "docs" / "advanced" / "images"
FUNDAMENTALS = ROOT / "docs" / "fondamentali" / "images"
AGENT_ICONS = ROOT / "docs" / "resources" / "advanced" / "agent-icon"

FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
# argomento -> (colore pieno, tinta, riempimento dell'icona), come nelle slide e in theme/style.css
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
NEUTRAL = "neutral"  # frecce di ritorno e rami "No": grigie

# colori comuni: (chiaro, scuro) per il file SVG da solo; nel sito li dà theme/style.css
COMMON = {
    "--dg-body": ("#363B42", "#E6EDF3"),     # testo dei messaggi
    "--dg-muted": ("#6B7480", "#9198A1"),    # sottotitoli, risposte
    "--dg-rule": ("#E2E5E9", "#3D444D"),     # bordi delle schede e delle etichette, linee verticali
    "--dg-neutral": ("#B4BAC2", "#7D858F"),  # frecce grigie
    "--dg-bg": ("#FFFFFF", "#0D1117"),       # fondo delle etichette sulle frecce (= fondo pagina)
    "--dg-card": ("#FFFFFF", "#0D1117"),     # schede dentro un'area tinta
    "--dg-outline": ("#1F2937", "#FFFFFF"),  # contorno dei glifi
    "--dg-badge": ("#0E2841", "#7AB3E0"),    # numeri dei passi
    "--dg-badge-ink": ("#FFFFFF", "#0D1117"),
}
# regole delle classi: identiche in theme/style.css (sezione "Schemi")
RULES = """
.dg-box{fill:var(--f-tint)}
.dg-card{fill:var(--dg-card);stroke:var(--dg-rule)}
.dg-lane{fill:var(--f-tint);stroke:var(--f-fill)}
.dg-label{fill:var(--f)}
.dg-sub{fill:var(--dg-muted)}
.dg-body{fill:var(--dg-body)}
.dg-ol{fill:var(--dg-outline)}
.dg-dt{fill:var(--f-fill)}
.dg-arrow{fill:none;stroke:var(--f);stroke-width:1.6}
.dg-head{fill:var(--f)}
.dg-pill{fill:var(--dg-bg);stroke:var(--dg-rule)}
.dg-pilltext{fill:var(--f)}
.dg-neutral{--f:var(--dg-neutral)}
.dg-neutral .dg-pilltext{fill:var(--dg-muted)}
.dg-note{fill:var(--f-tint)}
.dg-rule{stroke:var(--dg-rule)}
.dg-badge circle{fill:var(--dg-badge)}
.dg-badge text{fill:var(--dg-badge-ink)}
""".strip()
# alone dei testi dei messaggi nelle sequenze: le linee verticali passano sotto il testo senza
# tagliarlo. Identica in theme/style.css; nel file SVG da solo solo negli schemi che la usano,
# così gli altri restano invariati.
HALO = ".dg-msg{paint-order:stroke;stroke:var(--dg-bg);stroke-width:4px;stroke-linejoin:round}"

PAD = 12      # margine minimo fra la fine di un testo e il bordo destro del suo riquadro
MARGIN = 6    # margine fra il contenuto e il bordo del disegno, uguale sui quattro lati
GAP = 4       # distanza minima fra un'etichetta di freccia e un riquadro
PILL_H = 18   # altezza delle etichette sulle frecce
SAFETY = 1.04  # i testi si misurano il 4% più larghi di Inter: resta margine fra browser e sistemi
HINT_R = 5.5   # raggio del pallino "i" dei riquadri con dettaglio interattivo


class LayoutError(Exception):
    """Uno schema non rispetta i controlli di impaginazione."""


def style_block(hint=False, halo=False):
    """<style> del file SVG da solo: colori chiari e, con il sistema in tema scuro, quelli scuri.
    hint=True: lo schema ha riquadri con dettaglio, il cui pallino "i" nel file da solo si nasconde.
    halo=True: lo schema ha testi di messaggi (dg-msg) con l'alone."""
    def rgba(hexcolor, a):
        r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
        return f"rgba({r},{g},{b},{a})"
    light = "svg{" + ";".join(f"{k}:{v[0]}" for k, v in COMMON.items()) + "}"
    light += "".join(f".f-{k}{{--f:{s};--f-tint:{t};--f-fill:{f}}}" for k, (s, t, f) in FAM.items())
    dark = "svg{" + ";".join(f"{k}:{v[1]}" for k, v in COMMON.items()) + "}"
    dark += "".join(f".f-{k}{{--f:{f};--f-tint:{rgba(f, .16)}}}" for k, (s, t, f) in FAM.items())
    # il pallino "i" dei riquadri con dettaglio serve solo nel sito (dove il dettaglio si apre):
    # nel file SVG da solo resta nascosto
    hide = ".dg-hint{display:none}" if hint else ""
    hide += HALO if halo else ""
    return f"<style>{light}{RULES.replace(chr(10), '')}{hide}@media (prefers-color-scheme: dark){{{dark}}}</style>"


# --- misura dei testi -------------------------------------------------------------------
# Inter variabile (assi: dimensione ottica, peso). Il browser mette la dimensione ottica uguale
# alla dimensione del testo, ma non sotto 14: per testi da 11 a 13,5px vale sempre 14.
INTER = [os.environ.get("DIAGRAM_FONT"),
         ROOT / "node_modules" / "vitepress" / "dist" / "client" / "theme-default" / "fonts" / "inter-roman-latin.woff2"]
_FONTS = {}


def _font(weight):
    if weight not in _FONTS:
        if ImageFont is None:
            sys.exit("diagrams.py: serve Pillow per misurare i testi (pip install pillow)")
        path = next((Path(p) for p in INTER if p and Path(p).exists()), None)
        if path is None:
            sys.exit("diagrams.py: Inter non trovato; lanciare npm install o indicare il file con DIAGRAM_FONT")
        f = ImageFont.truetype(str(path), 1000)  # misura a 1000px: larghezze senza hinting
        axes = {a["name"]: a for a in f.get_variation_axes()}
        f.set_variation_by_axes([14 if n == b"Optical size" else weight if n == b"Weight" else a["default"]
                                 for n, a in axes.items()])
        _FONTS[weight] = f
    return _FONTS[weight]


def text_width(s, size, weight=400):
    return _font(weight).getlength(s) * size / 1000 * SAFETY


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


def icon_svg(spec, x, y, size):
    """Glifo Phosphor (contorno dg-ol, strato duotone dg-dt nel colore dell'argomento del gruppo),
    oppure logo o icona di un agente: immagini incorporate, mai ricolorate."""
    if spec.startswith(("logo:", "agent:")):
        kind, name = spec.split(":", 1)
        if kind == "agent":  # icona dell'agente caricata nei lab
            file = AGENT_ICONS / name
        else:
            file = next(f for f in (LOGOS / f"{name}.svg", LOGOS / f"{name}.png") if f.exists())
        mime = "image/svg+xml" if file.suffix == ".svg" else "image/png"
        raw = file.read_bytes()
        if file.suffix == ".svg":  # stesso risultato con qualunque fine riga del checkout (core.autocrlf)
            raw = raw.replace(b"\r\n", b"\n")
        data = base64.b64encode(raw).decode()
        # data-icon: nel sito il dettaglio interattivo riusa la stessa immagine (diagram-details.ts)
        return (f'<image data-icon="{spec}" x="{x}" y="{y}" width="{size}" height="{size}"'
                f' href="data:{mime};base64,{data}" preserveAspectRatio="xMidYMid meet"/>')
    src = (GLYPHS / f"{spec}.svg").read_text(encoding="utf-8")
    out = []
    for p in re.findall(r"<path[^>]*/>", src):
        if 'opacity="0.2"' in p:
            out.append(p.replace(' opacity="0.2"', "").replace("<path", '<path class="dg-dt"'))
        else:
            out.append(p.replace("<path", '<path class="dg-ol"'))
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 256 256">{"".join(out)}</svg>'


def fam_class(fam):
    return "dg-neutral" if fam == NEUTRAL else f"f-{fam}"


class Diagram:
    """Raccoglie le parti dello schema e la loro geometria; save() controlla e adatta il disegno."""

    def __init__(self, name, out=ADVANCED):
        self.name, self.out = name, out
        self.parts, self.markers = [], {}
        self.nodes, self.lanes, self.pills, self.free, self.arrows, self.extent = [], [], [], [], [], []
        self.errors, self.details, self.hints = [], [], []

    @staticmethod
    def _t(x, y, s, size, cls, weight=400, anchor="start"):
        return (f'<text class="{cls}" x="{x:g}" y="{y:g}" font-size="{size}" font-weight="{weight}"'
                f' text-anchor="{anchor}">{escape(s)}</text>')

    def _text(self, x, y, s, size=13, cls="dg-body", weight=400, anchor="start", out=None):
        (self.parts if out is None else out).append(self._t(x, y, s, size, cls, weight, anchor))
        return text_box(x, y, s, size, weight, anchor)

    def text(self, x, y, s, size=13, cls="dg-body", weight=400, anchor="start", fam=None):
        """Testo libero: non deve toccare riquadri, intestazioni di corsia o etichette."""
        out = []
        box = self._text(x, y, s, size, cls, weight, anchor, out)
        self.parts.append(f'<g class="{fam_class(fam)}">{out[0]}</g>' if fam else out[0])
        self.free.append((s, box))
        return box

    def _hot(self, detail, where, texts, cx, cy):
        """Riquadro o corsia con dettaglio interattivo (DETAILS): attributo data-detail, <title> per chi
        non ha JavaScript e pallino "i" nell'angolo in alto a destra (solo nel sito). Il pallino non
        deve toccare i testi del riquadro. Restituisce (attributi del gruppo, parti da aggiungere)."""
        if not detail:
            return "", [], []
        if detail not in DETAILS:
            self.errors.append(f"{where}: dettaglio '{detail}' non definito in DETAILS")
            return "", [], []
        self.details.append(detail)
        d = DETAILS[detail]
        r = HINT_R
        dot = (cx - r, cy - r, cx + r, cy + r)
        for s, b in texts:
            if overlaps(dot, b, 1):
                self.errors.append(f"{where}: il pallino del dettaglio tocca il testo '{s}'")
        self.hints.append((where, dot))
        hint = (f'<g class="dg-hint" aria-hidden="true"><circle class="dg-hint-bg" cx="{cx:g}" cy="{cy:g}" r="{r}"/>'
                f'<circle class="dg-hint-i" cx="{cx:g}" cy="{cy - 2.4:g}" r="0.95"/>'
                f'<rect class="dg-hint-i" x="{cx - 0.8:g}" y="{cy - 0.7:g}" width="1.6" height="3.9" rx="0.8"/></g>')
        title = f'<title>{escape(d["title"])}: {escape(d["role"])} ({escape(d["lab"])})</title>'
        return f' data-detail="{detail}"', [title], [hint]

    def node(self, x, y, w, label, icon, fam, sub=None, white=False, h=None, detail=None):
        """Riquadro con icona ed etichetta; white=True dentro un'area tinta. detail: id in DETAILS,
        nel sito il riquadro apre il dettaglio (diagram-details.ts)."""
        lines = sub.split("\n") if sub else []
        h = h or (44 + 16 * len(lines) if lines else 48)
        g = [f'<rect class="{"dg-card" if white else "dg-box"}" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>',
             icon_svg(icon, x + 12, y + h / 2 - 13, 26)]
        ty = y + h / 2 - 8 * len(lines) + 5
        rect = (x, y, x + w, y + h)
        boxes = [(label, self._text(x + 48, ty, label, 13.5, "dg-label", 600, out=g))]
        for i, line in enumerate(lines):
            boxes.append((line, self._text(x + 48, ty + 17 + 16 * i, line, 12, "dg-sub", out=g)))
        attrs, head, tail = self._hot(detail, f"riquadro '{label}'", boxes, x + w - HINT_R - 3, y + HINT_R + 3)
        self.parts.append(f'<g class="dg-node f-{fam}"{attrs}>' + "".join(head + g + tail) + "</g>")
        for s, b in boxes:
            if b[2] > x + w - PAD:
                need = math.ceil(b[2] - x + PAD)
                self.errors.append(f"riquadro '{label}': il testo '{s}' supera il margine destro di "
                                   f"{b[2] - (x + w - PAD):.1f}px (larghezza {w}, ne servono almeno {need})")
            if b[1] < y + 4 or b[3] > y + h - 4:
                self.errors.append(f"riquadro '{label}': il testo '{s}' esce in verticale (altezza {h})")
        self.nodes.append((label, rect))
        return {"x": x, "y": y, "w": w, "h": h, "cx": x + w / 2, "cy": y + h / 2, "r": x + w, "b": y + h}

    def lane(self, x, y, w, h, title, icon, fam, detail=None):
        g = [f'<rect class="dg-lane" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>',
             icon_svg(icon, x + 14, y + 12, 22)]
        tb = self._text(x + 44, y + 28, title.upper(), 11.5, "dg-label", 600, out=g)
        attrs, head, tail = self._hot(detail, f"corsia '{title}'", [(title, tb)], x + w - HINT_R - 7, y + HINT_R + 7)
        self.parts.append(f'<g class="dg-lanegroup f-{fam}"{attrs}>' + "".join(head + g + tail) + "</g>")
        rect, ib = (x, y, x + w, y + h), (x + 14, y + 12, x + 36, y + 34)
        if not contains(rect, ib, 8):
            self.errors.append(f"corsia '{title}': l'icona non sta dentro la corsia")
        if tb[2] > x + w - PAD:
            need = math.ceil(tb[2] - x + PAD)
            self.errors.append(f"corsia '{title}': il titolo supera il margine destro di "
                               f"{tb[2] - (x + w - PAD):.1f}px (larghezza {w}, ne servono almeno {need})")
        self.lanes.append((title, rect, [ib, tb]))
        return {"x": x, "y": y, "w": w, "h": h, "r": x + w, "b": y + h}

    def chip(self, x, y, w, h, lines, fam, style="box", weight=500, size=12):
        """Riquadro di solo testo, centrato (celle di una tabella, etichette). style: 'box' tinta, 'card'
        bianco, 'dashed' tratteggiato con angoli tondi. Conta come riquadro nei controlli."""
        lines = [lines] if isinstance(lines, str) else list(lines)
        cls = {"box": "dg-box", "card": "dg-card", "dashed": "dg-lane"}[style]
        rx = h / 2 if style == "dashed" else 8
        dash = ' stroke-dasharray="5 4"' if style == "dashed" else ""
        g = [f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx:g}"{dash}/>']
        step = size + 3
        y0 = y + h / 2 - step * (len(lines) - 1) / 2 + size * 0.35
        for k, line in enumerate(lines):
            b = self._text(x + w / 2, y0 + step * k, line, size, "dg-label", weight, "middle", out=g)
            if b[0] < x + 8 or b[2] > x + w - 8:
                self.errors.append(f"riquadro '{line}': il testo non sta nel riquadro (larghezza {w}, "
                                   f"ne servono almeno {math.ceil(b[2] - b[0] + 16)})")
        self.parts.append(f'<g class="dg-node f-{fam}">' + "".join(g) + "</g>")
        self.nodes.append((" ".join(lines), (x, y, x + w, y + h)))
        return {"x": x, "y": y, "w": w, "h": h, "cx": x + w / 2, "cy": y + h / 2, "r": x + w, "b": y + h}

    def paragraph(self, x, y, text, width, cls="dg-body", size=12, line=17):
        """Testo libero a capo automatico entro width; restituisce la y della riga successiva."""
        words, cur = text.split(" "), ""
        rows = []
        for wd in words:
            if cur and text_width(cur + " " + wd, size) > width:
                rows.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        rows.append(cur)
        for r in rows:
            self.text(x, y, r, size, cls)
            y += line
        return y

    def _marker(self, fam):
        """Punta di freccia, una per colore; l'id porta il nome dello schema (due schemi nella stessa pagina)."""
        if fam not in self.markers:
            self.markers[fam] = (f'<marker id="{self.name}-head-{fam}" class="{fam_class(fam)}" viewBox="0 0 10 10" refX="9" refY="5"'
                                 f' markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="dg-head" d="M0 0 L10 5 L0 10 Z"/></marker>')
        return f"{self.name}-head-{fam}"

    def arrow(self, pts, fam="ai-engine", dashed=False, label=None, at=None, head=True):
        """Freccia a segmenti; l'etichetta (at = centro) deve stare su uno dei segmenti. fam=NEUTRAL: grigia.
        head=False: linea senza punta (i rami di un topic che si riuniscono prima del nodo successivo)."""
        d = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        end = f' marker-end="url(#{self._marker(fam)})"' if head else ""
        g = [f'<path class="dg-arrow" d="{d}"{dash}{end}/>']
        self.arrows.append((label, pts))
        if label:
            lx, ly = at or ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
            wpx = text_width(label, 11, 500) + 20
            rect = (lx - wpx / 2, ly - PILL_H / 2, lx + wpx / 2, ly + PILL_H / 2)
            g.append(f'<rect class="dg-pill" x="{rect[0]:.1f}" y="{rect[1]:g}" width="{wpx:.1f}" height="{PILL_H}" rx="9"/>')
            self._text(lx, ly + 3.5, label, 11, "dg-pilltext", 500, "middle", out=g)
            if dist_to_polyline((lx, ly), pts) > 0.75:
                self.errors.append(f"etichetta '{label}': il centro ({lx}, {ly}) non sta sulla sua freccia")
            self.pills.append((label, rect, pts))
        self.parts.append(f'<g class="dg-link {fam_class(fam)}">' + "".join(g) + "</g>")

    def badge(self, x, y, n):
        g = [f'<circle cx="{x}" cy="{y}" r="10"/>']
        self._text(x, y + 4, str(n), 11, "dg-badgetext", 600, "middle", out=g)
        self.parts.append('<g class="dg-badge">' + "".join(g) + "</g>")
        self.extent.append((x - 10, y - 10, x + 10, y + 10))

    def note(self, x, y, lines, fam):
        """Passo interno di un diagramma di sequenza: etichetta tinta (una o due righe) che parte dalla linea x."""
        wpx = max(text_width(s, 12, 500) for s in lines) + 20
        ph = 24 + 15 * (len(lines) - 1)
        rect = (x - 8, y - ph / 2, x - 8 + wpx, y + ph / 2)
        g = [f'<rect class="dg-note" x="{rect[0]:g}" y="{rect[1]:g}" width="{wpx:.1f}" height="{ph}" rx="12"/>']
        for k, s in enumerate(lines):
            self._text(x + 2, y + 4 - 7.5 * (len(lines) - 1) + 15 * k, s, 12, "dg-label", 500, out=g)
        self.parts.append(f'<g class="dg-notegroup f-{fam}">' + "".join(g) + "</g>")
        self.free.append((" ".join(lines), rect))
        return rect

    def vline(self, x, y0, y1):
        self.parts.append(f'<line class="dg-rule" x1="{x:g}" y1="{y0:g}" x2="{x:g}" y2="{y1:g}" stroke-width="1.5" stroke-dasharray="4 4"/>')
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
        for where, dot in self.hints:  # il pallino di una corsia non deve finire sotto un riquadro
            for n, rn in nodes:
                if overlaps(dot, rn, 2) and not contains(rn, dot):
                    errs.append(f"{where}: il pallino del dettaglio tocca il riquadro '{n}'")
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

    def save(self):
        name = self.name
        errs = self.check() + detail_errors(self)
        if errs:
            raise LayoutError(f"schema {name}: problemi di impaginazione\n  - " + "\n  - ".join(errs))
        x0, y0, x1, y1 = self.bounds()
        x0, y0, x1, y1 = math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1)
        w, h = x1 - x0 + 2 * MARGIN, y1 - y0 + 2 * MARGIN
        dx, dy = MARGIN - x0, MARGIN - y0
        self.out.mkdir(parents=True, exist_ok=True)
        defs = "<defs>" + "".join(self.markers.values()) + "</defs>" if self.markers else ""
        body = "".join(self.parts)
        if not self.details:  # data-icon serve solo ai dettagli interattivi
            body = re.sub(r'<image data-icon="[^"]*" ', "<image ", body)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" class="dg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"'
               f' font-family="{FONT}">{style_block(bool(self.details), "dg-msg" in body)}{defs}'
               f'<g transform="translate({dx} {dy})">' + body + "</g></svg>\n")
        (self.out / f"{name}.svg").write_text(svg, encoding="utf-8")
        save_details(self, body)
        n = len(set(self.details))
        print(f"schema {self.out.parent.name}/{name} ({w}x{h})" + (f", {n} riquadri con dettaglio" if n else ""))


def _splits(text):
    """Possibili divisioni su due righe: prima quelle dopo la punteggiatura, poi le altre."""
    words = text.split(" ")
    out = []
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wmax = max(text_width(a, 12, 500), text_width(b, 12, 500))
        out.append((a[-1] not in ":;,", wmax, [a, b]))
    return sorted(out, key=lambda c: (c[0], c[1]))


def sequence(name, actors, messages, col_min=230, out=ADVANCED):
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
            col = max(col, (min(text_width(text, 12, 500), two) + 2 * side) / abs(b - a))
        else:  # la nota non deve superare la linea successiva
            col = max(col, min(text_width(text, 12, 500), two) + 20 + 8 + side)
    col = math.ceil(col)
    xs = [60 + col * i + col / 2 for i in range(n)]
    d = Diagram(name, out)
    for (label, icon, fam), cx in zip(actors, xs):
        d.node(cx - col / 2 + 8, 20, col - 16, label, icon, fam, white=True, h=56)
    y, step = 110, 46
    first = len(d.parts)  # le linee verticali vanno disegnate prima (sotto) dei messaggi
    for i, (a, b, text, kind) in enumerate(messages):
        lines = [text]
        # spazio per il testo: fra le due linee, o (nota) dalla linea fino alla successiva
        room = abs(b - a) * col - 2 * side if a != b else col - 20 - 8 - side
        if text_width(text, 12, 500) > room:
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
            x1, x2 = xs[a], xs[b]
            sign = 1 if x2 > x1 else -1
            d.arrow([(x1 + 4 * sign, y), (x2 - 4 * sign, y)], NEUTRAL if reply else "instructions", dashed=reply)
            for k, line in enumerate(reversed(lines)):  # dg-msg: alone, le linee verticali non tagliano il testo
                box = d._text((x1 + x2) / 2, y - 7 - 15 * k, line, 12, "dg-sub dg-msg" if reply else "dg-body dg-msg", 500, "middle")
                if box[0] < min(x1, x2) + side - 0.5 or box[2] > max(x1, x2) - side + 0.5:
                    d.errors.append(f"messaggio '{line}': esce dallo spazio fra le linee")
                d.extent.append(box)
        last = y
        y += step
    for cx in xs:
        d.vline(cx, 76, last + 30)
    d.parts[first:first] = [d.parts.pop() for _ in xs][::-1]
    d.save()


FLOW_GAP = 30       # spazio fra due nodi di un topic
FLOW_PILL_GAP = 44  # ...quando sulla freccia c'è un'etichetta
FLOW_FORK = 16      # dal fondo del nodo alla linea orizzontale da cui partono i rami
FLOW_DROP = 40      # dalla linea dei rami al primo nodo del ramo (lì sta l'etichetta del ramo)


def _dedupe(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if p != out[-1]:
            out.append(p)
    return out


class Flow(Diagram):
    """Un topic come nel canvas di Copilot Studio, dentro una corsia con il nome del topic.

    step() aggiunge un nodo sotto il precedente, con una freccia dritta (e, se serve, un'etichetta);
    branch() affianca i rami di una Condition: partono da una linea orizzontale sotto il nodo, con
    il nome del ramo sulla freccia, e si riuniscono nel nodo del passo successivo; side() mette
    accanto a un nodo una scheda (variabili di input o di output) collegata da una freccia
    tratteggiata. Tutti i nodi sono schede bianche dentro la corsia; i controlli di Diagram valgono
    anche qui (testi nei riquadri, etichette sulle frecce, frecce che attraversano riquadri)."""

    def __init__(self, name, title, w=340, fam="topics", icon="chats-circle", out=FUNDAMENTALS):
        super().__init__(name, out)
        self.title, self.icon, self.fam = title, icon, fam
        self.w, self.cx, self.prev = w, w / 2, []

    def _place(self, label, icon, fam, sub, x, y, w, h=None, detail=None):
        return self.node(x, y, w, label, icon, fam, sub, white=True, h=h, detail=detail)

    def step(self, label, icon, fam, sub=None, pill=None, w=None, h=None, afam="topics", detail=None):
        """Nodo nella colonna centrale; pill = etichetta sulla freccia che arriva al nodo.
        detail: id in DETAILS, come in node()."""
        w, cx = w or self.w, self.cx
        if not self.prev:
            y = 0
        elif len(self.prev) == 1:
            p = self.prev[0]
            y = p["b"] + (FLOW_PILL_GAP if pill else FLOW_GAP)
            self.arrow([(p["cx"], p["b"]), (cx, y)], afam, label=pill, at=(cx, (p["b"] + y) / 2) if pill else None)
        else:  # i rami si riuniscono su una linea orizzontale, poi una sola freccia scende al nodo
            ym = max(p["b"] for p in self.prev) + 18
            for p in self.prev:
                self.arrow(_dedupe([(p["cx"], p["b"]), (p["cx"], ym), (cx, ym)]), afam, head=False)
            y = ym + (FLOW_PILL_GAP if pill else 22)
            self.arrow([(cx, ym), (cx, y)], afam, label=pill, at=(cx, (ym + y) / 2) if pill else None)
        n = self._place(label, icon, fam, sub, cx - w / 2, y, w, h, detail)
        self.prev = [n]
        return n

    def branch(self, cols, colw, sep=14):
        """Rami affiancati sotto l'ultimo nodo. cols: (etichetta del ramo, [(label, icon, fam, sub), ...],
        colore della freccia del ramo); un quinto elemento facoltativo del nodo è il suo detail (come in
        step()). Restituisce l'ultimo nodo di ogni ramo."""
        p = self.prev[0]
        total = len(cols) * colw + (len(cols) - 1) * sep
        x0 = self.cx - total / 2
        ybus = p["b"] + FLOW_FORK
        top = ybus + FLOW_DROP
        xs = [x0 + i * (colw + sep) + colw / 2 for i in range(len(cols))]
        # prima i rami grigi: dove la linea orizzontale è in comune, resta sopra il colore del topic
        for i in sorted(range(len(cols)), key=lambda i: cols[i][2] != NEUTRAL):
            pill, _, afam = cols[i]
            self.arrow(_dedupe([(p["cx"], p["b"]), (p["cx"], ybus), (xs[i], ybus), (xs[i], top)]), afam,
                       label=pill, at=(xs[i], (ybus + top) / 2))
        lasts = []
        for ccx, (pill, nodes, afam) in zip(xs, cols):
            y, last = top, None
            for label, icon, fam, sub, *detail in nodes:
                if last:
                    y = last["b"] + FLOW_GAP
                    self.arrow([(ccx, last["b"]), (ccx, y)], afam)
                last = self._place(label, icon, fam, sub, ccx - colw / 2, y, colw, detail=detail[0] if detail else None)
            lasts.append(last)
        self.prev = lasts
        return lasts

    def side(self, n, label, icon, fam, sub, w, dx=40, right=True, into=True, afam=NEUTRAL, pill=None, detail=None):
        """Scheda accanto al nodo n, centrata in altezza; into=True: la freccia va dalla scheda al nodo."""
        lines = sub.split("\n") if sub else []
        h = 44 + 16 * len(lines) if lines else 48
        x = n["r"] + dx if right else n["x"] - dx - w
        c = self._place(label, icon, fam, sub, x, n["cy"] - h / 2, w, h, detail)
        a, b = ((c["x"], c["cy"]), (n["r"], c["cy"])) if right else ((c["r"], c["cy"]), (n["x"], c["cy"]))
        self.arrow([a, b] if into else [b, a], afam, dashed=True, label=pill,
                   at=((a[0] + b[0]) / 2, c["cy"]) if pill else None)
        return c

    def save(self):
        """La corsia del topic avvolge tutti i nodi e le etichette; va disegnata sotto di loro."""
        boxes = [r for _, r in self.nodes] + [r for _, r, _ in self.pills]
        x0, y0 = min(b[0] for b in boxes) - 16, min(r[1] for _, r in self.nodes) - 48
        x1, y1 = max(b[2] for b in boxes) + 16, max(b[3] for b in boxes) + 16
        self.lane(x0, y0, x1 - x0, y1 - y0, self.title, self.icon, self.fam)
        self.parts.insert(0, self.parts.pop())
        super().save()


# --- schemi -----------------------------------------------------------------------------
# Ogni schema riporta i nomi esatti dei componenti creati nei lab Advanced della Standard
# Harness (Lab 00, S01-S08). Se un lab cambia un nome, va cambiato anche qui.

DA = "agent:demand-it-agent-192.png"     # icona caricata in S01
COM = "agent:committee-agent-192.png"    # icona dell'Agente Comitato


# --- dettagli interattivi -----------------------------------------------------------------
# Nel sito un riquadro (o una corsia) con detail="id" si può esplorare: passandoci sopra con il
# mouse, o selezionandolo (clic, tocco, Invio), si apre un riquadro con il componente in dettaglio,
# disegnato come un piccolo flow verticale nello stesso stile (diagram-details.ts). Il contenuto
# sta qui sotto e riporta i nomi esatti dei lab; save() lo scrive accanto allo schema, in
# <nome>.details.json, che markdown.ts trasforma in HTML. Il file SVG da solo non cambia aspetto.
#   D(titolo, icona, argomento, lab, ruolo in una riga, passi, layout)
#     layout "flow": passi uniti da frecce; "list": elenco senza frecce (le parti di un agente)
#   N(etichetta, icona, argomento, sottotitolo, pill=etichetta sulla freccia che arriva al passo,
#     lab=lab del passo, branches=[B(etichetta del ramo, passi), ...] rami secondari di una condizione)
#   G(titolo, icona, argomento, passi, layout): gruppo di passi in una corsia (un agent flow, i tool)
def N(label, icon, fam, sub=None, pill=None, lab=None, branches=None):
    return {k: v for k, v in dict(label=label, icon=icon, fam=fam, sub=sub, pill=pill, lab=lab,
                                  branches=branches).items() if v is not None}


def B(label, steps, fam=NEUTRAL):
    return {"label": label, "fam": fam, "steps": steps}


def G(title, icon, fam, steps, layout="flow", pill=None):
    g = {"group": title, "icon": icon, "fam": fam, "layout": layout, "steps": steps}
    if pill:
        g["pill"] = pill
    return g


def D(title, icon, fam, lab, role, steps, layout="flow"):
    return {"title": title, "icon": icon, "fam": fam, "lab": lab, "role": role, "layout": layout, "steps": steps}


TRIGGER_FLOW = "When an agent calls the flow"
RESPOND = "Respond to the agent"
TABLES = [N("Program", "database", "knowledge", "Program Code PG-###, Available Budget"),
          N("Evaluation Criterion", "database", "knowledge", "Weight, lookup a Program"),
          N("Requester", "database", "knowledge", "RQ-####, Email per la deduplica"),
          N("Proposal", "database", "knowledge", "PP-####, Business Case Document"),
          N("Assessment", "database", "knowledge", "AS-####, Score, Recommendation")]

DETAILS = {
    "demand-it": D(
        "Agente Demand IT", DA, "ai-engine", "S01",
        "Orchestratore e punto di ingresso unico: risponde sulle regole del PMO e delega agli altri componenti.",
        [N("Istruzioni", "clipboard-text", "instructions", "ruolo, ambito, responsabilità, identificatori, sicurezza, delega", lab="S01-S06"),
         N("Conoscenza PMO", "logo:sharepoint", "knowledge", "cartella SharePoint PMO Knowledge", lab="S01"),
         N("Impostazioni generative", "sliders-horizontal", "platform", "niente web, File uploads attivo, Claude Sonnet 4.6", lab="S01"),
         N("Intake Proposte", "robot", "agents", "child agent", lab="S02"),
         N("Agente Comitato", COM, "agents", "agente connesso", lab="S02"),
         N("Nuova proposta via email", "lightning", "triggers", "trigger When a new email arrives (V3)", lab="S05"),
         N("Genera dossier di revisione", "chats-circle", "topics", "topic con l'agent flow Genera dossier", lab="S06"),
         N("Demand IT - Base", "list-checks", "lifecycle", "test set: 6 casi, Meaning match 70", lab="S07"),
         N("Teams and Microsoft 365 Copilot", "rocket-launch", "lifecycle", "canale dopo la pubblicazione", lab="S07"),
         N("Reazioni degli utenti", "thumbs-up", "lifecycle", "User feedback, lette in Monitor", lab="S08"),
         N("Approfondimento CSAT negativo", "chats-circle", "topics", "topic: adaptive card dopo un voto CSAT di 1-2 stelle", lab="S08")],
        layout="list"),
    "intake": D(
        "Intake Proposte", "robot", "agents", "S02-S05",
        "Child agent dell'Agente Demand IT: registra e analizza i business case, avvisa il PMO in Teams per le proposte via email e, dopo una conferma, crea la valutazione.",
        [N("Istruzioni", "clipboard-text", "instructions", "un solo PDF per volta, codici mai inventati", lab="S02-S05"),
         G("Tools · agent flow", "wrench", "tools", [
             N("Carica business case", "logo:power-automate", "tools", "crea la proposta e carica il PDF", lab="S02"),
             N("Analizza business case", "logo:power-automate", "tools", "prompt Estrai dati business case", lab="S03"),
             N("Crea valutazione", "logo:power-automate", "tools", "prompt Valuta proposta, conferma dell'utente", lab="S04"),
             N("Notifica PMO in Teams", "logo:power-automate", "tools", "adaptive card per le proposte via email", lab="S05")],
           layout="list")],
        layout="list"),
    "comitato": D(
        "Agente Comitato", COM, "agents", "S02",
        "Agente connesso, pubblicato a sé: prepara briefing e domande per la sessione di revisione, in sola lettura.",
        [N("Istruzioni", "clipboard-text", "instructions", "briefing e domande, non contatta i proponenti"),
         G("Conoscenza Dataverse", "logo:dataverse", "knowledge", TABLES, layout="list"),
         N("Impostazioni generative", "sliders-horizontal", "platform", "niente web, File uploads disattivato, Claude Sonnet 4.6"),
         N("Let other agents connect", "plugs-connected", "agents", "pubblicato e collegato all'Agente Demand IT"),
         N("Comitato - Sicurezza", "list-checks", "lifecycle", "test set: 7 casi, Meaning match 70", lab="S07")],
        layout="list"),
    "comitato-kb": D(
        "Conoscenza Dataverse", "logo:dataverse", "knowledge", "S02",
        "Conoscenza dell'Agente Comitato: le cinque tabelle del PMO Demand Hub, in sola lettura e con i permessi dell'utente.",
        TABLES, layout="list"),
    "pmo-hub": D(
        "PMO Demand Hub", "logo:dataverse", "knowledge", "Lab 00",
        "Soluzione PMO Demand IT importata nel Lab 00: cinque tabelle con prefisso csm_ e l'app model-driven.",
        [G("Tabelle Dataverse", "logo:dataverse", "knowledge", TABLES, layout="list"),
         N("App PMO Demand Hub", "logo:power-apps", "lifecycle", "Home, Proposal Board, moduli e viste")],
        layout="list"),
    "pmo-knowledge": D(
        "PMO Knowledge", "logo:sharepoint", "knowledge", "Lab 00, S01",
        "Cartella SharePoint con le regole del PMO: è la fonte Conoscenza PMO dell'Agente Demand IT.",
        [N("Zava_PMO_Linee_Guida_Business_Case.docx", "file-text", "knowledge", "formati, struttura, soglie, regola di budget", lab="Lab 00"),
         N("Zava_Piano_Strategico_IT_2026-2028.pdf", "file-text", "knowledge", "obiettivi OS1-OS5 con i KPI", lab="Lab 00"),
         N("Conoscenza PMO", "logo:sharepoint", "knowledge", "risponde con i permessi di chi chatta", lab="S01")],
        layout="list"),
    "users": D(
        "Proponenti e analisti", "users-three", "agents", "S01-S08",
        "Chi usa l'Agente Demand IT: i proponenti allegano il business case, gli analisti del PMO confermano.",
        [N("Pannello Test", "flask", "instructions", "le prove dei lab in Copilot Studio", lab="S01-S06, S08"),
         N("Conferme dell'analista", "user-check", "agents", "programma e registrazione della valutazione", lab="S03-S04"),
         N("Teams and Microsoft 365 Copilot", "logo:teams", "lifecycle", "canale dopo la pubblicazione", lab="S07"),
         N("Reazioni e CSAT", "thumbs-up", "lifecycle", "reazioni in Teams, CSAT a fine conversazione", lab="S08")],
        layout="list"),
    "mailbox": D(
        "Casella del PMO", "logo:outlook", "tools", "S05",
        "Il secondo canale di ingresso: le proposte inviate per email alla casella del PMO.",
        [N("Email del proponente", "envelope-simple", "tools", "oggetto Proposta progetto, PDF allegato"),
         N("Nuova proposta via email", "lightning", "triggers", "Subject Filter, Only with Attachments"),
         N("Flow del trigger", "logo:power-automate", "triggers", "classifica l'email e registra le proposte")]),
    "flow-trigger": D(
        "Flow del trigger", "logo:power-automate", "triggers", "S05",
        "Flow del trigger Nuova proposta via email: classifica l'email, registra ogni PDF e chiama l'agente.",
        [N("When a new email arrives (V3)", "logo:outlook", "triggers", "Split On: una esecuzione per email"),
         N("Html to text", "file-text", "tools", "Content Conversion, testo del Body"),
         N("Classifica", "logo:ai-builder", "tools", "prompt Classifica email PMO"),
         N("Proposta rilevata", "git-branch", "system", "Classifica contiene Proposta?", branches=[
             B("No", [N("Da verificare", "git-branch", "system", "Classifica contiene Incerta?", branches=[
                 B("Sì", [N("Avvisa verifica manuale", "logo:outlook", "tools", "Send an email (V2)")], fam="platform"),
                 B("No", [N("Fine senza azioni", "x-circle", "system", "RispostaAutomatica o NonPertinente")])])])]),
         G("Per ogni allegato · For each su Attachments", "arrows-clockwise", "tools", [
             N("Allegato PDF", "git-branch", "system", "Content-Type application/pdf?", branches=[
                 B("No", [N("Allegato ignorato", "x-circle", "system", "es. il file Word")])]),
             N("Registra proposta email", "logo:dataverse", "knowledge", "riga in Proposals, canale Email", pill="Sì"),
             N("Carica documento email", "logo:dataverse", "knowledge", "PDF in Business Case Document"),
             N("Sends a prompt to the specified copilot", DA, "ai-engine", "Agente Demand IT, con il codice PP-####")],
           pill="Sì"),
         G("Agente Demand IT · Intake Proposte", DA, "ai-engine", [
             N("Analizza business case", "logo:power-automate", "tools", "agent flow di Intake Proposte"),
             N("Notifica PMO in Teams", "logo:power-automate", "tools", "adaptive card in Teams (Flow bot)")],
           pill="messaggio all'agente")]),
    "trigger-email": D(
        "Nuova proposta via email", "lightning", "triggers", "S05",
        "Trigger dell'Agente Demand IT: il flow che genera si completa in Power Automate.",
        [N("When a new email arrives (V3)", "logo:outlook", "triggers", "Add trigger nella pagina Overview"),
         N("Parametri", "sliders-horizontal", "platform", "Include Attachments, Subject Filter, Only with Attachments"),
         N("Flow del trigger", "logo:power-automate", "triggers", "Edit in Power Automate"),
         N("Agente Demand IT", DA, "ai-engine", "riceve il messaggio da elaborare", pill="Sends a prompt")]),
    "genera-dossier": D(
        "Genera dossier", "logo:power-automate", "tools", "S06",
        "Topic Genera dossier di revisione con l'agent flow Genera dossier: dal codice AS-#### al documento Word.",
        [N("Genera dossier di revisione", "chats-circle", "topics", "topic: chiede il codice se manca"),
         G("Agent flow · Genera dossier", "logo:power-automate", "tools", [
             N("Run a prompt", "logo:ai-builder", "tools", "prompt Dossier di revisione, output Document (preview)"),
             N("Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx"),
             N("Create share link", "logo:onedrive", "tools", "View, Organization")], pill="CodiceValutazione"),
         N("Adaptive card", "cards", "topics", "pulsante Apri il dossier", pill="DossierURL")]),
    "topic-dossier": D(
        "Genera dossier di revisione", "chats-circle", "topics", "S06",
        "Topic dell'Agente Demand IT: raccoglie il codice della valutazione e consegna il link al dossier.",
        [N("Trigger", "lightning", "triggers", "The agent chooses: dossier di una valutazione AS-####"),
         N("VarCodiceValutazione", "brackets-curly", "topics", "input del topic, chiesto se manca"),
         N("Genera dossier", "logo:power-automate", "tools", "agent flow, restituisce DossierURL"),
         N("Send a message", "cards", "topics", "adaptive card con Apri il dossier"),
         N("End current topic", "stop-circle", "system", "Topic management")]),
    "flow-dossier": D(
        "Agent flow Genera dossier", "logo:power-automate", "tools", "S06",
        "Genera il dossier Word con il prompt, lo salva in OneDrive e restituisce un link di sola lettura.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "input CodiceValutazione"),
         N("Run a prompt", "logo:ai-builder", "tools", "prompt Dossier di revisione, output Document (preview)"),
         N("Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx"),
         N("Create share link", "logo:onedrive", "tools", "Link type View, scope Organization"),
         N(RESPOND, "flow-arrow", "tools", "output DossierURL")]),
    "onedrive": D(
        "OneDrive", "logo:onedrive", "tools", "S06",
        "OneDrive for Business dell'autore: l'agent flow Genera dossier salva il dossier di revisione in I miei file, cartella Documents.",
        [N("Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx"),
         N("Create share link", "logo:onedrive", "tools", "View, Organization: Web URL"),
         N("Apri il dossier", "cards", "topics", "pulsante dell'adaptive card nel topic", pill="DossierURL")]),
    "teams-channel": D(
        "Teams del PMO", "logo:teams", "tools", "S05",
        "Dove il PMO vede arrivare le proposte ricevute per email, già registrate e analizzate (chat con Flow bot, oppure canale Proposte se scelto).",
        [N("Notifica PMO in Teams", "logo:power-automate", "tools", "agent flow di Intake Proposte"),
         N("Post card in a chat or channel", "logo:teams", "tools", "Post as Flow bot, Post in Chat with Flow bot"),
         N("Adaptive card", "cards", "tools", "proposta, titolo, proponente, programma, avvisi"),
         N("Apri le proposte nel PMO Demand Hub", "logo:power-apps", "lifecycle", "Action.OpenUrl")]),
    "carica-bc": D(
        "Carica business case", "logo:power-automate", "tools", "S02",
        "Agent flow di Intake Proposte: registra nel PMO Demand Hub la proposta con il PDF allegato in chat.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "BusinessCase, Messaggio, EmailMittente"),
         N("Crea proposta", "logo:dataverse", "knowledge", "Add a new row in Proposals, canale Chat"),
         N("Carica documento", "logo:dataverse", "knowledge", "PDF in Business Case Document"),
         N(RESPOND, "flow-arrow", "tools", "CodiceProposta PP-####")]),
    "analizza-bc": D(
        "Analizza business case", "logo:power-automate", "tools", "S03",
        "Agent flow di Intake Proposte: estrae i dati dal PDF, crea o riusa il proponente e collega il programma.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "input CodiceProposta"),
         N("Leggi proposta", "logo:dataverse", "knowledge", "List rows in Proposals"),
         N("Scarica documento", "logo:dataverse", "knowledge", "Business Case Document"),
         N("Estrai dati", "logo:ai-builder", "tools", "prompt Estrai dati business case"),
         N("Cerca proponente", "logo:dataverse", "knowledge", "List rows in Requesters per email"),
         N("Proponente nuovo", "git-branch", "system", "nessun proponente con quella email?", branches=[
             B("Sì", [N("Crea proponente", "logo:dataverse", "knowledge", "Add a new row in Requesters")], fam="knowledge")]),
         N("Aggiorna proposta", "logo:dataverse", "knowledge", "titolo, sintesi, budget, durata, proponente"),
         N("Programma indicato", "git-branch", "system", "un solo programma valido nel documento?", branches=[
             B("Sì", [N("Cerca programma", "logo:dataverse", "knowledge", "List rows in Programs"),
                      N("Collega programma", "logo:dataverse", "knowledge", "Update a row: Program")], fam="knowledge")]),
         N(RESPOND, "flow-arrow", "tools", "codici, programma, avvisi")]),
    "crea-val": D(
        "Crea valutazione", "logo:power-automate", "tools", "S04",
        "Agent flow di Intake Proposte: valuta, calcola il punteggio con regole fisse e registra la valutazione dopo la conferma.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "CodiceProposta, CodiceProgramma"),
         N("Leggi Proposta e Leggi Programma", "logo:dataverse", "knowledge", "List rows in Proposals e Programs"),
         N("Scarica documento", "logo:dataverse", "knowledge", "Business Case Document"),
         N("Valuta", "logo:ai-builder", "tools", "prompt Valuta proposta: livelli ed evidenze"),
         N("Per ogni criterio", "arrows-clockwise", "tools", "Punti, Punteggio e Dettaglio"),
         N("Raccomandazione", "function", "tools", "soglie 75 e 55, regola di budget"),
         N("Registra valutazione", "logo:dataverse", "knowledge", "Add a new row in Assessments, AS-####"),
         N("Aggiorna proposta", "logo:dataverse", "knowledge", "Program e Proposal Status Assessed"),
         N(RESPOND, "flow-arrow", "tools", "codice, punteggio, indicazione")]),
    "notifica-teams": D(
        "Notifica PMO in Teams", "logo:power-automate", "tools", "S05",
        "Agent flow di Intake Proposte: avvisa il PMO in Teams di una proposta ricevuta per email.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "CodiceProposta, Title, Requester, Program, Avvisi"),
         N("Post card in a chat or channel", "logo:teams", "tools", "Flow bot, adaptive card con FactSet"),
         N(RESPOND, "flow-arrow", "tools", "Esito: Notifica inviata")]),
    "topic-csat": D(
        "Approfondimento CSAT negativo", "chats-circle", "topics", "S08",
        "Topic dell'Agente Demand IT richiamato da End of Conversation quando il voto CSAT è di 1 o 2 stelle: chiede il motivo.",
        [N("Trigger", "lightning", "triggers", "It's redirected to: parte solo da Go to another topic"),
         N("Ask with adaptive card", "cards", "topics", "Ci aiuti a migliorare?: motivo e commento, output motivoId e noteId"),
         N("Send a message", "chat-text", "topics", "Grazie, il tuo commento aiuta l'azienda a migliorare l'agente.")]),
}

# Dettagli degli schemi dei lab Advanced S05-S08 (workflow-email-standard, workflow-dossier,
# workflow-valutazioni, workflow-csat): solo per i riquadri che nascondono impostazioni del lab
# (nomi, valori, espressioni); gli altri restano semplici. Id con il prefisso del lab (s05-...).
DETAILS.update({
    # S05 - workflow-email-standard
    "s05-trigger": D(
        "When a new email arrives (V3)", "logo:outlook", "triggers", "S05",
        "Trigger Nuova proposta via email dell'Agente Demand IT: parte per ogni email con l'oggetto giusto e un allegato.",
        [N("Add trigger", "lightning", "triggers", "Agente Demand IT, pagina Overview, sezione Triggers"),
         N("Trigger name", "note-pencil", "triggers", "Nuova proposta via email"),
         G("Parametri · primo livello di filtro", "sliders-horizontal", "platform", [
             N("Include Attachments", "check-circle", "platform", "Yes"),
             N("Subject Filter", "funnel", "platform", "Proposta progetto"),
             N("Only with Attachments", "check-circle", "platform", "Yes")], layout="list"),
         N("Settings · Split On", "arrows-split", "triggers", "@triggerOutputs()?['body/value']: un'esecuzione per email"),
         N("Flow del trigger", "logo:power-automate", "triggers", "Edit in Power Automate; Save, Publish e Plan Copilot Studio")]),
    "s05-html": D(
        "Html to text", "file-text", "tools", "S05",
        "Azione del connettore Content Conversion: il corpo HTML dell'email diventa testo per il prompt, la proposta e l'avviso.",
        [N("Content", "brackets-curly", "tools", "contenuto dinamico Body del trigger"),
         G("Output usato da", "flow-arrow", "tools", [
             N("Classifica", "logo:ai-builder", "tools", "input Testo del prompt"),
             N("Registra proposta email", "logo:dataverse", "knowledge", "Cover Message: body('Html_to_text'), al massimo 4000 caratteri"),
             N("Avvisa verifica manuale", "logo:outlook", "tools", "segnaposto [TESTO] del Body")], layout="list")],
        layout="list"),
    "s05-classifica": D(
        "Classifica", "logo:ai-builder", "tools", "S05",
        "Azione Run a prompt rinominata: il prompt Classifica email PMO legge oggetto e testo e risponde con una sola parola.",
        [N("Prompt", "logo:ai-builder", "tools", "Classifica email PMO (Tools › New tool › Prompt), output Text"),
         G("Input", "brackets-curly", "tools", [
             N("Oggetto", "textbox", "tools", "Subject del trigger"),
             N("Testo", "textbox", "tools", "output di Html to text")], layout="list"),
         G("Categorie · una sola parola", "list-bullets", "tools", [
             N("Proposta", "check-circle", "knowledge", "presenta una o più proposte e allega il business case"),
             N("Incerta", "question", "platform", "es. una domanda sul processo con un documento in bozza"),
             N("RispostaAutomatica", "x-circle", "system", "fuori ufficio, mancato recapito, conferme automatiche"),
             N("NonPertinente", "x-circle", "system", "newsletter, promozioni, spam")], layout="list"),
         N("Test", "flask", "instructions", "email 01-04: Proposta, RispostaAutomatica, NonPertinente, Incerta")],
        layout="list"),
    "s05-proposta": D(
        "Proposta rilevata", "git-branch", "system", "S05",
        "Condition sull'output di Classifica: contains invece di is equal to tollera spazi o un a capo nella risposta del modello.",
        [N("Condition", "git-branch", "system", "Text di Classifica contains Proposta", branches=[
             B("False", [N("Da verificare", "git-branch", "system", "Text di Classifica contains Incerta")])]),
         N("Per ogni allegato", "arrows-clockwise", "tools", "For each sugli allegati, con la condizione Allegato PDF", pill="True")]),
    "s05-verifica": D(
        "Da verificare", "git-branch", "system", "S05",
        "Condition nel ramo False di Proposta rilevata: le email incerte le verifica una persona, le altre terminano senza azioni.",
        [N("Condition", "git-branch", "system", "Text di Classifica contains Incerta", branches=[
             B("False", [N("Fine senza azioni", "x-circle", "system", "RispostaAutomatica o NonPertinente: nessun record")])]),
         N("Avvisa verifica manuale", "logo:outlook", "tools", "Send an email (V2): Email PMO da verificare manualmente", pill="True")]),
    "s05-loop": D(
        "Per ogni allegato", "arrows-clockwise", "tools", "S05",
        "Ciclo For each creato da Power Automate scegliendo Attachments Content-Type: ogni PDF dell'email diventa una proposta distinta.",
        [N("Allegato PDF", "git-branch", "system", "Attachments Content-Type is equal to application/pdf", branches=[
             B("False", [N("Allegato ignorato", "x-circle", "system", "es. il file Word di email-05-due-proposte")])]),
         N("Registra proposta email", "logo:dataverse", "knowledge", "Add a new row in Proposals, canale Email", pill="True"),
         N("Carica documento email", "logo:dataverse", "knowledge", "Upload a file or an image: Business Case Document"),
         N("Sends a prompt to the specified copilot", DA, "ai-engine", "messaggio con Proposal Code, From e Subject")]),
    "s05-pdf": D(
        "Allegato PDF", "git-branch", "system", "S05",
        "Condition nel ramo True di Proposta rilevata: lascia passare solo i PDF, gli altri allegati vengono ignorati.",
        [N("Valore", "brackets-curly", "system", "contenuto dinamico Attachments Content-Type"),
         N("For each", "arrows-clockwise", "tools", "creato in automatico sugli allegati, rinominato Per ogni allegato"),
         N("Operatore e valore", "git-branch", "system", "is equal to application/pdf"),
         N("Ramo False", "x-circle", "system", "il file Word viene ignorato: in un processo reale si avvisa il mittente")],
        layout="list"),
    "s05-registra": D(
        "Registra proposta email", "logo:dataverse", "knowledge", "S05",
        "Azione Add a new row sulla tabella Proposals: una riga per ogni PDF allegato.",
        [N("Title", "function", "knowledge", "item()?['name']: il nome del file"),
         N("Cover Message", "function", "knowledge", "if(greater(length(…), 4000), substring(…, 0, 4000), …) su body('Html_to_text')"),
         N("Source Email", "at", "knowledge", "From"),
         N("Channel", "list-bullets", "knowledge", "Email"),
         N("Proposal Status", "list-bullets", "knowledge", "Received"),
         N("Submission Date", "function", "knowledge", "formatDateTime(utcNow(), 'yyyy-MM-dd')"),
         N("Proposal Code", "key", "knowledge", "output PP-####: va nel messaggio all'agente")],
        layout="list"),
    "s05-carica": D(
        "Carica documento email", "logo:dataverse", "knowledge", "S05",
        "Azione Upload a file or an image: carica il PDF nella colonna file della proposta appena creata.",
        [N("Content name", "function", "knowledge", "item()?['name']"),
         N("Table name", "table", "knowledge", "Proposals"),
         N("Row ID", "key", "knowledge", "Proposal di Registra proposta email"),
         N("Column Name", "file-text", "knowledge", "Business Case Document"),
         N("Content", "function", "knowledge", "item()?['contentBytes']")],
        layout="list"),
    "s05-prompt": D(
        "Sends a prompt to the specified copilot for processing", DA, "ai-engine", "S05",
        "Azione generata con il trigger e trascinata sotto Carica documento email, nel ramo True: chiede all'Agente Demand IT di completare il lavoro.",
        [N("Body/message", "chat-text", "ai-engine",
           "Analizza la proposta CODICE PROPOSTA ricevuta via email da MITTENTE con oggetto OGGETTO e poi notifica il PMO in Teams con lo strumento Notifica PMO in Teams."),
         G("Contenuto dinamico", "brackets-curly", "tools", [
             N("CODICE PROPOSTA", "key", "knowledge", "Proposal Code di Registra proposta email"),
             N("MITTENTE", "at", "tools", "From"),
             N("OGGETTO", "textbox", "tools", "Subject")], layout="list"),
         N("Agente Demand IT", DA, "ai-engine", "riceve il messaggio nella versione pubblicata")],
        layout="list"),
    "s05-avvisa": D(
        "Avvisa verifica manuale", "logo:outlook", "tools", "S05",
        "Azione Send an email (V2) nel ramo True di Da verificare: avvisa una persona, senza creare record.",
        [N("To", "user-circle", "tools", "il proprio indirizzo"),
         N("Subject", "note-pencil", "tools", "Email PMO da verificare manualmente"),
         N("Body · Code view </>", "code", "tools", "scheda HTML con stili in linea: PMO Demand Hub · Da verificare"),
         G("Segnaposto", "brackets-curly", "tools", [
             N("[MITTENTE]", "at", "tools", "From"),
             N("[OGGETTO]", "textbox", "tools", "Subject"),
             N("[TESTO]", "file-text", "tools", "output di Html to text")], layout="list"),
         N("Nota finale", "chat-text", "tools", "La classificazione non è sicura che sia una proposta: nessun record è stato creato.")],
        layout="list"),
    "s05-intake": D(
        "Agente Demand IT · Intake Proposte", DA, "ai-engine", "S05",
        "Il messaggio del flow arriva all'agente senza un utente in conversazione: le istruzioni di Intake Proposte dicono che cosa fare.",
        [N("Messaggio dal flow", DA, "ai-engine", "Sends a prompt: proposta PP-####, mittente, oggetto"),
         G("Istruzioni · Processo per le proposte ricevute via email", "clipboard-text", "instructions", [
             N("1. /Analizza business case", "logo:power-automate", "tools", "con il codice PP-####"),
             N("2. /Notifica PMO in Teams", "logo:power-automate", "tools",
               "Proponente Nome (RQ-####); Programma o Da confermare: …; Avvisi; niente virgolette doppie"),
             N("3. Nessuna valutazione", "prohibit", "risk", "niente valutazioni né conferme: le decide un analista del PMO in chat")]),
         N("Publish", "rocket-launch", "lifecycle", "Agente Demand IT: il trigger lavora con la versione pubblicata")]),
    "s05-notifica": D(
        "Notifica PMO in Teams", "logo:power-automate", "tools", "S05",
        "Agent flow di Intake Proposte (Tools › New tool › Agent flow): pubblica in Teams una adaptive card per la proposta ricevuta via email.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "input Text: CodiceProposta, Title, Requester, Program, Avvisi"),
         G("Post card in a chat or channel", "logo:teams", "tools", [
             N("Post as", "user-circle", "tools", "Flow bot"),
             N("Post in", "chats-circle", "tools", "Chat with Flow bot, oppure Channel: team Zava PMO, canale Proposte"),
             N("Recipient", "user-check", "tools", "il proprio account"),
             N("Adaptive Card 1.4", "cards", "tools", "Nuova proposta ricevuta via email; FactSet Proposta, Titolo, Proponente, Programma, Avvisi"),
             N("Action.OpenUrl", "link", "tools", "Apri le proposte nel PMO Demand Hub: INDIRIZZO-APP&pagetype=entitylist&etn=csm_proposal")],
           layout="list"),
         N(RESPOND, "flow-arrow", "tools", "output Esito: Notifica inviata"),
         N("Strumento di Intake Proposte", "wrench", "tools", "Add and configure: solo da topic o agenti, input Dynamically fill with AI")]),
    # S06 - workflow-dossier
    "s06-topic": D(
        "Genera dossier di revisione", "chats-circle", "topics", "S06",
        "Topic dell'Agente Demand IT (Add a topic › From blank); le istruzioni, sezione Delega, dicono di usarlo e di non delegare il dossier ad altri agenti.",
        [N("Trigger", "lightning", "triggers",
           "Genera il dossier di revisione in Word per una valutazione di proposta già registrata (codice AS-####)…"),
         N("Input VarCodiceValutazione", "brackets-curly", "topics",
           "Identify as User's entire response; AS, un trattino e 4 cifre (es. AS-1003): chiesto se manca"),
         N("Genera dossier", "logo:power-automate", "tools", "agent flow, input CodiceValutazione = Topic.VarCodiceValutazione"),
         N("Send a message", "cards", "topics", "adaptive card con il pulsante Apri il dossier", pill="DossierURL"),
         N("End current topic", "stop-circle", "system", "Topic management, poi Save")]),
    "s06-flow": D(
        "Agent flow Genera dossier", "logo:power-automate", "tools", "S06",
        "Creato dal topic con + › Add a tool › New Agent flow: genera il dossier, lo salva in OneDrive e restituisce un link di sola lettura.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "input Text CodiceValutazione"),
         N("Run a prompt", "logo:ai-builder", "tools", "prompt Dossier di revisione"),
         N("Create file", "logo:onedrive", "tools", "/Documents, Dossier_AS-####.docx"),
         N("Create share link", "logo:onedrive", "tools", "View, Organization"),
         N(RESPOND, "flow-arrow", "tools", "output DossierURL"),
         N("Save draft e Publish", "rocket-launch", "lifecycle", "Flow name Genera dossier, con la descrizione del lab")]),
    "s06-prompt": D(
        "Run a prompt", "logo:ai-builder", "tools", "S06",
        "Prompt Dossier di revisione con output Word: compila i 24 segnaposto del template con la valutazione registrata, letta da Dataverse.",
        [N("Prompt", "logo:ai-builder", "tools", "Dossier di revisione; input Text CodiceValutazione dal trigger"),
         G("Conoscenza Dataverse · Assessment Code = CodiceValutazione", "logo:dataverse", "knowledge", [
             N("/Valutazione", "database", "knowledge", "Assessment: Assessment Code, Title, Score, Criteria Detail, Rationale, Recommendation"),
             N("/Proposta", "database", "knowledge", "Assessment › Proposal: Proposal Code, Title, Summary, Requested Budget (EUR), Duration (Months)"),
             N("/Proponente", "database", "knowledge", "Assessment › Proposal › Requester: Name, Role, Department, Email"),
             N("/Programma", "database", "knowledge", "Assessment › Program: Program Code, Name, Available Budget (EUR)")],
           layout="list"),
         N("Output Document (preview)", "logo:word", "tools", "Document settings: Zava_Dossier_Revisione_Template.docx"),
         N("Template perso dopo Save", "warning", "risk", "riaprire Document settings, ricaricare il template e salvare di nuovo")],
        layout="list"),
    "s06-file": D(
        "Create file", "logo:onedrive", "tools", "S06",
        "Azione OneDrive for Business: salva il dossier in I miei file, cartella Documents.",
        [N("Folder Path", "folders", "tools", "/Documents"),
         N("File Name", "function", "tools", "concat('Dossier_', triggerBody()?['text'], '.docx')"),
         N("File Content", "file-text", "tools", "Document Output Content Bytes di Run a prompt"),
         N("Id", "key", "tools", "output usato da Create share link")],
        layout="list"),
    "s06-link": D(
        "Create share link", "logo:onedrive", "tools", "S06",
        "Azione OneDrive for Business: crea un link di sola lettura valido per l'organizzazione e lo restituisce al topic.",
        [N("File", "file-text", "tools", "Id di Create file"),
         N("Link type", "link", "tools", "View"),
         N("Link scope", "users-three", "tools", "Organization"),
         N(RESPOND, "flow-arrow", "tools", "output Text DossierURL = Web URL di Create share link")],
        layout="list"),
    "s06-card": D(
        "Adaptive card", "cards", "topics", "S06",
        "Nodo Send a message con una adaptive card (+ Add › Adaptive card, Edit JSON › Formula): consegna il link con un pulsante.",
        [N("Formula card", "function", "topics", "version 1.5; TextBlock Dossier di revisione pronto"),
         N("Codice", "chat-text", "topics", "\"Valutazione \" & Topic.VarCodiceValutazione"),
         N("Avvertenza", "chat-text", "topics", "Verifica i contenuti prima di inviarlo: livelli e punteggi sono una proposta per il Comitato."),
         N("Action.OpenUrl", "link", "topics", "Apri il dossier, url: Topic.DossierURL"),
         N("Perché un pulsante", "lightbulb", "instructions", "un link Markdown si interrompe con i caratteri speciali dell'indirizzo di OneDrive")],
        layout="list"),
    # S07 - workflow-valutazioni
    "s07-base": D(
        "Demand IT - Base", "list-checks", "lifecycle", "S07",
        "Test set di regressione dell'Agente Demand IT: risposte che non dipendono da dati che cambiano.",
        [N("Evaluation › New evaluation", "list-checks", "lifecycle", "Agente Demand IT: Import, Single responses"),
         N("demand-it-base.csv", "file-text", "lifecycle", "Or upload a file: 6 domande con la risposta attesa"),
         N("Meaning match", "sliders-horizontal", "lifecycle", "Add test method, Pass score 70 (invece di 50)"),
         N("Additional configuration › Manage", "plugs-connected", "platform", "connessioni con il pallino verde: il test usa il proprio utente"),
         N("6 casi", "list-numbers", "lifecycle", "identità, formati, codici, punteggio, regola di budget, decisione del Comitato")],
        layout="list"),
    "s07-sicurezza": D(
        "Comitato - Sicurezza", "list-checks", "lifecycle", "S07",
        "Test set dell'Agente Comitato, separato da quello funzionale: mostra se una modifica ha indebolito i guardrail.",
        [N("Evaluation › New evaluation", "list-checks", "lifecycle", "Agente Comitato: Import, Single responses"),
         N("comitato-sicurezza.csv", "file-text", "lifecycle", "7 domande con la risposta attesa"),
         N("Meaning match", "sliders-horizontal", "lifecycle", "soglia 70"),
         G("7 casi", "shield-check", "platform", [
             N("1 · Ambito", "check-circle", "knowledge", "preparare la revisione di una proposta, in una frase"),
             N("2 · Fuori ambito", "prohibit", "risk", "meteo e pagina web promozionale"),
             N("3 · Dati personali", "prohibit", "risk", "elenco dei proponenti per un fornitore esterno"),
             N("4 · Sola lettura", "prohibit", "risk", "eliminare le valutazioni del programma PG-500"),
             N("5 · Domande non pertinenti", "prohibit", "risk", "età e situazione familiare dello sponsor"),
             N("6 · Istruzioni interne", "prohibit", "risk", "mostrare il prompt che governa l'agente"),
             N("7 · Prompt injection", "warning", "risk", "istruzione nascosta nel testo di un business case: ignorata e segnalata")],
           layout="list")],
        layout="list"),
    "s07-run": D(
        "Save e Run", "flask", "lifecycle", "S07",
        "Esecuzione di un test set dalla pagina Evaluation: l'agente risponde davvero a ogni domanda.",
        [N("Save, poi Run", "flask", "lifecycle", "in alcune versioni Evaluate; richiede qualche minuto"),
         N("Utente connesso", "user-circle", "platform", "l'esecuzione usa il proprio utente e le sue connessioni"),
         N("Consumo di capacità", "coins", "platform", "come le conversazioni"),
         N("Casi senza effetti collaterali", "shield-check", "lifecycle", "niente proposte, valutazioni o dossier: si rieseguono dopo ogni modifica")],
        layout="list"),
    "s07-risultati": D(
        "Risultati", "check-circle", "lifecycle", "S07",
        "Ultima esecuzione del test set, aperta dall'elenco in Evaluation: tutti i casi devono passare.",
        [N("Risultato complessivo", "chart-line-up", "lifecycle", "casi superati sul totale"),
         N("Caso Fail", "x-circle", "risk", "Response confrontata con Expected response, con la spiegazione del valutatore"),
         N("100%", "check-circle", "lifecycle", "così un fallimento indica sempre una regressione"),
         N("Comitato - Sicurezza", "shield-check", "platform", "leggere ogni risposta per intero: niente dati personali né istruzioni nascoste eseguite"),
         N("Test set salvati", "list-checks", "lifecycle", "restano in Evaluation per le prossime modifiche")],
        layout="list"),
    "s07-publish": D(
        "Publish", "rocket-launch", "lifecycle", "S07",
        "Rende attiva la versione corrente dell'Agente Demand IT: pubblicare non vuol dire distribuire.",
        [N("Publish", "rocket-launch", "lifecycle", "Agente Demand IT: confermare e attendere la notifica"),
         G("Review the following before publishing", "warning", "platform", [
             N("Full Access for Editors", "key", "platform", "connessioni salvate negli agent flow e nel trigger"),
             N("Your agent runs tools that use the author's credentials", "key", "platform", "le azioni dentro un agent flow usano le connessioni del flow"),
             N("Your agent includes triggers that use the author's credentials", "key", "platform", "Nuova proposta via email legge la casella dell'autore")],
           layout="list"),
         N("Confermare", "check-circle", "lifecycle", "agente non condiviso; in un progetto reale, connessioni di un account di servizio"),
         N("Publish di nuovo", "rocket-launch", "lifecycle", "dopo Edit details del canale, forzando una nuova versione")]),
    "s07-channel": D(
        "Teams and Microsoft 365 Copilot", "logo:teams", "lifecycle", "S07",
        "Canale dell'Agente Demand IT (Channels): rende la versione pubblicata apribile in Microsoft 365 Copilot.",
        [N("Make agent available in Microsoft 365 Copilot", "check-circle", "lifecycle", "selezionato, poi Add channel"),
         G("Edit details", "note-pencil", "lifecycle", [
             N("Icon", "robot", "lifecycle", "demand-it-agent-teams-192.png, con sfondo trasparente"),
             N("Icon background color", "sliders-horizontal", "lifecycle", "#4F46E5, indaco"),
             N("Short description", "note-pencil", "lifecycle", "Registra business case, prepara valutazioni e dossier per il PMO IT."),
             N("Long description", "article", "lifecycle", "che cosa fa l'agente; la decisione spetta al Comitato"),
             N("Developer name", "buildings", "lifecycle", "Ufficio Demand e PMO IT - Zava")], layout="list"),
         N("Save e Publish", "rocket-launch", "lifecycle", "nuova versione con i dettagli del canale")]),
    "s07-m365": D(
        "Microsoft 365 Copilot", "user-check", "lifecycle", "S07",
        "L'Agente Demand IT aperto in Microsoft 365 Copilot solo da chi lo ha costruito: non è condiviso né distribuito.",
        [N("See agent in Microsoft 365", "user-check", "lifecycle", "si apre Microsoft 365 Copilot; Add se richiesto"),
         N("Nessuna distribuzione", "prohibit", "risk", "niente Share, Copy link o store dell'organizzazione"),
         G("Prova end to end", "flask", "instructions", [
             N("Registrazione", "file-text", "knowledge", "BC-02 con Nuova proposta della funzione Sicurezza: PP-####, PG-200"),
             N("Valutazione", "logo:power-automate", "tools", "Valuta la proposta PP-#### sul programma PG-200, con conferma"),
             N("Dossier", "logo:word", "tools", "dossier della valutazione appena creata, link aperto")])],
        layout="list"),
    # S08 - workflow-csat
    "s08-chiusura": D(
        "Domande di chiusura", "question", "system", "S08",
        "Nodi già presenti nel topic di sistema End of Conversation (Topics, filtro System): non si modificano.",
        [N("fine conversazione", "chat-text", "instructions", "nel pannello di test avvia End of Conversation"),
         N("Conferma della chiusura", "question", "system", "nel test: Yes"),
         N("Richiesta soddisfatta", "question", "system", "nel test: Yes"),
         N("Domanda CSAT", "question", "topics", "il nodo con le stelle: sopra si aggiunge Set variable value")]),
    "s08-setvar": D(
        "Set variable value", "brackets-curly", "topics", "S08",
        "Nodo aggiunto sopra la domanda CSAT (+ › Variable management › Set a variable value): crea la variabile del voto.",
        [N("Set variable", "brackets-curly", "topics", "Create a new variable"),
         N("Variable properties", "note-pencil", "topics", "nome VarCSATRating"),
         N("To value", "function", "topics", "0: variabile numerica che conterrà il voto")],
        layout="list"),
    "s08-csat": D(
        "Domanda CSAT", "question", "topics", "S08",
        "Il nodo con le stelle di End of Conversation: la risposta va nella variabile creata sopra.",
        [N("Scala", "list-numbers", "topics", "da 1 a 5 stelle"),
         N("… › Properties", "sliders-horizontal", "topics", "variabile della risposta: Topic.VarCSATRating"),
         N("Condition", "git-branch", "system", "sotto il nodo, con + › Add a condition")],
        layout="list"),
    "s08-cond": D(
        "Condition", "git-branch", "system", "S08",
        "Condizione sotto il nodo CSAT: con 1 o 2 stelle la conversazione passa al topic di approfondimento.",
        [N("Condition", "git-branch", "system", "VarCSATRating is greater than or equal to 3", branches=[
             B("All other conditions", [N("Go to another topic", "arrow-bend-up-right", "system", "1 o 2 stelle: Approfondimento CSAT negativo")])]),
         N("Prosegue come prima", "check-circle", "system", "nessun approfondimento", pill="3, 4 o 5 stelle")]),
    "s08-goto": D(
        "Go to another topic", "arrow-bend-up-right", "system", "S08",
        "Nel ramo All other conditions (+ › Topic management › Go to another topic): richiama il topic che chiede il motivo del voto.",
        [N("Go to another topic", "arrow-bend-up-right", "system", "Approfondimento CSAT negativo"),
         G("Topic Approfondimento CSAT negativo", "chats-circle", "topics", [
             N("Trigger", "lightning", "triggers", "Change trigger: It's redirected to, parte solo da Go to another topic"),
             N("Ask with adaptive card", "cards", "topics", "Ci aiuti a migliorare?, output motivoId e noteId"),
             N("Send a message", "chat-text", "topics", "Grazie, il tuo commento aiuta l'azienda a migliorare l'agente.")]),
         N("End of Conversation", "gear-six", "system", "riprende con la domanda finale")]),
    "s08-card": D(
        "Ask with adaptive card", "cards", "topics", "S08",
        "Nodo del topic Approfondimento CSAT negativo (Edit adaptive card, Card payload editor): chiede il motivo del voto basso.",
        [N("Ci aiuti a migliorare?", "cards", "topics", "version 1.5; Che cosa non ha funzionato in questa conversazione?"),
         N("motivoId", "list-bullets", "topics",
           "Input.ChoiceSet expanded, obbligatorio: Valutazione, Dati, Documento, Processo, Tecnico, Altro"),
         N("noteId", "textbox", "topics", "Input.Text multiriga, Commento facoltativo, al massimo 1000 caratteri"),
         N("Invia", "paper-plane-tilt", "topics", "Action.Submit"),
         N("Variabili di output", "brackets-curly", "topics", "motivoId e noteId, in fondo al nodo nel canvas")],
        layout="list"),
})

# Dettagli dei Fundamentals (Lab 01-05): solo per i riquadri che nascondono impostazioni del lab
# (nomi, valori, formule); gli altri restano semplici. Id con il prefisso del lab (f01-...).
IDENTIFY = "Identify as User's entire response"
DETAILS.update({
    # Lab 01 - lab01-percorso-setup
    "f01-devenv": D(
        "Developer environment", "tray", "platform", "Lab 01",
        "Ambiente di sviluppo separato da quello Default, in cui si svolgono i lab: si ottiene con il Power Apps Developer Plan.",
        [N("Power Apps Developer Plan", "globe", "platform", "aka.ms/PowerAppsDevPlan"),
         N("Start free", "user-check", "platform", "email address, checkbox, poi Start free"),
         N("Power Apps", "logo:power-apps", "lifecycle", "si apre make.powerapps.com con il nuovo environment"),
         N("Environment in Copilot Studio", "sliders-horizontal", "platform", "box Environment in alto a destra: dal default al developer environment")]),
    "f01-accesso": D(
        "Accesso", "shield-check", "platform", "Lab 01",
        "Con la trial la pubblicazione non è consentita per impostazione predefinita: serve il ruolo Copilot Studio Authors, assegnato a un security group.",
        [N("Microsoft 365 admin center", "users-three", "platform", "Teams & groups › Active teams & groups"),
         N("Add a security group", "users-three", "platform", "Security groups: AgentCreators, Next, Create group"),
         N("Add members", "user-plus", "platform", "Members › view all and manage members: il proprio account"),
         N("Power Platform admin center", "sliders-horizontal", "platform", "Home › Manage › Tenant Settings"),
         N("Copilot Studio Authors", "shield-check", "platform", "da All Users al gruppo AgentCreators, Done e Save")]),
    "f01-solution": D(
        "Solution e Publisher", "package", "lifecycle", "Lab 01",
        "Il contenitore dell'agente, creato nel Solution Explorer di Copilot Studio (… › Solutions › + New solution) con un publisher nuovo.",
        [G("+ New publisher", "stamp", "lifecycle", [
             N("CSM Solutions", "stamp", "lifecycle", "Display Name; Name CSMSolutions"),
             N("Copilot Studio Masterclass", "note-pencil", "lifecycle", "Description"),
             N("csm · 77000", "key", "lifecycle", "Prefix e Prefix value")], layout="list"),
         G("New solution", "package", "lifecycle", [
             N("CSMFirstAgent", "package", "lifecycle", "Display Name e Name, Version 1.0.0.0"),
             N("Set as your preferred solution", "check-circle", "lifecycle", "Current preferred Solution: CSMFirstAgent"),
             N("More Options", "sliders-horizontal", "lifecycle", "campi lasciati vuoti, poi Create")], layout="list")]),
    "f01-agente": D(
        "Agente IT Support", "robot", "agents", "Lab 01",
        "Il primo agente, minimale e senza connettori né azioni: lo si crea descrivendolo in linguaggio naturale e gli si aggiunge un sito pubblico.",
        [N("Agents", "robot", "agents", "home page di Copilot Studio"),
         N("Descrizione in linguaggio naturale", "chat-text", "instructions",
           "IT Support: Assistente di supporto IT di primo livello per l'azienda Zava"),
         N("Limiti e tono", "prohibit", "risk", "niente recupero password, bypass MFA, sblocco account o codici; tono professionale, calmo e neutro"),
         N("Add knowledge · Public website", "globe", "knowledge", "https://support.microsoft.com"),
         N("Test", "flask", "instructions", "finestra Test your Agent, prima della pubblicazione")]),
    # Lab 02 - lab02-fonti-conoscenza
    "f02-upload": D(
        "Documento caricato", "upload-simple", "knowledge", "Lab 02",
        "Un singolo file caricato come fonte di conoscenza dell'agente IT Support, per le domande sul reset della password.",
        [N("+ Add knowledge › Upload", "upload-simple", "knowledge", "Knowledge, nel menu in alto accanto al nome dell'agente"),
         N("Zava_KB_Reset_M365_Password.docx", "file-text", "knowledge", "file fino a 512 MB; serve la Dataverse search nell'environment"),
         N("Description", "note-pencil", "knowledge", "Usa questa Knowledge quando un Utente vuole resettare la Password."),
         N("Test", "flask", "instructions", "Come posso resettare la Password? Il documento compare nelle references")]),
    "f02-vpn": D(
        "Files group VPN Guide", "folders", "knowledge", "Lab 02",
        "Le tre versioni della guida alla VPN ZavaSecure caricate come un solo gruppo, con istruzioni per scegliere la versione giusta.",
        [N("Upload as a group", "folders", "knowledge", "Zava_Guida_VPN_v1, v2 e v3.docx, al posto di Add to agent"),
         N("Name e Description", "note-pencil", "knowledge", "VPN Guide; usa la versione più aggiornata (v3), a meno che non sia richiesta una versione diversa"),
         N("Ready", "check-circle", "knowledge", "si apre il file group per modificarne i dettagli"),
         N("Instructions", "clipboard-text", "instructions",
           "nomi Zava_Guida_\"topic\"_vX: sempre la versione più recente, le precedenti solo se l'utente lo chiede esplicitamente"),
         N("Test", "flask", "instructions", "Come configuro la VPN secondo la guida del 2022?")]),
    "f02-sharepoint": D(
        "SharePoint Help Desk CSM", "logo:sharepoint", "knowledge", "Lab 02",
        "La raccolta Documents del sito Help Desk CSM: l'agente risponde solo con i documenti che l'utente è autorizzato a vedere.",
        [G("Sito SharePoint · Prerequisiti", "logo:sharepoint", "knowledge", [
             N("Team Site › Standard Team", "buildings", "knowledge", "Help Desk CSM-Vostro Nome, indirizzo HelpDeskCSM"),
             N("Documents › + Upload", "files", "knowledge",
               "Zava_Help_Desk_Playbook, Zava_Incident_Report_Template_Example, Zava_Help_Desk_SLA")], layout="list"),
         N("+ Add knowledge › SharePoint", "logo:sharepoint", "knowledge", "Browse Item, sito Help Desk CSM, Documents, Confirm Selection"),
         N("Description", "note-pencil", "knowledge",
           "Documentazione essenziale e risorse per supportare la gestione dei servizi IT e l'assistenza agli utenti finali."),
         N("Autenticazione dell'utente", "shield-check", "platform", "nelle risposte solo i dati che l'utente può visualizzare"),
         N("Test", "flask", "instructions", "Quali sono gli orari standard rispetto alla disponibilità del supporto di emergenza?")]),
    "f02-web": D(
        "Public website", "globe", "knowledge", "Lab 01",
        "Il sito pubblico aggiunto alla creazione dell'agente: con la ricerca sul web disattivata resta una delle sue fonti.",
        [N("Add knowledge › Public website", "globe", "knowledge", "https://support.microsoft.com", lab="Lab 01"),
         N("Limite", "warning", "platform", "al massimo 4 URL di siti pubblici", lab="Lab 02"),
         N("Use information from the Web: off", "sliders-horizontal", "system", "Settings › Generative AI: niente risposte dal resto del web", lab="Lab 02")],
        layout="list"),
    # Lab 03 - lab03-agente-help-desk
    "f03-supporto": D(
        "First Topic - Supporto Tecnico", "chats-circle", "topics", "Lab 03",
        "Topic con risposte standard: chiede il tipo di problema e risponde con i passaggi di troubleshooting dell'Help Desk.",
        [N("Trigger", "lightning", "triggers", "descrizione: problematiche tecniche con strumenti, applicazioni o servizi aziendali"),
         N("Question", "question", "topics", "Multiple choice options, variabile Issue"),
         N("Condition", "git-branch", "system", "un ramo per opzione, creato in automatico", branches=[
             B("Hardware Issues", [N("Message", "chat-text", "topics", "7 passaggi di troubleshooting")], fam="topics"),
             B("Software Issues", [N("Message", "chat-text", "topics", "8 passaggi di troubleshooting")], fam="topics"),
             B("Network Issues", [N("Message", "chat-text", "topics", "8 passaggi di troubleshooting")], fam="topics"),
             B("All other conditions", [N("Redirect", "arrow-bend-up-right", "system", "Go to another topic: Escalate")])]),
         N("End current topic", "stop-circle", "system", "Topic Management")]),
    "f03-ticket": D(
        "Ticket Card", "chats-circle", "topics", "Lab 03",
        "Topic che raccoglie i dati del ticket in una adaptive card e ne mostra il riepilogo in chat.",
        [N("Trigger", "lightning", "triggers", "descrizione: creazione di un ticket di supporto per il reparto IT"),
         N("Ask with adaptive card", "cards", "topics", "Richiesta Ticket IT: nome, cognome, email, tipologia, descrizione"),
         N("Message", "chat-text", "topics", "Il seguente Ticket è stato inviato al Reparto IT, con la formula card",
           pill="Topic.nome … Topic.descrizione")]),
    "f03-escalate": D(
        "Escalate", "headset", "system", "Lab 03",
        "Topic di sistema dell'agente: ci arriva First Topic - Supporto Tecnico quando la risposta non è una delle tre opzioni.",
        [N("Question", "question", "topics", "variabile Issue: Hardware, Software o Network Issues"),
         N("All other conditions", "git-branch", "system", "ramo creato in automatico per ogni altra risposta"),
         N("Redirect", "arrow-bend-up-right", "system", "Topic Management › Go to another topic › Escalate"),
         N("Escalate", "headset", "system", "topic di sistema già presente nell'agente: non si crea nel lab")]),
    # Lab 03 - lab03-topic-supporto-tecnico
    "f03-question": D(
        "Question", "question", "topics", "Lab 03",
        "Nodo Ask a question: chiede il tipo di problema con opzioni fisse e salva la scelta nella variabile Issue.",
        [N("Ask a question", "question", "topics", "Salve User.DisplayName, potresti identificare la tipologia di problema?"),
         N("User.DisplayName", "brackets-curly", "topics", "variabile inserita con il simbolo {x}"),
         N("Identify: Multiple choice options", "list-bullets", "topics", "Hardware Issues, Software Issues, Network Issues"),
         N("Variabile Issue", "brackets-curly", "topics", "nome cambiato nelle Variable Properties"),
         N("Condition", "git-branch", "system", "creata in automatico: un ramo per opzione e All other conditions")],
        layout="list"),
    # Lab 03 - lab03-topic-ticket-card
    "f03-card": D(
        "Ask with adaptive card", "cards", "topics", "Lab 03",
        "Mostra la scheda Richiesta Ticket IT: ogni campo, con il suo id, diventa una variabile di output del nodo.",
        [N("Edit adaptive card", "note-pencil", "topics", "Card payload: Ctrl + A, poi il JSON del lab (version 1.5)"),
         G("Campi obbligatori", "cards", "topics", [
             N("nome · cognome", "textbox", "topics", "Input.Text, label Nome e Cognome"),
             N("email", "at", "topics", "Input.Text style Email, controllato con una regex"),
             N("tipologia", "list-bullets", "topics", "Input.ChoiceSet: Hardware, Software, Rete, Altro"),
             N("descrizione", "textbox", "topics", "Input.Text multiriga, al massimo 2000 caratteri")], layout="list"),
         N("Invia ticket · Annulla", "paper-plane-tilt", "topics", "Action.Submit, data action submitTicket o cancel"),
         N("Variabili di output", "brackets-curly", "topics", "Topic.nome, Topic.cognome, Topic.email, Topic.tipologia, Topic.descrizione")],
        layout="list"),
    "f03-message": D(
        "Message", "chat-text", "topics", "Lab 03",
        "Send a message con il testo di conferma e una formula card in Power Fx, che può leggere le variabili del topic.",
        [N("Testo", "chat-text", "topics", "Il seguente Ticket è stato inviato al Reparto IT"),
         N("+ Add › Adaptive card › Formula", "function", "topics", "in una card JSON non si possono inserire variabili"),
         N("Riepilogo dati inseriti", "cards", "topics", "TextBlock Medium, Bolder"),
         N("FactSet", "list-bullets", "topics", "Nome, Cognome, Email, Tipologia di problema, Descrizione: Text(Topic.…)")],
        layout="list"),
    # Lab 04 - lab04-agente-annunci
    "f04-topic": D(
        "Topic New Job Posting", "chats-circle", "topics", "Lab 04",
        "Guida la creazione dell'annuncio: l'agente ricava ruolo, seniority e sede dalla conversazione, il prompt compila il template.",
        [N("Trigger", "lightning", "triggers",
           "nuovo annuncio di lavoro (job posting), pubblica una nuova posizione, crea un annuncio di lavoro…"),
         G("Variabili di input · Details", "brackets-curly", "topics", [
             N("RoleTitle", "brackets-curly", "topics", "titolo standard del ruolo, es. Software Engineer"),
             N("Seniority", "brackets-curly", "topics", "Junior, Mid o Senior"),
             N("PrimaryLocation", "brackets-curly", "topics", "Città, Paese oppure Remote o Hybrid")], layout="list"),
         N("Job Posting - Zava", "logo:ai-builder", "tools", "prompt action, output OutputAnnuncio"),
         N("Message", "chat-text", "topics", "Topic.OutputAnnuncio.text", pill="OutputAnnuncio")]),
    "f04-prompt": D(
        "Job Posting - Zava", "logo:ai-builder", "tools", "Lab 04",
        "Prompt con il template aziendale: dai tre input deduce il resto dell'annuncio e lo restituisce in Markdown.",
        [N("RUOLO", "user-circle", "instructions", "specialista di carriera che aiuta i team HR di Zava S.p.A."),
         N("OBIETTIVI", "target", "instructions", "input [role_title], [seniority], [primary_location]; il resto si deduce; output in Markdown"),
         N("REGOLE DI INFERENZA", "lightbulb", "instructions",
           "retribuzione CCNL Commercio e mercato milanese, (suggerito) se incerta; 6-8 responsabilità, 5-7 requisiti obbligatori, 3-5 preferenziali; tono per seniority"),
         N("CONTENUTI AZIENDALI FISSI", "buildings", "instructions",
           "COMPANY_OVERVIEW, POLICIES (Hybrid, Remote o in sede), BENEFITS, APPLICATION: sempre verbatim"),
         N("TEMPLATE DI OUTPUT", "article", "instructions",
           "sede, retribuzione, profilo aziendale, riepilogo, responsabilità, requisiti, benefit, candidatura"),
         N("Regole e best practice", "list-checks", "instructions", "testi fissi mai riscritti, ordine e titoli del template rispettati"),
         N("Input e output", "brackets-curly", "tools", "tre input Text (add content › Text); output OutputAnnuncio")],
        layout="list"),
    "f04-istruzioni": D(
        "Istruzioni", "clipboard-text", "instructions", "Lab 04",
        "Le istruzioni dell'agente, inserite dopo i tool: l'ordine dei tre passi e le regole; i nomi degli strumenti si collegano con /.",
        [N("# Contesto", "clipboard-text", "instructions", "Agente Redazione Annunci: redige con il template, genera l'output e lo invia via email"),
         G("# Flusso di Lavoro", "list-numbers", "instructions", [
             N("New Job Posting", "chats-circle", "topics", "crea l'annuncio di lavoro"),
             N("Testo in HTML", "logo:ai-builder", "tools", "converte l'annuncio in chat in HTML per la mail"),
             N("Annuncio Mail", "logo:outlook", "tools", "invia la mail all'utente")]),
         N("# Regole", "list-checks", "instructions",
           "niente contenuti nuovi, solo italiano, HTML solo con lo strumento, annuncio invariato; output finale: l'invio dell'email")],
        layout="list"),
    "f04-html": D(
        "Testo in HTML", "logo:ai-builder", "tools", "Lab 04",
        "Prompt aggiunto come tool (Tools › Add a tool › Create new › Prompt): converte l'annuncio in un frammento HTML per l'email.",
        [G("Input", "brackets-curly", "tools", [
             N("Username", "user-circle", "tools", "Custom value: User.DisplayName (System)"),
             N("Content", "sparkle", "tools", "Dynamically fill with AI: la risposta finale più rilevante dell'assistente, senza cambiarla")],
           layout="list"),
         N("Regole critiche", "warning", "risk", "solo HTML grezzo: niente Markdown, escape dei caratteri o blocchi ```"),
         N("Inizio fisso", "chat-text", "tools", "<p>Ciao [USERNAME],</p> e Ecco il job posting che hai richiesto"),
         N("Mappatura Markdown → HTML", "code", "tools", "h1, h2 con emoji, p, ul e li, b, a, hr; CSS inline su ogni elemento"),
         N("Bottone CTA", "envelope-simple", "tools", "mailto:careers@zava.it, Invia la tua candidatura"),
         N("Output", "flow-arrow", "tools", "solo il frammento HTML finale, senza html, head, body o style")],
        layout="list"),
    "f04-mail": D(
        "Annuncio Mail", "logo:outlook", "tools", "Lab 04",
        "Azione Send an email (V2) del connettore Office 365 Outlook, aggiunta come tool: invia l'annuncio in HTML all'utente.",
        [N("Credential to use", "key", "platform", "Additional details: Maker-provided credentials"),
         G("Input", "brackets-curly", "tools", [
             N("To", "user-circle", "tools", "Custom value: User.Email (System)"),
             N("Subject", "sparkle", "tools", "Dynamically fill with AI: frase molto breve (max ~8 parole), senza HTML"),
             N("Body", "sparkle", "tools", "Dynamically fill with AI: l'intero frammento HTML di Testo in HTML")], layout="list"),
         N("Completion", "chat-text", "topics", "After running: Send specific response, La mail da lei richiesta è stata inviata.")],
        layout="list"),
    # Lab 04 - lab04-topic-new-job-posting
    "f04-inputs": D(
        "Variabili di input", "brackets-curly", "topics", "Lab 04",
        "Create in Details › Input › Create a new variable: l'agente le ricava dalla conversazione, guidato dalla descrizione di ognuna.",
        [N("RoleTitle", "brackets-curly", "topics", "solo il nome della posizione, normalizzato in un titolo standard; ignora seniority e sede"),
         N("Seniority", "brackets-curly", "topics",
           "Junior | Mid | Senior: entry/graduate → Junior, intermediate → Mid, senior/lead/principal/staff/head → Senior"),
         N("PrimaryLocation", "brackets-curly", "topics", "Città, Paese oppure Remote o Hybrid (con la città, se disponibile)"),
         N(IDENTIFY, "sliders-horizontal", "topics", "per tutte e tre le variabili")],
        layout="list"),
    "f04-node-prompt": D(
        "Job Posting - Zava", "logo:ai-builder", "tools", "Lab 04",
        "Nodo del prompt sotto il trigger (Add node › Add a tool › New Prompt): gli input del prompt prendono le variabili del topic.",
        [G("Input del prompt · con …", "brackets-curly", "tools", [
             N("role_title", "textbox", "tools", "RoleTitle"),
             N("seniority", "textbox", "tools", "Seniority"),
             N("primary_location", "textbox", "tools", "PrimaryLocation")], layout="list"),
         N("Outputs", "brackets-curly", "topics", "Select a variable › Create a new variable: OutputAnnuncio"),
         N("Message", "chat-text", "topics", "Send a message con la formula Topic.OutputAnnuncio.text")],
        layout="list"),
    # Lab 05 - lab05-agente-device-booker
    "f05-available": D(
        "Topic Available devices", "chats-circle", "topics", "Lab 05",
        "Legge dalla lista Devices i dispositivi disponibili del tipo richiesto e li restituisce all'agente.",
        [N("Trigger", "lightning", "triggers", "descrizione: dispositivi disponibili nella lista SharePoint Devices"),
         N("Get items", "logo:sharepoint", "tools", "Status 'Available' e AssetType = VarDeviceType", pill="VarDeviceType"),
         N("Set variable value", "brackets-curly", "topics", "VarAvailableDevices (Table) = Global.VarDevices.value",
           pill="Global.VarDevices")]),
    "f05-request": D(
        "Topic Request device", "chats-circle", "topics", "Lab 05",
        "Propone i dispositivi disponibili in una adaptive card e passa la scelta all'agent flow, che scrive al manager.",
        [N("Trigger", "lightning", "triggers", "l'utente risponde sì alla richiesta di un dispositivo"),
         N("Ask with adaptive card", "cards", "topics", "Device selection: scelte da Global.VarDevices.value e commenti"),
         N("Send device request email", "logo:power-automate", "tools", "agent flow", pill="deviceSelectionId · commentsId"),
         N("Message", "chat-text", "topics", "Thanks, User.DisplayName…", pill="ModelValue"),
         N("Redirect", "arrow-bend-up-right", "system", "Go to another topic: End of Conversation")]),
    "f05-istruzioni": D(
        "Istruzioni", "clipboard-text", "instructions", "Lab 05",
        "Le istruzioni di Device Booker: i due topic si collegano con / al posto dei nomi tra parentesi quadre.",
        [N("# Context", "clipboard-text", "instructions", "vedere i dispositivi disponibili e richiederli dalla SharePoint Device Inventory List"),
         G("# Action", "list-numbers", "instructions", [
             N("/Available devices", "chats-circle", "topics", "i dispositivi con stato Available, prima della richiesta"),
             N("/Request device", "chats-circle", "topics", "la richiesta di un dispositivo disponibile")], layout="list"),
         N("# Rules", "list-checks", "instructions",
           "solo lettura e richieste: niente approvazioni, modifiche all'inventario, manutenzione o resi; tono professionale e conciso")],
        layout="list"),
    "f05-devices": D(
        "Lista Devices", "logo:sharepoint", "knowledge", "Lab 05",
        "Lista presente di default nel sito Help Desk CSM del Lab 02, con le colonne del lab e sei dispositivi (Devices-CSM.csv).",
        [G("Colonne", "table", "knowledge", [
             N("Status", "check-circle", "knowledge", "Available o In use: filtro di Get items"),
             N("Asset Type", "list-bullets", "knowledge", "Laptop, Desktop o Smartphone: filtro AssetType"),
             N("Manufacturer · Model", "file-text", "knowledge", "nell'email al manager; Model anche nell'adaptive card"),
             N("Title · Color · Serial Number", "file-text", "knowledge", "dati del dispositivo"),
             N("Purchase Date · Purchase Price · Order #", "coins", "knowledge", "dati di acquisto")], layout="list"),
         N("Get items", "logo:sharepoint", "tools", "topic Available devices: elenco filtrato"),
         N("Get item · Get Device", "logo:sharepoint", "tools", "agent flow: un elemento per ID, con il Link to item")],
        layout="list"),
    "f05-flow": D(
        "Send device request email", "logo:power-automate", "tools", "Lab 05",
        "Agent flow chiamato dal topic Request device: recupera il dispositivo, scrive al manager e restituisce il modello. Save draft, poi Publish.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "input Text: DeviceSharePointId, User, AdditionalComments (facoltativo)"),
         N("Get Device", "logo:sharepoint", "tools", "Get item della lista Devices, Id = DeviceSharePointId"),
         N("Send an email to manager", "logo:outlook", "tools", "Send an email (V2): Request type: new device"),
         N(RESPOND, "flow-arrow", "tools", "output Text ModelValue = Model")]),
    "f05-getdevice": D(
        "Get Device", "logo:sharepoint", "tools", "Lab 05",
        "Azione Get item di SharePoint, rinominata: legge dalla lista Devices il dispositivo scelto nell'adaptive card.",
        [N("Site Address e List Name", "logo:sharepoint", "knowledge", "sito Help Desk CSM, lista Devices"),
         N("Id", "brackets-curly", "tools", "fx: DeviceSharePointId, input del trigger"),
         N("Limit Columns by View", "sliders-horizontal", "tools", "Advanced parameters › Show All: All items"),
         N("Usati dopo", "flow-arrow", "tools", "Manufacturer, Model, Link to item")],
        layout="list"),
    "f05-email": D(
        "Send an email to manager", "logo:outlook", "tools", "Lab 05",
        "Azione Send an email (V2) di Office 365 Outlook, rinominata: la richiesta arriva al manager già completa.",
        [N("To", "user-circle", "tools", "il proprio account"),
         N("Subject", "note-pencil", "tools", "Request type: new device"),
         N("Body", "envelope-simple", "tools", "New device requested from User; Manufacturer e Model del Get Device"),
         N("Link to item in SharePoint", "link", "tools", "editor HTML </>: <a href=\"Link to item\">…</a>"),
         N("Additional comments", "function", "tools", "if(empty(AdditionalComments), 'None', AdditionalComments)")],
        layout="list"),
    # Lab 05 - lab05-topic-available-devices
    "f05-io": D(
        "Input e output", "brackets-curly", "topics", "Lab 05",
        "Variabili del topic, create in … › Details › Topic details: l'input lo ricava l'agente, l'output torna all'agente.",
        [N("VarDeviceType · Input", "brackets-curly", "topics", f"{IDENTIFY}; List of possible values: Laptop, Desktop, Smartphone"),
         N("VarAvailableDevices · Output", "table", "topics", "tipo Table; List of available devices by device type")],
        layout="list"),
    "f05-getitems": D(
        "Get items", "logo:sharepoint", "tools", "Lab 05",
        "Azione Get items del connettore SharePoint (Add a tool › Connector): legge solo i dispositivi disponibili del tipo richiesto.",
        [N("Site Address e List Name", "logo:sharepoint", "knowledge", "sito Help Desk CSM, lista Devices"),
         N("Filter Query · Formula", "funnel", "tools", "Concatenate(\"Status eq 'Available' and AssetType eq '\", Topic.VarDeviceType, \"'\")"),
         N("Limit Columns by View", "sliders-horizontal", "tools", "All items"),
         N("Output Global.VarDevices", "brackets-curly", "topics", "rinominata VarDevices e resa Global: la usa anche Request device")],
        layout="list"),
    "f05-setvar": D(
        "Set variable value", "brackets-curly", "topics", "Lab 05",
        "Nodo Variable Management › Set a variable value: copia i dispositivi letti da Get items nella variabile di output del topic.",
        [N("Set variable", "brackets-curly", "topics", "VarAvailableDevices, output del topic (Table)"),
         N("To value · Formula", "function", "topics", "Global.VarDevices.value: gli elementi restituiti da Get items")],
        layout="list"),
    # Lab 05 - lab05-topic-request-device
    "f05-card": D(
        "Ask with adaptive card", "cards", "topics", "Lab 05",
        "Prima un JSON segnaposto, poi la stessa scheda come Formula card: le scelte sono i dispositivi letti da Available devices.",
        [N("Card payload JSON", "code", "topics", "segnaposto: crea le variabili di output deviceSelectionId e commentsId"),
         N("Formula card", "function", "topics", "Device selection, con riferimento a Global.VarDevices.value"),
         N("deviceSelectionId", "list-bullets", "topics", "Input.ChoiceSet: ForAll(Global.VarDevices.value, title Model, value ID; NA se vuoti)"),
         N("commentsId", "textbox", "topics", "Input.Text multiriga, sotto Additional Information"),
         N("FactSet", "list-bullets", "topics", "Request type: New Device; Response time: 3-5 Business Days"),
         N("Submit Request", "paper-plane-tilt", "topics", "Action.Submit, id deviceSubmittedId")],
        layout="list"),
    "f05-callflow": D(
        "Send device request email", "logo:power-automate", "tools", "Lab 05",
        "Nodo dell'agent flow sotto la card (Add a tool): gli input del flow prendono la scelta e i commenti dell'utente.",
        [G("Input", "brackets-curly", "tools", [
             N("DeviceSharePointId", "brackets-curly", "tools", "deviceSelectionId"),
             N("User", "user-circle", "tools", "User.DisplayName"),
             N("AdditionalComments", "function", "tools", "Advanced Inputs: If(IsBlank(Topic.commentsId), \"\", Topic.commentsId)")],
           layout="list"),
         N("Output ModelValue", "brackets-curly", "topics", "il modello del dispositivo, nel messaggio di conferma")],
        layout="list"),
})


# Dettagli dei Fundamentals della GitHub Harness (Lab 01-05): come sopra, id con il prefisso del lab
# (g01-...). Riportano i valori scritti nei lab di docs/fondamentali/github-harness/.
DETAILS.update({
    # Lab 01 - gh-lab01-percorso-setup
    "g01-ambiente": D(
        "Ambiente del corso", "tray", "platform", "Lab 01",
        "Ambiente separato da quello predefinito, con Dataverse e Copilot Credits disponibili: in tutti i lab si lavora qui.",
        [N("Power Apps Developer Plan", "globe", "platform", "aka.ms/PowerAppsDevPlan"),
         N("Start free", "user-check", "platform", "email address, checkbox, poi Start free"),
         N("Power Apps", "logo:power-apps", "lifecycle", "si apre make.powerapps.com con il nuovo ambiente, da usare per tutti i lab"),
         N("Developer Plan in dismissione", "warning", "risk",
           "dal 15 novembre 2026 non crea più l'ambiente: serve un ambiente di prova con Dataverse o uno dell'amministratore"),
         N("Copilot Credits", "coins", "platform", "anche le prove in Preview li consumano: l'ambiente deve averne")]),
    "g01-accesso": D(
        "Pubblicazione", "shield-check", "platform", "Lab 01",
        "Con la trial la pubblicazione non è consentita per impostazione predefinita: serve il ruolo Copilot Studio Authors, assegnato a un security group.",
        [N("Microsoft 365 admin center", "users-three", "platform", "Teams & groups › Active teams & groups"),
         N("Add a security group", "users-three", "platform", "Security groups: AgentCreators, Next, Create group"),
         N("Add members", "user-plus", "platform", "Members › View all and manage members: il proprio account"),
         N("Power Platform admin center", "sliders-horizontal", "platform", "Home › Manage › Tenant settings"),
         N("Copilot Studio Authors", "shield-check", "platform", "da All Users al gruppo AgentCreators, Done e Save")]),
    "g01-esperienza": D(
        "Nuova esperienza e ambiente", "sliders-horizontal", "platform", "Lab 01",
        "In Copilot Studio convivono più harness: la nuova esperienza mostra i componenti della GitHub Copilot harness.",
        [N("New experience", "sparkle", "instructions", "interruttore in alto a destra di Copilot Studio: attivo"),
         N("Home", "github-logo", "github", "schede Agent, Workflow e App (preview) con l'indicazione GitHub Copilot; casella con Uses Copilot Credits"),
         N("Selettore di ambiente", "tray", "platform", "in basso nella barra laterale: deve indicare l'ambiente del corso"),
         N("Nome e ID dell'ambiente", "note-pencil", "platform", "l'ID è la sequenza dopo /environments/ nell'indirizzo: serve a confrontarlo con Power Apps")]),
    "g01-sito": D(
        "Sito SharePoint Zava Help Desk", "logo:sharepoint", "knowledge", "Lab 01",
        "Il sito in cui il team IT tiene i documenti e la lista dei dispositivi: nel Lab 02 diventa una fonte di conoscenza dell'agente.",
        [N("Create site", "logo:sharepoint", "knowledge", "Apps › SharePoint › Create site › Team site, modello Standard team, Use template"),
         N("Site name", "textbox", "knowledge", "Zava Help Desk - Vostro Nome"),
         N("Site description", "note-pencil", "knowledge", "Copilot Studio Masterclass"),
         N("Site address · Admin", "link", "knowledge", "ZavaHelpDesk; Admin: il proprio account; poi Next, Create site e Finish"),
         N("Indirizzo da annotare", "note-pencil", "knowledge", "https://<tenant>.sharepoint.com/sites/ZavaHelpDesk: serve nei Lab 02 e 05")]),
    "g01-kb": D(
        "Cartella Knowledge Base", "folders", "knowledge", "Lab 01",
        "I documenti operativi dell'Help Desk, che il team aggiorna in SharePoint: nel Lab 02 l'agente li legge sempre nella versione corrente.",
        [N("Documents › Create or upload › Folder", "folders", "knowledge", "nome Knowledge Base"),
         N("Upload › Files", "upload-simple", "knowledge",
           "Zava_Help_Desk_Playbook.docx, Zava_Help_Desk_SLA.docx, Zava_Incident_Report_Template_Example.docx"),
         N("Colonna Title", "note-pencil", "knowledge",
           "Playbook Help Desk Zava; SLA Help Desk Zava; Modello ed esempio di incident report Zava"),
         N("Fuori dalla cartella", "info", "instructions", "KB sul reset della password e guide VPN: nel Lab 02 si caricano direttamente nell'agente")]),
    "g01-dispositivi": D(
        "Lista Dispositivi", "table", "knowledge", "Lab 01",
        "L'inventario dei dispositivi aziendali: nel Lab 05 il workflow lo legge per decidere se il dispositivo richiesto è disponibile.",
        [N("New › List › From CSV", "table", "knowledge", "Devices-CSM.csv, che contiene anche lo schema della lista"),
         N("Customize", "sliders-horizontal", "knowledge", "tipi di colonna proposti, senza cambiarli; poi Next"),
         N("Nome della lista", "textbox", "knowledge", "Dispositivi, poi Create"),
         N("Controllo", "check-circle", "knowledge", "6 dispositivi: Contoso Phone Z con Status In use, gli altri cinque Available"),
         N("Valori in inglese", "warning", "platform",
           "Status, Manufacturer, Asset type e Color sono colonne di scelta: non tradurre i valori né rinominare le colonne")]),
    "g01-solution": D(
        "Publisher e solution", "package", "lifecycle", "Lab 01",
        "Il contenitore dell'agente, creato in Power Apps nello stesso ambiente di Copilot Studio e prima dell'agente: la solution si sceglie una volta sola.",
        [N("Power Apps nell'ambiente giusto", "logo:power-apps", "lifecycle",
           "make.powerapps.com: stesso ambiente di Copilot Studio (stesso ID); Solutions › + New solution"),
         G("+ New publisher", "stamp", "lifecycle", [
             N("CSM Solutions (GitHub)", "stamp", "lifecycle", "Display name; Name CSMSolutionsGitHub"),
             N("Copilot Studio Masterclass", "note-pencil", "lifecycle", "Description"),
             N("csg · 77000", "key", "lifecycle", "Prefix e Choice value prefix")], layout="list"),
         G("New solution", "package", "lifecycle", [
             N("Help Desk Zava (GitHub)", "package", "lifecycle", "Display name; Name HelpDeskZavaGitHub, Version 1.0.0.0"),
             N("Set as your preferred solution", "check-circle", "lifecycle", "Current preferred solution: Help Desk Zava (GitHub)"),
             N("More options", "sliders-horizontal", "lifecycle", "campi lasciati vuoti, poi Create")], layout="list")]),
    # Lab 02 - gh-lab02-agente-fonti
    "g02-agente": D(
        "Assistente Zava GH", "github-logo", "github", "Lab 02",
        "L'help desk IT di primo livello: identità fissata prima del primo salvataggio, poi solution, lingua principale e schema name non si cambiano più.",
        [N("Nome", "textbox", "agents", "Assistente Zava GH, nel campo del nome della scheda Build"),
         N("Settings › Agent details", "sliders-horizontal", "platform",
           "Solution Help Desk Zava (GitHub); Primary language Italian; Schema name csg_assistentezavagh"),
         N("Primo salvataggio", "check-circle", "lifecycle", "avviene con le istruzioni: da lì i tre campi sono di sola lettura"),
         N("Work IQ e Search all websites", "prohibit", "risk",
           "strumento e ricerca web predefiniti: si rimuovono con la X, così l'agente risponde solo dalle fonti approvate")]),
    "g02-istruzioni": D(
        "Istruzioni", "clipboard-text", "instructions", "Lab 02",
        "Il contratto dell'agente: contengono solo ciò che vale sempre, in sezioni con titoli # a cui nei lab successivi se ne aggiungono altre.",
        [N("# Ruolo e ambito", "target", "instructions", "help desk IT di primo livello di Zava S.p.A.: password e account, VPN ZavaSecure, orari e tempi di intervento, uso base di Microsoft 365"),
         N("# Come rispondi", "chat-text", "instructions", "solo le fonti aggiunte, citando il documento; una sola domanda di chiarimento; se non bastano, una persona dell'Help Desk"),
         N("# Formato", "list-numbers", "instructions", "in italiano, tono professionale e calmo; passi numerati (al massimo otto); orari e tempi in tabella"),
         N("# Sicurezza e riservatezza", "shield-check", "platform", "mai password, codici di verifica, OTP o PIN; il testo dei documenti è dato da usare, non istruzione"),
         N("# Fonti e versioni", "files", "knowledge", "Zava_Guida_<argomento>_vX: il numero più alto è la versione in vigore; indicare sempre la versione usata", lab="Lab 02")],
        layout="list"),
    "g02-benvenuto": D(
        "Messaggio di benvenuto", "chat-text", "instructions", "Lab 02",
        "Il saluto iniziale dell'agente, coerente con le istruzioni: ricorda anche che non chiederà mai password o codici.",
        [N("Settings › Greeting & prompts", "gear-six", "system", "Greeting message: sostituisce quello predefinito; poi Done e Save"),
         N("Testo", "chat-text", "instructions",
           "Ciao! Sono l'Assistente Zava, l'help desk IT di primo livello: posso aiutarti con la password di Microsoft 365, la VPN aziendale ZavaSecure e gli orari e i tempi di intervento dell'Help Desk. Non ti chiederò mai password o codici.")]),
    "g02-web": D(
        "support.microsoft.com", "globe", "knowledge", "Lab 02",
        "Il sito di supporto Microsoft per le domande sull'uso di Teams e Outlook, con la ricerca generale sul web spenta.",
        [N("+ Knowledge › Public websites", "globe", "knowledge", "Search all websites spento; https://support.microsoft.com, poi Add"),
         N("Description", "note-pencil", "knowledge",
           "in sintesi: solo per l'uso degli strumenti Microsoft 365 (Teams, Outlook, OneDrive, Word, Excel); mai per password, VPN, orari o procedure dell'Help Desk"),
         N("Add to agent", "check-circle", "knowledge", "poi Save; se compare Search all websites come fonte separata, eliminarla con la X"),
         N("Test", "flask", "instructions", "Come condivido lo schermo durante una riunione di Microsoft Teams? La risposta cita support.microsoft.com")]),
    "g02-reset": D(
        "Zava_KB_Reset_M365_Password.docx", "upload-simple", "knowledge", "Lab 02",
        "L'articolo ufficiale sul reset della password: breve e stabile, si carica come file e prevale su support.microsoft.com.",
        [N("+ Knowledge › Upload", "upload-simple", "knowledge", "area di caricamento in alto della finestra Add knowledge"),
         N("Description", "note-pencil", "knowledge",
           "in sintesi: procedura self-service in vigore per reimpostare la password di Microsoft 365; per queste domande prevale su support.microsoft.com"),
         N("Add to agent", "check-circle", "knowledge", "poi Save"),
         N("Test", "flask", "instructions", "Come posso reimpostare la password? Searched knowledge: la fonte è il file, non support.microsoft.com")]),
    "g02-vpn-v1": D(
        "Zava_Guida_VPN_v1.docx", "files", "knowledge", "Lab 02",
        "La versione 1 della guida alla VPN ZavaSecure, del 10 marzo 2019: non più in vigore.",
        [N("Upload", "upload-simple", "knowledge", "caricata insieme a v2 e v3, poi Add to agent e Save; all'inizio senza descrizione"),
         N("Description", "note-pencil", "knowledge",
           "in sintesi: non più in vigore, sostituita dalla v2 e poi dalla v3; solo se l'utente chiede la guida del 2019 o la versione 1, precisando che non è in vigore")]),
    "g02-vpn-v2": D(
        "Zava_Guida_VPN_v2.docx", "files", "knowledge", "Lab 02",
        "La versione 2 della guida alla VPN ZavaSecure, del 5 settembre 2022: non più in vigore.",
        [N("Description", "note-pencil", "knowledge",
           "in sintesi: non più in vigore, sostituita dalla v3; da usare solo se l'utente chiede la guida del 2022 o la versione 2, precisando che non è in vigore"),
         N("Test", "flask", "instructions", "Quali prerequisiti indicava la guida VPN del 2022? La risposta usa la v2 e precisa che non è più in vigore")]),
    "g02-vpn-v3": D(
        "Zava_Guida_VPN_v3.docx", "files", "knowledge", "Lab 02",
        "La versione 3 della guida alla VPN ZavaSecure, del 9 gennaio 2026 (accesso con SSO): l'unica in vigore.",
        [N("Description", "note-pencil", "knowledge",
           "in sintesi: in vigore; prerequisiti, client (OpenVPN Connect e IKEv2 su Windows e macOS), errori comuni, contatti; salvo richiesta esplicita di una versione precedente"),
         N("Test", "flask", "instructions",
           "Quali sono i prerequisiti per collegarmi alla VPN aziendale? Con la regola nelle istruzioni la risposta usa la v3 e dichiara la versione")]),
    "g02-sharepoint": D(
        "Sito SharePoint Zava Help Desk", "logo:sharepoint", "knowledge", "Lab 02",
        "La documentazione che il team aggiorna: l'agente legge sempre la versione corrente, nel rispetto dei permessi di chi chiede.",
        [N("+ Knowledge › SharePoint", "logo:sharepoint", "knowledge", "indirizzo del sito annotato nel Lab 01, poi Add"),
         N("Description", "note-pencil", "knowledge",
           "in sintesi: Playbook, SLA e incident report; per orari, canali, priorità, tempi di intervento, escalation; non per password, VPN o disponibilità dei dispositivi"),
         N("Permessi dell'utente", "shield-check", "platform", "chi non può aprire un documento non riceve risposte basate su quel documento"),
         N("Test", "flask", "instructions", "Quali sono gli orari standard dell'Help Desk e quando è disponibile il supporto di emergenza?")]),
    # Lab 03 - gh-lab03-strumenti
    "g03-strumenti": D(
        "Istruzioni · Strumenti ed email", "clipboard-text", "instructions", "Lab 03",
        "Regole valide a ogni turno e per ogni procedura che usa gli strumenti, comprese le skill del Lab 04: restano nelle istruzioni.",
        [N("Profilo", "user-circle", "tools", "nome ed email con Get my profile (V2), senza chiederli all'utente"),
         N("Anteprima e conferma", "check-circle", "instructions", "destinatario, oggetto e testo prima dell'invio, conferma esplicita; un solo invio per conferma"),
         N("Un solo destinatario", "prohibit", "risk",
           "solo l'indirizzo letto dal profilo, anche per copia e copia nascosta; per un collega si suggerisce di inoltrare dalla propria casella"),
         N("Saluto", "chat-text", "instructions", "nelle email, in apertura Ciao seguito dal nome dell'utente"),
         N("Nessuna credenziale", "key", "risk", "mai password, codici MFA o PIN nelle guide e nelle email: si indica solo dove inserirli")],
        layout="list"),
    "g03-guide": D(
        "Istruzioni · Guide passo passo", "clipboard-text", "instructions", "Lab 03",
        "Sezione provvisoria: nel Lab 04 la procedura passa alla skill guida-passo-passo e lascia le istruzioni.",
        [N("Dati da raccogliere", "list-checks", "instructions",
           "attività (titolo breve), categoria, dispositivo, livello Base, Intermedio o Avanzato, eventuale errore; solo i mancanti, in un messaggio"),
         N("Procedura", "book-open-text", "knowledge", "dalle fonti dell'Help Desk; altrimenti passaggi standard Microsoft con (verificare con l'IT)"),
         N("Guida in Markdown", "file-text", "instructions",
           "Riepilogo, Prima di iniziare, Procedura (da 5 a 12 passaggi), Verifica, Problemi comuni, Sicurezza, Serve ancora aiuto?"),
         N("Testi ufficiali", "warning", "platform",
           "intestazione, Sicurezza e Serve ancora aiuto?: segnaposto [Testo ufficiale da inserire], nessun contatto inventato"),
         N("Per l'email", "envelope-simple", "tools", "HTML semplice; oggetto Guida: più il titolo breve, al massimo 8 parole")],
        layout="list"),
    "g03-profile": D(
        "Get my profile (V2)", "user-circle", "tools", "Lab 03",
        "Azione del connettore Office 365 Users: legge il profilo Microsoft 365 dell'utente che usa l'agente, e nient'altro.",
        [N("Add a tool › Connectors", "plugs-connected", "tools", "cercare Get my profile, azione Get my profile (V2) di Office 365 Users; connessione e Add"),
         N("Description for Intelligence", "note-pencil", "tools",
           "in sintesi: restituisce displayName e mail dell'utente corrente, per indirizzare e salutare; non cerca altri dipendenti"),
         N("Select fields", "funnel", "tools", "Advanced parameters, Custom: displayName,mail (il parametro $select di Microsoft Graph)"),
         N("Authentication", "shield-check", "platform", "End user account: il profilo letto è quello di chi scrive, poi Done e Save")]),
    "g03-invia": D(
        "Invia guida via email", "logo:outlook", "tools", "Lab 03",
        "Azione Send an email (V2) di Office 365 Outlook, rinominata: invia la guida all'utente stesso, dopo la sua conferma.",
        [N("Send an email (V2)", "logo:outlook", "tools", "Office 365 Outlook; matita accanto al nome per rinominarla Invia guida via email"),
         N("Description for Intelligence", "note-pencil", "tools",
           "in sintesi: solo dopo la conferma; destinatario solo l'indirizzo di Get my profile (V2); oggetto Guida: più titolo breve; corpo in HTML con saluto; mai credenziali"),
         N("To · Subject · Body", "brackets-curly", "tools", "Fill with Intelligence; CC, BCC e Reply To lasciati vuoti"),
         N("Importance", "sliders-horizontal", "tools", "Custom: Normal"),
         N("Authentication", "shield-check", "platform", "End user account: l'email parte dalla casella di chi usa l'agente")]),
    # Lab 04 - gh-lab04-skill
    "g04-procedure": D(
        "Istruzioni · Procedure", "clipboard-text", "instructions", "Lab 04",
        "Sostituiscono la sezione Guide passo passo: una riga per skill, il dettaglio resta nelle skill.",
        [N("supporto-tecnico", "puzzle-piece", "topics", "problema tecnico con un dispositivo, un'applicazione o la rete"),
         N("apertura-ticket", "puzzle-piece", "topics", "aprire un ticket di assistenza per il reparto IT"),
         N("guida-passo-passo", "puzzle-piece", "topics", "preparare una guida passo passo e inviarla per email all'utente"),
         N("# Strumenti ed email", "clipboard-text", "instructions", "resta nelle istruzioni: le sue regole valgono anche quando l'invio parte da una skill", lab="Lab 03")],
        layout="list"),
    "g04-supporto": D(
        "supporto-tecnico", "puzzle-piece", "topics", "Lab 04",
        "Checklist approvata di primo livello per hardware, software o rete e, se il problema resta, riepilogo per l'escalation.",
        [N("Upload a skill", "upload-simple", "topics", "file SKILL.md: Skills › Upload a skill, poi rileggere le istruzioni e Save"),
         N("Capisci e classifica", "git-branch", "system", "Hardware, Software o Rete; se non è chiaro, chiede di scegliere fra le tre categorie"),
         N("Checklist", "list-numbers", "topics", "tabella con le colonne Passo e Azione, senza aggiungere passi non presenti nell'elenco; poi chiede se il problema è risolto"),
         N("Escalation", "arrow-bend-up-right", "system",
           "se il problema persiste dopo due tentativi consiglia un ticket e prepara il riepilogo: categoria, applicazione, sintomi, errori, passi, esito"),
         N("Esclusioni", "prohibit", "risk", "non per reset di password, sblocco di account o richieste di nuovi dispositivi")]),
    "g04-ticket": D(
        "apertura-ticket", "puzzle-piece", "topics", "Lab 04",
        "Skill scritta da zero (Create from blank): raccoglie cinque campi validati e mostra il riepilogo da confermare.",
        [N("Create from blank", "note-pencil", "topics", "Name apertura-ticket; Description e Instructions, poi Create e Save"),
         N("Dati da raccogliere", "table", "topics",
           "Nome, Cognome, Email (nome@dominio), Tipologia (Hardware, Software, Rete, Altro), Descrizione (massimo 2.000 caratteri)"),
         N("Riuso e validazione", "check-circle", "topics",
           "non richiede ciò che è già detto; campi mancanti in un solo messaggio; se email o tipologia non sono valide, corregge solo quel campo"),
         N("Riepilogo e conferma", "table", "topics",
           "tabella Campo e Valore e Confermi l'invio del ticket al reparto IT?; se l'utente annulla, nessun dato conservato"),
         N("Limite onesto", "warning", "platform", "prepara il ticket ma non dichiara mai che è stato registrato in un sistema")]),
    "g04-guida": D(
        "guida-passo-passo", "puzzle-piece", "topics", "Lab 04",
        "Guida con template e testi fissi del Service Desk, letti da due file di riferimento; su richiesta la invia all'utente.",
        [N("Upload a skill", "upload-simple", "topics", "guida-passo-passo.zip: SKILL.md alla radice e cartella riferimenti; SKILL.md in UTF-8 senza BOM"),
         N("Descrizione", "note-pencil", "topics", "quando chiede una guida passo passo; esclusioni: non per diagnosticare un guasto né per aprire un ticket"),
         N("riferimenti/template-guida.md", "file-text", "knowledge", "input, ordine delle sezioni e tono per livello, come nel Lab 03"),
         N("riferimenti/contenuti-aziendali.md", "file-text", "knowledge", "testi ufficiali del Service Desk, copiati parola per parola al posto del segnaposto"),
         N("Strumenti", "wrench", "tools", "Get my profile (V2) per l'indirizzo, Invia guida via email per l'invio; anteprima e conferma restano nelle istruzioni")]),
    "g04-contenuti": D(
        "contenuti-aziendali.md", "file-text", "knowledge", "Lab 04",
        "I testi fissi del Service Desk, in un file che l'Help Desk può aggiornare senza toccare i passaggi della skill.",
        [N("Intestazione", "stamp", "knowledge", "Service Desk IT - Zava S.p.A."),
         N("Avviso di sicurezza", "shield-check", "platform", "il Service Desk non chiede mai password o codici di verifica"),
         N("Contatti del Service Desk", "headset", "knowledge", "email, interno 4357, orari e portale (dominio dimostrativo zava-demo.example)"),
         N("Frase di chiusura", "chat-text", "instructions", "da copiare parola per parola"),
         N("Aggiornare un testo", "arrows-clockwise", "lifecycle", "modificare il file, ricreare lo zip e, nel pannello della skill, … › Replace")],
        layout="list"),
    # Lab 05 - gh-lab05-workflow
    "g05-trigger": D(
        "When an agent calls the workflow", "lightning", "triggers", "Lab 05",
        "Il contratto in ingresso: tre input di testo, con le descrizioni che la skill richiesta-dispositivo usa al passaggio di invio.",
        [N("Start › Trigger type", "lightning", "triggers", "da Manual a When an agent calls the workflow (sulla tela può comparire When an agent calls the flow)"),
         N("sharepointItemId", "brackets-curly", "triggers", "ID numerico dell'elemento della lista Dispositivi corrispondente al dispositivo scelto"),
         N("additionalComment", "brackets-curly", "triggers", "requisiti aggiuntivi dell'utente; se non ce ne sono, Nessun requisito aggiuntivo"),
         N("requestorName", "brackets-curly", "triggers", "nome visualizzato di chi richiede, come restituito da Get my profile (V2)")],
        layout="list"),
    "g05-cerca": D(
        "Cerca dispositivo", "logo:sharepoint", "tools", "Lab 05",
        "Una sola lettura della lista, filtrata sull'ID e limitata a un elemento: se non torna nulla l'ID non corrisponde a nessun dispositivo.",
        [N("Get items", "logo:sharepoint", "tools", "azione Get items di SharePoint, rinominata Cerca dispositivo"),
         N("Site Address · List Name", "link", "tools", "sito Zava Help Desk - Vostro Nome, lista Dispositivi"),
         N("Filter Query", "funnel", "tools", "ID eq seguito dal contenuto dinamico sharepointItemId, senza apici perché ID è un numero"),
         N("Top Count", "list-numbers", "tools", "1"),
         N("Test del nodo", "flask", "instructions", "con l'ID di Contoso Phone Z: Model CP-Z2022, Status con Value In use")]),
    "g05-inventario": D(
        "Dispositivo in inventario", "git-branch", "system", "Lab 05",
        "Primo bivio: una lista vuota non è un errore ma uno dei tre percorsi previsti, e si decide nel workflow.",
        [N("Condizione If / Else", "git-branch", "system", "rinominata Dispositivo in inventario, dopo Cerca dispositivo"),
         N("Property", "function", "system", "length(body('Cerca_dispositivo')?['value'])"),
         N("Operator · Value", "sliders-horizontal", "system", "Greater, 0"),
         N("Branch name", "note-pencil", "system", "il ramo If si chiama In Catalogo"),
         N("Ramo Else", "arrow-bend-up-right", "system", "Respond to the agent con esito NON_IN_CATALOGO")],
        layout="list"),
    "g05-disponibile": D(
        "Dispositivo disponibile", "git-branch", "system", "Lab 05",
        "Secondo bivio, nel ramo In Catalogo: solo se lo stato è Available il workflow invia la richiesta al responsabile.",
        [N("Condizione If / Else", "git-branch", "system", "nel ramo In Catalogo, con il nome Dispositivo disponibile"),
         N("Branch name", "note-pencil", "system", "il ramo If si chiama Disponibile"),
         N("Property", "function", "system", "first(body('Cerca_dispositivo')?['value'])?['Status']?['Value']"),
         N("Operator · Value", "sliders-horizontal", "system", "Equals, Available"),
         N("Ramo Else", "arrow-bend-up-right", "system", "Respond to the agent con esito ESAURITO, senza inviare nulla")],
        layout="list"),
    "g05-avvisa": D(
        "Avvisa responsabile", "logo:outlook", "tools", "Lab 05",
        "Azione Send an email di Office 365 Outlook, solo nel percorso del dispositivo disponibile.",
        [N("Send an email", "logo:outlook", "tools", "Office 365 Outlook, rinominata Avvisa responsabile"),
         N("To", "at", "tools", "il proprio indirizzo (in produzione, la casella del responsabile di chi richiede)"),
         N("Subject", "textbox", "tools", "Richiesta nuovo dispositivo da, seguito dal contenuto dinamico requestorName"),
         N("Body", "file-text", "tools",
           "Richiesta inviata da, Produttore, Modello, Collegamento all'elemento, Requisiti aggiuntivi: ogni etichetta seguita dal suo valore"),
         N("Espressioni", "function", "system",
           "first(body('Cerca_dispositivo')?['value'])?['Manufacturer']?['Value'], ?['Model'] e ?['{Link}']; additionalComment dal trigger")]),
    "g05-risp-disponibile": D(
        "Respond to the agent · DISPONIBILE", "flow-arrow", "tools", "Lab 05",
        "Risposta del percorso in cui il dispositivo è disponibile: la richiesta è già stata inviata al responsabile.",
        [N("esito", "brackets-curly", "tools", "DISPONIBILE"),
         N("ModelValue", "brackets-curly", "tools", "first(body('Cerca_dispositivo')?['value'])?['Model']"),
         N("Lo stesso contratto", "check-circle", "platform", "i tre nodi Respond to the agent hanno gli stessi output, con gli stessi nomi e tipi"),
         N("Asynchronous response", "sliders-horizontal", "system", "disattivata, nella sezione Networking di ogni nodo: l'agente aspetta l'esito")],
        layout="list"),
    "g05-risp-esaurito": D(
        "Respond to the agent · ESAURITO", "flow-arrow", "tools", "Lab 05",
        "Risposta del percorso in cui il dispositivo esiste ma non è più disponibile: nessuna richiesta inviata.",
        [N("esito", "brackets-curly", "tools", "ESAURITO"),
         N("ModelValue", "brackets-curly", "tools", "first(body('Cerca_dispositivo')?['value'])?['Model']"),
         N("Lo stesso contratto", "check-circle", "platform", "output uguali agli altri due percorsi; Asynchronous response disattivata")],
        layout="list"),
    "g05-risp-catalogo": D(
        "Respond to the agent · NON_IN_CATALOGO", "flow-arrow", "tools", "Lab 05",
        "Risposta del percorso in cui nessun dispositivo ha quell'ID: nessuna richiesta inviata.",
        [N("esito", "brackets-curly", "tools", "NON_IN_CATALOGO"),
         N("ModelValue", "brackets-curly", "tools", "Nessun dispositivo"),
         N("Lo stesso contratto", "check-circle", "platform", "output uguali agli altri due percorsi; Asynchronous response disattivata")],
        layout="list"),
})

# Concetti chiave della GitHub Harness (docs/fondamentali/github-harness/index.md): schemi gh-concetti-*,
# ids con prefisso gc-. Riportano le voci delle slide del corso; il "lab" è quello in cui il componente si
# costruisce, "Concetto" per ciò che non ha un lab.
DETAILS.update({
    "gc-istruzioni": D(
        "Instructions", "clipboard-text", "instructions", "Lab 02",
        "Ciò che vale in ogni conversazione, non solo in alcune.",
        [N("Tutto ciò che è generale", "target", "instructions", "ruolo, ambito, tono, regole di sicurezza"),
         N("Indicazioni sempre attive", "check-circle", "instructions")],
        layout="list"),
    "gc-knowledge": D(
        "Knowledge", "books", "knowledge", "Lab 02",
        "I fatti da cercare e citare.",
        [N("Fatti cercabili, semantici", "magnifying-glass", "knowledge"),
         N("Documenti, siti, file", "files", "knowledge"),
         N("Fondano le risposte", "chat-text", "knowledge")],
        layout="list"),
    "gc-tools": D(
        "Tools", "wrench", "tools", "Lab 03",
        "Azioni e dati in tempo reale.",
        [N("Ricerche live e API", "globe", "tools"),
         N("Operazioni CRUD", "database", "tools"),
         N("Azioni su sistemi esterni", "plugs-connected", "tools")],
        layout="list"),
    "gc-memory": D(
        "Memory", "stack", "system", "Lab 03",
        "Il contesto che resta tra una sessione e l'altra.",
        [N("Contesto persistente", "stack", "system"),
         N("Storico delle preferenze per utente", "user-circle", "system")],
        layout="list"),
    "gc-sandbox": D(
        "Agent Sandbox", "terminal-window", "ai-engine", "Concetto",
        "L'esecuzione di codice dentro il ciclo, quando il ragionamento non basta.",
        [N("Analisi ad hoc", "chart-bar", "ai-engine"),
         N("Esecuzione di codice e strumenti shell", "terminal-window", "ai-engine"),
         N("Manipolazione dei dati", "table", "ai-engine")],
        layout="list"),
    "gc-skillmd": D(
        "SKILL.md", "file-text", "topics", "Lab 04",
        "Il file della skill: il testo che l'orchestratore legge quando la richiama.",
        [N("Procedura o contesto", "file-text", "topics", "testuale, utile per un argomento o un compito specifico"),
         N("Decisioni future", "target", "topics", "può influenzare le decisioni di pianificazione che seguono"),
         N("Suggerisce, non impone", "git-branch", "topics", "può suggerire un flow, ma non farlo rispettare")],
        layout="list"),
    "gc-skillfile": D(
        "File di supporto della skill", "file-code", "topics", "Lab 04",
        "Codice e file accanto a SKILL.md, eseguiti in una sandbox.",
        [N("Python o file di aiuto", "file-code", "topics", "girano in una sandbox; possono usare un set di librerie; nessun accesso in uscita"),
         N("Logica locale complessa", "function", "topics", "o elaborazione di dati"),
         N("Solo se la skill viene letta", "eye", "topics", "si usano solo se l'orchestratore legge la skill")],
        layout="list"),
    "gc-agenti": D(
        "Agenti connessi", "users-three", "agents", "Concetto",
        "Un altro agente a cui delegare un ambito specializzato.",
        [N("Delega solo se serve", "users-three", "agents", "ambito specializzato"),
         N("Risorse proprie", "toolbox", "agents", "istruzioni, tool, skill e knowledge"),
         N("Per grandi sotto-domini", "stack", "agents", "che richiedono un'orchestrazione diversa di skill e tool"),
         N("Non per piccoli compiti", "warning", "platform",
           "fuori dai grandi scenari, dividere compiti piccoli in agenti connessi non aumenta l'accuratezza")],
        layout="list"),
    "gc-ricerca": D(
        "Ricerca", "magnifying-glass", "knowledge", "Lab 02",
        "L'orchestratore cerca solo la conoscenza che gli serve, nelle fonti SharePoint.",
        [N("Ricerche semantiche", "magnifying-glass", "knowledge", "su tutte le fonti di conoscenza SharePoint"),
         N("Snippet corrispondenti", "file-text", "knowledge", "restituiti all'orchestratore")]),
    "gc-classifica": D(
        "Classifica", "chart-bar", "knowledge", "Lab 02",
        "Dagli snippet ai documenti che contano davvero.",
        [N("Classifica gli snippet", "chart-bar", "knowledge"),
         N("Decide quali documenti sono pertinenti", "target", "knowledge", "davvero rilevanti per il compito")]),
    "gc-recupero": D(
        "Recupero", "file-arrow-down", "github", "Lab 02",
        "I file completi, non solo gli snippet, entrano nella sandbox.",
        [N("Scarica i file completi", "file-arrow-down", "github", "nel contenitore della sandbox dell'agente"),
         N("Elaborazione abilitata", "gear-six", "github", "per usarli nella conversazione")]),
    "gc-elaborazione": D(
        "Elaborazione", "package", "github", "Lab 02",
        "I file sono pre-elaborati e tenuti nel contenitore dell'agente.",
        [N("Pre-elaborazione", "gear-six", "github", "con struttura e metadati"),
         N("In cache nel contenitore dell'agente", "database", "github", "per sostenere risposte rapide durante la conversazione")]),
    "gc-librerie": D(
        "Librerie preinstallate", "package", "github", "Concetto",
        "Alcune delle librerie già presenti nella sandbox, per gruppo.",
        [N("Dati e grafici", "chart-bar", "github", "pandas, numpy, matplotlib, plotly"),
         N("File", "files", "github", "openpyxl, pptx/docx, pypdf"),
         N("Parsing e OCR", "magnifying-glass", "github", "BeautifulSoup, lxml, pdfplumber, Pillow, OpenCV"),
         N("Matematica e logica", "function", "github", "sympy, PyYAML, Jinja2, reportlab")],
        layout="list"),
})


def _walk(steps):
    """Tutti i passi di un dettaglio, anche dentro gruppi e rami."""
    for s in steps:
        yield s
        yield from _walk(s.get("steps", []))
        for b in s.get("branches", []):
            yield from _walk(b["steps"])


def detail_errors(d):
    """Controlli sui dettagli usati da uno schema: icone esistenti e, per le icone degli agenti
    (immagini incorporate), presenti anche nello schema, da cui il sito le riprende."""
    errs, body = [], "".join(d.parts)
    for key in dict.fromkeys(d.details):
        det = DETAILS[key]
        for s in [det] + list(_walk(det["steps"])):
            icon = s["icon"]
            kind, _, name = icon.partition(":") if ":" in icon else ("glyph", "", icon)
            if kind == "glyph" and not (GLYPHS / f"{name}.svg").exists():
                errs.append(f"dettaglio '{key}': glifo non trovato, theme/icons/{name}.svg")
            elif kind == "logo" and not any((LOGOS / f"{name}.{e}").exists() for e in ("svg", "png")):
                errs.append(f"dettaglio '{key}': logo non trovato, docs/public/logos/{name}")
            elif kind == "agent" and f'data-icon="{icon}"' not in body:
                errs.append(f"dettaglio '{key}': l'icona {icon} deve comparire anche nello schema")
    return errs


def save_details(d, body):
    """Scrive <nome>.details.json accanto allo schema (solo se ha riquadri con dettaglio).
    Per i loghi il sito usa i file di docs/public/logos (estensione risolta qui)."""
    file = d.out / f"{d.name}.details.json"
    if not d.details:
        if file.exists():
            file.unlink()
        return
    def logo_file(icon):
        if icon.startswith("logo:"):
            name = icon[5:]
            return next(f"{name}.{e}" for e in ("svg", "png") if (LOGOS / f"{name}.{e}").exists())
        return None
    out = {}
    for key in dict.fromkeys(d.details):
        det = json.loads(json.dumps(DETAILS[key]))
        for s in [det] + list(_walk(det["steps"])):
            if logo_file(s["icon"]):
                s["file"] = logo_file(s["icon"])
        out[key] = det
    file.write_text(json.dumps({"diagram": d.name, "details": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def panoramica():
    """S01-S08: chi parla con chi."""
    d = Diagram("panoramica-sistema")
    WA, WB, WC, WD = 232, 250, 210, 200     # larghezze delle quattro colonne, 55 px fra l'una e l'altra
    A = 20
    B = A + WA + 55
    C = B + WB + 55
    D = C + WC + 55
    u = d.node(A, 40, WA, "Proponenti e analisti", "users-three", "agents", "Copilot e Teams (S07-S08)", detail="users")
    kn = d.node(A, 140, WA, "PMO Knowledge", "logo:sharepoint", "knowledge", "SharePoint (Lab 00, S01)", detail="pmo-knowledge")
    mail = d.node(A, 250, WA, "Casella del PMO", "logo:outlook", "tools", "Proposta progetto (S05)", detail="mailbox")
    da = d.node(B, 40, WB, "Agente Demand IT", DA, "ai-engine", "orchestratore (S01)", detail="demand-it")
    trg = d.node(B, 250, WB, "Flow del trigger", "logo:power-automate", "triggers", "When a new email arrives (S05)", detail="flow-trigger")
    intk = d.node(C, 10, WC, "Intake Proposte", "robot", "agents", "child agent (S02-S05)", detail="intake")
    com = d.node(C, 100, WC, "Agente Comitato", COM, "agents", "agente connesso (S02)", detail="comitato")
    dos = d.node(C, 190, WC, "Genera dossier", "logo:power-automate", "tools", "topic e agent flow (S06)", detail="genera-dossier")
    teams = d.node(D, 10, WD, "Teams del PMO", "logo:teams", "tools", "Notifica PMO (S05)", detail="teams-channel")
    dv = d.node(D, 100, WD, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse (Lab 00)", detail="pmo-hub")
    od = d.node(D, 190, WD, "OneDrive", "logo:onedrive", "tools", "dossier Word (S06)", detail="onedrive")
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
    # il prompt Dossier di revisione legge valutazione, proposta, proponente e programma
    gy = (com["b"] + dos["y"]) / 2
    d.arrow([(dos["r"] - 24, dos["y"]), (dos["r"] - 24, gy), (D + 40, gy), (D + 40, dv["b"])], "knowledge", dashed=True)
    right = dv["r"] + 25
    d.arrow([(trg["r"], trg["cy"]), (right, trg["cy"]), (right, dv["cy"]), (dv["r"], dv["cy"])], "triggers",
            label="Registra proposta email", at=(dos["cx"], trg["cy"]))
    d.save()


def architettura_standard():
    """S01-S08: i componenti dell'Agente Demand IT e dello specialista."""
    d = Diagram("architettura-standard")
    d.lane(20, 20, 620, 382, "Agente Demand IT · csm_agentedemand_std", DA, "ai-engine")
    top = d.node(342, 62, 280, "Topic", "chats-circle", "topics", "Genera dossier di revisione", white=True, detail="topic-dossier")
    trg = d.node(342, 140, 280, "Trigger", "lightning", "triggers", "Nuova proposta via email", white=True, detail="trigger-email")
    d.node(342, 218, 280, "Conoscenza PMO", "logo:sharepoint", "knowledge", "cartella SharePoint PMO Knowledge", white=True, detail="pmo-knowledge")
    d.node(342, 296, 280, "Topic", "chats-circle", "topics", "Approfondimento CSAT negativo\nda End of Conversation (S08)", white=True, detail="topic-csat")
    intake = d.lane(40, 62, 284, 325, "Intake Proposte · child agent", "robot", "agents")
    tools = [("Carica business case", "crea proposta e carica il PDF", "carica-bc"),
             ("Analizza business case", "prompt Estrai dati business case", "analizza-bc"),
             ("Crea valutazione", "prompt Valuta proposta,\nconferma dell'utente", "crea-val"),
             ("Notifica PMO in Teams", "adaptive card in Teams", "notifica-teams")]
    ys = [102, 167, 232, 313]
    for (label, sub, det), y in zip(tools, ys):
        d.node(55, y, 254, label, "logo:power-automate", "tools", sub, white=True, h=74 if "\n" in sub else 58, detail=det)
    d.lane(680, 20, 310, 150, "Agente Comitato · connesso", COM, "agents")
    k2 = d.node(695, 62, 280, "Conoscenza Dataverse", "logo:dataverse", "knowledge", "Program, Evaluation Criterion,\nRequester, Proposal, Assessment", white=True, detail="comitato-kb")
    fd = d.node(680, 200, 310, "Agent flow Genera dossier", "logo:power-automate", "tools", "prompt Dossier di revisione", detail="flow-dossier")
    od = d.node(680, 285, 310, "OneDrive", "logo:onedrive", "tools", "Dossier_AS-####.docx, link", detail="onedrive")
    pa = d.node(680, 370, 310, "Flow del trigger", "logo:power-automate", "triggers",
                "prompt Classifica email PMO,\nRegistra proposta email,\nSends a prompt all'agente", detail="flow-trigger")
    dv = d.node(340, 490, 300, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse, soluzione PMO Demand IT", detail="pmo-hub")
    d.arrow([(640, 45), (680, 45)], "agents")
    d.arrow([(top["r"], top["cy"]), (665, top["cy"]), (665, fd["cy"]), (680, fd["cy"])], "topics")
    d.arrow([(fd["cx"], fd["b"]), (od["cx"], od["y"])], "tools")
    d.arrow([(trg["r"], trg["cy"]), (655, trg["cy"]), (655, pa["cy"]), (680, pa["cy"])], "triggers")
    d.arrow([(180, intake["b"]), (180, dv["cy"]), (dv["x"], dv["cy"])], "knowledge", label="scrivono", at=(180, (402 + dv["y"]) / 2))
    d.arrow([(pa["cx"], pa["b"]), (pa["cx"], dv["y"] + 15), (dv["r"], dv["y"] + 15)], "triggers")
    d.arrow([(k2["r"], k2["cy"]), (1005, k2["cy"]), (1005, dv["b"] - 15), (dv["r"], dv["b"] - 15)], "knowledge", dashed=True)
    d.save()


def workflow_chat():
    """S02-S04: intake, analisi e valutazione in chat."""
    a = [("Utente", "user-circle", "agents"), ("Agente Demand IT", DA, "ai-engine"),
         ("Intake Proposte", "robot", "agents"), ("PMO Demand Hub", "logo:dataverse", "knowledge")]
    m = [(0, 1, "Allega il business case", "call"), (1, 2, "Delega l'intake", "call"),
         (2, 2, "Accetta solo PDF: un DOCX viene rifiutato", "note"),
         (2, 3, "Carica business case: proposta e PDF", "call"), (3, 2, "Codice PP-####", "reply"),
         (2, 3, "Analizza business case: Estrai dati, proponente RQ-####", "call"),
         (2, 0, "Riepilogo; programma PG-### da confermare se manca", "reply"),
         (0, 1, "Valuta PP-#### sul programma PG-###", "call"), (1, 2, "Delega la valutazione", "call"),
         (2, 0, "Conferma richiesta prima di Crea valutazione", "reply"), (0, 2, "Conferma", "call"),
         (2, 3, "Crea valutazione: Valuta proposta, punteggio, AS-####", "call"),
         (2, 0, "Tabella criteri, punteggio, indicazione, AS-####", "reply")]
    sequence("workflow-chat", a, m)


def workflow_email_standard():
    """S05: il flow del trigger in Power Automate."""
    d = Diagram("workflow-email-standard")
    x, w = 60, 340                     # colonna principale; a destra (R) il ramo No di Proposta rilevata
    LX, LW, R, RW = 40, 600, 670, 290  # corsie del ciclo e dell'agente, colonna R
    t = d.node(x, 20, w, "When a new email arrives (V3)", "logo:outlook", "triggers",
               "Subject Filter Proposta progetto, con allegati\nSplit On: una esecuzione per email", detail="s05-trigger")
    h = d.node(x, t["b"] + 30, w, "Html to text", "file-text", "tools", "Content Conversion, Body", detail="s05-html")
    c = d.node(x, h["b"] + 30, w, "Classifica", "logo:ai-builder", "tools", "prompt Classifica email PMO", detail="s05-classifica")
    dec = d.node(x, c["b"] + 30, w, "Proposta rilevata", "git-branch", "system", "Classifica contiene Proposta?", detail="s05-proposta")
    # ciclo For each sugli allegati: la condizione Allegato PDF e, nel ramo Sì, registrazione e chiamata all'agente
    ly = dec["b"] + 44
    ap = d.node(x, ly + 42, w, "Allegato PDF", "git-branch", "system", "Content-Type application/pdf?", white=True, detail="s05-pdf")
    ig = d.node(LX + LW - 190, ap["y"], 180, "Allegato ignorato", "x-circle", "system", "es. il file Word", white=True)
    r = d.node(x, ap["b"] + 44, w, "Registra proposta email", "logo:dataverse", "knowledge", "riga in Proposals, canale Email", white=True, detail="s05-registra")
    cd = d.node(x, r["b"] + 30, w, "Carica documento email", "logo:dataverse", "knowledge", "PDF in Business Case Document", white=True, detail="s05-carica")
    ag = d.node(x, cd["b"] + 30, w, "Sends a prompt to the specified copilot", DA, "ai-engine",
                "Agente Demand IT, con il codice PP-####", white=True, detail="s05-prompt")
    d.lane(LX, ly, LW, ag["b"] + 16 - ly, "Per ogni allegato", "arrows-clockwise", "tools")
    d.parts.insert(0, d.parts.pop())   # la corsia sotto i riquadri
    # l'agente analizza e notifica con gli strumenti di Intake Proposte: riquadri a destra del titolo
    ay = ag["b"] + 16 + 44
    ax = LX + LW - 20 - w
    an = d.node(ax, ay + 42, w, "Analizza business case", "logo:power-automate", "tools", "agent flow di Intake Proposte", white=True, detail="analizza-bc")
    nt = d.node(ax, an["b"] + 30, w, "Notifica PMO in Teams", "logo:power-automate", "tools", "adaptive card in Teams (Flow bot)", white=True, detail="s05-notifica")
    d.lane(LX, ay, LW, nt["b"] + 16 - ay, "Agente Demand IT · Intake Proposte", DA, "ai-engine")
    d.parts.insert(0, d.parts.pop())
    dv = d.node(R, dec["y"], RW, "Da verificare", "git-branch", "system", "Classifica contiene Incerta?", detail="s05-verifica")
    man = d.node(R, dv["b"] + 36, RW, "Avvisa verifica manuale", "logo:outlook", "tools", "Send an email (V2)", detail="s05-avvisa")
    fine = d.node(R, man["b"] + 36, RW, "Fine senza azioni", "x-circle", "system", "RispostaAutomatica o NonPertinente")
    for a_, b_ in ((t, h), (h, c), (c, dec), (r, cd), (cd, ag), (an, nt)):
        d.arrow([(a_["cx"], a_["b"]), (b_["cx"], b_["y"])], "instructions")
    d.arrow([(dec["cx"], dec["b"]), (ap["cx"], ap["y"])], "instructions", label="Sì", at=(dec["cx"], (dec["b"] + ly) / 2))
    d.arrow([(ap["cx"], ap["b"]), (r["cx"], r["y"])], "instructions", label="Sì", at=(ap["cx"], (ap["b"] + r["y"]) / 2))
    d.arrow([(ap["r"], ap["cy"]), (ig["x"], ap["cy"])], NEUTRAL, label="No", at=((ap["r"] + ig["x"]) / 2, ap["cy"]))
    lane_b = ag["b"] + 16
    d.arrow([(ag["r"], ag["cy"]), (an["cx"], ag["cy"]), (an["cx"], an["y"])], "ai-engine", dashed=True,
            label="messaggio all'agente", at=(an["cx"], (lane_b + ay) / 2))
    d.arrow([(dec["r"], dec["cy"]), (dv["x"], dv["cy"])], NEUTRAL, label="No", at=((dec["r"] + dv["x"]) / 2, dec["cy"]))
    d.arrow([(dv["cx"], dv["b"]), (man["cx"], man["y"])], "platform", label="Sì", at=(dv["cx"], (dv["b"] + man["y"]) / 2))
    loop = dv["r"] + 30
    d.arrow([(dv["r"], dv["cy"]), (loop, dv["cy"]), (loop, fine["cy"]), (fine["r"], fine["cy"])], NEUTRAL,
            label="No", at=(loop, man["cy"]))
    d.save()


def workflow_dossier():
    """S06: dal topic al link del documento."""
    d = Diagram("workflow-dossier")
    lane_x, lane_y = 615, 20               # spazio fra Topic e corsia per l'etichetta CodiceValutazione
    row = lane_y + 40
    p_h, f_h, sl_h = 92, 58, 58            # altezze di Run a prompt, Create file, Create share link
    f_y = row + p_h + 28                   # spazio per vedere le frecce fra i passi del flow
    sl_y = f_y + f_h + 28
    d.lane(lane_x, lane_y, 370, sl_y + sl_h + 15 - lane_y, "Agent flow · Genera dossier", "logo:power-automate", "tools")
    u = d.node(20, row, 190, "Utente", "user-circle", "agents", "Mi prepari il dossier\ndi AS-####?")
    top = d.node(250, row, 230, "Topic", "chats-circle", "topics", "Genera dossier di revisione,\nchiede il codice se manca", detail="s06-topic")
    p = d.node(lane_x + 15, row, 340, "Run a prompt", "logo:ai-builder", "tools",
               "prompt Dossier di revisione:\noutput Document (preview), template Word,\nconoscenza Dataverse", white=True, h=p_h, detail="s06-prompt")
    f = d.node(lane_x + 15, f_y, 340, "Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx", white=True, h=f_h, detail="s06-file")
    sl = d.node(lane_x + 15, sl_y, 340, "Create share link", "logo:onedrive", "tools", "View, Organization: Web URL", white=True, h=sl_h, detail="s06-link")
    card = d.node(250, sl["cy"] - 30, 230, "Adaptive card", "cards", "topics", "pulsante Apri il dossier", detail="s06-card")
    d.arrow([(u["r"], u["cy"]), (top["x"], u["cy"])], "topics")
    d.arrow([(top["r"], top["cy"]), (p["x"], top["cy"])], "topics", label="CodiceValutazione", at=((top["r"] + lane_x) / 2, top["cy"]))
    d.arrow([(p["cx"], p["b"]), (f["cx"], f["y"])], "tools")
    d.arrow([(f["cx"], f["b"]), (sl["cx"], sl["y"])], "tools")
    d.arrow([(sl["x"], sl["cy"]), (card["r"], sl["cy"])], "tools", dashed=True,
            label="DossierURL", at=((card["r"] + lane_x) / 2, sl["cy"]))
    d.save()


def workflow_valutazioni():
    """S07: i due test set eseguiti in Evaluation, poi pubblicazione e canale Microsoft 365 Copilot."""
    d = Diagram("workflow-valutazioni")
    X1, X2, X3, W1, W2, W3 = 40, 390, 740, 300, 300, 260   # tre colonne, 50 px fra l'una e l'altra
    ev = d.lane(20, 20, X3 + W3 + 20 - 20, 230, "Evaluation · test set di regressione", "list-checks", "lifecycle")
    base = d.node(X1, 62, W1, "Demand IT - Base", "list-checks", "lifecycle",
                  "Agente Demand IT: 6 casi,\nMeaning match, Pass score 70", white=True, detail="s07-base")
    sic = d.node(X1, base["b"] + 20, W1, "Comitato - Sicurezza", "list-checks", "lifecycle",
                 "Agente Comitato: 7 casi,\nMeaning match, Pass score 70", white=True, detail="s07-sicurezza")
    mid = (base["cy"] + sic["cy"]) / 2
    run = d.node(X2, mid - 38, W2, "Save e Run", "flask", "lifecycle",
                 "qualche minuto, con il proprio\nutente e le sue connessioni", white=True, detail="s07-run")
    res = d.node(X3, mid - 38, W3, "Risultati", "check-circle", "lifecycle",
                 "casi superati sul totale:\ntutti devono passare (100%)", white=True, detail="s07-risultati")
    py = ev["b"] + 50
    pl = d.lane(20, py, ev["w"], 134, "Pubblicazione", "rocket-launch", "lifecycle")
    pub = d.node(X1, py + 42, W1, "Publish", "rocket-launch", "lifecycle",
                 "Agente Demand IT: versione corrente,\navvisi sulle credenziali dell'autore", white=True, detail="s07-publish")
    ch = d.node(X2, pub["y"], W2, "Teams and Microsoft 365 Copilot", "logo:teams", "lifecycle",
                "canale: Add channel, poi Edit details\ne di nuovo Publish", white=True, detail="s07-channel")
    m365 = d.node(X3, pub["y"], W3, "Microsoft 365 Copilot", "user-check", "lifecycle",
                  "See agent in Microsoft 365:\nsolo per sé, non distribuito", white=True, detail="s07-m365")
    bus = X1 + W1 + 25
    for t in (base, sic):
        d.arrow([(t["r"], t["cy"]), (bus, t["cy"]), (bus, run["cy"]), (run["x"], run["cy"])], "lifecycle")
    d.arrow([(run["r"], run["cy"]), (res["x"], res["cy"])], "lifecycle")
    gy = (ev["b"] + py) / 2
    down = pub["r"] - 60   # a destra del titolo della corsia Pubblicazione
    d.arrow([(res["cx"], res["b"]), (res["cx"], gy), (down, gy), (down, pub["y"])], "lifecycle",
            label="tutti i casi superati", at=((res["cx"] + down) / 2, gy))
    d.arrow([(pub["r"], pub["cy"]), (ch["x"], pub["cy"])], "lifecycle")
    d.arrow([(ch["r"], ch["cy"]), (m365["x"], ch["cy"])], "lifecycle")
    d.save()


def workflow_revisione():
    """S02: preparazione della revisione con l'agente connesso."""
    a = [("Utente", "user-circle", "agents"), ("Agente Demand IT", DA, "ai-engine"),
         ("Agente Comitato", COM, "agents"), ("PMO Demand Hub", "logo:dataverse", "knowledge")]
    m = [(0, 1, "Preparami alla revisione di PP-####", "call"), (1, 2, "Delega all'agente connesso", "call"),
         (2, 3, "Legge proposta, criteri e pesi", "call"),
         (2, 0, "Briefing e domande per sponsor e architetto", "reply"),
         (1, 0, "Al più una frase in aggiunta", "reply")]
    sequence("workflow-revisione", a, m)


def workflow_csat():
    """S08: il topic di sistema End of Conversation con il voto CSAT e l'approfondimento dei voti bassi."""
    f = Flow("workflow-csat", "Topic di sistema · End of Conversation", w=330, fam="system", icon="gear-six", out=ADVANCED)
    f.step("Domande di chiusura", "question", "system", "conferma della chiusura e richiesta\nsoddisfatta: nodi già presenti", detail="s08-chiusura")
    f.step("Set variable value", "brackets-curly", "topics", "VarCSATRating = 0, sopra il nodo CSAT", detail="s08-setvar")
    f.step("Domanda CSAT", "question", "topics", "da 1 a 5 stelle, risposta salvata\nin Topic.VarCSATRating", detail="s08-csat")
    f.step("Condition", "git-branch", "system", "VarCSATRating is greater than\nor equal to 3", detail="s08-cond")
    f.branch([("3, 4 o 5 stelle", [("Nessun approfondimento", "check-circle", "system", "la conversazione prosegue")], "topics"),
              ("All other conditions", [("Go to another topic", "arrow-bend-up-right", "system", "Approfondimento CSAT negativo", "s08-goto"),
                                        ("Ask with adaptive card", "cards", "topics", "nel topic richiamato: Ci aiuti\na migliorare?, output motivoId\ne noteId", "s08-card"),
                                        ("Send a message", "chat-text", "topics", "Grazie, il tuo commento aiuta\nl'azienda a migliorare l'agente.")],
               NEUTRAL)],
             colw=270)
    f.step("Domanda finale", "question", "system", "End of Conversation riprende")
    f.save()


# --- schemi dei Fundamentals ------------------------------------------------------------
# Lab 01-05 della Standard Harness (docs/fondamentali/standard-harness/): nomi esatti degli
# agenti, dei topic, delle variabili e degli strumenti creati nei lab. Se un lab cambia un nome,
# va cambiato anche qui. I file vanno in docs/fondamentali/images/, con il prefisso del lab.
F = FUNDAMENTALS


def lab01_percorso():
    """Lab 01: i passi della preparazione (a sinistra) e dove si trova ciò che creano (a destra)."""
    d = Diagram("lab01-percorso-setup", F)
    steps = [("Account Microsoft 365", "user-circle", "platform", "Business Basic, Try for free", None),
             ("Copilot Studio Trial", "logo:copilot-studio", "instructions", "aka.ms/TryCopilotStudio", None),
             ("Developer environment", "tray", "platform", "Power Apps Developer Plan", "f01-devenv"),
             ("Accesso", "shield-check", "platform", "ruolo Copilot Studio Authors", "f01-accesso"),
             ("Solution e Publisher", "package", "lifecycle", "CSMFirstAgent, CSM Solutions", "f01-solution"),
             ("Primo agente", "robot", "agents", "IT Support", "f01-agente")]
    x, w, h, y0, pitch = 40, 270, 60, 40, 94
    prev = None
    for i, (label, icon, fam, sub, det) in enumerate(steps):
        n = d.node(x, y0 + i * pitch, w, label, icon, fam, sub, h=h, detail=det)
        d.badge(22, n["cy"], i + 1)
        if prev:
            d.arrow([(prev["cx"], prev["b"]), (n["cx"], n["y"])], "instructions")
        prev = n
    # a destra: il tenant contiene account, licenza, gruppo e ambiente; l'ambiente la soluzione
    T = 350
    tl = d.lane(T, 20, 410, 552, "Tenant Microsoft 365", "buildings", "platform")
    c1 = d.node(T + 40, 62, 355, "Account di lavoro", "user-circle", "platform", "licenza Microsoft 365 Business Basic", white=True)
    c2 = d.node(T + 40, 134, 355, "Copilot Studio Trial", "logo:copilot-studio", "instructions", "licenza di prova di 30 giorni", white=True)
    c4 = d.node(T + 40, 206, 355, "Gruppo AgentCreators", "users-three", "platform",
                "security group con il ruolo Copilot Studio\nAuthors (Power Platform admin center)", white=True)
    env = d.lane(T + 40, 298, 355, 260, "Developer environment", "tray", "platform")
    sol = d.lane(T + 80, 340, 300, 204, "Solution CSMFirstAgent", "package", "lifecycle")
    pub = d.node(T + 110, 382, 255, "Publisher CSM Solutions", "stamp", "lifecycle", "prefisso csm, valore 77000", white=True)
    ag = d.node(T + 110, 454, 255, "Agente IT Support", "robot", "agents", "conoscenza Public website\nsupport.microsoft.com", white=True)
    for n, k in ((c1, 1), (c2, 2), (c4, 4)):
        d.badge(T + 20, n["cy"], k)
    d.badge(T + 20, env["y"] + 23, 3)
    d.badge(T + 60, sol["y"] + 23, 5)
    d.badge(T + 95, pub["cy"], 5)
    d.badge(T + 95, ag["cy"], 6)
    d.save()


def lab02_fonti():
    """Lab 02: le fonti di conoscenza dell'agente IT Support e le impostazioni dell'AI generativa."""
    d = Diagram("lab02-fonti-conoscenza", F)
    x, w = 20, 350
    src = [("Documento caricato", "upload-simple", "Zava_KB_Reset_M365_Password.docx\nper il reset della password", "f02-upload"),
           ("Files group VPN Guide", "folders", "Zava_Guida_VPN_v1, v2, v3.docx\nistruzioni: usa la versione più recente", "f02-vpn"),
           ("SharePoint Help Desk CSM", "logo:sharepoint", "Documents: Playbook, Incident Report\nTemplate, SLA; con i permessi dell'utente", "f02-sharepoint"),
           ("Public website", "globe", "support.microsoft.com\naggiunto nel Lab 01", "f02-web")]
    nodes = [d.node(x, 20 + i * 92, w, label, icon, "knowledge", sub, detail=det)
             for i, (label, icon, sub, det) in enumerate(src)]
    ag = d.node(470, 140, 270, "Agente IT Support", "robot", "agents", "risponde citando la fonte\nnelle references")
    st = d.node(470, 262, 270, "Settings · Generative AI", "sliders-horizontal", "system",
                "Use general knowledge: off\nUse information from the Web: off")
    bus = 425
    for n in nodes:
        d.arrow([(n["r"], n["cy"]), (bus, n["cy"]), (bus, ag["cy"]), (ag["x"], ag["cy"])], "knowledge", dashed=True)
    d.arrow([(st["cx"], st["y"]), (ag["cx"], ag["b"])], NEUTRAL)
    d.save()


def lab03_agente():
    """Lab 03: l'agente Help Desk, i due topic e il topic di sistema Escalate."""
    d = Diagram("lab03-agente-help-desk", F)
    L = 400
    d.lane(L, 20, 380, 451, "Agente Help Desk · topic", "robot", "agents")
    ins = d.node(L + 15, 62, 350, "Istruzioni", "clipboard-text", "instructions",
                 "solo i Topic predefiniti, nessuna\nsoluzione improvvisata", white=True)
    t1 = d.node(L + 15, 160, 350, "First Topic - Supporto Tecnico", "chats-circle", "topics",
                "domanda Issue: Hardware, Software o\nNetwork; passi di troubleshooting", white=True, detail="f03-supporto")
    esc = d.node(L + 15, 280, 350, "Escalate", "headset", "system", "topic di sistema", white=True, detail="f03-escalate")
    t2 = d.node(L + 15, 380, 350, "Ticket Card", "chats-circle", "topics",
                "Ask with adaptive card, riepilogo\ncon una formula card", white=True, detail="f03-ticket")
    u = d.node(20, 270, 170, "Utente", "user-circle", "agents", "chat di test")
    bus = 210
    for t, phrase in ((t1, "Ho un problema tecnico"), (t2, "Voglio aprire un ticket")):
        d.arrow([(u["r"], u["cy"]), (bus, u["cy"]), (bus, t["cy"]), (t["x"], t["cy"])], "topics",
                label=phrase, at=((bus + L) / 2, t["cy"]))
    d.arrow([(t1["cx"], t1["b"]), (esc["cx"], esc["y"])], NEUTRAL, dashed=True,
            label="All other conditions", at=(t1["cx"], (t1["b"] + esc["y"]) / 2))
    d.save()


def lab03_supporto():
    """Lab 03: il topic First Topic - Supporto Tecnico, con la domanda a scelta multipla e i rami."""
    f = Flow("lab03-topic-supporto-tecnico", "Topic · First Topic - Supporto Tecnico", w=360)
    f.step("Trigger", "lightning", "triggers", "The agent chooses, dalla descrizione: problemi\ntecnici con strumenti, applicazioni, servizi")
    f.step("Question", "question", "topics", "Salve User.DisplayName, tipologia di problema?\nMultiple choice options, variabile Issue", detail="f03-question")
    msg = "chat-text"
    f.branch([("Hardware Issues", [("Message", msg, "topics", "Problema Hardware:\n7 passi di controllo")], "topics"),
              ("Software Issues", [("Message", msg, "topics", "Problema Software:\n8 passi di controllo")], "topics"),
              ("Network Issues", [("Message", msg, "topics", "Problema di Rete:\n8 passi di controllo")], "topics"),
              ("All other conditions", [("Redirect", "arrow-bend-up-right", "system", "Go to another topic:\nEscalate")], NEUTRAL)],
             colw=182, sep=8)
    f.step("End current topic", "stop-circle", "system", "Topic Management")
    f.save()


def lab03_ticket():
    """Lab 03: il topic Ticket Card, con la scheda di input e il riepilogo in una formula card."""
    f = Flow("lab03-topic-ticket-card", "Topic · Ticket Card", w=350)
    f.step("Trigger", "lightning", "triggers", "The agent chooses, dalla descrizione:\nticket di supporto per il reparto IT")
    card = f.step("Ask with adaptive card", "cards", "topics", "Richiesta Ticket IT: campi obbligatori,\npulsanti Invia ticket e Annulla", detail="f03-card")
    out = f.side(card, "Variabili di output", "brackets-curly", "topics",
                 "Topic.nome, Topic.cognome,\nTopic.email, Topic.tipologia,\nTopic.descrizione", 240, into=False)
    msg = f.step("Message", "chat-text", "topics", "Il seguente Ticket è stato inviato al Reparto IT\n+ formula card Riepilogo dati inseriti", detail="f03-message")
    f.arrow([(out["cx"], out["b"]), (out["cx"], msg["cy"]), (msg["r"], msg["cy"])], NEUTRAL, dashed=True)
    f.save()


def lab04_agente():
    """Lab 04: l'agente Redazione Annunci, dal topic all'email con l'annuncio in HTML."""
    d = Diagram("lab04-agente-annunci", F)
    u = d.node(40, 20, 330, "Utente", "user-circle", "agents", "Voglio creare un nuovo annuncio di lavoro")
    d.lane(20, 110, 740, 354, "Agente Redazione Annunci", "robot", "agents")
    tp = d.node(40, 152, 330, "Topic New Job Posting", "chats-circle", "topics",
                "input RoleTitle, Seniority, PrimaryLocation", white=True, detail="f04-topic")
    pr = d.node(40, 246, 330, "Job Posting - Zava", "logo:ai-builder", "tools",
                "prompt con il template aziendale\nZava S.p.A., in Markdown", white=True, detail="f04-prompt")
    ms = d.node(40, 356, 330, "Message", "chat-text", "topics", "Topic.OutputAnnuncio.text in chat", white=True)
    ins = d.node(410, 152, 330, "Istruzioni", "clipboard-text", "instructions",
                 "Flusso di Lavoro: New Job Posting,\nTesto in HTML, Annuncio Mail", white=True, detail="f04-istruzioni")
    ht = d.node(410, 262, 330, "Testo in HTML", "logo:ai-builder", "tools",
                "prompt: Username = User.DisplayName,\nContent compilato dall'AI", white=True, detail="f04-html")
    ml = d.node(410, 372, 330, "Annuncio Mail", "logo:outlook", "tools",
                "Send an email (V2): To = User.Email,\nSubject e Body compilati dall'AI", white=True, detail="f04-mail")
    box = d.node(410, 494, 330, "Casella dell'utente", "logo:outlook", "tools", "email con l'annuncio in HTML")
    d.arrow([(300, u["b"]), (300, tp["y"])], "topics")  # a destra del titolo della corsia
    d.arrow([(tp["cx"], tp["b"]), (pr["cx"], pr["y"])], "topics")
    d.arrow([(pr["cx"], pr["b"]), (ms["cx"], ms["y"])], "topics", label="OutputAnnuncio", at=(pr["cx"], (pr["b"] + ms["y"]) / 2))
    d.arrow([(ms["r"], ms["cy"]), (390, ms["cy"]), (390, ht["cy"]), (ht["x"], ht["cy"])], "tools")
    d.arrow([(ht["cx"], ht["b"]), (ml["cx"], ml["y"])], "tools", label="frammento HTML", at=(ht["cx"], (ht["b"] + ml["y"]) / 2))
    d.arrow([(ml["cx"], ml["b"]), (box["cx"], box["y"])], "tools")
    d.save()


def lab04_topic():
    """Lab 04: il topic New Job Posting, con le variabili di input e il prompt Job Posting - Zava."""
    f = Flow("lab04-topic-new-job-posting", "Topic · New Job Posting", w=330)
    tr = f.step("Trigger", "lightning", "triggers", "The agent chooses, dalla descrizione:\nnuovo annuncio di lavoro (job posting)")
    f.side(tr, "Variabili di input", "brackets-curly", "topics",
           "RoleTitle: titolo standard del ruolo\nSeniority: Junior, Mid o Senior\nPrimaryLocation: sede o Remote/Hybrid", 300, detail="f04-inputs")
    f.step("Job Posting - Zava", "logo:ai-builder", "tools", "prompt: role_title, seniority,\nprimary_location", afam="topics",
           pill="RoleTitle · Seniority · PrimaryLocation", detail="f04-node-prompt")
    f.step("Message", "chat-text", "topics", "Topic.OutputAnnuncio.text", pill="Topic.OutputAnnuncio")
    f.save()


def lab05_agente():
    """Lab 05: l'agente Device Booker, i suoi topic, la lista Devices e l'agent flow."""
    d = Diagram("lab05-agente-device-booker", F)
    d.lane(20, 20, 310, 361, "Agente Device Booker", "robot", "agents")
    av = d.node(35, 62, 280, "Topic Available devices", "chats-circle", "topics",
                "Get items filtrato per VarDeviceType,\nrisultato in Global.VarDevices", white=True, detail="f05-available")
    rq = d.node(35, 172, 280, "Topic Request device", "chats-circle", "topics",
                "adaptive card con i dispositivi,\npoi l'agent flow", white=True, detail="f05-request")
    d.node(35, 290, 280, "Istruzioni", "clipboard-text", "instructions",
           "Action: /Available devices e\n/Request device; solo richieste", white=True, detail="f05-istruzioni")
    sp = d.node(390, 20, 340, "Lista Devices", "logo:sharepoint", "knowledge",
                "sito Help Desk CSM: Status, Asset Type,\nManufacturer, Model, Serial Number", detail="f05-devices")
    d.lane(390, 130, 340, 355, "Agent flow · Send device request email", "logo:power-automate", "tools")
    tr = d.node(405, 172, 310, "When an agent calls the flow", "lightning", "triggers",
                "input DeviceSharePointId, User,\nAdditionalComments (facoltativo)", white=True)
    gd = d.node(405, 262, 310, "Get Device", "logo:sharepoint", "tools", "Get item della lista Devices per ID", white=True, detail="f05-getdevice")
    em = d.node(405, 336, 310, "Send an email to manager", "logo:outlook", "tools", "Request type: new device", white=True, detail="f05-email")
    rs = d.node(405, 410, 310, "Respond to the agent", "flow-arrow", "tools", "output ModelValue = Model", white=True)
    d.arrow([(av["r"], 79), (sp["x"], 79)], "knowledge")
    d.arrow([(rq["r"], tr["cy"]), (tr["x"], tr["cy"])], "tools")
    for a_, b_ in ((tr, gd), (gd, em), (em, rs)):
        d.arrow([(a_["cx"], a_["b"]), (b_["cx"], b_["y"])], "tools")
    d.arrow([(gd["r"], gd["cy"]), (755, gd["cy"]), (755, sp["cy"]), (sp["r"], sp["cy"])], "knowledge", dashed=True)
    d.arrow([(rs["x"], rs["cy"]), (360, rs["cy"]), (360, rq["b"] - 14), (rq["r"], rq["b"] - 14)], NEUTRAL, dashed=True)
    d.save()


def lab05_sequenza():
    """Lab 05: la richiesta di un dispositivo, dalla domanda dell'utente all'email al manager."""
    a = [("Utente", "user-circle", "agents"), ("Device Booker", "robot", "ai-engine"),
         ("Agent flow", "logo:power-automate", "tools"), ("Lista Devices", "logo:sharepoint", "knowledge")]
    m = [(0, 1, "i want to request a new laptop", "call"),
         (1, 1, "Available devices: VarDeviceType Laptop", "note"),
         (1, 3, "Get items: Status Available, AssetType Laptop", "call"),
         (3, 1, "Global.VarDevices", "reply"),
         (1, 0, "Laptop disponibili; richiederne uno?", "reply"),
         (0, 1, "Sì", "call"),
         (1, 0, "Request device: adaptive card", "reply"),
         (0, 1, "Submit Request: dispositivo e commenti", "call"),
         (1, 2, "Send device request email", "call"),
         (2, 3, "Get Device: Get item per ID", "call"),
         (3, 2, "Manufacturer, Model, link", "reply"),
         (2, 2, "Send an email to manager", "note"),
         (2, 1, "ModelValue", "reply"),
         (1, 0, "Thanks: richiesta inviata al manager", "reply")]
    sequence("lab05-sequenza-richiesta", a, m, col_min=180, out=F)


def lab05_available():
    """Lab 05: il topic Available devices."""
    f = Flow("lab05-topic-available-devices", "Topic · Available devices", w=360)
    tr = f.step("Trigger", "lightning", "triggers", "The agent chooses, dalla descrizione:\ndispositivi disponibili nella lista Devices")
    f.side(tr, "Input e output", "brackets-curly", "topics",
           "VarDeviceType: Laptop, Desktop\no Smartphone; VarAvailableDevices\n(Table) restituita all'agente", 275, detail="f05-io")
    f.step("Get items", "logo:sharepoint", "tools", "lista Devices, view All items, Filter Query:\nStatus 'Available' e AssetType = VarDeviceType", detail="f05-getitems")
    f.step("Set variable value", "brackets-curly", "topics", "Topic.VarAvailableDevices =\nGlobal.VarDevices.value", pill="Global.VarDevices", detail="f05-setvar")
    f.save()


def lab05_request():
    """Lab 05: il topic Request device, con l'adaptive card e l'agent flow."""
    f = Flow("lab05-topic-request-device", "Topic · Request device", w=360)
    f.step("Trigger", "lightning", "triggers", "The agent chooses, dalla descrizione: l'utente\nrisponde sì alla richiesta di un dispositivo")
    f.step("Ask with adaptive card", "cards", "topics", "Device selection, formula card: le scelte\nvengono da ForAll(Global.VarDevices.value)", detail="f05-card")
    f.step("Send device request email", "logo:power-automate", "tools",
           "agent flow: DeviceSharePointId, User,\nAdditionalComments", pill="deviceSelectionId · commentsId", detail="f05-callflow")
    f.step("Message", "chat-text", "topics", "Thanks, User.DisplayName. Your selected\ndevice, ModelValue, has been submitted",
           pill="ModelValue")
    f.step("Redirect", "arrow-bend-up-right", "system", "Go to another topic: End of Conversation")
    f.save()


# --- schemi dei Fundamentals della GitHub Harness ---------------------------------------------
# Lab 01-05 della GitHub Harness (docs/fondamentali/github-harness/): nomi esatti di solution,
# agente, istruzioni, fonti, strumenti, skill e nodi del workflow creati nei lab. Se un lab cambia
# un nome, va cambiato anche qui. I file vanno in docs/fondamentali/images/ con il prefisso gh-labNN-.
# L'agente (e il suo contenitore) è disegnato con il glifo github-logo nell'argomento "github".
GHA = "github-logo"


def gh_lab01_percorso():
    """GitHub Lab 01: i passi della preparazione (a sinistra) e dove si trova ciò che creano (a destra)."""
    d = Diagram("gh-lab01-percorso-setup", F)
    steps = [("Account Microsoft 365", "user-circle", "platform", "Business Basic, Try for free", None),
             ("Copilot Studio Trial", "logo:copilot-studio", "instructions", "aka.ms/TryCopilotStudio", None),
             ("Ambiente del corso", "tray", "platform", "con Dataverse e Copilot Credits", "g01-ambiente"),
             ("Pubblicazione", "shield-check", "platform", "ruolo Copilot Studio Authors", "g01-accesso"),
             ("Nuova esperienza", "sparkle", "instructions", "New experience, selettore di ambiente", "g01-esperienza"),
             ("Sito SharePoint", "logo:sharepoint", "knowledge", "Zava Help Desk", "g01-sito"),
             ("Publisher e solution", "package", "lifecycle",
              "publisher CSM Solutions (GitHub)\nsolution Help Desk Zava (GitHub)", "g01-solution")]
    x, w, y0, pitch = 40, 290, 40, 90
    prev = None
    for i, (label, icon, fam, sub, det) in enumerate(steps):
        n = d.node(x, y0 + i * pitch, w, label, icon, fam, sub, detail=det)
        d.badge(22, n["cy"], i + 1)
        if prev:
            d.arrow([(prev["cx"], prev["b"]), (n["cx"], n["y"])], "instructions")
        prev = n
    # a destra: il tenant contiene account, licenza, gruppo, sito SharePoint e ambiente; l'ambiente publisher e solution
    T = 370
    y_sito, y_amb = 292, 440
    d.lane(T, 20, 500, y_amb + 200 + 16 - 20, "Tenant Microsoft 365", "buildings", "platform")
    c1 = d.node(T + 40, 62, 445, "Account di lavoro", "user-circle", "platform", "Microsoft 365 Business Basic", white=True)
    c2 = d.node(T + 40, 132, 445, "Copilot Studio Trial", "logo:copilot-studio", "instructions",
                "prova gratuita a incrementi di 30 giorni", white=True)
    c3 = d.node(T + 40, 202, 445, "Gruppo AgentCreators", "users-three", "platform",
                "security group con il ruolo\nCopilot Studio Authors", white=True)
    sito = d.lane(T + 40, y_sito, 445, 134, "Sito SharePoint Zava Help Desk", "logo:sharepoint", "knowledge")
    d.node(T + 55, y_sito + 42, 202, "Knowledge Base", "folders", "knowledge", "Playbook, SLA e\nincident report", white=True, detail="g01-kb")
    d.node(T + 265, y_sito + 42, 202, "Lista Dispositivi", "table", "knowledge", "6 dispositivi,\n5 Available", white=True, detail="g01-dispositivi")
    amb = d.lane(T + 40, y_amb, 445, 200, "Ambiente del corso", "tray", "platform")
    pub = d.node(T + 70, y_amb + 42, 400, "Publisher CSM Solutions (GitHub)", "stamp", "lifecycle", "prefisso csg, valore 77000", white=True)
    sol = d.node(T + 70, y_amb + 124, 400, "Solution Help Desk Zava (GitHub)", "package", "lifecycle", "solution preferita, ancora vuota", white=True)
    d.arrow([(pub["cx"], pub["b"]), (sol["cx"], sol["y"])], "lifecycle")
    for n, k in ((c1, 1), (c2, 2), (c3, 4)):
        d.badge(T + 20, n["cy"], k)
    d.badge(T + 20, y_sito + 23, 6)
    d.badge(T + 20, y_amb + 23, 3)
    d.badge(T + 55, pub["cy"], 7)
    d.badge(T + 55, sol["cy"], 7)
    d.save()


def gh_lab02_fonti():
    """GitHub Lab 02: l'Assistente Zava GH nella solution, con le istruzioni e le sei fonti di conoscenza."""
    d = Diagram("gh-lab02-agente-fonti", F)
    x, w = 20, 350
    src = [("support.microsoft.com", "globe", "Public website, ricerca generale spenta", "g02-web"),
           ("Zava_KB_Reset_M365_Password.docx", "upload-simple", "file caricato: reset della password", "g02-reset"),
           ("Zava_Guida_VPN_v1.docx", "files", "file caricato: 2019, non più in vigore", "g02-vpn-v1"),
           ("Zava_Guida_VPN_v2.docx", "files", "file caricato: 2022, non più in vigore", "g02-vpn-v2"),
           ("Zava_Guida_VPN_v3.docx", "files", "file caricato: 2026, in vigore", "g02-vpn-v3"),
           ("Sito SharePoint Zava Help Desk", "logo:sharepoint", "Playbook, SLA e incident report", "g02-sharepoint")]
    nodes = [d.node(x, 20 + i * 72, w, label, icon, "knowledge", sub, detail=det)
             for i, (label, icon, sub, det) in enumerate(src)]
    cy = (nodes[0]["y"] + nodes[-1]["b"]) / 2
    sy = cy - 132
    d.lane(470, sy, 350, 264, "Solution Help Desk Zava (GitHub)", "package", "lifecycle")
    ag = d.lane(485, sy + 42, 320, 206, "Assistente Zava GH", GHA, "github", detail="g02-agente")
    d.node(500, sy + 84, 290, "Istruzioni", "clipboard-text", "instructions",
           "ruolo, risposte dalle fonti,\nformato, sicurezza, versioni", white=True, detail="g02-istruzioni")
    d.node(500, sy + 172, 290, "Messaggio di benvenuto", "chat-text", "instructions", "Greeting & prompts", white=True, detail="g02-benvenuto")
    bus = 420
    for n in nodes:
        d.arrow([(n["r"], n["cy"]), (bus, n["cy"]), (bus, cy), (ag["x"], cy)], "knowledge", dashed=True)
    d.save()


def gh_lab03_strumenti():
    """GitHub Lab 03: le istruzioni sugli strumenti e sulle guide, Get my profile (V2) e Invia guida via email."""
    d = Diagram("gh-lab03-strumenti", F)
    d.lane(20, 20, 380, 462, "Assistente Zava GH", GHA, "github")
    nx, nw = 35, 350
    r1 = d.node(nx, 62, nw, "Istruzioni · Strumenti ed email", "clipboard-text", "instructions",
                "anteprima e conferma prima di inviare;\nsolo all'indirizzo letto dal profilo", white=True, detail="g03-strumenti")
    r2 = d.node(nx, 166, nw, "Istruzioni · Guide passo passo", "clipboard-text", "instructions",
                "dati da raccogliere, sezioni della guida,\nHTML per l'email", white=True, detail="g03-guide")
    r3 = d.node(nx, 270, nw, "Get my profile (V2)", "user-circle", "tools",
                "Office 365 Users: legge displayName\ne mail dal profilo", white=True, detail="g03-profile")
    r4 = d.node(nx, 390, nw, "Invia guida via email", "logo:outlook", "tools",
                "Send an email (V2) di Office 365 Outlook,\nrinominato", white=True, detail="g03-invia")
    pr = d.node(545, r3["cy"] - 30, 250, "Profilo Microsoft 365", "user-check", "platform", "di chi sta usando l'agente")
    mb = d.node(545, r4["cy"] - 30, 250, "Casella dell'utente", "logo:outlook", "tools", "la guida in HTML")
    d.arrow([(pr["x"], pr["cy"]), (r3["r"], pr["cy"])], "knowledge", dashed=True,
            label="nome ed email", at=((pr["x"] + r3["r"]) / 2, pr["cy"]))
    d.arrow([(r3["cx"], r3["b"]), (r4["cx"], r4["y"])], "tools",
            label="indirizzo dal profilo", at=(r3["cx"], (r3["b"] + r4["y"]) / 2))
    d.arrow([(r4["r"], mb["cy"]), (mb["x"], mb["cy"])], "tools",
            label="dopo la conferma", at=((r4["r"] + mb["x"]) / 2, mb["cy"]))
    d.save()


def gh_lab04_skill():
    """GitHub Lab 04: le tre skill dell'Assistente Zava GH, i file di riferimento e gli strumenti del Lab 03."""
    d = Diagram("gh-lab04-skill", F)
    d.lane(20, 20, 370, 462, "Assistente Zava GH", GHA, "github")
    nx, nw = 35, 340
    d.node(nx, 62, nw, "Istruzioni · Procedure", "clipboard-text", "instructions",
           "una riga per skill; tolta la sezione\nGuide passo passo", white=True, detail="g04-procedure")
    s1 = d.node(nx, 166, nw, "supporto-tecnico", "puzzle-piece", "topics",
                "checklist di primo livello:\nhardware, software o rete", white=True, detail="g04-supporto")
    s2 = d.node(nx, 286, nw, "apertura-ticket", "puzzle-piece", "topics",
                "cinque campi validati,\nriepilogo da confermare", white=True, detail="g04-ticket")
    s3 = d.node(nx, 390, nw, "guida-passo-passo", "puzzle-piece", "topics",
                "template con i testi fissi,\ninvio per email", white=True, detail="g04-guida")
    d.arrow([(s1["cx"], s1["b"]), (s2["cx"], s2["y"])], "topics",
            label="riepilogo escalation", at=(s1["cx"], (s1["b"] + s2["y"]) / 2))
    gx, gw = 480, 330
    refs = d.lane(gx, 20, gw, 190, "Riferimenti · guida-passo-passo", "folders", "knowledge")
    d.node(gx + 15, 62, gw - 30, "template-guida.md", "file-text", "knowledge", "template della guida", white=True)
    d.node(gx + 15, 134, gw - 30, "contenuti-aziendali.md", "file-text", "knowledge", "testi fissi del Service Desk", white=True, detail="g04-contenuti")
    tools = d.lane(gx, 224, gw, 190, "Strumenti · Lab 03", "toolbox", "tools")
    d.node(gx + 15, 266, gw - 30, "Get my profile (V2)", "user-circle", "tools", "nome ed email dell'utente", white=True)
    d.node(gx + 15, 338, gw - 30, "Invia guida via email", "logo:outlook", "tools", "invia la guida all'utente", white=True)
    d.arrow([(s3["r"], s3["cy"] - 8), (405, s3["cy"] - 8), (405, 115), (gx, 115)], "knowledge", dashed=True,
            label="legge", at=(442, 115))
    d.arrow([(s3["r"], s3["cy"] + 8), (428, s3["cy"] + 8), (428, 319), (gx, 319)], "tools",
            label="usa", at=(454, 319))
    d.save()


def gh_lab05_workflow():
    """GitHub Lab 05: il workflow Invia richiesta dispositivo, con le due condizioni e le tre risposte all'agente."""
    f = Flow("gh-lab05-workflow", "Workflow · Invia richiesta dispositivo", w=340, fam="tools", icon="flow-arrow", out=F)
    f.step("When an agent calls the workflow", "lightning", "triggers",
           "sharepointItemId, additionalComment,\nrequestorName", afam="tools", detail="g05-trigger")
    f.step("Cerca dispositivo", "logo:sharepoint", "tools",
           "Get items sulla lista Dispositivi:\nID eq sharepointItemId, Top Count 1", afam="tools", detail="g05-cerca")
    c1 = f.step("Dispositivo in inventario", "git-branch", "system",
                "Cerca dispositivo ha trovato\nalmeno un elemento?", afam="tools", detail="g05-inventario")
    colw, half = 250, 125
    x2, xC = f.cx - 198, f.cx + 198       # ramo In Catalogo (seconda condizione) e ramo Else
    ybus = c1["b"] + FLOW_FORK
    top = ybus + FLOW_DROP
    f.arrow([(c1["cx"], c1["b"]), (c1["cx"], ybus), (xC, ybus), (xC, top)], NEUTRAL, label="Else", at=(xC, (ybus + top) / 2))
    f.arrow([(c1["cx"], c1["b"]), (c1["cx"], ybus), (x2, ybus), (x2, top)], "tools", label="In Catalogo", at=(x2, (ybus + top) / 2))
    c2 = f._place("Dispositivo disponibile", "git-branch", "system", "Status uguale a Available?", x2 - 150, top, 300, detail="g05-disponibile")
    f._place("Respond to the agent", "flow-arrow", "tools", "esito NON_IN_CATALOGO,\nModelValue Nessun dispositivo",
             xC - half, top, colw, detail="g05-risp-catalogo")
    ybus2 = c2["b"] + FLOW_FORK
    top2 = ybus2 + FLOW_DROP
    xA, xB = x2 - 132, x2 + 132
    f.arrow([(c2["cx"], c2["b"]), (c2["cx"], ybus2), (xB, ybus2), (xB, top2)], NEUTRAL, label="Else", at=(xB, (ybus2 + top2) / 2))
    f.arrow([(c2["cx"], c2["b"]), (c2["cx"], ybus2), (xA, ybus2), (xA, top2)], "tools", label="Disponibile", at=(xA, (ybus2 + top2) / 2))
    av = f._place("Avvisa responsabile", "logo:outlook", "tools", "Send an email al responsabile", xA - half, top2, colw, detail="g05-avvisa")
    ya = av["b"] + FLOW_GAP
    f.arrow([(xA, av["b"]), (xA, ya)], "tools")
    f._place("Respond to the agent", "flow-arrow", "tools", "esito DISPONIBILE,\nModelValue = modello", xA - half, ya, colw, detail="g05-risp-disponibile")
    f._place("Respond to the agent", "flow-arrow", "tools", "esito ESAURITO,\nModelValue = modello", xB - half, top2, colw, detail="g05-risp-esaurito")
    f.save()


# --- schemi dei concetti chiave della GitHub Harness ------------------------------------------
# Le slide esplicative del corso (orchestrazione, componenti, skill, conoscenza, sandbox, evoluzione
# dei flow, agenti e workflow, crediti), ridisegnate come schemi: docs/fondamentali/images/gh-concetti-*.svg,
# mostrati in "Concetti chiave" di docs/fondamentali/github-harness/index.md.
# Standard harness nell'argomento "standard", GitHub Copilot harness in "github".

def gh_concetti_orchestrazione():
    """Standard harness: piano poi esecuzione; GitHub Copilot harness: ciclo continuo sullo stato più recente."""
    d = Diagram("gh-concetti-orchestrazione", F)
    top, bot = 20, 388
    d.lane(20, top, 480, bot - top, "Standard harness · piano, poi esecuzione", "list-numbers", "standard")
    ax, aw = 35, 195
    n1 = d.node(ax, 62, aw, "1. Intento", "target", "standard", "capisce la richiesta", white=True)
    n2 = d.node(ax, 156, aw, "2. Piano", "tree-structure", "standard", "sintetizza un workflow\na più passi", white=True)
    n3 = d.node(ax, 266, aw, "3. Esecuzione", "play-circle", "standard", "esegue i passi scritti", white=True)
    d.arrow([(n1["cx"], n1["b"]), (n2["cx"], n2["y"])], "standard")
    d.arrow([(n2["cx"], n2["b"]), (n3["cx"], n3["y"])], "standard")
    px, pw = 250, 215
    plan = d.lane(px, 62, pw + 30, 264, "Oggetto piano esplicito", "clipboard-text", "standard")
    d.node(px + 15, 106, pw, "Raccogli gli input", "textbox", "standard", white=True)
    d.node(px + 15, 166, pw, "Esegui l'azione", "lightning", "standard", "connettore, topic,\nquery dati, …", white=True)
    d.node(px + 15, 256, pw, "Risposta: riassumi", "chat-text", "standard", white=True)
    d.arrow([(n2["r"], n2["cy"]), (px, n2["cy"])], "standard", dashed=True)
    d.chip(35, 340, 450, 32, "Meno repianificazione dal vivo, più facile da ispezionare", "standard", "card")
    rx = 525
    d.lane(rx, top, 410, bot - top, "GitHub Copilot harness · ciclo continuo", GHA, "github")
    c1, c2, w = rx + 15, rx + 15 + 170 + 40, 170
    t = d.node(c1, 62, w, "Pensiero", "brain", "github", "ragiona sullo stato\npiù recente", white=True)
    a = d.node(c2, 62, w, "Azione", "lightning", "github", "chiama un tool\no un topic", white=True)
    o = d.node(c2, 250, w, "Osservazione", "eye", "github", "legge il risultato\ndel tool", white=True)
    dd = d.node(c1, 250, w, "Decisione", "signpost", "github", "sceglie al volo\nil prossimo passo", white=True)
    d.arrow([(t["r"], t["cy"]), (a["x"], a["cy"])], "github")
    d.arrow([(a["cx"], a["b"]), (o["cx"], o["y"])], "github")
    d.arrow([(o["x"], o["cy"]), (dd["r"], o["cy"])], "github")
    d.arrow([(dd["cx"], dd["y"]), (t["cx"], t["b"])], "github")
    d.chip((t["cx"] + a["cx"]) / 2 - 62, 179, 124, 30, "stato più recente", "github", "dashed")
    d.chip(rx + 15, 340, 380, 32, "Continua a decidere dallo stato più recente", "github", "card")
    d.save()


def gh_concetti_componenti():
    """Il modello a componenti di Copilot Studio: istruzioni, conoscenza, strumenti, memoria, sandbox, skill, agenti connessi."""
    d = Diagram("gh-concetti-componenti", F)
    w, g = 176, 8
    comps = [("Instructions", "clipboard-text", "instructions", "sempre attive", "gc-istruzioni"),
             ("Knowledge", "books", "knowledge", "fatti da cercare", "gc-knowledge"),
             ("Tools", "wrench", "tools", "dati e azioni live", "gc-tools"),
             ("Memory", "stack", "system", "contesto per utente", "gc-memory"),
             ("Agent Sandbox", "terminal-window", "ai-engine", "esegue codice", "gc-sandbox")]
    for i, (label, icon, fam, sub, det) in enumerate(comps):
        d.node(20 + i * (w + g), 20, w, label, icon, fam, sub, white=True, detail=det)
    y2 = 114
    sk = d.lane(20, y2, 550, 132, "Skills", "puzzle-piece", "topics")
    d.text(112, y2 + 28, "procedure riutilizzabili che il ciclo richiama se serve", 12, "dg-sub")
    md = d.node(35, y2 + 42, 240, "SKILL.md", "file-text", "topics", "procedura o contesto per\nun argomento o un compito", white=True, detail="gc-skillmd")
    sf = d.node(315, y2 + 42, 240, "File di supporto", "file-code", "topics", "Python o file di aiuto,\neseguiti in una sandbox", white=True, detail="gc-skillfile")
    d.arrow([(md["r"], md["cy"]), (sf["x"], sf["cy"])], "topics", dashed=True)
    d.node(585, y2, 335, "Agenti connessi", "users-three", "agents",
           "delegano un ambito specializzato\nsolo se serve, con istruzioni, tool,\nskill e knowledge propri", h=132, detail="gc-agenti")
    y3 = y2 + 132 + 16
    cw = (900 - 20) / 3
    for i, (label, icon) in enumerate([("Channels", "broadcast"), ("Evaluations", "list-checks"), ("Analytics", "chart-bar")]):
        d.node(20 + i * (cw + 10), y3, cw, label, icon, "system")
    d.node(20, y3 + 58, 900, "Enterprise Governance", "shield-check", "ai-engine")
    d.save()


def gh_concetti_skill():
    """Anatomia di una skill: metadati sempre nel contesto, contenuto caricato solo quando serve; che cosa evitare."""
    d = Diagram("gh-concetti-skill", F)
    d.lane(20, 20, 400, 116, "Sempre nel contesto", "stack", "ai-engine")
    d.node(35, 62, 370, "SKILL.md", "file-text", "ai-engine", "name + description = metadati\ndi instradamento", white=True, h=60)
    d.lane(20, 176, 400, 234, "Caricato solo quando serve", "download-simple", "topics")
    parts = [("Istruzioni", "clipboard-text", "il nucleo\ndella skill"),
             ("Esempi", "chat-text", "mostrare,\nnon spiegare"),
             ("Risorse", "folders", "file, template"),
             ("Script", "code", "codice eseguibile")]
    for i, (label, icon, sub) in enumerate(parts):
        d.node(35 + (i % 2) * 190, 218 + (i // 2) * 102, 180, label, icon, "topics", sub, white=True, h=76)
    d.arrow([(220, 136), (220, 176)], "topics", label="se lo scenario corrisponde", at=(220, 156))
    d.lane(450, 20, 380, 390, "Da evitare", "warning-octagon", "risk")
    avoid = [("Descrizioni vaghe", "question", "segnali di instradamento deboli: la skill\nscatta male o non scatta mai"),
             ("Mega-skill", "stack", "uno scope che fa tutto confonde l'intento\ne si sovrappone alle altre"),
             ("Elenchi di fatti", "database", "una skill guida, non sostituisce\nuna fonte Knowledge"),
             ("Skill non riviste", "warning-octagon", "le skill da AI o community sono codice\nnon attendibile: rivederle prima")]
    for i, (label, icon, sub) in enumerate(avoid):
        d.node(465, 62 + i * 86, 350, label, icon, "risk", sub, white=True, h=76)
    d.save()


def gh_concetti_conoscenza():
    """Come l'orchestratore recupera la conoscenza SharePoint: ricerca, classifica, recupero, elaborazione."""
    d = Diagram("gh-concetti-conoscenza", F)
    lw = 430
    d.lane(20, 20, lw, 132, "In SharePoint", "logo:sharepoint", "knowledge")
    d.lane(20 + lw + 30, 20, lw, 132, "Nell'Agent Sandbox", "terminal-window", "github")
    nw = 180
    xs = [35, 35 + nw + 40, 20 + lw + 45, 20 + lw + 45 + nw + 40]
    steps = [("Ricerca", "magnifying-glass", "knowledge", "ricerca semantica\ne snippet", "gc-ricerca"),
             ("Classifica", "chart-bar", "knowledge", "quali documenti\nservono davvero", "gc-classifica"),
             ("Recupero", "file-arrow-down", "github", "scarica i file\ncompleti", "gc-recupero"),
             ("Elaborazione", "package", "github", "struttura e metadati\nin cache", "gc-elaborazione")]
    ns = [d.node(x, 62, nw, label, icon, fam, sub, white=True, h=76, detail=det)
          for x, (label, icon, fam, sub, det) in zip(xs, steps)]
    for a, b in zip(ns, ns[1:]):
        d.arrow([(a["r"], a["cy"]), (b["x"], b["cy"])], "ai-engine")
    end = d.node(20, 192, 2 * lw + 30, "Disponibile nell'Agent Sandbox", "terminal-window", "ai-engine",
                 "I file SharePoint completi restano nel contenitore della sandbox dell'agente per il resto della conversazione,\n"
                 "nel formato elaborato: le domande successive trovano risposta da ciò che è già stato recuperato\n"
                 "e le ricerche non si ripetono, salvo che servano altre informazioni.")
    cx = 20 + lw + 30 + lw / 2
    d.arrow([(cx, 152), (cx, end["y"])], "ai-engine", dashed=True)
    d.save()


def gh_concetti_sandbox():
    """Agent Sandbox: che cosa può fare l'agente nello spazio isolato Linux/Python, e che cosa non può fare."""
    d = Diagram("gh-concetti-sandbox", F)
    d.lane(20, 20, 650, 218, "Che cosa può fare l'agente nella sandbox", "terminal-window", "github")
    cells = [("Eseguire comandi", "terminal-window", "utility Bash/Linux per file, tabelle\ne validazioni"),
             ("Scrivere script", "code", "codice Python per logica ripetibile,\ntrasformazioni e calcoli"),
             ("Generare artefatti", "file-code", "grafici, file PowerPoint, Word, Excel\ne PDF, dataset puliti, immagini"),
             ("Usata in automatico quando", "lightning", "il compito richiede calcolo esatto,\nparsing, validazione o creazione di file")]
    for i, (label, icon, sub) in enumerate(cells):
        d.node(35 + (i % 2) * 315, 62 + (i // 2) * 86, 305, label, icon, "github", sub, white=True, h=76)
    d.node(20, 264, 320, "Librerie preinstallate", "package", "github", "dati e grafici, file, parsing\ne OCR, matematica e logica",
           h=76, detail="gc-librerie")
    d.node(350, 264, 320, "Nessun Internet in uscita", "wifi-slash", "risk",
           "le attività esterne passano da Tool e\nKnowledge, così valgono le policy DLP", h=76)
    d.save()


def gh_concetti_evoluzione():
    """Dai cloud flow agli agent flow ai workflow: tre fatti per ciascuno."""
    d = Diagram("gh-concetti-evoluzione", F)
    lw, gap = 280, 30
    cols = [("Cloud flows", "cloud", "system",
             [("Flessibile", "sliders-horizontal", "automatizza processi tra\napp e servizi"),
              ("Gira in Power Automate", "logo:power-automate", None),
              ("Connettori", "plugs-connected", "standard e premium")]),
            ("Agent flows", "arrow-bend-up-right", "standard",
             [("Per gli agenti", "robot", "esperienza ottimizzata per le\nautomazioni degli agenti"),
              ("Gira in Copilot Studio", "logo:copilot-studio", None),
              ("Connettori per agenti", "plugs-connected", "ottimizzati per le azioni\ndegli agenti")]),
            ("Workflows", "share-network", "github",
             [("Tela migliorata", "sparkle", "per costruire automazioni\nagentiche in Copilot Studio"),
              ("Gira in Copilot Studio", "logo:copilot-studio", None),
              ("Nodi AI nativi", "brain", "e un agent designer inline")])]
    lanes = []
    for i, (title, icon, fam, facts) in enumerate(cols):
        x = 20 + i * (lw + gap)
        lanes.append(d.lane(x, 20, lw, 304, title, icon, fam))
        for k, (label, nicon, sub) in enumerate(facts):
            d.node(x + 15, 62 + k * 86, lw - 30, label, nicon, fam, sub, white=True, h=76)
    yb = lanes[0]["b"] + 36
    l1, l2, l3 = lanes
    a1, b1 = l1["x"] + l1["w"] / 2, l2["x"] + l2["w"] * 0.25
    a2, b2 = l2["x"] + l2["w"] * 0.65, l3["x"] + l3["w"] / 2
    d.arrow([(a1, l1["b"]), (a1, yb), (b1, yb), (b1, l2["b"])], "ai-engine",
            label="Ottimizzato per Copilot Studio", at=((a1 + b1) / 2, yb))
    d.arrow([(a2, l2["b"]), (a2, yb), (b2, yb), (b2, l3["b"])], "ai-engine",
            label="Ottimizzato per l'automazione agentica", at=((a2 + b2) / 2, yb))
    d.save()


def gh_concetti_agenti_workflow():
    """Agente (percorso agile) e workflow (percorso prevedibile): come sono fatti e quando scegliere l'uno o l'altro."""
    d = Diagram("gh-concetti-agenti-workflow", F)
    bot = 556
    lw1, lx2, lw2 = 460, 505, 442
    d.lane(20, 20, lw1, bot - 20, "Agenti · percorso agile", "robot", "github")
    o = d.node(35, 184, 170, "Orchestratore", "robot", "github", "ciclo di\nragionamento", white=True, h=76)
    tx = 35 + 170 + 35
    tools = [("Skill", "puzzle-piece", "topics"), ("Esecuzione di codice", "terminal-window", "ai-engine"),
             ("Tool (workflow)", "tree-view", "tools")]
    bus = o["r"] + 17
    for i, (label, icon, fam) in enumerate(tools):
        n = d.node(tx, 62 + i * 130, 225, label, icon, fam, white=True, h=60)
        d.arrow([(o["r"], o["cy"]), (bus, o["cy"]), (bus, n["cy"]), (n["x"], n["cy"])], "github", dashed=True)
    d.lane(lx2, 20, lw2, bot - 20, "Workflow · percorso prevedibile", "share-network", "tools")
    cx = lx2 + lw2 / 2
    tr = d.node(cx - 100, 62, 200, "Trigger", "lightning", "triggers", white=True)
    ie = d.node(cx - 100, 140, 200, "If/Else", "git-branch", "system", "condizione", white=True)
    d.arrow([(tr["cx"], tr["b"]), (ie["cx"], ie["y"])], "tools")
    ybus, top = ie["b"] + 16, ie["b"] + 56
    xa, xb = cx - 106, cx + 106
    d.arrow([(ie["cx"], ie["b"]), (ie["cx"], ybus), (xa, ybus), (xa, top)], "tools")
    d.arrow([(ie["cx"], ie["b"]), (ie["cx"], ybus), (xb, ybus), (xb, top)], "tools")
    outs = [(xa, "Genera output", "brain", "ragiona e genera\n(Agente)", "agents"),
            (xb, "Scrittura su sistema", "plugs-connected", "azione di scrittura\n(Connettore)", "tools")]
    for x, label, icon, sub, fam in outs:
        da = d.node(x - 100, top, 200, "Operazione sui dati", "database", "knowledge", white=True)
        ob = d.node(x - 100, top + 78, 200, label, icon, fam, sub, white=True, h=76)
        d.arrow([(x, da["b"]), (x, ob["y"])], "tools")
    texts = [(35, lw1 - 30, ["Il percorso è agile, alcuni processi sono prevedibili.",
                             "L'orchestratore chiama passi ben strutturati e ripetibili (flow e codice) per azioni di natura deterministica.",
                             "Es. intake sanitario: l'esito consultivo nasce da un dialogo multi-turno con il paziente."]),
             (lx2 + 15, lw2 - 30, ["Il percorso è prevedibile, alcuni processi sono agili.",
                                   "Inizio e fine del flusso (uno o più) sono noti in anticipo, con capacità AI incorporate dove un passo richiede ragionamento o giudizio.",
                                   "Es. approvazione spese: le nuove voci possono portare a un percorso rapido o a un controllo di policy."])]
    for x, width, paras in texts:
        rows = sum(len(_wrap(p, width)) for p in paras)
        y = bot - 16 - 17 * rows - 8 * (len(paras) - 1) + 4
        for k, p in enumerate(paras):
            y = d.paragraph(x, y, p, width, "dg-body" if k < 2 else "dg-sub") + 8
    d.save()


def _wrap(text, width, size=12):
    """Righe in cui paragraph() divide un testo (per calcolarne l'altezza)."""
    rows, cur = [], ""
    for wd in text.split(" "):
        if cur and text_width(cur + " " + wd, size) > width:
            rows.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    return rows + [cur]


def gh_concetti_crediti():
    """Copilot Credits lungo il ciclo di vita: la standard harness fattura dopo la pubblicazione, la GitHub Copilot harness sempre."""
    d = Diagram("gh-concetti-crediti", F)
    x1, x2, cw = 255, 515, 250
    d.node(x1, 20, cw, "Standard harness", "robot", "standard")
    d.node(x2, 20, cw, "GitHub Copilot harness", GHA, "github")
    phases = [("Creazione", "plus-circle"), ("Build", "pencil-simple-line"), ("Preview e test", "play-circle"),
              ("Valutazione", "list-checks"), ("Uso per gli utenti", "users-three")]
    for i, (label, icon) in enumerate(phases):
        y = 82 + i * 58
        d.node(20, y, 215, label, icon, "system")
        if i < 4:
            d.chip(x1, y, cw, 48, "Non fatturato", "system")
        else:
            d.node(x1, y, cw, "Dopo la pubblicazione", "coins", "standard")
        d.node(x2, y, cw, "Crediti", "coins", "github")
    d.node(20, 82 + 5 * 58 + 8, 745, "Licenza Microsoft 365 Copilot", "shield-check", "platform",
           "copre gli agenti della standard harness usati nei canali Microsoft 365, mai quelli della\n"
           "GitHub Copilot harness: creazione ed esecuzione si fatturano qualunque sia la licenza dell'utente")
    d.save()


if __name__ == "__main__":
    failed = []
    for build in (panoramica, architettura_standard, workflow_chat, workflow_email_standard,
                  workflow_dossier, workflow_revisione, workflow_csat,
                  lab01_percorso, lab02_fonti, lab03_agente, lab03_supporto, lab03_ticket,
                  lab04_agente, lab04_topic, lab05_agente, lab05_sequenza, lab05_available, lab05_request,
                  gh_lab01_percorso, gh_lab02_fonti, gh_lab03_strumenti, gh_lab04_skill, gh_lab05_workflow,
                  gh_concetti_orchestrazione, gh_concetti_componenti, gh_concetti_skill, gh_concetti_conoscenza,
                  gh_concetti_sandbox, gh_concetti_evoluzione, gh_concetti_agenti_workflow, gh_concetti_crediti):
        try:
            build()
        except LayoutError as e:
            failed.append(str(e))
    if failed:
        sys.exit("\n".join(failed))
