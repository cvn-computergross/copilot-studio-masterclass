<script setup lang="ts">
// Nell'header, subito dopo il nome del corso: "· Standard Harness · Lab 05", calcolato dal
// percorso della pagina (sezione = prima cartella, lab = numero della cartella NN-nome).
import { computed } from 'vue'
import { useData } from 'vitepress'

const { page, theme } = useData()

const parts = computed(() => {
  const [section, lab] = page.value.relativePath.split('/')
  const label = (theme.value.sections ?? {})[section]
  if (!label) return []
  const num = lab?.match(/^(\d\d)-/)
  return num ? [label, `Lab ${num[1]}`] : [label]
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
