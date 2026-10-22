// Configurazione del sito (VitePress). Le guide sono in docs/, scritte per GitHub:
// il menu si costruisce dalle cartelle (content.ts) e la sintassi si adatta in markdown.ts.
import fs from 'node:fs'
import path from 'node:path'
import { defineConfig } from 'vitepress'
import { DOCS, EXPERIENCES, LEVELS, SECTIONS, sidebar } from './content'
import { masterclass } from './markdown'

const base = '/copilot-studio-masterclass/'
const repo = 'https://github.com/cvn-computergross/copilot-studio-masterclass'

export default defineConfig({
  lang: 'it-IT',
  title: 'Copilot Studio Masterclass',
  description: 'Laboratori pratici per creare agenti con Microsoft Copilot Studio',
  base,
  // ogni lab è un README.md (così GitHub lo mostra aprendo la cartella): nel sito è la pagina della cartella
  rewrites: { ':level/:section/:lab/README.md': ':level/:section/:lab/index.md' },
  // i materiali (docs/resources/) sono file da scaricare, non pagine del sito
  srcExclude: ['resources/**'],
  head: [['link', { rel: 'icon', type: 'image/svg+xml', href: `${base}logos/copilot-studio.svg` }]],

  // anime.js preparato subito dal server di sviluppo
  vite: { optimizeDeps: { include: ['animejs/lib/anime.es.js'] } },

  // i file da scaricare (docs/resources/) non sono pagine: i lab li collegano con un link
  // relativo, che funziona su GitHub; nel sito vengono copiati così come sono
  buildEnd(site) {
    fs.cpSync(path.join(DOCS, 'resources'), path.join(site.outDir, 'resources'), { recursive: true })
  },

  markdown: {
    config: (md) => masterclass(md),
    // titoli dei riquadri ::: tip / ::: warning (quelli "> [!NOTE]" li traduce markdown.ts)
    container: {
      tipLabel: 'Suggerimento',
      warningLabel: 'Attenzione',
      dangerLabel: 'Pericolo',
      infoLabel: 'Informazione',
      detailsLabel: 'Dettagli',
    },
  },

  themeConfig: {
    logo: '/logos/copilot-studio.svg',
    sidebar: sidebar(),
    // usati dall'header ("· Advanced · Standard Harness · Lab 01") e dal selettore del percorso
    levels: Object.fromEntries(LEVELS),
    sections: Object.fromEntries(SECTIONS),
    experiences: EXPERIENCES,
    // navigazione in inglese, contenuti in italiano
    outline: { level: [2, 3], label: 'On this page' },
    socialLinks: [{ icon: 'github', link: repo, ariaLabel: 'GitHub repository' }],
    docFooter: { prev: 'Previous', next: 'Next' },
    sidebarMenuLabel: 'Menu',
    returnToTopLabel: 'Return to top',
    search: { provider: 'local' },
  } as any,
})
