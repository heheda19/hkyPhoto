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
  background: #1e293b;
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s;
  display: block;
}
.album-card:hover { transform: translateY(-4px); }
.album-cover {
  aspect-ratio: 4/3;
  background: #334155;
}
.album-cover .el-image { width: 100%; height: 100%; }
.album-cover-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  color: #64748b;
}
.album-info { padding: 12px 14px; }
.album-info h3 { font-size: 15px; margin-bottom: 4px; color: #e2e8f0; }
.album-info span { font-size: 12px; color: #94a3b8; }
</style>
