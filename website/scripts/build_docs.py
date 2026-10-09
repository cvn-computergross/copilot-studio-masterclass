"""Prepara il sorgente MkDocs a partire dai lab del branch main.

Uso:
    python website/scripts/build_docs.py <cartella-repo> <cartella-sito>
    (es. dalla radice della repo: python website/scripts/build_docs.py . website)

Lo script:
  1. copia la pagina Info, gli indici delle sezioni, i lab (README + images/) e le
     risorse da scaricare (docs/resources/) da docs/ del branch main in website/docs/;
  2. converte la sintassi GitHub nella sintassi MkDocs Material
     (README.md -> index.md, callout "> [!NOTE]" -> admonition "!!! note",
     rientri delle liste a 4 spazi, rimozione delle barre di navigazione,
     passi numerati dei lab trasformati in caselle spuntabili);
  3. genera mkdocs.gen.yml (eredita mkdocs.yml e aggiunge la nav).

I lab restano la fonte unica: i file generati non vanno committati.
"""
import re
import shutil
import sys
from pathlib import Path

# (cartella in docs/, voce di menu)
SECTIONS = [
    ("standard-harness", "Standard Harness"),
    ("github-harness", "GitHub Harness"),
]
ADMONITION = {
    "NOTE": ("note", "Nota"),
    "TIP": ("tip", "Suggerimento"),
    "IMPORTANT": ("info", "Importante"),
    "WARNING": ("warning", "Attenzione"),
    "CAUTION": ("danger", "Pericolo"),
}
LIST_MARKER = re.compile(r"^(\s*)((?:\d+\.|[-*+])\s+)")
NAV_LINE = re.compile(r"^(\[?Previous\b|\[Back to )")


def fix_links(text):
    # README.md -> index.md nei link relativi (le pagine indice di MkDocs)
    return re.sub(r"\]\((?!https?://)([^)#]*?)README\.md", r"](\1index.md", text)


def convert_callouts(lines):
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"^>\s*\[!(\w+)\]\s*$", lines[i])
        if m and m.group(1) in ADMONITION:
            kind, title = ADMONITION[m.group(1)]
            out.append(f'!!! {kind} "{title}"')
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

    docs/javascripts/checklist.js ricorda le spunte nel browser e mostra
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


def convert(text, checklist=False):
    lines = strip_nav(fix_links(text).split("\n"))
    lines = convert_callouts(reindent_lists(lines))
    if checklist:
        lines = add_checkboxes(lines)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def h1(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def main(src, site):
    src, site = Path(src), Path(site)
    lab_docs, docs = src / "docs", site / "docs"
    # ripulisce solo i contenuti generati, non assets/javascripts/stylesheets
    (docs / "index.md").unlink(missing_ok=True)
    (docs / "info.md").unlink(missing_ok=True)
    for name in [n for n, _ in SECTIONS] + ["resources"]:
        shutil.rmtree(docs / name, ignore_errors=True)

    def copy_md(md, dest, checklist=False):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(convert(md.read_text(encoding="utf-8"), checklist), encoding="utf-8")

    # pagina iniziale del sito: website/home.md, già scritta in sintassi MkDocs;
    # in mancanza si usa docs/index.md della repo
    home = site / "home.md"
    if home.is_file():
        shutil.copyfile(home, docs / "index.md")
    else:
        copy_md(lab_docs / "index.md", docs / "index.md")
    nav = ["  - Home: index.md"]
    # pagina Info: website/info.md (sintassi MkDocs) o, in mancanza, docs/info.md
    if (site / "info.md").is_file():
        shutil.copyfile(site / "info.md", docs / "info.md")
        nav.append("  - Info studenti: info.md")
    elif (lab_docs / "info.md").is_file():
        copy_md(lab_docs / "info.md", docs / "info.md")
        nav.append("  - Info studenti: info.md")
    for name, label in SECTIONS:
        section = lab_docs / name
        if not (section / "index.md").is_file():
            continue
        copy_md(section / "index.md", docs / name / "index.md")
        nav.append(f'  - "{label}":')
        nav.append(f"    - Panoramica: {name}/index.md")
        for lab in sorted(p for p in section.iterdir() if (p / "README.md").is_file()):
            copy_md(lab / "README.md", docs / name / lab.name / "index.md", checklist=True)
            if (lab / "images").is_dir():
                shutil.copytree(lab / "images", docs / name / lab.name / "images")
            # nel menu "Lab 01 · Environment Setup"
            title = re.sub(r"^(Lab \d+) - ", r"\1 · ", h1(lab / "README.md"))
            nav.append(f'    - "{title}": {name}/{lab.name}/index.md')

    # file da scaricare (docs/resources/): copiati così i link nei lab funzionano,
    # ma senza pagina né voce nel menu
    if (lab_docs / "resources").is_dir():
        shutil.copytree(lab_docs / "resources", docs / "resources")

    (site / "mkdocs.gen.yml").write_text(
        "# File generato da scripts/build_docs.py: non modificare.\n"
        "INHERIT: mkdocs.yml\nnav:\n" + "\n".join(nav) + "\n",
        encoding="utf-8",
    )
    print(f"Generati {len(list(docs.rglob('*.md')))} file Markdown in {docs}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
