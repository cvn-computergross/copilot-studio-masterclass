// Tema del sito: il tema predefinito di VitePress con qualche aggiunta.
//   header      dopo il nome del corso, "· Standard Harness · Lab 05" (HeaderPath)
//   colonna dx  pulsante Cerca e barra di avanzamento del lab            (AsideTools)
//   sopra testo selettore del percorso nelle pagine delle harness       (ExperienceSwitch)
//               barra di avanzamento sugli schermi senza colonna destra (DocProgress)
//   fondo       copyright e loghi EDUlabs/CVN e Computer Gross          (SiteFooter)
// Caselle dei passi (checklist.ts) e animazioni anime.js (animations.ts) si preparano
// a ogni cambio di pagina.
import { h, nextTick, onMounted, watch } from 'vue'
import { useData, useRoute } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import HeaderPath from './components/HeaderPath.vue'
import AsideTools from './components/AsideTools.vue'
import DocProgress from './components/DocProgress.vue'
import ExperienceSwitch from './components/ExperienceSwitch.vue'
import SiteFooter from './components/SiteFooter.vue'
import { setupChecklist } from './checklist'
import { setupAnimations } from './animations'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout: () =>
    h(DefaultTheme.Layout, null, {
      'nav-bar-content-before': () => h(HeaderPath),
      'aside-outline-before': () => h(AsideTools),
      'doc-before': () => [h(ExperienceSwitch), h(DocProgress)],
      'layout-bottom': () => h(SiteFooter),
    }),
  setup() {
    const route = useRoute()
    const { page } = useData()
    const enhance = () =>
      nextTick(() => {
        setupChecklist(route.path, page.value.relativePath)
        setupAnimations()
      })
    onMounted(() => {
      enhance()
      // server di sviluppo: salvando un .md la pagina si ridisegna senza cambiare indirizzo
      // e perde le caselle aggiunte da checklist.ts; si rimettono dopo ogni aggiornamento
      import.meta.hot?.on('vite:afterUpdate', enhance)
    })
    watch(() => route.path, enhance)
  },
} satisfies Theme
