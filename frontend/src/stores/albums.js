import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAlbums as fetchAlbums, getAlbumPhotos as fetchAlbumPhotos } from '@/api/albums'

export const useAlbumsStore = defineStore('albums', () => {
  const albums = ref([])
  const loading = ref(false)

  async function loadAlbums() {
    loading.value = true
    try {
      const { data } = await fetchAlbums()
      albums.value = data.results || data
    } finally {
      loading.value = false
    }
  }

  return { albums, loading, loadAlbums }
})
