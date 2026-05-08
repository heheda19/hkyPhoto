<template>
  <div>
    <h2 class="page-title">MyAlbum</h2>
    <p class="page-subtitle">个人照片展示</p>

    <section v-if="recentPhotos.length > 0" class="section">
      <h3 class="section-title">最近上传</h3>
      <PhotoGrid
        :photos="recentPhotos"
        :loading="false"
        :has-more="false"
        @photo-click="openLightbox"
      />
      <div class="section-footer">
        <router-link to="/timeline" class="see-all">查看全部 &rarr;</router-link>
      </div>
    </section>

    <section v-if="albums.length > 0" class="section">
      <h3 class="section-title">相册</h3>
      <div class="album-grid">
        <AlbumCard v-for="album in albums.slice(0, 6)" :key="album.id" :album="album" />
      </div>
      <div v-if="albums.length > 6" class="section-footer">
        <router-link to="/albums" class="see-all">查看全部 &rarr;</router-link>
      </div>
    </section>

    <section v-if="locations.length > 0" class="section">
      <h3 class="section-title">地点</h3>
      <div class="location-grid">
        <LocationCard v-for="loc in locations.slice(0, 6)" :key="loc.id" :location="loc" />
      </div>
      <div v-if="locations.length > 6" class="section-footer">
        <router-link to="/locations" class="see-all">查看全部 &rarr;</router-link>
      </div>
    </section>

    <Lightbox
      :visible="lightboxVisible"
      :photos="recentPhotos"
      :index="lightboxIndex"
      @close="lightboxVisible = false"
      @prev="lightboxIndex = Math.max(0, lightboxIndex - 1)"
      @next="lightboxIndex = Math.min(recentPhotos.length - 1, lightboxIndex + 1)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTimelinePhotos } from '@/api/photos'
import { getAlbums } from '@/api/albums'
import { getLocations } from '@/api/locations'
import PhotoGrid from '@/components/PhotoGrid.vue'
import AlbumCard from '@/components/AlbumCard.vue'
import LocationCard from '@/components/LocationCard.vue'
import Lightbox from '@/components/Lightbox.vue'

const recentPhotos = ref([])
const albums = ref([])
const locations = ref([])
const lightboxVisible = ref(false)
const lightboxIndex = ref(0)

function openLightbox(photo) {
  lightboxIndex.value = recentPhotos.value.findIndex(p => p.id === photo.id)
  lightboxVisible.value = true
}

onMounted(async () => {
  try {
    const [photoRes, albumRes, locRes] = await Promise.all([
      getTimelinePhotos(1),
      getAlbums(),
      getLocations(),
    ])
    recentPhotos.value = (photoRes.data.results || photoRes.data).slice(0, 12)
    albums.value = albumRes.data.results || albumRes.data
    locations.value = locRes.data.results || locRes.data
  } catch (e) { /* ignore */ }
})
</script>

<style scoped>
.page-title { font-size: 28px; font-weight: 700; color: #1e293b; }
.page-subtitle { color: #64748b; margin-bottom: 32px; font-size: 15px; }
.section { margin-bottom: 40px; }
.section-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; border-left: 3px solid #3b82f6; padding-left: 10px; color: #1e293b; }
.section-footer { margin-top: 16px; text-align: right; }
.see-all { color: #3b82f6; text-decoration: none; font-size: 14px; }
.album-grid, .location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
</style>
