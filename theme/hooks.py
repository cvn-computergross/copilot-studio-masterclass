"""Hook di MkDocs: pubblica le guide di docs/ così come sono scritte per GitHub.

Le guide restano la fonte unica e non vengono copiate né modificate su disco: le
conversioni avvengono in memoria a ogni build (e a ogni salvataggio con `mkdocs serve`).

  on_config         costruisce il menu dalla struttura di docs/ (sezioni e lab);
  on_page_markdown  converte la sintassi GitHub in quella di MkDocs Material:
                    - toglie le barre di navigazione ("Previous | Back to | Next");
                    - "> [!NOTE]" diventa un riquadro (admonition) con la sua icona;
                    - rientri delle liste a 4 spazi (GitHub ne accetta 2-3);
                    - nei lab, i passi numerati diventano caselle spuntabili;
                    - "<!-- icon: nome classi -->" diventa un'icona (vedi theme/README.md);
                    - "<!-- labs: sezione -->" diventa il numero di lab della sezione.
"""
import logging
import re
from pathlib import Path

from mkdocs.utils import get_relative_url

log = logging.getLogger("mkdocs.hooks.masterclass")
THEME = Path(__file__).parent

# (cartella in docs/, voce di menu)
SECTIONS = [
    ("standard-harness", "Standard Harness"),
    ("github-harness", "GitHub Harness"),
]
# callout GitHub -> (tipo admonition, titolo, glifo Phosphor); il colore lo dà il tipo
ADMONITION = {
    "NOTE": ("note", "Nota", "note-pencil"),
    "TIP": ("tip", "Suggerimento", "lightbulb"),
    "IMPORTANT": ("info", "Importante", "info"),
    "WARNING": ("warning", "Attenzione", "warning"),
    "CAUTION": ("danger", "Pericolo", "prohibit"),
}
LIST_MARKER = re.compile(r"^(\s*)((?:\d+\.|[-*+])\s+)")
NAV_LINE = re.compile(r"^(\[?Previous\b|\[Back to |\[← )")
ICON = re.compile(r"<!--\s*icon:\s*([a-z0-9-]+)((?:\s+[a-z0-9_-]+)*)\s*-->")
LAB_COUNT = re.compile(r"<!--\s*labs:\s*([a-z0-9-]+)\s*-->")
HEADING_ICON = re.compile(r"^(#{1,6})\s+(.*?)\s*(<!--\s*icon:[^>]*-->)\s*$")
LAB_PAGE = re.compile(r"^[^/]+/\d\d-[^/]+/README\.md$")


# --- menu ---------------------------------------------------------------------------

def labs(section):
    """Cartelle dei lab di una sezione (NN-nome/README.md), in ordine."""
    if not section.is_dir():
        return []
    return sorted(p for p in section.iterdir() if (p / "README.md").is_file())


