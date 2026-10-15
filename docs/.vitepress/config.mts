// Configurazione del sito (VitePress). Le guide sono in docs/, scritte per GitHub:
// il menu si costruisce dalle cartelle (content.ts) e la sintassi si adatta in markdown.ts.
import fs from 'node:fs'
import path from 'node:path'
import { defineConfig } from 'vitepress'
import { DOCS, SECTIONS, sidebar } from './content'
import { masterclass } from './markdown'

const base = '/copilot-studio-masterclass/'
const repo = 'https://github.com/cvn-computergross/copilot-studio-masterclass'

export default defineConfig({
  lang: 'it-IT',
  title: 'Copilot Studio Masterclass',
  description: 'Laboratori pratici per creare agenti con Microsoft Copilot Studio',
  base,
  // ogni lab è un README.md (così GitHub lo mostra aprendo la cartella): nel sito è la pagina della cartella
  rewrites: { ':section/:lab/README.md': ':section/:lab/index.md' },
  head: [['link', { rel: 'icon', type: 'image/svg+xml', href: `${base}logos/copilot-studio.svg` }]],

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
    // usato dall'header per mostrare "· Standard Harness · Lab 05"
    sections: Object.fromEntries(SECTIONS),
    outline: { level: [2, 3], label: 'Indice' },
    socialLinks: [{ icon: 'github', link: repo, ariaLabel: 'Repository su GitHub' }],
    docFooter: { prev: 'Precedente', next: 'Successivo' },
    darkModeSwitchLabel: 'Tema',
    lightModeSwitchTitle: 'Passa al tema chiaro',
    darkModeSwitchTitle: 'Passa al tema scuro',
    sidebarMenuLabel: 'Menu',
    returnToTopLabel: 'Torna su',
    notFound: { title: 'Pagina non trovata', quote: 'La pagina che cerchi non esiste o è stata spostata.', linkText: 'Torna alla home' },
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: 'Cerca', buttonAriaLabel: 'Cerca' },
          modal: {
            displayDetails: 'Mostra dettagli',
            resetButtonTitle: 'Cancella la ricerca',
            backButtonTitle: 'Chiudi la ricerca',
            noResultsText: 'Nessun risultato per',
            footer: { selectText: 'per aprire', navigateText: 'per navigare', closeText: 'per chiudere' },
          },
        },
      },
    },
  } as any,
})
