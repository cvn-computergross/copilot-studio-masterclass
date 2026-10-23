"""Schemi dei lab della Standard Harness: Advanced (S01, S02, S04, S05, S06) e Fundamentals (Lab 01-05).

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

PAD = 12      # margine minimo fra la fine di un testo e il bordo destro del suo riquadro
MARGIN = 6    # margine fra il contenuto e il bordo del disegno, uguale sui quattro lati
GAP = 4       # distanza minima fra un'etichetta di freccia e un riquadro
PILL_H = 18   # altezza delle etichette sulle frecce
SAFETY = 1.04  # i testi si misurano il 4% più larghi di Inter: resta margine fra browser e sistemi
HINT_R = 5.5   # raggio del pallino "i" dei riquadri con dettaglio interattivo


class LayoutError(Exception):
    """Uno schema non rispetta i controlli di impaginazione."""


def style_block(hint=False):
    """<style> del file SVG da solo: colori chiari e, con il sistema in tema scuro, quelli scuri.
    hint=True: lo schema ha riquadri con dettaglio, il cui pallino "i" nel file da solo si nasconde."""
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
               f' font-family="{FONT}">{style_block(bool(self.details))}{defs}'
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
            for k, line in enumerate(reversed(lines)):
                box = d._text((x1 + x2) / 2, y - 7 - 15 * k, line, 12, "dg-sub" if reply else "dg-body", 500, "middle")
                if box[0] < min(x1, x2) + side - 0.5 or box[2] > max(x1, x2) - side + 0.5:
                    d.errors.append(f"messaggio '{line}': esce dallo spazio fra le linee")
                d.extent.append(box)
        last = y
        y += step
    for cx in xs:
        d.vline(cx, 76, last + 30)
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

    def _place(self, label, icon, fam, sub, x, y, w, h=None):
        return self.node(x, y, w, label, icon, fam, sub, white=True, h=h)

    def step(self, label, icon, fam, sub=None, pill=None, w=None, h=None, afam="topics"):
        """Nodo nella colonna centrale; pill = etichetta sulla freccia che arriva al nodo."""
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
        n = self._place(label, icon, fam, sub, cx - w / 2, y, w, h)
        self.prev = [n]
        return n

    def branch(self, cols, colw, sep=14):
        """Rami affiancati sotto l'ultimo nodo. cols: (etichetta del ramo, [(label, icon, fam, sub), ...],
        colore della freccia del ramo). Restituisce l'ultimo nodo di ogni ramo."""
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
            for label, icon, fam, sub in nodes:
                if last:
                    y = last["b"] + FLOW_GAP
                    self.arrow([(ccx, last["b"]), (ccx, y)], afam)
                last = self._place(label, icon, fam, sub, ccx - colw / 2, y, colw)
            lasts.append(last)
        self.prev = lasts
        return lasts

    def side(self, n, label, icon, fam, sub, w, dx=40, right=True, into=True, afam=NEUTRAL, pill=None):
        """Scheda accanto al nodo n, centrata in altezza; into=True: la freccia va dalla scheda al nodo."""
        lines = sub.split("\n") if sub else []
        h = 44 + 16 * len(lines) if lines else 48
        x = n["r"] + dx if right else n["x"] - dx - w
        c = self._place(label, icon, fam, sub, x, n["cy"] - h / 2, w, h)
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
# Harness (Lab 00, S01-S07). Se un lab cambia un nome, va cambiato anche qui.

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
        [N("Istruzioni", "clipboard-text", "instructions", "ruolo, ambito, responsabilità, identificatori, delega", lab="S01"),
         N("Conoscenza PMO", "logo:sharepoint", "knowledge", "cartella SharePoint PMO Knowledge", lab="S01"),
         N("Impostazioni generative", "sliders-horizontal", "platform", "niente web, File uploads attivo, Claude Sonnet 4.6", lab="S01"),
         N("Intake Proposte", "robot", "agents", "child agent", lab="S02"),
         N("Agente Comitato", COM, "agents", "agente connesso", lab="S02"),
         N("Nuova proposta via email", "lightning", "triggers", "trigger When a new email arrives (V3)", lab="S05"),
         N("Genera dossier di revisione", "chats-circle", "topics", "topic con l'agent flow Genera dossier", lab="S06"),
         N("Teams and Microsoft 365 Copilot", "rocket-launch", "lifecycle", "canale dopo la pubblicazione", lab="S07")],
        layout="list"),
    "intake": D(
        "Intake Proposte", "robot", "agents", "S02-S05",
        "Child agent dell'Agente Demand IT: registra e analizza i business case e, dopo una conferma, crea la valutazione.",
        [N("Istruzioni", "clipboard-text", "instructions", "un solo PDF per volta, codici mai inventati", lab="S02"),
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
         N("Let other agents connect", "plugs-connected", "agents", "pubblicato e collegato all'Agente Demand IT")],
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
        "PMO Knowledge", "logo:sharepoint", "knowledge", "S01",
        "Cartella SharePoint con le regole del PMO: è la fonte Conoscenza PMO dell'Agente Demand IT.",
        [N("Zava_PMO_Linee_Guida_Business_Case.docx", "file-text", "knowledge", "formati, struttura, soglie, regola di budget", lab="Lab 00"),
         N("Zava_Piano_Strategico_IT_2026-2028.pdf", "file-text", "knowledge", "obiettivi OS1-OS5 con i KPI", lab="Lab 00"),
         N("Conoscenza PMO", "logo:sharepoint", "knowledge", "risponde con i permessi di chi chatta", lab="S01")],
        layout="list"),
    "users": D(
        "Proponenti e analisti", "users-three", "agents", "S01-S08",
        "Chi usa l'Agente Demand IT: i proponenti allegano il business case, gli analisti del PMO confermano.",
        [N("Pannello Test", "flask", "instructions", "le prove dei lab in Copilot Studio", lab="S01-S06"),
         N("Conferme dell'analista", "user-check", "agents", "programma e registrazione della valutazione", lab="S04"),
         N("Teams and Microsoft 365 Copilot", "logo:teams", "lifecycle", "canale dopo la pubblicazione", lab="S07"),
         N("Reazioni e CSAT", "thumbs-up", "lifecycle", "feedback degli utenti in Teams", lab="S08")],
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
         N("Html to text", "file-text", "tools", "testo del Body"),
         N("Classifica", "logo:ai-builder", "tools", "prompt Classifica email PMO"),
         N("Proposta rilevata", "git-branch", "system", "Classifica contiene Proposta?", branches=[
             B("No", [N("Da verificare", "git-branch", "system", "Classifica contiene Incerta?", branches=[
                 B("Sì", [N("Avvisa verifica manuale", "logo:outlook", "tools", "Send an email (V2)")], fam="platform"),
                 B("No", [N("Fine senza azioni", "x-circle", "system", "RispostaAutomatica o NonPertinente")])])])]),
         N("Per ogni allegato", "arrows-clockwise", "tools", "condizione Allegato PDF", pill="Sì"),
         N("Registra proposta email", "logo:dataverse", "knowledge", "riga in Proposals, canale Email"),
         N("Carica documento email", "logo:dataverse", "knowledge", "PDF in Business Case Document"),
         N("Sends a prompt to the specified copilot", DA, "ai-engine", "Agente Demand IT"),
         N("Analizza business case", "robot", "agents", "strumento di Intake Proposte"),
         N("Notifica PMO in Teams", "logo:teams", "tools", "adaptive card")]),
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
             N("Run a prompt", "logo:ai-builder", "tools", "prompt Dossier di revisione, output Document"),
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
         N("Run a prompt", "logo:ai-builder", "tools", "prompt Dossier di revisione, output Document"),
         N("Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx"),
         N("Create share link", "logo:onedrive", "tools", "Link type View, scope Organization"),
         N(RESPOND, "flow-arrow", "tools", "output DossierURL")]),
    "onedrive": D(
        "OneDrive", "logo:onedrive", "tools", "S06",
        "OneDrive for Business dell'autore: qui l'agent flow Genera dossier salva il dossier di revisione.",
        [N("Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx"),
         N("Create share link", "logo:onedrive", "tools", "View, Organization: Web URL"),
         N("Apri il dossier", "cards", "topics", "pulsante dell'adaptive card nel topic", pill="DossierURL")]),
    "teams-channel": D(
        "Canale del PMO", "logo:teams", "tools", "S05",
        "Dove il PMO vede arrivare le proposte ricevute per email, già registrate e analizzate.",
        [N("Notifica PMO in Teams", "logo:power-automate", "tools", "agent flow di Intake Proposte"),
         N("Post card in a chat or channel", "logo:teams", "tools", "Post as Flow bot"),
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
         N("Aggiorna proposta", "logo:dataverse", "knowledge", "titolo, sintesi, budget, proponente"),
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
         N("Aggiorna proposta", "logo:dataverse", "knowledge", "Proposal Status Assessed"),
         N(RESPOND, "flow-arrow", "tools", "codice, punteggio, indicazione")]),
    "notifica-teams": D(
        "Notifica PMO in Teams", "logo:power-automate", "tools", "S05",
        "Agent flow di Intake Proposte: avvisa il PMO in Teams di una proposta ricevuta per email.",
        [N(TRIGGER_FLOW, "lightning", "triggers", "CodiceProposta, Title, Requester, Program, Avvisi"),
         N("Post card in a chat or channel", "logo:teams", "tools", "Flow bot, adaptive card con FactSet"),
         N(RESPOND, "flow-arrow", "tools", "Esito: Notifica inviata")]),
}


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
    """S01-S07: chi parla con chi."""
    d = Diagram("panoramica-sistema")
    WA, WB, WC, WD = 232, 250, 210, 200     # larghezze delle quattro colonne, 55 px fra l'una e l'altra
    A = 20
    B = A + WA + 55
    C = B + WB + 55
    D = C + WC + 55
    u = d.node(A, 40, WA, "Proponenti e analisti", "users-three", "agents", "Teams e M365 Copilot (S07)", detail="users")
    kn = d.node(A, 140, WA, "PMO Knowledge", "logo:sharepoint", "knowledge", "conoscenza SharePoint", detail="pmo-knowledge")
    mail = d.node(A, 250, WA, "Casella del PMO", "logo:outlook", "tools", "oggetto Proposta progetto", detail="mailbox")
    da = d.node(B, 40, WB, "Agente Demand IT", DA, "ai-engine", "orchestratore (S01)", detail="demand-it")
    trg = d.node(B, 250, WB, "Flow del trigger", "logo:power-automate", "triggers", "When a new email arrives (S05)", detail="flow-trigger")
    intk = d.node(C, 10, WC, "Intake Proposte", "robot", "agents", "child agent (S02-S05)", detail="intake")
    com = d.node(C, 100, WC, "Agente Comitato", COM, "agents", "agente connesso (S02)", detail="comitato")
    dos = d.node(C, 190, WC, "Genera dossier", "logo:power-automate", "tools", "topic e agent flow (S06)", detail="genera-dossier")
    teams = d.node(D, 10, WD, "Canale del PMO", "logo:teams", "tools", "Notifica PMO in Teams", detail="teams-channel")
    dv = d.node(D, 100, WD, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse (Lab 00)", detail="pmo-hub")
    od = d.node(D, 190, WD, "OneDrive", "logo:onedrive", "tools", "dossier Word e link", detail="onedrive")
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
    d.save()


def architettura_standard():
    """S01-S06: i componenti dell'Agente Demand IT e dello specialista."""
    d = Diagram("architettura-standard")
    d.lane(20, 20, 620, 382, "Agente Demand IT · csm_agentedemand_std", DA, "ai-engine", detail="demand-it")
    top = d.node(342, 62, 280, "Topic", "chats-circle", "topics", "Genera dossier di revisione", white=True, detail="topic-dossier")
    trg = d.node(342, 140, 280, "Trigger", "lightning", "triggers", "When a new email arrives (V3)", white=True, detail="trigger-email")
    d.node(342, 218, 280, "Conoscenza PMO Knowledge", "logo:sharepoint", "knowledge", "Linee guida PMO, Piano Strategico IT", white=True, detail="pmo-knowledge")
    intake = d.lane(40, 62, 284, 325, "Intake Proposte · child agent", "robot", "agents", detail="intake")
    tools = [("Carica business case", "crea proposta e carica il PDF", "carica-bc"),
             ("Analizza business case", "prompt Estrai dati business case", "analizza-bc"),
             ("Crea valutazione", "prompt Valuta proposta,\nconferma dell'utente", "crea-val"),
             ("Notifica PMO in Teams", "adaptive card nel canale", "notifica-teams")]
    ys = [102, 167, 232, 313]
    for (label, sub, det), y in zip(tools, ys):
        d.node(55, y, 254, label, "logo:power-automate", "tools", sub, white=True, h=74 if "\n" in sub else 58, detail=det)
    d.lane(680, 20, 310, 150, "Agente Comitato · connesso", COM, "agents", detail="comitato")
    k2 = d.node(695, 62, 280, "Conoscenza Dataverse", "logo:dataverse", "knowledge", "Program, Evaluation Criterion,\nRequester, Proposal, Assessment", white=True, detail="comitato-kb")
    fd = d.node(680, 200, 310, "Agent flow Genera dossier", "logo:power-automate", "tools", "prompt Dossier di revisione", detail="flow-dossier")
    od = d.node(680, 285, 310, "OneDrive", "logo:onedrive", "tools", "Dossier_AS-####.docx, link", detail="onedrive")
    pa = d.node(680, 370, 310, "Flow del trigger", "logo:power-automate", "triggers", "prompt Classifica email PMO,\nRegistra proposta email", detail="flow-trigger")
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
         (0, 1, "Valuta la proposta", "call"), (1, 2, "Delega la valutazione", "call"),
         (2, 0, "Conferma richiesta prima di Crea valutazione", "reply"), (0, 2, "Conferma", "call"),
         (2, 3, "Crea valutazione: Valuta proposta, punteggio, AS-####", "call"),
         (2, 0, "Punteggio, indicazione e codice AS-####", "reply")]
    sequence("workflow-chat", a, m)


