<script setup lang="ts">
// In cima alla colonna destra: il pulsante Cerca e, nei lab, la barra di avanzamento.
// Il pulsante apre la ricerca di VitePress premendo quello dell'header, che su questi
// schermi è nascosto (style.css); Ctrl+K funziona comunque.
import ProgressBar from './ProgressBar.vue'

function openSearch() {
  document.querySelector<HTMLElement>('.VPNavBarSearch .DocSearch-Button')?.click()
}
</script>

<template>
  <div class="aside-tools">
    <button type="button" class="aside-search" @click="openSearch">
      <svg viewBox="0 0 256 256" aria-hidden="true">
        <path d="M192,112a80,80,0,1,1-80-80A80,80,0,0,1,192,112Z" opacity="0.2" />
        <path d="M229.66,218.34,179.6,168.28a88.21,88.21,0,1,0-11.32,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z" />
      </svg>
      <span>Cerca</span>
      <kbd>Ctrl K</kbd>
    </button>
    <ProgressBar />
  </div>
</template>
