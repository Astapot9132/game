<script setup lang="ts">
import { RouterView } from 'vue-router';
import TopNav from '@/components/TopNav.vue'
</script>

<template>
  <TopNav />
  <main class="app">
  <!-- RouterView подставляет нужную страницу в зависимости от URL -->
  <RouterView />
  </main>
</template>



<style scoped>
  .app {
    padding-top: 64px;
  }
</style>