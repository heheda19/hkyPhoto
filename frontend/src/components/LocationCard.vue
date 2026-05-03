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
  background: #1e293b; border-radius: 12px; overflow: hidden;
  text-decoration: none; color: inherit; display: block;
  transition: transform 0.2s;
}
.location-card:hover { transform: translateY(-4px); }
.location-cover { aspect-ratio: 16/10; background: #334155; }
.location-cover .el-image { width: 100%; height: 100%; }
.cover-fallback {
  width: 100%; height: 100%; display: flex; align-items: center;
  justify-content: center; font-size: 40px;
}
.location-info { padding: 12px 14px; }
.location-info h3 { font-size: 15px; margin-bottom: 4px; color: #e2e8f0; }
.location-info span { font-size: 12px; color: #94a3b8; }
</style>
