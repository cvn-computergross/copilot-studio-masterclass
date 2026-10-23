// Schemi interattivi: nei riquadri con dettaglio (tools/diagrams.py, DETAILS; markdown.ts li
// rende pulsanti con l'HTML del dettaglio nascosto sotto lo schema) si apre un riquadro con il
// componente in dettaglio.
//   mouse     passandoci sopra si apre dopo un attimo e si chiude uscendo (anche dal riquadro aperto);
//             un clic lo fissa, un altro clic, Esc o un clic fuori lo chiudono
//   tastiera  i riquadri sono nella sequenza del Tab; Invio o Spazio aprono e chiudono, Esc chiude
//   tocco     un tocco apre e chiude
// Il riquadro aperto sta in un livello sopra la pagina (figlio di <body>), così non viene tagliato
// dallo scorrimento orizzontale dello schema: si mette sotto o sopra il riquadro dello schema, o
// di fianco, dove c'è posto, e se non sta in altezza scorre. Compare con anime.js (niente
// animazioni con movimento ridotto). I listener sono delegati sul documento: valgono per ogni
// pagina; a ogni cambio di pagina setupDiagramDetails() chiude il riquadro aperto.
import anime from 'animejs/lib/anime.es.js'
import { withBase } from 'vitepress'

const OPEN_DELAY = 110   // ms prima di aprire passando con il mouse (niente sfarfallio attraversando lo schema)
const CLOSE_DELAY = 220  // ms prima di chiudere uscendo: c'è il tempo di entrare nel riquadro aperto
const GAP = 8            // distanza fra il riquadro dello schema e quello aperto
const EDGE = 8           // margine dai bordi della finestra

interface State { box: Element; pop: HTMLElement; pinned: boolean; side: string; byKey: boolean }
let state: State | null = null
let openTimer = 0
let closeTimer = 0
let installed = false

const reduce = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

function clearTimers() {
  clearTimeout(openTimer)
  clearTimeout(closeTimer)
}

/** Copia del dettaglio nascosto sotto lo schema, con le immagini di loghi e agenti. */
function build(box: Element): HTMLElement | null {
  const fig = box.closest('figure.diagram')
  const id = box.getAttribute('data-detail')
  const src = fig?.querySelector<HTMLElement>(`.dg-details [data-detail-id="${CSS.escape(id ?? '')}"]`)
  if (!fig || !src) return null
  const pop = document.createElement('div')
  pop.className = 'dg-pop'
  const body = src.cloneNode(true) as HTMLElement
  const srcId = body.id
  body.removeAttribute('id')
  pop.id = `${srcId}-pop`
  pop.setAttribute('role', 'dialog')
  pop.setAttribute('aria-label', body.querySelector('.dgp-title')?.textContent ?? '')
  pop.appendChild(body)
  // loghi e icone degli agenti: la stessa immagine già incorporata nello schema, altrimenti il
  // file di docs/public/logos
  pop.querySelectorAll<HTMLElement>('.dgp-img').forEach((el) => {
    const icon = el.dataset.icon ?? ''
    const href = fig.querySelector(`image[data-icon="${CSS.escape(icon)}"]`)?.getAttribute('href')
    const url = href ?? (el.dataset.file ? withBase(`/logos/${el.dataset.file}`) : '')
    if (url) el.style.backgroundImage = `url("${url}")`
  })
  return pop
}

/** Parte visibile del riquadro dello schema: se lo schema scorre in orizzontale, solo quella. */
function anchorRect(box: Element): DOMRect {
  const r = box.getBoundingClientRect()
  const fig = box.closest('figure.diagram')?.getBoundingClientRect()
  if (!fig) return r
  const left = Math.max(r.left, fig.left)
  const right = Math.min(r.right, fig.right)
  return right > left ? new DOMRect(left, r.top, right - left, r.height) : r
}

/** Bordo inferiore dell'header fisso di VitePress (e della barra "Menu" sugli schermi stretti). */
function topLimit(): number {
  let top = 0
  document.querySelectorAll('.VPNav, .VPLocalNav').forEach((el) => {
    const r = el.getBoundingClientRect()
    if (r.height && r.top <= 1) top = Math.max(top, r.bottom)
  })
  return top + EDGE
}

/** Posizione del riquadro aperto: sotto, sopra, a destra o a sinistra del riquadro dello schema,
    il primo lato dove sta per intero; altrimenti il lato con più spazio, con lo scorrimento.
    keepSide: dopo uno scorrimento orizzontale dello schema resta dalla stessa parte. */
