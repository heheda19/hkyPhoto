<template>
  <router-link :to="`/locations/${location.id}`" class="location-card">
    <div class="location-cover">
      <el-image v-if="location.cover_url" :src="location.cover_url" fit="cover" />
      <div v-else class="cover-fallback">📍</div>
    </div>
    <div class="location-info">
      <h3>{{ location.city || location.name }}</h3>
      <span>{{ location.photo_count }} 张照片</span>
    </div>
  </router-link>
</template>

<script setup>
defineProps({ location: { type: Object, required: true } })
</script>

<style scoped>
.location-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  overflow: hidden;
  text-decoration: none; color: inherit; display: block;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.location-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}
.location-cover { aspect-ratio: 16/10; background: #e2e8f0; }
.location-cover .el-image { width: 100%; height: 100%; }
.cover-fallback {
  width: 100%; height: 100%; display: flex; align-items: center;
  justify-content: center; font-size: 40px;
}
.location-info { padding: 14px 16px; }
.location-info h3 { font-size: 15px; margin-bottom: 4px; color: #1e293b; }
.location-info span { font-size: 12px; color: #94a3b8; }
</style>
