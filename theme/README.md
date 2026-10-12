# Tema del sito

Questa cartella contiene tutto ciò che riguarda l'aspetto e il comportamento del sito. Le guide stanno in `docs/` e non vanno copiate qui: MkDocs le legge direttamente e `hooks.py` le converte in memoria a ogni build.

| Percorso | Contenuto |
|---|---|
| `hooks.py` | Costruisce il menu dalle cartelle di `docs/` e converte la sintassi GitHub in quella di MkDocs Material (callout, liste, passi spuntabili, icone) |
| `assets/stylesheets/extra.css` | Stile: colori per argomento, tipografia, header, menu, card, ricerca |
| `assets/javascripts/` | Caselle spuntabili con avanzamento, ricerca (Ctrl+K), percorso nell'header, animazioni (anime.js) |
| `assets/img/` | Loghi del footer e, in `logos/`, loghi dei prodotti |
| `.icons/phosphor/` | Glifi dell'Icon Pack (Phosphor duotone) usati dal sito |
| `partials/` | Pezzi del tema sostituiti: footer e link alla repo |

## Anteprima locale

Dalla cartella principale della repo, la prima volta:

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Poi, ogni volta:

```powershell
.venv\Scripts\mkdocs serve
```

Aprire <http://127.0.0.1:8000/copilot-studio-masterclass/> (`Ctrl+C` per fermare). La pagina si ricarica da sola quando si salva una guida, il CSS o uno script. Dopo una modifica a `hooks.py` o a `mkdocs.yml` il server va riavviato.

Prima di pubblicare conviene controllare che non ci siano link o icone mancanti:

```powershell
.venv\Scripts\mkdocs build --strict
```

## Icone

Regola: se il concetto è un prodotto con un logo ufficiale (Copilot Studio, SharePoint, Dataverse, GitHub...) si usa il **logo**; altrimenti un **glifo** dell'Icon Pack, con lo strato colorato nel colore dell'argomento.

Nelle guide un'icona si scrive come commento HTML, così su GitHub resta invisibile:

```markdown
## Prerequisiti <!-- icon: list-checks -->
### Una sandbox dedicata <!-- icon: tray f-platform -->
| 02 | Knowledge Sources | <!-- icon: books f-knowledge --> Conoscenza |
Si usa <!-- icon: logo-sharepoint --> SharePoint come fonte.
```

- `nome` è il file in `.icons/phosphor/` (senza `.svg`); con il prefisso `logo-` è il file in `assets/img/logos/`.
- Le parole dopo il nome sono classi CSS: il colore dell'argomento (`f-…`) e la dimensione (`i-lg`, `i-xl`).
- In un titolo il commento va in fondo alla riga: l'icona viene messa davanti al testo.
- Per aggiungere un glifo basta copiare l'SVG dalla cartella `phosphor-duotone` dell'Icon Pack in `.icons/phosphor/`; per un logo, copiare il file (SVG o PNG) in `assets/img/logos/`.

### Colori per argomento

| Classe | Argomento | Glifo tipico |
|---|---|---|
| `f-instructions` | Copilot Studio, istruzioni, passi (colore predefinito) | `clipboard-text`, `list-numbers`, `lightbulb` |
| `f-ai-engine` | Orchestrazione, modelli | `cpu`, `brain` |
| `f-knowledge` | Fonti di conoscenza, grounding | `books`, `globe`, `database` |
| `f-tools` | Tool, connettori, agent flow, prompt, MCP | `wrench`, `plugs-connected`, `flow-arrow`, `sparkle` |
| `f-topics` | Topic, nodi, variabili | `chats-circle` |
| `f-agents` | Agenti, multi-agente, utenti | `robot`, `user-circle`, `users-three` |
| `f-triggers` | Trigger, agenti autonomi | `lightning`, `calendar-dots` |
| `f-lifecycle` | Soluzioni, pubblicazione, telemetria | `package`, `rocket-launch`, `chart-line-up` |
| `f-platform` | Ambienti, sicurezza, licenze, crediti | `tray`, `shield-check`, `coins` |
| `f-system` | Topic di sistema, elementi classici | `gear-six` |
| `f-risk` | Errori, limiti, avvisi | `warning`, `prohibit` |

I callout di GitHub ricevono icona e colore da soli: `NOTE`, `TIP` e `IMPORTANT` in blu, `WARNING` e `CAUTION` in rosso.

## Altri segnaposto

- `<!-- labs: standard-harness -->` diventa il numero di lab della sezione ("13 lab"), o "In preparazione" se non ce ne sono.

## Home

`docs/index.md` è la pagina iniziale del sito ed è scritta in sintassi MkDocs Material, con i blocchi definiti in `extra.css`: `hero`, `card-grid` e `card`, `feature-grid` e `feature`, `topics` e `topic`, `logo-row`.

## Animazioni

Tutte le animazioni usano anime.js e stanno in `assets/javascripts/animations.js`. Muovono solo posizione, scala e trasparenza, e si disattivano se il sistema operativo chiede movimento ridotto.

## Pubblicazione

A ogni push su `main` il workflow `.github/workflows/pages.yml` compila il sito e lo scrive nel branch `GitHub-Page`, che GitHub Pages pubblica. Quel branch contiene solo il sito compilato e viene riscritto a ogni aggiornamento: non va modificato a mano.

## Licenze

- Phosphor Icons: MIT (`.icons/phosphor/LICENSE.txt`).
- anime.js: MIT (`assets/javascripts/vendor/anime.min.js`).
- I loghi dei prodotti in `assets/img/logos/` sono marchi dei rispettivi proprietari (Microsoft, GitHub) e non vanno ricolorati né modificati.