function place(s: State, keepSide = false) {
  const { pop } = s
  const r = anchorRect(s.box)
  const vw = document.documentElement.clientWidth
  const vh = window.innerHeight
  const top0 = topLimit()
  pop.style.maxHeight = ''
  pop.style.left = '0px'
  pop.style.top = '0px'
  const w = pop.offsetWidth
  const h = pop.scrollHeight + pop.offsetHeight - pop.clientHeight // con il bordo
  const room = {
    below: vh - EDGE - (r.bottom + GAP),
    above: r.top - GAP - top0,
    right: vw - EDGE - (r.right + GAP),
    left: r.left - GAP - EDGE,
  }
  const fullH = vh - top0 - EDGE
  const fits: Record<string, boolean> = {
    below: room.below >= h,
    above: room.above >= h,
    right: room.right >= w && fullH >= h,
    left: room.left >= w && fullH >= h,
  }
  let side = keepSide ? s.side : (['below', 'above', 'right', 'left'].find((k) => fits[k]) ?? '')
  let maxH = 0
  if (!side) {
    // non sta per intero da nessuna parte: sopra o sotto, dove c'è più spazio, e scorre
    side = room.below >= room.above ? 'below' : 'above'
    maxH = Math.max(160, side === 'below' ? room.below : room.above)
  }
  const clampX = (x: number) => Math.min(Math.max(x, EDGE), vw - EDGE - w)
  const clampY = (y: number, hh: number) => Math.min(Math.max(y, top0), vh - EDGE - hh)
  let x: number
  let y: number
  if (maxH) pop.style.maxHeight = `${maxH}px`
  const hh = maxH ? Math.min(h, maxH) : h
  if (side === 'below') { x = clampX(r.left + r.width / 2 - w / 2); y = r.bottom + GAP }
  else if (side === 'above') { x = clampX(r.left + r.width / 2 - w / 2); y = r.top - GAP - hh }
  else if (side === 'right') { x = r.right + GAP; y = clampY(r.top + r.height / 2 - hh / 2, hh) }
  else { x = r.left - GAP - w; y = clampY(r.top + r.height / 2 - hh / 2, hh) }
  s.side = side
  pop.dataset.side = side
  // coordinate del documento: scorrendo la pagina il riquadro aperto segue lo schema
  pop.style.left = `${Math.round(x + window.scrollX)}px`
  pop.style.top = `${Math.round(y + window.scrollY)}px`
}

function animateIn(pop: HTMLElement, side: string) {
  if (reduce()) return
  const d = 8
  const from = side === 'below' ? [0, -d] : side === 'above' ? [0, d] : side === 'right' ? [-d, 0] : [d, 0]
  anime({
    targets: pop,
    opacity: [0, 1],
    translateX: [from[0], 0],
    translateY: [from[1], 0],
    scale: [0.97, 1],
    easing: 'spring(1, 200, 20, 0)',
  })
}

function open(box: Element, pinned: boolean, byKey = false) {
  clearTimers()
  if (state?.box === box) {
    state.pinned = state.pinned || pinned
    state.byKey = byKey
    return
  }
  close(true)
  const pop = build(box)
  if (!pop) return
  document.body.appendChild(pop)
  state = { box, pop, pinned, side: '', byKey }
  box.setAttribute('aria-expanded', 'true')
  box.setAttribute('aria-controls', pop.id)
  place(state)
  animateIn(pop, state.side)
}

function close(instant = false) {
  clearTimers()
  if (!state) return
  const { box, pop, side } = state
  state = null
  box.setAttribute('aria-expanded', 'false')
  box.removeAttribute('aria-controls')
  if (instant || reduce()) { pop.remove(); return }
  anime.remove(pop)
  const d = 4
  anime({
    targets: pop,
    opacity: 0,
    translateY: side === 'below' ? -d : side === 'above' ? d : 0,
    duration: 120,
    easing: 'easeOutQuad',
    complete: () => pop.remove(),
  })
}

const boxOf = (t: EventTarget | null) => (t instanceof Element ? t.closest('figure.diagram [data-detail]') : null)
const inPop = (t: EventTarget | null) => !!state && t instanceof Node && state.pop.contains(t)

function scheduleClose() {
  if (!state || state.pinned) return
  clearTimeout(closeTimer)
  closeTimer = window.setTimeout(() => { if (state && !state.pinned) close() }, CLOSE_DELAY)
}

