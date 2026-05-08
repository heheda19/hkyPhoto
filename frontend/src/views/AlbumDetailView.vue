<template>
  <div>
    <div class="page-header">
      <router-link to="/albums" class="back-link">&larr; 返回相册</router-link>
      <h2 class="page-title">{{ album?.name }}</h2>
      <p v-if="album?.description" class="page-desc">{{ album.description }}</p>
    </div>

    <div v-if="photoError" class="error-msg">{{ photoError }}</div>

    <PhotoGrid
      :photos="photos"
      :loading="loading"
      :has-more="hasMore"
      @photo-click="openLightbox"
      @load-more="loadMore"
    />

    <Lightbox
      :visible="lightboxVisible"
      :photos="photos"
      :index="lightboxIndex"
      @close="lightboxVisible = false"
      @prev="lightboxIndex = Math.max(0, lightboxIndex - 1)"
      @next="lightboxIndex = Math.min(photos.length - 1, lightboxIndex + 1)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAlbum, getAlbumPhotos } from '@/api/albums'
import PhotoGrid from '@/components/PhotoGrid.vue'
import Lightbox from '@/components/Lightbox.vue'

const route = useRoute()
const album = ref(null)
const photos = ref([])
const loading = ref(true)
const hasMore = ref(false)
const page = ref(1)
const photoError = ref('')
const lightboxVisible = ref(false)
const lightboxIndex = ref(0)

async function loadPhotos() {
  loading.value = true
  photoError.value = ''
  try {
    const { data } = await getAlbumPhotos(route.params.id, page.value)
    photos.value = page.value === 1 ? data.results : [...photos.value, ...data.results]
    hasMore.value = !!data.next
  } catch (e) {
    photoError.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}

function loadMore() { page.value++; loadPhotos() }

function openLightbox(photo) {
  lightboxIndex.value = photos.value.findIndex(p => p.id === photo.id)
  lightboxVisible.value = true
}

onMounted(async () => {
  try {
    const { data } = await getAlbum(route.params.id)
    album.value = data
  } catch (e) { /* ignore */ }
  loadPhotos()
})
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.back-link { color: #3b82f6; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #1e293b; }
.page-desc { color: #64748b; margin-top: 6px; font-size: 14px; }
.error-msg { color: #ef4444; padding: 12px 0; }
</style>
