<template>
  <router-link :to="`/albums/${album.id}`" class="album-card">
    <div class="album-cover">
      <el-image v-if="album.cover_url" :src="album.cover_url" fit="cover" />
      <div v-else class="album-cover-placeholder">
        <el-icon :size="32"><Picture /></el-icon>
      </div>
    </div>
    <div class="album-info">
      <h3>{{ album.name }}</h3>
      <span>{{ album.photo_count }} 张照片</span>
    </div>
  </router-link>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'
defineProps({ album: { type: Object, required: true } })
</script>

<style scoped>
.album-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s, box-shadow 0.2s;
  display: block;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.album-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}
.album-cover {
  aspect-ratio: 4/3;
  background: #e2e8f0;
}
.album-cover .el-image { width: 100%; height: 100%; }
.album-cover-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  color: #94a3b8;
}
.album-info { padding: 14px 16px; }
.album-info h3 { font-size: 15px; margin-bottom: 4px; color: #1e293b; }
.album-info span { font-size: 12px; color: #94a3b8; }
</style>