function install() {
  if (installed) return
  installed = true

  // mouse: si apre passandoci sopra, si chiude uscendo dal riquadro dello schema e da quello aperto
  document.addEventListener('pointerover', (e) => {
    if (e.pointerType !== 'mouse') return
    const box = boxOf(e.target)
    if (box) {
      clearTimeout(closeTimer)
      if (state?.pinned || state?.box === box) return
      clearTimeout(openTimer)
      openTimer = window.setTimeout(() => open(box, false), OPEN_DELAY)
    } else if (inPop(e.target)) {
      clearTimeout(closeTimer)
    }
  })
  document.addEventListener('pointerout', (e) => {
    if (e.pointerType !== 'mouse') return
    const from = boxOf(e.target) ?? (inPop(e.target) ? state!.pop : null)
    if (!from) return
    const to = e.relatedTarget
    if (to instanceof Node && from.contains(to)) return
    if (boxOf(to) === state?.box || inPop(to)) return
    clearTimeout(openTimer)
    scheduleClose()
  })

  // clic e tocco: fissa (o apre e fissa), di nuovo chiude; un clic fuori chiude
  document.addEventListener('click', (e) => {
    const box = boxOf(e.target)
    if (box) {
      if (state?.box === box && state.pinned) close()
      else open(box, true)
      return
    }
    if (state && !inPop(e.target)) close()
  })

  // tastiera: Invio o Spazio sul riquadro dello schema, Esc ovunque
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && state) {
      const { box } = state
      const focusInside = inPop(document.activeElement)
      close()
      if (focusInside) (box as SVGElement).focus()
      return
    }
    if (e.key !== 'Enter' && e.key !== ' ') return
    const box = boxOf(e.target)
    if (!box || e.target !== box) return
    e.preventDefault()
    if (state?.box === box && state.pinned) close()
    else open(box, true, true)
  })
  // aperto con la tastiera: si chiude quando il fuoco passa altrove
  document.addEventListener('focusout', (e) => {
    if (!state?.byKey || e.target !== state.box) return
    const to = e.relatedTarget
    if (inPop(to) || boxOf(to) === state.box) return
    close()
  })

  // lo schema scorre in orizzontale: il riquadro aperto lo segue; la finestra cambia: si riposiziona
  document.addEventListener('scroll', (e) => {
    if (state && e.target instanceof Element && e.target.contains(state.box)) place(state, true)
  }, { capture: true, passive: true })
  window.addEventListener('resize', () => { if (state) place(state) }, { passive: true })
}

/** Da chiamare a ogni cambio di pagina. */
export function setupDiagramDetails() {
  install()
  close(true)
  // il <title> dei riquadri serve senza JavaScript (suggerimento del browser); qui diventerebbe un
  // secondo suggerimento sopra il riquadro aperto: si toglie, il testo resta come nome accessibile
  document.querySelectorAll('figure.diagram [data-detail] > title').forEach((t) => {
    t.parentElement?.setAttribute('aria-label', t.textContent ?? '')
    t.remove()
  })
  if (import.meta.env.DEV) (window as unknown as { __dgCheck: typeof checkDiagrams }).__dgCheck = checkDiagrams
}

/** Controllo (solo con il server di sviluppo, dalla console: await __dgCheck()): nei riquadri degli
    schemi i testi stanno dentro il riquadro e non toccano il pallino; ogni dettaglio, aperto per
    davvero, sta nella finestra e i suoi testi stanno nei loro riquadri. Restituisce i problemi. */
export async function checkDiagrams(): Promise<string[]> {
  const errs: string[] = []
  const inside = (o: DOMRect, i: DOMRect, pad = 0) =>
    i.left >= o.left + pad - 0.5 && i.top >= o.top + pad - 0.5 && i.right <= o.right - pad + 0.5 && i.bottom <= o.bottom - pad + 0.5
  document.querySelectorAll('figure.diagram .dg-node').forEach((g) => {
    const rect = g.querySelector(':scope > rect')!.getBoundingClientRect()
    const dot = g.querySelector('.dg-hint-bg')?.getBoundingClientRect()
    g.querySelectorAll(':scope > text').forEach((t) => {
      const b = t.getBoundingClientRect()
      if (!inside(rect, b, 2)) errs.push(`schema: '${t.textContent}' esce dal suo riquadro`)
      if (dot && b.right > dot.left && b.left < dot.right && b.bottom > dot.top && b.top < dot.bottom)
        errs.push(`schema: '${t.textContent}' tocca il pallino del dettaglio`)
    })
  })
  const boxes = [...document.querySelectorAll('figure.diagram [data-detail]')]
  for (const box of boxes) {
    (box as SVGElement).scrollIntoView({ block: 'center', inline: 'center' })
    await new Promise((r) => setTimeout(r, 0))
    open(box, true)
    const s = state
    if (!s) { errs.push(`dettaglio ${box.getAttribute('data-detail')}: non si apre`); continue }
    anime.remove(s.pop)
    s.pop.style.opacity = '1'
    s.pop.style.transform = 'none'
    const name = box.getAttribute('data-detail')
    const p = s.pop.getBoundingClientRect()
    const vw = document.documentElement.clientWidth
    if (p.left < 0 || p.right > vw || p.top < 0 || p.bottom > window.innerHeight)
      errs.push(`dettaglio ${name}: esce dalla finestra (${Math.round(p.left)},${Math.round(p.top)} ${Math.round(p.width)}x${Math.round(p.height)})`)
    s.pop.querySelectorAll<HTMLElement>('.dgp-node, .dgp-grouphead, .dgp-head').forEach((n) => {
      const nr = n.getBoundingClientRect()
      n.querySelectorAll<HTMLElement>('.dgp-label, .dgp-sub, .dgp-tag, .dgp-title, .dgp-role, .dgp-lab, .dgp-grouphead > span:not(.dgp-icon)').forEach((t) => {
        if (t.scrollWidth > t.clientWidth + 1 || !inside(nr, t.getBoundingClientRect()))
          errs.push(`dettaglio ${name}: '${t.textContent}' non sta nel suo riquadro`)
      })
    })
    close(true)
  }
  return errs
}
