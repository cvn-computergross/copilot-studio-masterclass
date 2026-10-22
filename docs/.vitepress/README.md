# Come funziona il sito

Il sito è fatto con [VitePress](https://vitepress.dev/), lo stesso strumento di Microsoft Agent Academy. VitePress legge le guide di `docs/` così come sono scritte per GitHub e le trasforma in un sito statico: menu, ricerca, tema chiaro/scuro e indice della pagina sono già inclusi.

## Avviare l'anteprima

Serve [Node.js](https://nodejs.org/) (versione 20 o successiva). Dalla cartella principale della repo, la prima volta:

```powershell
npm install
```

Poi, ogni volta:

```powershell
npm run docs:dev
```

Aprire <http://localhost:5173/copilot-studio-masterclass/>. La pagina si aggiorna da sola quando si salva una guida o un file del tema; per fermare il server, `Ctrl+C`.

Altri comandi:

| Comando | A cosa serve |
|---|---|
| `npm run docs:build` | Compila il sito in `docs/.vitepress/dist/`. Si ferma se un link porta a una pagina che non esiste |
| `npm run docs:preview` | Mostra il sito compilato, come sarà su GitHub Pages |

## Dove sta cosa

| Percorso | Contenuto |
|---|---|
| `config.mts` | Configurazione: titolo, indirizzo del sito, menu, ricerca, testi in italiano |
| `content.ts` | Costruisce il menu laterale dalle cartelle di `docs/` |
| `markdown.ts` | Adatta le guide al sito, in memoria, senza modificarle (vedi sotto) |
| `theme/index.ts` | Tema: quello di VitePress con le aggiunte del corso |
| `theme/style.css` | Colori, header, menu, riquadri, blocchi della home |
| `theme/components/` | Percorso nell'header, pulsante Cerca e barra di avanzamento, fondo pagina |
| `theme/checklist.ts` | Caselle spuntabili dei passi dei lab |
| `theme/animations.ts` | Animazioni (anime.js) |
| `theme/icons/` | Glifi dell'Icon Pack (Phosphor duotone) |
| `../public/` | File serviti così come sono: loghi dei prodotti (`logos/`) e del footer (`brand/`) |

## Cosa succede a una guida

Le guide restano scritte per GitHub e non vanno modificate per il sito. A ogni build `markdown.ts`:

- toglie le righe di navigazione scritte per GitHub (`Previous: … | Back to … | Next: …`, `[← Home del corso]`);
- fa puntare i link a `README.md` alla pagina del lab;
- lascia i link ai file di `docs/resources/` come file da scaricare (cartelle e pagine Markdown dei materiali si aprono su GitHub);
- mostra come testo i segnaposto tra doppie graffe (`{{Campo}}`);
- sostituisce i segnaposto delle icone e il numero dei lab;
- nei lab, separa un passo numerato scritto subito sotto un paragrafo, così diventa un passo come gli altri.

Gli schemi dell'Advanced sono SVG generati da `tools/diagrams.py` (glifi Phosphor e loghi Microsoft): si modificano lì e si rigenerano con `python tools/diagrams.py`. I callout di GitHub (`> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`…) VitePress li riconosce da solo; qui se ne traduce il titolo in italiano.

Nel browser, `theme/checklist.ts` mette una casella davanti a ogni passo numerato dei lab e ricorda le spunte; la barra di avanzamento sta nella colonna destra (o sopra il testo, sugli schermi più stretti).

## Struttura e menu laterale

Le guide stanno in `docs/<livello>/<sezione>/NN-nome/README.md`: livelli `fondamentali` (Fundamentals) e `advanced` (Advanced), sezioni `standard-harness` e `github-harness`.

Il menu si costruisce da solo dalle cartelle: Home, Student info, poi un gruppo per livello. Nel gruppo Advanced ci sono prima le pagine di riferimento del caso pratico (`LEVEL_PAGES` in `content.ts`), poi le sezioni. Il nome di una sezione apre la sua panoramica (`index.md`) e contiene i lab in ordine di numero; il nome nel menu è il titolo `# ` del lab. Livelli, sezioni e testi del selettore "Choose your experience" sono in `content.ts` (`LEVELS`, `SECTIONS`, `EXPERIENCES`).

I termini di navigazione (menu, Previous/Next, ricerca, avanzamento) sono in inglese; i contenuti in italiano.

Quando si aggiunge o si rinomina una cartella di lab, il server di anteprima va riavviato perché il menu si aggiorni.

## Icone

Regola: se il concetto è un prodotto con un logo ufficiale (Copilot Studio, SharePoint, Dataverse, GitHub…) si usa il **logo**; altrimenti un **glifo** dell'Icon Pack, con lo strato colorato nel colore dell'argomento.

Nelle guide un'icona si scrive come commento HTML, così su GitHub resta invisibile:

```markdown
## Prerequisiti <!-- icon: list-checks -->
### Una sandbox dedicata <!-- icon: tray f-platform -->
| 02 | Knowledge Sources | <!-- icon: books f-knowledge --> Conoscenza |
Si usa <!-- icon: logo-sharepoint --> SharePoint come fonte.
```

- `nome` è il file in `theme/icons/` (senza `.svg`); con il prefisso `logo-` è il file in `docs/public/logos/`.
- Le parole dopo il nome sono classi CSS, di solito il colore dell'argomento (`f-…`).
- In un titolo il commento va in fondo alla riga: l'icona viene messa davanti al testo.
- Per aggiungere un glifo basta copiare l'SVG dalla cartella `phosphor-duotone` dell'Icon Pack in `theme/icons/`; per un logo, copiare il file (SVG o PNG) in `docs/public/logos/`.

Se un'icona o un logo non esistono, la build si ferma e dice quale manca.

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

## Altri segnaposto

- `<!-- labs: fondamentali/standard-harness -->` diventa il numero di lab della sezione ("13 lab"), o "In preparazione" se non ce ne sono.

## Home

`docs/index.md` è la pagina iniziale del sito: Markdown con qualche blocco HTML, definito in `theme/style.css` (`hero`, `actions`, `card-grid` e `card`, `feature-grid` e `feature`, `topics` e `topic`, `logo-row`). Gli attributi tra graffe, come `{.button .brand}`, aggiungono classi all'elemento che li precede.

## Animazioni

Tutte le animazioni usano anime.js e stanno in `theme/animations.ts`: comparsa dei blocchi, pulsanti che rimbalzano, caselle, barra di avanzamento, interruttore del tema, frecce del menu. Muovono solo posizione, scala, rotazione e trasparenza, e si disattivano se il sistema operativo chiede movimento ridotto.

## Pubblicazione

A ogni push su `main` il workflow `.github/workflows/pages.yml` installa VitePress, compila il sito e lo scrive nel branch `GitHub-Page`, che GitHub Pages pubblica su <https://cvn-computergross.github.io/copilot-studio-masterclass/>. Quel branch contiene solo il sito compilato e viene riscritto a ogni aggiornamento: non va modificato a mano.

## Licenze

- VitePress: MIT. anime.js: MIT. Phosphor Icons: MIT (`theme/icons/LICENSE.txt`).
- I loghi in `docs/public/logos/` sono marchi dei rispettivi proprietari (Microsoft, GitHub) e non vanno ricolorati né modificati.
