<template>
  <div>
    <router-link to="/locations" class="back-link">&larr; 返回地点</router-link>
    <h2 class="page-title">📍 {{ location?.city || location?.name }}</h2>
    <p v-if="location?.province" class="page-desc">{{ location.province }}{{ location.country ? ' · ' + location.country : '' }}</p>

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
import { getLocationPhotos } from '@/api/locations'
import PhotoGrid from '@/components/PhotoGrid.vue'
import Lightbox from '@/components/Lightbox.vue'

const route = useRoute()
const location = ref(null)
const photos = ref([])
const loading = ref(true)
const hasMore = ref(false)
const page = ref(1)
const lightboxVisible = ref(false)
const lightboxIndex = ref(0)

async function load() {
  loading.value = true
  try {
    const { data } = await getLocationPhotos(route.params.id, page.value)
    photos.value = page.value === 1 ? data.results : [...photos.value, ...data.results]
    hasMore.value = !!data.next
    if (page.value === 1 && data.results.length > 0) {
      location.value = {
        city: data.results[0]?.location_name || '',
        name: data.results[0]?.location_name || '',
      }
    }
  } finally {
    loading.value = false
  }
}

function loadMore() { page.value++; load() }
function openLightbox(photo) {
  lightboxIndex.value = photos.value.findIndex(p => p.id === photo.id)
  lightboxVisible.value = true
}

onMounted(() => load())
</script>

<style scoped>
.back-link { color: #3b82f6; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 12px; }
.page-title { font-size: 24px; font-weight: 700; color: #1e293b; }
.page-desc { color: #64748b; margin-top: 4px; margin-bottom: 20px; }
</style>
