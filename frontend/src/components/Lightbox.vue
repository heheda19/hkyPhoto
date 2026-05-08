<template>
  <Teleport to="body">
    <div v-if="visible" class="lightbox-overlay" @click.self="$emit('close')">
      <div class="lightbox-toolbar">
        <span class="lightbox-title">{{ current?.title || '' }}</span>
        <span class="lightbox-counter">{{ index + 1 }} / {{ photos.length }}</span>
        <el-button circle @click="$emit('close')" class="close-btn">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
      <div class="lightbox-body" @touchstart="onTouchStart" @touchend="onTouchEnd">
        <el-image :src="current?.thumbnail_url" fit="contain" class="lightbox-img" />
      </div>
      <button class="nav-btn prev" @click="$emit('prev')" v-if="photos.length > 1">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <button class="nav-btn next" @click="$emit('next')" v-if="photos.length > 1">
        <el-icon><ArrowRight /></el-icon>
      </button>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { Close, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  photos: { type: Array, required: true },
  index: { type: Number, default: 0 },
})
const emit = defineEmits(['close', 'prev', 'next'])

const current = computed(() => props.photos[props.index] || null)

let touchStartX = 0
function onTouchStart(e) { touchStartX = e.touches[0].clientX }
function onTouchEnd(e) {
  const diff = touchStartX - e.changedTouches[0].clientX
  if (Math.abs(diff) > 60) {
    diff > 0 ? emit('next') : emit('prev')
  }
}
</script>

<style scoped>
.lightbox-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.96);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.lightbox-toolbar {
  position: absolute; top: 0; left: 0; right: 0;
  padding: 12px 16px; display: flex; align-items: center; gap: 12px; color: #fff;
  background: linear-gradient(rgba(0,0,0,0.6), transparent);
  z-index: 10;
}
.lightbox-title { flex: 1; font-size: 15px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lightbox-counter { font-size: 13px; color: #86868b; }
.close-btn { color: #fff; background: transparent; border-color: rgba(255,255,255,0.2); }
.close-btn:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.3); }
.lightbox-body { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; padding: 60px 48px; }
.lightbox-img { max-width: 100%; max-height: 100%; }
.nav-btn {
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 20px;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.nav-btn:hover { background: rgba(255,255,255,0.2); }
.nav-btn.prev { left: 12px; }
.nav-btn.next { right: 12px; }
@media (max-width: 640px) {
  .lightbox-body { padding: 50px 12px; }
  .nav-btn { width: 36px; height: 36px; }
}
</style>
