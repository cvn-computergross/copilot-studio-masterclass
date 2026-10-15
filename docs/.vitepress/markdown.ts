// Plugin Markdown: le guide restano scritte per GitHub e vengono adattate qui, in memoria,
// a ogni build (e a ogni salvataggio con il server di anteprima).
//   - toglie le barre di navigazione scritte per GitHub ("Previous | Back to | Next", "← Home");
//   - i link a README.md puntano alla pagina del lab (README.md diventa index.md),
//     i link ai file di docs/resources/ restano link a file da scaricare;
//   - "<!-- icon: nome classi -->" diventa un'icona (vedi docs/.vitepress/README.md);
//   - "<!-- labs: sezione -->" diventa il numero di lab della sezione;
//   - nei lab, un passo numerato scritto subito sotto un paragrafo diventa comunque un passo.
// I callout "> [!NOTE]" e le liste li gestisce già VitePress, con la stessa sintassi di GitHub:
// qui se ne traduce solo il titolo.
import fs from 'node:fs'
import path from 'node:path'
import type MarkdownIt from 'markdown-it'
import { labs } from './content'

const ICONS = path.resolve(__dirname, 'theme', 'icons')
const LOGOS = path.resolve(__dirname, '..', 'public', 'logos')

const NAV_LINE = /^\s*(\[?Previous\b|\[Back to |\[← ).*$/gm
const ICON = /<!--\s*icon:\s*([a-z0-9-]+)((?:\s+[a-z0-9_-]+)*)\s*-->/g
const HEADING_ICON = /^(#{1,6})\s+(.*?)\s*(<!--\s*icon:[^>]*-->)\s*$/gm
const LAB_COUNT = /<!--\s*labs:\s*([a-z0-9-]+)\s*-->/g
const LAB_PAGE = /^[^/]+\/\d\d-[^/]+\/(README|index)\.md$/

/** Nei lab un passo "N. testo" scritto subito sotto un paragrafo, senza riga vuota, per
    Markdown è ancora parte del paragrafo: si aggiunge la riga vuota, così diventa un passo
    (con la sua casella) come gli altri. Il codice tra ``` resta com'è. */
function separateSteps(src: string): string {
  const out: string[] = []
  let fence = false
  for (const line of src.split('\n')) {
    if (/^\s*```/.test(line)) fence = !fence
    const prev = out[out.length - 1] ?? ''
    if (!fence && /^\d+\.\s/.test(line) && prev.trim() && !/^(\s|\d+\.\s|[-*+]\s|>)/.test(prev)) out.push('')
    out.push(line)
  }
  return out.join('\n')
}

// titoli dei callout di GitHub ("> [!NOTE]") in italiano
const ALERT_TITLES: Record<string, [string, string]> = {
  note: ['NOTE', 'Nota'],
  tip: ['TIP', 'Suggerimento'],
  important: ['IMPORTANT', 'Importante'],
  warning: ['WARNING', 'Attenzione'],
  caution: ['CAUTION', 'Pericolo'],
}

const svgCache = new Map<string, string>()

/** Glifo dell'Icon Pack (Phosphor duotone), inserito nella pagina: il CSS colora lo strato duotone. */
function phosphor(name: string, classes: string[], file: string): string {
  const svgFile = path.join(ICONS, `${name}.svg`)
  if (!fs.existsSync(svgFile)) throw new Error(`${file}: icona non trovata, docs/.vitepress/theme/icons/${name}.svg`)
  if (!svgCache.has(name)) {
    const svg = fs.readFileSync(svgFile, 'utf8').trim().replace('<svg ', '<svg aria-hidden="true" ')
    svgCache.set(name, svg)
  }
  return `<span class="icon ${classes.join(' ')}">${svgCache.get(name)}</span>`
}

/** Logo ufficiale di un prodotto (Microsoft, GitHub): un'immagine, mai ricolorata.
    Il percorso parte da docs/public: VitePress aggiunge da solo la base del sito. */
function logo(name: string, classes: string[], file: string): string {
  const found = ['svg', 'png'].map((ext) => `${name}.${ext}`).find((f) => fs.existsSync(path.join(LOGOS, f)))
  if (!found) throw new Error(`${file}: logo non trovato, docs/public/logos/${name}.(svg|png)`)
  return `<img class="logo logo-${name} ${classes.join(' ')}" src="/logos/${found}" alt="">`
}

export function masterclass(md: MarkdownIt) {
  // trasformazioni sul testo, prima che markdown-it lo legga
  md.core.ruler.before('normalize', 'masterclass-source', (state) => {
    const file = state.env?.relativePath ?? ''
    if (LAB_PAGE.test(file)) state.src = separateSteps(state.src)
    state.src = state.src
      .replace(NAV_LINE, '')
      .replace(LAB_COUNT, (_, section) => {
        const n = labs(section).length
        return n === 0 ? 'In preparazione' : `${n} lab`
      })
      // nei titoli il segnaposto sta in fondo alla riga: l'icona va davanti al testo
      .replace(HEADING_ICON, '$1 $3 $2')
      .replace(ICON, (_, name: string, rest: string) => {
        const classes = rest.split(/\s+/).filter(Boolean)
        return name.startsWith('logo-') ? logo(name.slice(5), classes, file) : phosphor(name, classes, file)
      })
  })

  // callout di GitHub: VitePress li riconosce già, qui si traduce solo il titolo predefinito
  md.core.ruler.push('masterclass-alert-titles', (state) => {
    for (const token of state.tokens) {
      if (token.type !== 'github_alert_open') continue
      const [english, italian] = ALERT_TITLES[token.meta?.type] ?? []
      if (token.meta.title === english) token.meta.title = italian
    }
  })

  // link relativi: ".../README.md" punta alla pagina del lab, che nel sito è ".../index.md";
  // un file da scaricare (docs/resources/) resta un file, con l'attributo download
  md.core.ruler.push('masterclass-links', (state) => {
    for (const block of state.tokens) {
      for (const token of block.children ?? []) {
        if (token.type !== 'link_open') continue
        const href = token.attrGet('href')
        if (!href || /^[a-z]+:/i.test(href)) continue
        if (/(^|\/)resources\//.test(href)) token.attrSet('download', '')
        else token.attrSet('href', href.replace(/(^|\/)README\.md(?=#|$)/, '$1index.md'))
      }
    }
  })
}
