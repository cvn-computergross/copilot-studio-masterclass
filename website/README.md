# Sorgenti del sito GitHub Pages

Questa cartella contiene i componenti del sito (tema MkDocs Material, loghi, CSS, script di build).

Le lab **non** vanno copiate qui: il sito si genera dalla cartella `docs/` della repo (indici delle sezioni e lab).

Sito pubblicato: <https://cvn-computergross.github.io/copilot-studio-masterclass/>

## Come si aggiorna

A ogni push su `main` il workflow `.github/workflows/pages.yml`:

1. esegue `scripts/build_docs.py`, che converte i lab nel formato MkDocs, genera la navigazione dalla struttura della repo e trasforma i passi dei lab in caselle spuntabili;
2. compila il sito e lo scrive nel branch **`GitHub-Page`**, che GitHub Pages pubblica.

Il branch `GitHub-Page` contiene solo il sito compilato e viene riscritto a ogni aggiornamento: non modificarlo a mano.

| Percorso | Contenuto |
|---|---|
| `home.md` | Pagina iniziale del sito: presentazione e schede delle sezioni |
| `mkdocs.yml` | Configurazione del sito (titolo, tema, estensioni Markdown) |
| `requirements.txt` | Versioni di MkDocs e del tema Material |
| `overrides/` | Personalizzazioni del tema (footer) |
| `docs/assets/`, `docs/stylesheets/`, `docs/javascripts/` | Loghi, CSS e script delle caselle spuntabili e del menu |
| `scripts/build_docs.py` | Conversione dei lab in pagine MkDocs + navigazione |

## Anteprima locale

Dalla cartella principale della repo:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r website/requirements.txt
python website/scripts/build_docs.py . website
.venv\Scripts\mkdocs serve -f website/mkdocs.gen.yml
```

Aprire <http://127.0.0.1:8000>. I file generati (`website/docs/index.md`, `website/docs/standard-harness`, `website/docs/github-harness`, `website/mkdocs.gen.yml`) non vanno committati.
