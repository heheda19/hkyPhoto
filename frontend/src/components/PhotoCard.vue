<template>
  <div class="photo-card" @click="$emit('click')">
    <el-image
      :src="photo.thumbnail_url"
      fit="cover"
      lazy
      class="photo-image"
    >
      <template #placeholder>
        <div class="photo-placeholder" />
      </template>
    </el-image>
    <div class="photo-overlay">
      <span v-if="photo.title" class="photo-title">{{ photo.title }}</span>
      <span v-if="photo.location_name" class="photo-location">{{ photo.location_name }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ photo: { type: Object, required: true } })
defineEmits(['click'])
</script>

<style scoped>
.photo-card {
  break-inside: avoid;
  margin-bottom: 12px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}
.photo-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.photo-image {
  width: 100%;
  display: block;
}
.photo-placeholder {
  aspect-ratio: 4/3;
  background: #e2e8f0;
}
.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px 10px;
  background: linear-gradient(transparent, rgba(0,0,0,0.5));
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 12px;
}
.photo-card:hover .photo-overlay { opacity: 1; }
.photo-title { color: #fff; display: block; }
.photo-location { color: rgba(255,255,255,0.7); font-size: 11px; }
</style>
