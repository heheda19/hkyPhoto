<template>
  <div>
    <h2 class="page-title">地点</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="locations.length === 0" class="empty-state">
      <p>还没有地点信息，上传含 GPS 信息的照片将自动生成</p>
    </div>
    <div v-else class="location-grid">
      <LocationCard v-for="loc in locations" :key="loc.id" :location="loc" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLocations } from '@/api/locations'
import LocationCard from '@/components/LocationCard.vue'

const locations = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await getLocations()
    locations.value = data.results || data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-title { font-size: 28px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 28px; color: #1d1d1f; }
.location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}
.loading, .empty-state { text-align: center; padding: 80px 20px; color: #94a3b8; }
</style>
