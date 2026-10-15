// Lettura della struttura di docs/: sezioni, lab e titoli. Usata dalla configurazione
// (menu laterale) e dal plugin Markdown (numero di lab nella home).
import fs from 'node:fs'
import path from 'node:path'

export const DOCS = path.resolve(__dirname, '..')

// (cartella in docs/, nome nel menu e nell'header)
export const SECTIONS: [string, string][] = [
  ['standard-harness', 'Standard Harness'],
  ['github-harness', 'GitHub Harness'],
]

const ICON_COMMENT = /<!--\s*icon:[^>]*-->/g

/** Cartelle dei lab di una sezione (NN-nome/README.md), in ordine. */
export function labs(section: string): string[] {
  const dir = path.join(DOCS, section)
  if (!fs.existsSync(dir)) return []
  return fs
    .readdirSync(dir)
    .filter((name) => /^\d\d-/.test(name) && fs.existsSync(path.join(dir, name, 'README.md')))
    .sort()
}

/** Primo titolo "# ..." di un file Markdown, senza segnaposto delle icone. */
export function h1(file: string): string {
  const line = fs.readFileSync(file, 'utf8').split(/\r?\n/).find((l) => l.startsWith('# '))
  return line ? line.slice(2).replace(ICON_COMMENT, '').trim() : path.basename(path.dirname(file))
}

/** Menu laterale: Home, Info studenti, poi una voce per sezione con i suoi lab. */
export function sidebar() {
  const items: any[] = [{ text: 'Home', link: '/' }]
  if (fs.existsSync(path.join(DOCS, 'info.md'))) items.push({ text: 'Info studenti', link: '/info' })
  for (const [name, label] of SECTIONS) {
    if (!fs.existsSync(path.join(DOCS, name, 'index.md'))) continue
    items.push({
      text: label,
      collapsed: true,
      items: [
        { text: 'Panoramica', link: `/${name}/` },
        ...labs(name).map((lab) => ({
          // nel menu "Lab 01 · Environment Setup"
          text: h1(path.join(DOCS, name, lab, 'README.md')).replace(/^(Lab \d+) - /, '$1 · '),
          link: `/${name}/${lab}/`,
        })),
      ],
    })
  }
  return items
}