def workflow_email_standard():
    """S05: il flow del trigger in Power Automate."""
    d = Diagram("workflow-email-standard")
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
    d.text(dec["cx"] + 8, (dec["b"] + lo["y"]) / 2 + 4, "Sì", 11, "dg-sub", 600)
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
    p_h, f_h, sl_h = 76, 58, 58            # altezze di Run a prompt, Create file, Create share link
    f_y = row + p_h + 9
    sl_y = f_y + f_h + 12
    d.lane(lane_x, lane_y, 370, sl_y + sl_h + 15 - lane_y, "Agent flow · Genera dossier", "logo:power-automate", "tools")
    u = d.node(20, row, 190, "Utente", "user-circle", "agents", "Mi prepari il dossier\ndi AS-####?")
    top = d.node(250, row, 230, "Topic", "chats-circle", "topics", "Genera dossier di revisione,\nchiede il codice se manca")
    p = d.node(lane_x + 15, row, 340, "Run a prompt", "logo:ai-builder", "tools", "prompt Dossier di revisione: output Document,\ntemplate Word, conoscenza Dataverse", white=True, h=p_h)
    f = d.node(lane_x + 15, f_y, 340, "Create file", "logo:onedrive", "tools", "/Documents/Dossier_AS-####.docx", white=True, h=f_h)
    sl = d.node(lane_x + 15, sl_y, 340, "Create share link", "logo:onedrive", "tools", "View, Organization: output DossierURL", white=True, h=sl_h)
    card = d.node(250, sl["cy"] - 30, 230, "Adaptive card", "cards", "topics", "link al dossier in chat")
    d.arrow([(u["r"], u["cy"]), (top["x"], u["cy"])], "topics")
    d.arrow([(top["r"], top["cy"]), (p["x"], top["cy"])], "topics", label="CodiceValutazione", at=((top["r"] + lane_x) / 2, top["cy"]))
    d.arrow([(p["cx"], p["b"]), (f["cx"], f["y"])], "tools")
    d.arrow([(f["cx"], f["b"]), (sl["cx"], sl["y"])], "tools")
    d.arrow([(sl["x"], sl["cy"]), (card["r"], sl["cy"])], "tools", dashed=True)
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


