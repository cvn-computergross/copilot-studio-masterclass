<script setup lang="ts">
// "Scegli il percorso": in cima alla panoramica e ai lab di una harness, le due esperienze
// del corso affiancate; quella della pagina è evidenziata, l'altra porta alla sua panoramica.
// Le esperienze sono elencate in content.ts (EXPERIENCES).
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'

const { page, theme } = useData()

const experiences = computed<{ section: string; title: string; text: string }[]>(() => theme.value.experiences ?? [])
const current = computed(() => page.value.relativePath.split('/')[0])
const visible = computed(() => experiences.value.some((e) => e.section === current.value))
</script>

<template>
  <nav v-if="visible" class="experience" aria-label="Scegli il percorso">
    <p class="experience__title"><span class="experience__dot" aria-hidden="true" />Scegli il percorso</p>
    <div class="experience__options">
      <a
        v-for="e in experiences"
        :key="e.section"
        :href="withBase(`/${e.section}/`)"
        class="experience__option"
        :class="{ 'experience__option--active': e.section === current, [`f-${e.section === 'github-harness' ? 'github' : 'standard'}`]: true }"
        :aria-current="e.section === current ? 'page' : undefined"
      >
        <span class="experience__name">{{ e.title }}</span>
        <span class="experience__text">{{ e.text }}</span>
      </a>
    </div>
  </nav>
</template>
