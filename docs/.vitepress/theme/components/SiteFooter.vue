<script setup lang="ts">
// Fondo pagina: copyright a sinistra, loghi EDUlabs/CVN e Computer Gross piccoli a destra.
// Ogni logo ha la versione per il tema chiaro e quella bianca per il tema scuro: il CSS
// mostra quella giusta (così la pagina generata sul server e quella nel browser coincidono).
import { withBase } from 'vitepress'

const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="site-footer__inner">
      <span class="site-footer__copy">© {{ year }} Alessandro Lapi · Collaboration Value Next · Computer Gross · <a :href="withBase('/credits.html')">Riferimenti e licenze</a></span>
      <span class="site-footer__logos">
        <img class="only-light" :src="withBase('/brand/edulabs-cvn.png')" alt="EDUlabs · Collaboration Value Next" />
        <img class="only-dark" :src="withBase('/brand/edulabs-cvn-white.png')" alt="EDUlabs · Collaboration Value Next" />
        <span class="site-footer__sep" />
        <img class="only-light" :src="withBase('/brand/cgross.png')" alt="Computer Gross" />
        <img class="only-dark" :src="withBase('/brand/cgross-white.png')" alt="Computer Gross" />
      </span>
    </div>
  </footer>
</template>