# --- schemi dei Fundamentals ------------------------------------------------------------
# Lab 01-05 della Standard Harness (docs/fondamentali/standard-harness/): nomi esatti degli
# agenti, dei topic, delle variabili e degli strumenti creati nei lab. Se un lab cambia un nome,
# va cambiato anche qui. I file vanno in docs/fondamentali/images/, con il prefisso del lab.
F = FUNDAMENTALS


def lab01_percorso():
    """Lab 01: i passi della preparazione (a sinistra) e dove si trova ciò che creano (a destra)."""
    d = Diagram("lab01-percorso-setup", F)
    steps = [("Account Microsoft 365", "user-circle", "platform", "Business Basic, Try for free"),
             ("Copilot Studio Trial", "logo:copilot-studio", "instructions", "aka.ms/TryCopilotStudio"),
             ("Developer environment", "tray", "platform", "Power Apps Developer Plan"),
             ("Accesso", "shield-check", "platform", "ruolo Copilot Studio Authors"),
             ("Solution e Publisher", "package", "lifecycle", "CSMFirstAgent, CSM Solutions"),
             ("Primo agente", "robot", "agents", "IT Support")]
    x, w, h, y0, pitch = 40, 270, 60, 40, 94
    prev = None
    for i, (label, icon, fam, sub) in enumerate(steps):
        n = d.node(x, y0 + i * pitch, w, label, icon, fam, sub, h=h)
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
    src = [("Documento caricato", "upload-simple", "Zava_KB_Reset_M365_Password.docx\nper il reset della password"),
           ("Files group VPN Guide", "folders", "Zava_Guida_VPN_v1, v2, v3.docx\nistruzioni: usa la versione più recente"),
           ("SharePoint Help Desk CSM", "logo:sharepoint", "Documents: Playbook, Incident Report\nTemplate, SLA; con i permessi dell'utente"),
           ("Public website", "globe", "support.microsoft.com\naggiunto nel Lab 01")]
    nodes = [d.node(x, 20 + i * 92, w, label, icon, "knowledge", sub) for i, (label, icon, sub) in enumerate(src)]
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
                "domanda Issue: Hardware, Software o\nNetwork; passi di troubleshooting", white=True)
    esc = d.node(L + 15, 280, 350, "Escalate", "headset", "system", "topic di sistema", white=True)
    t2 = d.node(L + 15, 380, 350, "Ticket Card", "chats-circle", "topics",
                "Ask with adaptive card, riepilogo\ncon una formula card", white=True)
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
    f.step("Question", "question", "topics", "Salve User.DisplayName, tipologia di problema?\nMultiple choice options, variabile Issue")
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
    card = f.step("Ask with adaptive card", "cards", "topics", "Richiesta Ticket IT: campi obbligatori,\npulsanti Invia ticket e Annulla")
    out = f.side(card, "Variabili di output", "brackets-curly", "topics",
                 "Topic.nome, Topic.cognome,\nTopic.email, Topic.tipologia,\nTopic.descrizione", 240, into=False)
    msg = f.step("Message", "chat-text", "topics", "Il seguente Ticket è stato inviato al Reparto IT\n+ formula card Riepilogo dati inseriti")
    f.arrow([(out["cx"], out["b"]), (out["cx"], msg["cy"]), (msg["r"], msg["cy"])], NEUTRAL, dashed=True)
    f.save()