def h1(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return ICON.sub("", line[2:]).strip()
    return path.stem


def on_config(config):
    docs = Path(config["docs_dir"])
    nav = [{"Home": "index.md"}]
    if (docs / "info.md").is_file():
        nav.append({"Info studenti": "info.md"})
    for name, label in SECTIONS:
        section = docs / name
        if not (section / "index.md").is_file():
            continue
        items = [{"Panoramica": f"{name}/index.md"}]
        for lab in labs(section):
            # nel menu "Lab 01 · Environment Setup"
            title = re.sub(r"^(Lab \d+) - ", r"\1 · ", h1(lab / "README.md"))
            items.append({title: f"{name}/{lab.name}/README.md"})
        nav.append({label: items})
    config["nav"] = nav
    return config


# --- icone --------------------------------------------------------------------------

def phosphor(name, classes=()):
    """Glifo dell'Icon Pack (Phosphor duotone); il tema colora lo strato duotone."""
    if not (THEME / ".icons" / "phosphor" / f"{name}.svg").is_file():
        log.warning("icona Phosphor non trovata: theme/.icons/phosphor/%s.svg", name)
        return ""
    cls = " ".join(f".{c}" for c in ("icon", *classes))
    return f":phosphor-{name}:{{ {cls} }}"


def logo(name, classes, page_url):
    """Logo ufficiale di un prodotto (Microsoft, GitHub): un'immagine, mai ricolorata."""
    folder = THEME / "assets" / "img" / "logos"
    file = next((f for f in (folder / f"{name}.svg", folder / f"{name}.png") if f.is_file()), None)
    if file is None:
        log.warning("logo non trovato: theme/assets/img/logos/%s.(svg|png)", name)
        return ""
    src = get_relative_url(f"assets/img/logos/{file.name}", page_url)
    cls = " ".join(("logo", f"logo-{name}", *classes))
    return f'<img class="{cls}" src="{src}" alt="">'


def convert_icons(lines, page_url):
    def render(m):
        name, classes = m.group(1), tuple(m.group(2).split())
        if name.startswith("logo-"):
            return logo(name[5:], classes, page_url)
        return phosphor(name, classes)

    out = []
    for line in lines:
        h = HEADING_ICON.match(line)
        if h:  # nei titoli il segnaposto sta in fondo alla riga, l'icona va davanti al testo
            line = f"{h.group(1)} {h.group(3)} {h.group(2)}"
        out.append(ICON.sub(render, line))
    return out


# --- sintassi GitHub -> MkDocs Material ---------------------------------------------

def convert_callouts(lines):
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"^>\s*\[!(\w+)\]\s*$", lines[i])
        if m and m.group(1) in ADMONITION:
            kind, title, glyph = ADMONITION[m.group(1)]
            out.append(f'!!! {kind} "{phosphor(glyph)} {title}"')
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                body = lines[i][1:]
                body = body[1:] if body.startswith(" ") else body
                out.append(("    " + body) if body.strip() else "")
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return out


def reindent_lists(lines):
    """GitHub accetta 2-3 spazi di rientro nelle liste, Python-Markdown ne vuole 4."""
    out, stack, fence_delta, in_fence = [], [], 0, False
    for line in lines:
        stripped = line.lstrip(" ")
        n = len(line) - len(stripped)
        if in_fence:
            out.append(" " * max(0, n + fence_delta) + stripped if stripped else "")
            if stripped.startswith("```"):
                in_fence = False
            continue
        if not stripped:
            out.append("")
            continue
        if n == 0:
            stack = []
        while stack and n < stack[-1]:
            stack.pop()
        new_n = len(stack) * 4
        out.append(" " * new_n + stripped)
        if stripped.startswith("```"):
            in_fence, fence_delta = True, new_n - n
            continue
        m = LIST_MARKER.match(line)
        if m:
            stack.append(n + len(m.group(2)))
    return out


def strip_nav(lines):
    out = [l for l in lines if not NAV_LINE.match(l.strip())]
    while out and out[-1].strip() in ("", "---"):
        out.pop()
    return out


def add_checkboxes(lines):
    """Trasforma i passi numerati (primo livello) in caselle spuntabili.

    assets/javascripts/checklist.js ricorda le spunte nel browser e mostra
    l'avanzamento della pagina.
    """
    out, in_fence = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^(\d+)\.\s+(.*)$", line)
        if m:
            # MkDocs riconosce una lista solo se preceduta da una riga vuota
            # (GitHub no): senza, il passo resterebbe senza casella
            prev = out[-1] if out else ""
            if prev.strip() and not prev.startswith(("- ", " ")):
                out.append("")
            out.append(f"- [ ] **{m.group(1)}.** {m.group(2)}")
        else:
            out.append(line)
    return out


def lab_count(markdown, docs):
    def render(m):
        n = len(labs(docs / m.group(1)))
        return "In preparazione" if n == 0 else f"{n} lab"

    return LAB_COUNT.sub(render, markdown)


def on_page_markdown(markdown, page, config, files):
    src = page.file.src_uri
    markdown = lab_count(markdown.replace("\r\n", "\n"), Path(config["docs_dir"]))
    lines = markdown.split("\n")
    if src == "index.md":
        # la home è già scritta in sintassi MkDocs: servono solo le icone
        return "\n".join(convert_icons(lines, page.url))
    lines = strip_nav(lines)
    lines = convert_icons(lines, page.url)
    lines = convert_callouts(reindent_lists(lines))
    if LAB_PAGE.match(src):
        lines = add_checkboxes(lines)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"
