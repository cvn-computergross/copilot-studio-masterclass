// Animazioni del sito, tutte con anime.js. Per restare fluide muovono solo posizione,
// scala, rotazione e trasparenza, con easing a molla; si disattivano se il sistema
// operativo chiede movimento ridotto.
import anime from 'animejs/lib/anime.es.js'

const SPRING = 'spring(1, 180, 18, 0)' // morbida, senza rimbalzo evidente
const SPRING_SOFT = 'spring(1, 120, 16, 0)' // più lenta, per blocchi grandi
const PRESS = 'spring(1, 260, 12, 0)' // ritorno dei pulsanti

const reduce = () => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

/** Barra di avanzamento: si allunga con una scala orizzontale, non con la larghezza. */
export function animateProgress(fill: HTMLElement, ratio: number) {
  if (reduce()) { fill.style.transform = `scaleX(${ratio})`; return }
  anime.remove(fill)
  anime({ targets: fill, scaleX: ratio, easing: SPRING_SOFT })
}

/** Casella spuntata: piccolo "pop". */
export function popCheckbox(box: HTMLElement) {
  if (reduce()) return
  anime.remove(box)
  anime({ targets: box, scale: [0.7, 1], easing: 'spring(1, 300, 10, 0)' })
}

/** Pulsanti: si abbassano alla pressione e tornano su con una molla al rilascio. */
function pressable(el: HTMLElement) {
  if (el.dataset.animPress) return
  el.dataset.animPress = '1'
  el.addEventListener('pointerdown', () => {
    anime.remove(el)
    anime({ targets: el, scale: 0.94, duration: 120, easing: 'easeOutQuad' })
  })
  for (const ev of ['pointerup', 'pointerleave', 'pointercancel']) {
    el.addEventListener(ev, () => {
      anime.remove(el)
      anime({ targets: el, scale: 1, easing: PRESS })
    })
  }
}

/** Card cliccabili: si sollevano appena al passaggio del mouse. */
function liftable(el: HTMLElement) {
  if (el.dataset.animLift) return
  el.dataset.animLift = '1'
  el.addEventListener('pointerenter', () => { anime.remove(el); anime({ targets: el, translateY: -3, easing: SPRING }) })
  el.addEventListener('pointerleave', () => { anime.remove(el); anime({ targets: el, translateY: 0, easing: SPRING }) })
}

/** Interruttore chiaro/scuro: il pallino scorre e ruota (al posto della transizione CSS). */
function themeSwitch(button: HTMLElement) {
  if (button.dataset.animSwitch) return
  button.dataset.animSwitch = '1'
  button.addEventListener('click', () => {
    const knob = button.querySelector<HTMLElement>('.check')
    if (!knob || reduce()) return
    // il tema cambia subito dopo il clic: si parte dalla posizione opposta e a fine corsa
    // torna a valere quella data dal CSS
    requestAnimationFrame(() => {
      const dark = document.documentElement.classList.contains('dark')
      anime.remove(knob)
      anime({
        targets: knob,
        translateX: dark ? [0, 18] : [18, 0],
        rotate: dark ? [0, 180] : [180, 0],
        easing: SPRING,
        complete: () => { knob.style.transform = '' },
      })
    })
  })
}

/** Menu laterale: la freccia di una sezione ruota quando la si apre (verso il basso) o chiude. */
function sidebarCaret(group: HTMLElement) {
  if (group.dataset.animCaret) return
  group.dataset.animCaret = '1'
  // si segue la classe "collapsed" invece del clic: al momento del clic Vue può averla già
  // cambiata o no, e cliccando il testo di una sezione con link la sezione non si apre
  let collapsed = group.classList.contains('collapsed')
  new MutationObserver(() => {
    const now = group.classList.contains('collapsed')
    if (now === collapsed) return
    collapsed = now
    const caret = group.querySelector<HTMLElement>(':scope > .item .caret-icon')
    if (!caret || reduce()) return
    const to = now ? 0 : 90
    // se un'animazione è in corso si riparte dall'angolo raggiunto
    const interrupted = caret.style.transform !== ''
    anime.remove(caret)
    anime({
      targets: caret,
      rotate: interrupted ? to : [now ? 90 : 0, to],
      easing: SPRING,
      complete: () => { caret.style.transform = '' },
    })
  }).observe(group, { attributes: true, attributeFilter: ['class'] })
}

/** Da chiamare a ogni cambio di pagina. */
export function setupAnimations() {
  if (reduce()) return
  document
    .querySelectorAll<HTMLElement>('.VPButton, .vp-doc a.button, .experience__option, .VPSocialLink, .aside-search, .progress-reset, .vp-doc button.copy, .VPNavBarSearch .DocSearch-Button')
    .forEach(pressable)
  document.querySelectorAll<HTMLElement>('.VPSwitchAppearance').forEach(themeSwitch)
  document.querySelectorAll<HTMLElement>('.VPSidebarItem.collapsible').forEach(sidebarCaret)
  document.querySelectorAll<HTMLElement>('.vp-doc .card--link').forEach(liftable)

  // contenuto: sulla home prima il titolo, poi card, voci e loghi uno dopo l'altro;
  // sulle altre pagine una dissolvenza leggera del testo
  const hero = document.querySelectorAll('.vp-doc .hero > *, .vp-doc .actions')
  const blocks = document.querySelectorAll('.vp-doc .card-grid > *, .vp-doc .feature-grid > *, .vp-doc .logo-row > span')
  if (hero.length) {
    anime({ targets: hero, opacity: [0, 1], translateY: [12, 0], easing: SPRING_SOFT, delay: anime.stagger(70) })
    anime({ targets: blocks, opacity: [0, 1], translateY: [16, 0], easing: SPRING_SOFT, delay: anime.stagger(60, { start: 180 }) })
  } else {
    const doc = document.querySelector('.vp-doc')
    if (doc) anime({ targets: doc, opacity: [0, 1], translateY: [6, 0], easing: SPRING_SOFT })
  }
}