def lab04_agente():
    """Lab 04: l'agente Redazione Annunci, dal topic all'email con l'annuncio in HTML."""
    d = Diagram("lab04-agente-annunci", F)
    u = d.node(40, 20, 330, "Utente", "user-circle", "agents", "Voglio creare un nuovo annuncio di lavoro")
    d.lane(20, 110, 740, 354, "Agente Redazione Annunci", "robot", "agents")
    tp = d.node(40, 152, 330, "Topic New Job Posting", "chats-circle", "topics",
                "input RoleTitle, Seniority, PrimaryLocation", white=True)
    pr = d.node(40, 246, 330, "Job Posting - Zava", "logo:ai-builder", "tools",
                "prompt con il template aziendale\nZava S.p.A., in Markdown", white=True)
    ms = d.node(40, 356, 330, "Message", "chat-text", "topics", "Topic.OutputAnnuncio.text in chat", white=True)
    ins = d.node(410, 152, 330, "Istruzioni", "clipboard-text", "instructions",
                 "Flusso di Lavoro: New Job Posting,\nTesto in HTML, Annuncio Mail", white=True)
    ht = d.node(410, 262, 330, "Testo in HTML", "logo:ai-builder", "tools",
                "prompt: Username = User.DisplayName,\nContent compilato dall'AI", white=True)
    ml = d.node(410, 372, 330, "Annuncio Mail", "logo:outlook", "tools",
                "Send an email (V2): To = User.Email,\nSubject e Body compilati dall'AI", white=True)
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
           "RoleTitle: titolo standard del ruolo\nSeniority: Junior, Mid o Senior\nPrimaryLocation: sede o Remote/Hybrid", 300)
    f.step("Job Posting - Zava", "logo:ai-builder", "tools", "prompt: role_title, seniority,\nprimary_location", afam="topics",
           pill="RoleTitle · Seniority · PrimaryLocation")
    f.step("Message", "chat-text", "topics", "Topic.OutputAnnuncio.text", pill="Topic.OutputAnnuncio")
    f.save()


