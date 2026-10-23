// Plugin Markdown: le guide restano scritte per GitHub e vengono adattate qui, in memoria,
// a ogni build (e a ogni salvataggio con il server di anteprima).
//   - toglie le barre di navigazione scritte per GitHub ("Previous | Back to | Next", "← Home");
//   - i link a README.md puntano alla pagina del lab (README.md diventa index.md),
//     i link ai file di docs/resources/ restano link a file da scaricare;
//   - "<!-- icon: nome classi -->" diventa un'icona (vedi docs/.vitepress/README.md);
//   - "<!-- labs: sezione -->" diventa il numero di lab della sezione;
//   - nei lab, un passo numerato scritto subito sotto un paragrafo diventa comunque un passo;
//   - un'immagine da sola in un paragrafo che punta a docs/advanced/images/*.svg o a
//     docs/fondamentali/images/*.svg (schemi di tools/diagrams.py) diventa lo schema inserito
//     nella pagina: <figure class="diagram"> con l'SVG, senza il suo <style>; colori e tema
//     scuro vengono da theme/style.css. Se accanto c'è <nome>.details.json, i riquadri con
//     dettaglio diventano pulsanti e i dettagli HTML nascosti (aperti da theme/diagram-details.ts).
// I callout "> [!NOTE]" e le liste li gestisce già VitePress, con la stessa sintassi di GitHub:
// qui se ne traduce il titolo e gli si mette davanti il glifo dell'Icon Pack.
import fs from 'node:fs'
import path from 'node:path'
import type MarkdownIt from 'markdown-it'
import { labs } from './content'

const ICONS = path.resolve(__dirname, 'theme', 'icons')
const LOGOS = path.resolve(__dirname, '..', 'public', 'logos')
const DOCS = path.resolve(__dirname, '..')
// cartelle degli schemi di tools/diagrams.py: Advanced e Fundamentals
const DIAGRAMS = [path.join(DOCS, 'advanced', 'images'), path.join(DOCS, 'fondamentali', 'images')]

