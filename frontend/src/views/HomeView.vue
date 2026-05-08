<template>
  <div>
    <section v-if="recentPhotos.length > 0" class="section" style="margin-top:0">
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
.section { margin-bottom: 48px; }
.section-title { font-size: 22px; font-weight: 600; letter-spacing: -0.01em; margin-bottom: 20px; color: #1d1d1f; }
.section-footer { margin-top: 20px; text-align: right; }
.see-all { color: #06c; text-decoration: none; font-size: 15px; font-weight: 500; }
.see-all:hover { text-decoration: underline; }
.album-grid, .location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
</style>
