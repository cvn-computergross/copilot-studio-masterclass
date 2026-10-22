// Lettura della struttura di docs/: livelli, sezioni, lab e titoli. Usata dalla configurazione
// (menu laterale) e dal plugin Markdown (numero di lab nella home).
//
//   docs/<livello>/<sezione>/NN-nome/README.md
//   livelli: fondamentali, advanced     sezioni: standard-harness, github-harness
import fs from 'node:fs'
import path from 'node:path'

export const DOCS = path.resolve(__dirname, '..')

// (cartella in docs/, nome nel menu e nell'header)
export const LEVELS: [string, string][] = [
  ['fondamentali', 'Fundamentals'],
  ['advanced', 'Advanced'],
]
export const SECTIONS: [string, string][] = [
  ['standard-harness', 'Standard Harness'],
  ['github-harness', 'GitHub Harness'],
]

// pagine di riferimento di un livello, nel menu prima delle sezioni (file in docs/<livello>/)
const LEVEL_PAGES: Record<string, [string, string][]> = {}

// selettore "Choose your experience" in cima alle pagine delle harness (ExperienceSwitch.vue)
export const EXPERIENCES: Record<string, { section: string; title: string; text: string; soon?: boolean }[]> = {
  fondamentali: [
    { section: 'standard-harness', title: 'Standard Harness', text: 'Le basi di Copilot Studio nel portale: ambiente, conoscenza, topic, tool e agent flow' },
    { section: 'github-harness', title: 'GitHub Copilot Harness', text: 'Le stesse basi con istruzioni, skill, tool e workflow' },
  ],
  advanced: [
    { section: 'standard-harness', title: 'Standard Harness', text: "Costruisci l'Agente Demand IT del PMO di Zava con child agent, prompt e agent flow" },
    { section: 'github-harness', title: 'GitHub Copilot Harness', text: 'Lo stesso agente con istruzioni, skill, Dataverse MCP e workflow' },
  ],
}

const ICON_COMMENT = /<!--\s*icon:[^>]*-->/g

/** Cartelle dei lab di una sezione ("livello/sezione"), NN-nome/README.md, in ordine. */
export function labs(section: string): string[] {
  const dir = path.join(DOCS, section)
  if (!fs.existsSync(dir)) return []
  return fs
    .readdirSync(dir)
    .filter((name) => /^\d\d-/.test(name) && fs.existsSync(path.join(dir, name, 'README.md')))
    .sort()
}

// una harness senza lab è ancora in preparazione: nel selettore appare attenuata
for (const [level, list] of Object.entries(EXPERIENCES)) {
  for (const e of list) e.soon = labs(`${level}/${e.section}`).length === 0
}

/** Primo titolo "# ..." di un file Markdown, senza segnaposto delle icone. */
export function h1(file: string): string {
  const line = fs.readFileSync(file, 'utf8').split(/\r?\n/).find((l) => l.startsWith('# '))
  return line ? line.slice(2).replace(ICON_COMMENT, '').trim() : path.basename(path.dirname(file))
}

/** Voce di menu di una sezione: il nome apre la panoramica (index.md), dentro ci sono i lab. */
function sectionItem(dir: string, label: string) {
  const items = labs(dir).map((lab) => ({
    // nel menu "Lab 01 · Environment Setup", "Lab S01 · Agente orchestratore"
    text: h1(path.join(DOCS, dir, lab, 'README.md')).replace(/^(Lab S?\d+) - /, '$1 · '),
    link: `/${dir}/${lab}/`,
  }))
  return items.length ? { text: label, link: `/${dir}/`, collapsed: true, items } : { text: label, link: `/${dir}/` }
}

/** Menu laterale: Home, Student info, Riferimenti e licenze, poi un gruppo per livello con le sue
    sezioni. Il gruppo è solo un titolo fisso: non si chiude e non apre una pagina. */
export function sidebar() {
  const items: any[] = [{ text: 'Home', link: '/' }]
  if (fs.existsSync(path.join(DOCS, 'info.md'))) items.push({ text: 'Student info', link: '/info' })
  if (fs.existsSync(path.join(DOCS, 'credits.md'))) items.push({ text: 'Riferimenti e licenze', link: '/credits' })
  for (const [level, levelLabel] of LEVELS) {
    if (!fs.existsSync(path.join(DOCS, level))) continue
    const group: any = { text: levelLabel, items: [] }
    for (const [page, label] of LEVEL_PAGES[level] ?? []) {
      if (fs.existsSync(path.join(DOCS, level, `${page}.md`))) group.items.push({ text: label, link: `/${level}/${page}` })
    }
    for (const [section, label] of SECTIONS) {
      if (fs.existsSync(path.join(DOCS, level, section, 'index.md'))) group.items.push(sectionItem(`${level}/${section}`, label))
    }
    items.push(group)
  }
  return items
}
