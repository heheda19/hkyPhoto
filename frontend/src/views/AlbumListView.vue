<template>
  <div>
    <h2 class="page-title">相册</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="albums.length === 0" class="empty-state">
      <p>还没有相册</p>
    </div>
    <div v-else class="album-grid">
      <AlbumCard v-for="album in albums" :key="album.id" :album="album" />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAlbumsStore } from '@/stores/albums'
import { storeToRefs } from 'pinia'
import AlbumCard from '@/components/AlbumCard.vue'

const store = useAlbumsStore()
const { albums, loading } = storeToRefs(store)

onMounted(() => { store.loadAlbums() })
</script>

<style scoped>
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 24px; color: #e2e8f0; }
.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}
.loading, .empty-state { text-align: center; padding: 80px 20px; color: #64748b; }
</style>
