"""Schemi dei lab Advanced della Standard Harness (S01, S02, S04, S05, S06).

Disegna ogni schema come file SVG in docs/advanced/images/, nello stile delle slide del corso:
riquadri tinti nel colore dell'argomento con glifo dell'Icon Pack (Phosphor duotone), logo
Microsoft o icona dell'agente, frecce sottili colorate, ritorni tratteggiati.

Uso, dalla cartella principale della repo (servono Pillow e `npm install` già fatto):
    python tools/diagrams.py

Per cambiare uno schema si modifica la sua funzione qui sotto e si rilancia lo script.

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


class LayoutError(Exception):
    """Uno schema non rispetta i controlli di impaginazione."""


def style_block():
    """<style> del file SVG da solo: colori chiari e, con il sistema in tema scuro, quelli scuri."""
    def rgba(hexcolor, a):
        r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
        return f"rgba({r},{g},{b},{a})"
    light = "svg{" + ";".join(f"{k}:{v[0]}" for k, v in COMMON.items()) + "}"
    light += "".join(f".f-{k}{{--f:{s};--f-tint:{t};--f-fill:{f}}}" for k, (s, t, f) in FAM.items())
    dark = "svg{" + ";".join(f"{k}:{v[1]}" for k, v in COMMON.items()) + "}"
    dark += "".join(f".f-{k}{{--f:{f};--f-tint:{rgba(f, .16)}}}" for k, (s, t, f) in FAM.items())
    return f"<style>{light}{RULES.replace(chr(10), '')}@media (prefers-color-scheme: dark){{{dark}}}</style>"


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
        data = base64.b64encode(file.read_bytes()).decode()
        return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:{mime};base64,{data}" preserveAspectRatio="xMidYMid meet"/>'
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

    def __init__(self, name):
        self.name = name
        self.parts, self.markers = [], {}
        self.nodes, self.lanes, self.pills, self.free, self.arrows, self.extent = [], [], [], [], [], []
        self.errors = []

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

    def node(self, x, y, w, label, icon, fam, sub=None, white=False, h=None):
        """Riquadro con icona ed etichetta; white=True dentro un'area tinta."""
        lines = sub.split("\n") if sub else []
        h = h or (44 + 16 * len(lines) if lines else 48)
        g = [f'<rect class="{"dg-card" if white else "dg-box"}" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>',
             icon_svg(icon, x + 12, y + h / 2 - 13, 26)]
        ty = y + h / 2 - 8 * len(lines) + 5
        rect = (x, y, x + w, y + h)
        boxes = [(label, self._text(x + 48, ty, label, 13.5, "dg-label", 600, out=g))]
        for i, line in enumerate(lines):
            boxes.append((line, self._text(x + 48, ty + 17 + 16 * i, line, 12, "dg-sub", out=g)))
        self.parts.append(f'<g class="dg-node f-{fam}">' + "".join(g) + "</g>")
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
        g = [f'<rect class="dg-lane" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>',
             icon_svg(icon, x + 14, y + 12, 22)]
        tb = self._text(x + 44, y + 28, title.upper(), 11.5, "dg-label", 600, out=g)
        self.parts.append(f'<g class="dg-lanegroup f-{fam}">' + "".join(g) + "</g>")
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

    def arrow(self, pts, fam="ai-engine", dashed=False, label=None, at=None):
        """Freccia a segmenti; l'etichetta (at = centro) deve stare su uno dei segmenti. fam=NEUTRAL: grigia."""
        mid = self._marker(fam)
        d = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        g = [f'<path class="dg-arrow" d="{d}"{dash} marker-end="url(#{mid})"/>']
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
        errs = self.check()
        if errs:
            raise LayoutError(f"schema {name}: problemi di impaginazione\n  - " + "\n  - ".join(errs))
        x0, y0, x1, y1 = self.bounds()
        x0, y0, x1, y1 = math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1)
        w, h = x1 - x0 + 2 * MARGIN, y1 - y0 + 2 * MARGIN
        dx, dy = MARGIN - x0, MARGIN - y0
        OUT.mkdir(parents=True, exist_ok=True)
        defs = "<defs>" + "".join(self.markers.values()) + "</defs>" if self.markers else ""
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" class="dg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"'
               f' font-family="{FONT}">{style_block()}{defs}'
               f'<g transform="translate({dx} {dy})">' + "".join(self.parts) + "</g></svg>\n")
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"schema {name} ({w}x{h})")