const NAV_LINE = /^\s*(\[?Previous\b|\[Back to |\[← ).*$/gm
const ICON = /<!--\s*icon:\s*([a-z0-9-]+)((?:\s+[a-z0-9_-]+)*)\s*-->/g
const HEADING_ICON = /^(#{1,6})\s+(.*?)\s*(<!--\s*icon:[^>]*-->)\s*$/gm
// cartelle e pagine Markdown dei materiali si aprono nella repo su GitHub
const REPO = 'https://github.com/cvn-computergross/copilot-studio-masterclass'
const LAB_COUNT = /<!--\s*labs:\s*([a-z0-9/-]+)\s*-->/g
const LAB_PAGE = /^[^/]+\/[^/]+\/\d\d-[^/]+\/(README|index)\.md$/

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

// glifo e colore davanti al titolo dei callout (gli stessi colori del riquadro in style.css):
// nota blu, suggerimento verde, importante indaco, attenzione ambra, pericolo rosso
const ALERT_ICONS: Record<string, [string, string]> = {
  note: ['note-pencil', 'f-instructions'],
  tip: ['lightbulb', 'f-knowledge'],
  important: ['info', 'f-topics'],
  info: ['info', 'f-instructions'],
  warning: ['warning', 'f-platform'],
  caution: ['prohibit', 'f-risk'],
  danger: ['prohibit', 'f-risk'],
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

/** Schema generato da tools/diagrams.py, inserito nella pagina al posto dell'immagine.
    Il suo <style> (colori per GitHub, con il tema scuro del sistema operativo) si toglie:
    nel sito i colori vengono da theme/style.css e seguono la classe .dark di VitePress.
    Il testo alternativo diventa il nome accessibile dello schema. La larghezza dello schema va
    in --dg-w: sugli schermi stretti uno schema non scende sotto 640px, né sotto la sua
    larghezza se è più stretto (style.css). */
function diagram(svgFile: string, alt: string, esc: (s: string) => string, file: string): string {
  let svg = fs.readFileSync(svgFile, 'utf8')
    .replace(/<\?xml[^>]*\?>\s*/, '')
    .replace(/<style[\s\S]*?<\/style>/g, '')
    .trim()
    .replace(/^<svg /, `<svg role="img" aria-label="${esc(alt)}" `)
    .replace(/^(<svg[^>]*>)/, `$1<title>${esc(alt)}</title>`)
  const width = Number(/^<svg[^>]*\swidth="(\d+(?:\.\d+)?)"/.exec(svg)?.[1])
  const style = width > 0 ? ` style="--dg-w: ${width}px"` : ''
  // schema interattivo: accanto all'SVG c'è <nome>.details.json (tools/diagrams.py)
  const sidecar = svgFile.replace(/\.svg$/, '.details.json')
  if (!fs.existsSync(sidecar)) return `<figure class="diagram"${style} v-pre>${svg}</figure>`
  const data = JSON.parse(fs.readFileSync(sidecar, 'utf8')) as { details: Record<string, Detail> }
  const name = path.basename(svgFile, '.svg')
  // i riquadri con dettaglio diventano pulsanti; la descrizione accessibile è il dettaglio stesso
  // (nascosto, sotto lo schema). Con riquadri attivi lo schema è un gruppo, non un'immagine.
  svg = svg
    .replace(/^<svg role="img"/, '<svg role="group"')
    .replace(/<g ([^>]*?) data-detail="([^"]+)">/g, (_, attrs: string, id: string) => {
      if (!data.details[id]) throw new Error(`${file}: dettaglio '${id}' mancante in ${path.basename(sidecar)}`)
      return `<g ${attrs} data-detail="${id}" tabindex="0" role="button" aria-expanded="false" aria-describedby="dg-${name}-${id}">`
    })
  const details = Object.entries(data.details)
    .map(([id, d]) => detailHtml(`dg-${name}-${id}`, id, d, esc, file)).join('')
  return `<figure class="diagram diagram--interactive"${style} v-pre>${svg}`
    + `<figcaption class="diagram-hint">Passa il mouse su un riquadro o selezionalo per vederne il dettaglio.</figcaption>`
    + `<div class="dg-details" hidden>${details}</div></figure>`
}

// --- dettagli degli schemi interattivi (tools/diagrams.py, DETAILS) -------------------------
// Ogni dettaglio diventa HTML nascosto sotto lo schema: theme/diagram-details.ts lo copia nel
// riquadro che si apre (passando il mouse o selezionando il riquadro dello schema). Glifi come le
// altre icone; loghi e icone degli agenti come segnaposto (span.dgp-img) che il browser riempie
// con l'immagine già presente nello schema o con il file di docs/public/logos.
interface Step {
  label?: string; icon: string; fam: string; sub?: string; pill?: string; lab?: string; file?: string
  group?: string; layout?: string; steps?: Step[]
  branches?: { label: string; fam: string; steps: Step[] }[]
}
interface Detail { title: string; icon: string; fam: string; lab: string; role: string; layout: string; steps: Step[]; file?: string }

const famClass = (fam: string) => (fam === 'neutral' ? 'dg-neutral' : `f-${fam}`)

function detailIcon(s: { icon: string; file?: string }, esc: (s: string) => string, file: string): string {
  if (/^(logo|agent):/.test(s.icon)) {
    const f = s.file ? ` data-file="${esc(s.file)}"` : ''
    return `<span class="dgp-icon dgp-img" data-icon="${esc(s.icon)}"${f} aria-hidden="true"></span>`
  }
  return phosphor(s.icon, ['dgp-icon'], file)
}

function detailSteps(steps: Step[], layout: string, esc: (s: string) => string, file: string, first = false): string {
  const flow = layout !== 'list'
  const items = steps.map((s, i) => {
    // freccia che arriva al passo (nei flow), con l'eventuale etichetta; il primo passo di un ramo
    // ha la freccia con il nome del ramo
    const link = flow && (i > 0 || first)
      ? `<span class="dgp-link${s.pill ? ' dgp-link--pill' : ''}" aria-hidden="true">${s.pill ? `<span class="dgp-pill">${esc(s.pill)}</span>` : ''}</span>`
      : ''
    let body: string
    if (s.group) {
      body = `<div class="dgp-group ${famClass(s.fam)}"><p class="dgp-grouphead">${detailIcon(s, esc, file)}<span>${esc(s.group)}</span></p>`
        + detailSteps(s.steps ?? [], s.layout ?? 'flow', esc, file) + '</div>'
    } else {
      const sub = s.sub ? `<span class="dgp-sub">${esc(s.sub)}</span>` : ''
      const tag = s.lab ? `<span class="dgp-tag">${esc(s.lab)}</span>` : ''
      body = `<div class="dgp-node ${famClass(s.fam)}">${detailIcon(s, esc, file)}`
        + `<span class="dgp-text"><span class="dgp-label">${esc(s.label ?? '')}</span>${sub}</span>${tag}</div>`
    }
    const branches = s.branches?.length
      ? `<div class="dgp-branches">${s.branches.map((b) => `<div class="dgp-branch ${famClass(b.fam)}">`
        + detailSteps(b.steps.map((x, k) => (k === 0 ? { ...x, pill: b.label } : x)), 'flow', esc, file, true) + '</div>').join('')}</div>`
      : ''
    return `<li class="dgp-item${branches ? ' dgp-item--fork' : ''}">${link}${body}${branches}</li>`
  })
  return `<ol class="dgp-steps dgp-steps--${flow ? 'flow' : 'list'}">${items.join('')}</ol>`
}

function detailHtml(id: string, key: string, d: Detail, esc: (s: string) => string, file: string): string {
  return `<div class="dgp ${famClass(d.fam)}" id="${id}" data-detail-id="${esc(key)}">`
    + `<div class="dgp-head">${detailIcon(d, esc, file)}`
    + `<div class="dgp-headtext"><p class="dgp-title">${esc(d.title)}</p><p class="dgp-role">${esc(d.role)}</p></div>`
    + `<span class="dgp-lab" title="Lab in cui si costruisce">${esc(d.lab)}</span></div>`
    + detailSteps(d.steps, d.layout, esc, file) + '</div>'
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

  // le doppie graffe dei segnaposto ({{Campo}}) per Vue sarebbero codice: si mostrano come testo
  md.core.ruler.push('masterclass-mustache', (state) => {
    for (const block of state.tokens) {
      for (const token of block.children ?? []) {
        if (token.type === 'code_inline') token.attrSet('v-pre', '')
        else if (token.type === 'text' && token.content.includes('{{')) {
          token.type = 'html_inline'
          token.content = md.utils.escapeHtml(token.content).replace(/\{\{/g, '&#123;&#123;')
        }
      }
    }
  })

  // callout di GitHub: VitePress li riconosce già, qui si traduce solo il titolo predefinito
  md.core.ruler.push('masterclass-alert-titles', (state) => {
    for (const token of state.tokens) {
      if (token.type !== 'github_alert_open') continue
      const [english, italian] = ALERT_TITLES[token.meta?.type] ?? []
      if (token.meta.title === english) token.meta.title = italian
    }
  })

  // ...e davanti al titolo il glifo dell'Icon Pack, inserito come le altre icone (strato duotone colorato)
  const alertOpen = md.renderer.rules.github_alert_open
  if (alertOpen) {
    md.renderer.rules.github_alert_open = (tokens, idx, options, env, self) => {
      const html = alertOpen(tokens, idx, options, env, self)
      const [name, color] = ALERT_ICONS[tokens[idx].meta?.type] ?? []
      if (!name) return html
      const icon = phosphor(name, ['callout-icon', color], env?.relativePath ?? '')
      return html.replace('<p class="custom-block-title">', (open) => open + icon)
    }
  }

  // schemi dell'Advanced e dei Fundamentals: un paragrafo fatto solo di "![testo](…/images/nome.svg)"
  // diventa lo schema inserito nella pagina (riquadri e testi veri, colori del tema chiaro/scuro del sito)
  md.core.ruler.push('masterclass-diagrams', (state) => {
    const file = state.env?.relativePath ?? ''
    const tokens = state.tokens
    for (let i = 0; i + 2 < tokens.length; i++) {
      if (tokens[i].type !== 'paragraph_open' || tokens[i + 1].type !== 'inline' || tokens[i + 2].type !== 'paragraph_close') continue
      const parts = (tokens[i + 1].children ?? []).filter((t) => !(t.type === 'text' && !t.content.trim()) && t.type !== 'softbreak')
      if (parts.length !== 1 || parts[0].type !== 'image') continue
      const src = parts[0].attrGet('src') ?? ''
      if (/^[a-z]+:/i.test(src) || !/\.svg$/i.test(src)) continue
      const svgFile = path.resolve(DOCS, path.dirname(file), src)
      if (!DIAGRAMS.includes(path.dirname(svgFile))) continue
      if (!fs.existsSync(svgFile)) throw new Error(`${file}: schema non trovato, ${path.relative(DOCS, svgFile)}`)
      const block = new state.Token('html_block', '', 0)
      block.content = diagram(svgFile, parts[0].content, md.utils.escapeHtml, file) + '\n'
      block.map = tokens[i].map
      tokens.splice(i, 3, block)
    }
  })

  // link relativi: ".../README.md" punta alla pagina del lab, che nel sito è ".../index.md";
  // un file da scaricare (docs/resources/) resta un file, con l'attributo download
  // un file da scaricare si distingue dal testo da copiare e dai link normali: davanti al
  // nome il glifo download-simple, e il link è un riquadro arrotondato (a.download in style.css);
  // il nome sta in <span class="download-name">, così se va a capo resta accanto al glifo
  md.core.ruler.push('masterclass-links', (state) => {
    const file = state.env?.relativePath ?? ''
    for (const block of state.tokens) {
      const children = block.children ?? []
      for (let i = 0; i < children.length; i++) {
        const token = children[i]
        if (token.type !== 'link_open') continue
        const href = token.attrGet('href')
        if (!href || /^[a-z]+:/i.test(href)) continue
        if (/(^|\/)resources\//.test(href)) {
          // una cartella o una pagina Markdown dei materiali si apre su GitHub; un file si scarica
          if (/\/$|\.md(#|$)/.test(href)) {
            const target = path.posix.normalize(path.posix.join(path.posix.dirname(file), href))
            token.attrSet('href', `${REPO}/${href.endsWith('/') ? 'tree' : 'blob'}/main/docs/${target}`)
            token.attrSet('target', '_blank')
          } else {
            token.attrSet('download', '')
            token.attrJoin('class', 'download')
            const icon = new state.Token('html_inline', '', 0)
            icon.content = phosphor('download-simple', ['download-icon', 'f-instructions'], file) + '<span class="download-name">'
            const close = children.findIndex((t, k) => k > i && t.type === 'link_close')
            const end = new state.Token('html_inline', '', 0)
            end.content = '</span>'
            if (close > i) children.splice(close, 0, end)
            else children.push(end)
            children.splice(i + 1, 0, icon)
          }
        } else token.attrSet('href', href.replace(/(^|\/)README\.md(?=#|$)/, '$1index.md'))
      }
    }
  })
}
