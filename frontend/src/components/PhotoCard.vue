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
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  background: #1e293b;
  transition: transform 0.2s;
}
.photo-card:hover { transform: scale(1.02); }
.photo-image {
  width: 100%;
  display: block;
}
.photo-placeholder {
  aspect-ratio: 4/3;
  background: #1e293b;
}
.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px 10px;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 12px;
}
.photo-card:hover .photo-overlay { opacity: 1; }
.photo-title { color: #fff; display: block; }
.photo-location { color: #94a3b8; font-size: 11px; }
</style>