def _splits(text):
    """Possibili divisioni su due righe: prima quelle dopo la punteggiatura, poi le altre."""
    words = text.split(" ")
    out = []
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wmax = max(text_width(a, 12, 500), text_width(b, 12, 500))
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
            col = max(col, (min(text_width(text, 12, 500), two) + 2 * side) / abs(b - a))
        else:  # la nota non deve superare la linea successiva
            col = max(col, min(text_width(text, 12, 500), two) + 20 + 8 + side)
    col = math.ceil(col)
    xs = [60 + col * i + col / 2 for i in range(n)]
    d = Diagram(name)
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


# --- schemi -----------------------------------------------------------------------------
# Ogni schema riporta i nomi esatti dei componenti creati nei lab Advanced della Standard
# Harness (Lab 00, S01-S07). Se un lab cambia un nome, va cambiato anche qui.

DA = "agent:demand-it-agent-192.png"     # icona caricata in S01
COM = "agent:committee-agent-192.png"    # icona dell'Agente Comitato


def panoramica():
    """S01-S07: chi parla con chi."""
    d = Diagram("panoramica-sistema")
    WA, WB, WC, WD = 232, 250, 210, 200     # larghezze delle quattro colonne, 55 px fra l'una e l'altra
    A = 20
    B = A + WA + 55
    C = B + WB + 55
    D = C + WC + 55
    u = d.node(A, 40, WA, "Proponenti e analisti", "users-three", "agents", "Teams e M365 Copilot (S07)")
    kn = d.node(A, 140, WA, "PMO Knowledge", "logo:sharepoint", "knowledge", "conoscenza SharePoint")
    mail = d.node(A, 250, WA, "Casella del PMO", "logo:outlook", "tools", "oggetto Proposta progetto")
    da = d.node(B, 40, WB, "Agente Demand IT", DA, "ai-engine", "orchestratore (S01)")
    trg = d.node(B, 250, WB, "Flow del trigger", "logo:power-automate", "triggers", "When a new email arrives (S05)")
    intk = d.node(C, 10, WC, "Intake Proposte", "robot", "agents", "child agent (S02-S05)")
    com = d.node(C, 100, WC, "Agente Comitato", COM, "agents", "agente connesso (S02)")
    dos = d.node(C, 190, WC, "Genera dossier", "logo:power-automate", "tools", "topic e agent flow (S06)")
    teams = d.node(D, 10, WD, "Canale del PMO", "logo:teams", "tools", "Notifica PMO in Teams")
    dv = d.node(D, 100, WD, "PMO Demand Hub", "logo:dataverse", "knowledge", "Dataverse (Lab 00)")
    od = d.node(D, 190, WD, "OneDrive", "logo:onedrive", "tools", "dossier Word e link")
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
    d.lane(20, 20, 620, 382, "Agente Demand IT · csm_agentedemand_std", DA, "ai-engine")
    top = d.node(342, 62, 280, "Topic", "chats-circle", "topics", "Genera dossier di revisione", white=True)
    trg = d.node(342, 140, 280, "Trigger", "lightning", "triggers", "When a new email arrives (V3)", white=True)
    d.node(342, 218, 280, "Conoscenza PMO Knowledge", "logo:sharepoint", "knowledge", "Linee guida PMO, Piano Strategico IT", white=True)
    intake = d.lane(40, 62, 284, 325, "Intake Proposte · child agent", "robot", "agents")
    tools = [("Carica business case", "crea proposta e carica il PDF"),
             ("Analizza business case", "prompt Estrai dati business case"),
             ("Crea valutazione", "prompt Valuta proposta,\nconferma dell'utente"),
             ("Notifica PMO in Teams", "adaptive card nel canale")]
    ys = [102, 167, 232, 313]
    for (label, sub), y in zip(tools, ys):
        d.node(55, y, 254, label, "logo:power-automate", "tools", sub, white=True, h=74 if "\n" in sub else 58)
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
