<template>
  <div v-if="photos.length === 0 && !loading" class="empty-state">
    <p>暂无照片</p>
  </div>
  <div v-else class="photo-grid">
    <PhotoCard
      v-for="photo in photos"
      :key="photo.id"
      :photo="photo"
      @click="$emit('photo-click', photo)"
    />
  </div>
  <div v-if="loading" class="loading-more">
    <el-icon class="is-loading"><Loading /></el-icon>
  </div>
  <div v-if="hasMore && !loading" class="load-more" @click="$emit('load-more')">
    <el-button text>加载更多</el-button>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'
import PhotoCard from './PhotoCard.vue'

defineProps({
  photos: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  hasMore: { type: Boolean, default: false },
})
defineEmits(['photo-click', 'load-more'])
</script>

<style scoped>
.photo-grid {
  columns: 4;
  column-gap: 12px;
}
@media (max-width: 1024px) { .photo-grid { columns: 3; } }
@media (max-width: 768px) { .photo-grid { columns: 2; } }
@media (max-width: 480px) { .photo-grid { columns: 2; column-gap: 8px; } }
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
  font-size: 16px;
}
.loading-more, .load-more {
  text-align: center;
  padding: 24px;
}
.load-more .el-button { color: #60a5fa; }
</style>
