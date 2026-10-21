<script setup lang="ts">
// Nell'header, subito dopo il nome del corso: "· Advanced · Standard Harness · Lab 01", calcolato dal
// percorso della pagina (livello, sezione, numero della cartella NN-nome).
import { computed } from 'vue'
import { useData } from 'vitepress'

const { page, theme } = useData()

const parts = computed(() => {
  const [level, section, lab] = page.value.relativePath.split('/')
  const levelLabel = (theme.value.levels ?? {})[level]
  if (!levelLabel) return []
  const sectionLabel = (theme.value.sections ?? {})[section]
  if (!sectionLabel) return [levelLabel]
  if (!lab?.match(/^\d\d-/)) return [levelLabel, sectionLabel]
  // il codice del lab dal titolo ("Lab S02 - ..." -> "Lab S02"), altrimenti dal numero della cartella
  const code = page.value.title.match(/^Lab (S?\d+)/)?.[1] ?? lab.slice(0, 2)
  return [levelLabel, sectionLabel, `Lab ${code}`]
})
</script>

<template>
  <span v-if="parts.length" class="header-path">
    <template v-for="part in parts" :key="part">
      <span class="header-path__sep" aria-hidden="true">·</span>
      <span class="header-path__part">{{ part }}</span>
    </template>
  </span>
</template>
