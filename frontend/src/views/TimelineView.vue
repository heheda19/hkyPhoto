<template>
  <div>
    <h2 class="page-title">时间线</h2>

    <div v-if="loading && photos.length === 0" class="loading">加载中...</div>

    <template v-for="group in groupedPhotos" :key="group.label">
      <div class="timeline-header">{{ group.label }}</div>
      <PhotoGrid
        :photos="group.photos"
        :loading="false"
        :has-more="false"
        @photo-click="openLightbox"
      />
    </template>

    <div v-if="hasMore" class="load-more">
      <el-button :loading="loading" @click="loadMore">加载更多</el-button>
    </div>

    <Lightbox
      :visible="lightboxVisible"
      :photos="allPhotos"
      :index="lightboxIndex"
      @close="lightboxVisible = false"
      @prev="lightboxIndex = Math.max(0, lightboxIndex - 1)"
      @next="lightboxIndex = Math.min(allPhotos.length - 1, lightboxIndex + 1)"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTimelinePhotos } from '@/api/photos'
import PhotoGrid from '@/components/PhotoGrid.vue'
import Lightbox from '@/components/Lightbox.vue'

const photos = ref([])
const loading = ref(false)
const hasMore = ref(false)
const page = ref(1)
const lightboxVisible = ref(false)
const lightboxIndex = ref(0)

const allPhotos = computed(() => photos.value)

const groupedPhotos = computed(() => {
  const groups = {}
  for (const p of photos.value) {
    const d = p.taken_at ? new Date(p.taken_at) : new Date(p.uploaded_at)
    const label = `${d.getFullYear()}年 ${d.getMonth() + 1}月`
    if (!groups[label]) groups[label] = []
    groups[label].push(p)
  }
  return Object.entries(groups).map(([label, items]) => ({ label, photos: items }))
})

async function load() {
  loading.value = true
  try {
    const { data } = await getTimelinePhotos(page.value)
    photos.value = page.value === 1 ? data.results : [...photos.value, ...data.results]
    hasMore.value = !!data.next
  } finally {
    loading.value = false
  }
}

function loadMore() { page.value++; load() }

function openLightbox(photo) {
  lightboxIndex.value = allPhotos.value.findIndex(p => p.id === photo.id)
  lightboxVisible.value = true
}

onMounted(() => load())
</script>

<style scoped>
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 24px; color: #e2e8f0; }
.timeline-header {
  font-size: 16px; font-weight: 600; color: #94a3b8;
  padding: 16px 0 12px; border-top: 1px solid #1e293b;
  margin-top: 8px;
}
.loading, .load-more { text-align: center; padding: 32px; }
</style>
