<script setup lang="ts">
// Barra di avanzamento dei passi di un lab, con il pulsante per ricominciare.
import { ref, watch, onMounted } from 'vue'
import { progress } from '../checklist'
import { animateProgress } from '../animations'

const fill = ref<HTMLElement>()
const update = () => {
  if (fill.value) animateProgress(fill.value, progress.total ? progress.done / progress.total : 0)
}
onMounted(update)
watch(() => [progress.done, progress.total], update)
</script>

<template>
  <div v-if="progress.total" class="progress">
    <span class="progress-label">{{ progress.done }} / {{ progress.total }} completed</span>
    <button type="button" class="progress-reset" @click="progress.reset()">Reset</button>
    <div class="progress-track"><div ref="fill" class="progress-fill" /></div>
  </div>
</template>
