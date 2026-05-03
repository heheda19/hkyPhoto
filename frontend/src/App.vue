<template>
  <div class="app">
    <AppHeader />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import AppHeader from '@/components/AppHeader.vue'
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0f172a; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.app { min-height: 100vh; display: flex; flex-direction: column; }
.main-content { flex: 1; max-width: 1200px; width: 100%; margin: 0 auto; padding: 24px 16px; }
</style>
