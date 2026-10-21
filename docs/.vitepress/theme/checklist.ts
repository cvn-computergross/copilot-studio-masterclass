// Caselle spuntabili nei lab: ogni passo numerato (liste numerate di primo livello)
// riceve una casella; le spunte restano salvate nel browser del lettore.
// Spuntare un passo spunta anche i precedenti, togliere la spunta la toglie ai successivi.
import { reactive } from 'vue'
import { popCheckbox } from './animations'

/** Stato letto dalle barre di avanzamento (AsideTools, DocProgress). */
export const progress = reactive({ total: 0, done: 0, reset: () => {} })

const LAB = /^[^/]+\/[^/]+\/\d\d-[^/]+\/index\.md$/

export function setupChecklist(path: string, relativePath: string) {
  progress.total = 0
  progress.done = 0
  progress.reset = () => {}
  if (!LAB.test(relativePath)) return

  const content = document.querySelector('.vp-doc > div')
  if (!content) return
  const key = `checklist:${path}`
  let saved: Record<number, boolean> = {}
  try { saved = JSON.parse(localStorage.getItem(key) || '{}') } catch {}

  const boxes: HTMLInputElement[] = []
  content.querySelectorAll<HTMLOListElement>(':scope > ol').forEach((ol) => {
    ol.classList.add('steps')
    const start = Number(ol.getAttribute('start') || 1)
    Array.from(ol.children).forEach((li, i) => {
      let box = li.querySelector<HTMLInputElement>(':scope > .step-check')
      if (!box) {
        box = Object.assign(document.createElement('input'), { type: 'checkbox', className: 'step-check' })
        box.setAttribute('aria-label', `Step ${start + i} completed`)
        const num = Object.assign(document.createElement('span'), { className: 'step-num', textContent: `${start + i}.` })
        li.prepend(box, num)
      }
      boxes.push(box)
    })
  })

  const save = () => {
    boxes.forEach((b, j) => (saved[j] = b.checked))
    try { localStorage.setItem(key, JSON.stringify(saved)) } catch {}
    progress.done = boxes.filter((b) => b.checked).length
  }
  boxes.forEach((box, i) => {
    box.checked = !!saved[i]
    box.onchange = () => {
      boxes.forEach((b, j) => {
        if (box.checked && j < i) b.checked = true
        if (!box.checked && j > i) b.checked = false
      })
      popCheckbox(box)
      save()
    }
  })
  progress.reset = () => {
    boxes.forEach((b) => (b.checked = false))
    saved = {}
    try { localStorage.removeItem(key) } catch {}
    progress.done = 0
  }
  progress.total = boxes.length
  progress.done = boxes.filter((b) => b.checked).length
}