def lab05_agente():
    """Lab 05: l'agente Device Booker, i suoi topic, la lista Devices e l'agent flow."""
    d = Diagram("lab05-agente-device-booker", F)
    d.lane(20, 20, 310, 361, "Agente Device Booker", "robot", "agents")
    av = d.node(35, 62, 280, "Topic Available devices", "chats-circle", "topics",
                "Get items filtrato per VarDeviceType,\nrisultato in Global.VarDevices", white=True)
    rq = d.node(35, 172, 280, "Topic Request device", "chats-circle", "topics",
                "adaptive card con i dispositivi,\npoi l'agent flow", white=True)
    d.node(35, 290, 280, "Istruzioni", "clipboard-text", "instructions",
           "Action: /Available devices e\n/Request device; solo richieste", white=True)
    sp = d.node(390, 20, 340, "Lista Devices", "logo:sharepoint", "knowledge",
                "sito Help Desk CSM: Status, Asset Type,\nManufacturer, Model, Serial Number")
    d.lane(390, 130, 340, 355, "Agent flow · Send device request email", "logo:power-automate", "tools")
    tr = d.node(405, 172, 310, "When an agent calls the flow", "lightning", "triggers",
                "input DeviceSharePointId, User,\nAdditionalComments (facoltativo)", white=True)
    gd = d.node(405, 262, 310, "Get Device", "logo:sharepoint", "tools", "Get item della lista Devices per ID", white=True)
    em = d.node(405, 336, 310, "Send an email to manager", "logo:outlook", "tools", "Request type: new device", white=True)
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
           "VarDeviceType: Laptop, Desktop\no Smartphone; VarAvailableDevices\n(Table) restituita all'agente", 275)
    f.step("Get items", "logo:sharepoint", "tools", "lista Devices, view All items, Filter Query:\nStatus 'Available' e AssetType = VarDeviceType")
    f.step("Set variable value", "brackets-curly", "topics", "Topic.VarAvailableDevices =\nGlobal.VarDevices.value", pill="Global.VarDevices")
    f.save()


