<script setup lang="ts">
// "Choose your experience": in cima alla panoramica di una harness (non nei lab), le due harness
// dello stesso livello affiancate; quella della pagina è evidenziata, l'altra porta alla sua panoramica.
// Le esperienze sono elencate in content.ts (EXPERIENCES).
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'

const { page, theme } = useData()

const level = computed(() => page.value.relativePath.split('/')[0])
const current = computed(() => page.value.relativePath.split('/')[1])
const experiences = computed<{ section: string; title: string; text: string; soon?: boolean }[]>(() => (theme.value.experiences ?? {})[level.value] ?? [])
// solo sulla panoramica della sezione (docs/<livello>/<sezione>/index.md), non sui lab
const isOverview = computed(() => /^[^/]+\/[^/]+\/index\.md$/.test(page.value.relativePath))
const visible = computed(() => isOverview.value && experiences.value.some((e) => e.section === current.value))
</script>

<template>
  <nav v-if="visible" class="experience" aria-label="Choose your experience">
    <p class="experience__title"><span class="experience__dot" aria-hidden="true" />Choose your experience</p>
    <div class="experience__options">
      <a
        v-for="e in experiences"
        :key="e.section"
        :href="withBase(`/${level}/${e.section}/`)"
        class="experience__option"
        :class="{ 'experience__option--active': e.section === current, 'experience__option--soon': e.soon, [`f-${e.section === 'github-harness' ? 'github' : 'standard'}`]: true }"
        :aria-current="e.section === current ? 'page' : undefined"
      >
        <span class="experience__name">{{ e.title }}</span>
        <span class="experience__text">{{ e.text }}</span>
        <span v-if="e.soon" class="experience__soon">In preparazione</span>
      </a>
    </div>
  </nav>
</template>