def lab05_request():
    """Lab 05: il topic Request device, con l'adaptive card e l'agent flow."""
    f = Flow("lab05-topic-request-device", "Topic · Request device", w=360)
    f.step("Trigger", "lightning", "triggers", "The agent chooses, dalla descrizione: l'utente\nrisponde sì alla richiesta di un dispositivo")
    f.step("Ask with adaptive card", "cards", "topics", "Device selection, formula card: le scelte\nvengono da ForAll(Global.VarDevices.value)")
    f.step("Send device request email", "logo:power-automate", "tools",
           "agent flow: DeviceSharePointId, User,\nAdditionalComments", pill="deviceSelectionId · commentsId")
    f.step("Message", "chat-text", "topics", "Thanks, User.DisplayName. Your selected\ndevice, ModelValue, has been submitted",
           pill="ModelValue")
    f.step("Redirect", "arrow-bend-up-right", "system", "Go to another topic: End of Conversation")
    f.save()


if __name__ == "__main__":
    failed = []
    for build in (panoramica, architettura_standard, workflow_chat, workflow_email_standard,
                  workflow_dossier, workflow_revisione,
                  lab01_percorso, lab02_fonti, lab03_agente, lab03_supporto, lab03_ticket,
                  lab04_agente, lab04_topic, lab05_agente, lab05_sequenza, lab05_available, lab05_request):
        try:
            build()
        except LayoutError as e:
            failed.append(str(e))
    if failed:
        sys.exit("\n".join(failed))
