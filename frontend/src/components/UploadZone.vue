<template>
  <div class="upload-zone-wrapper">
    <!-- Drag & Drop Zone (always fixed size, no file thumbnails inside) -->
    <div
      class="drop-zone"
      :class="{ 'is-dragover': dragOver }"
      @click="triggerFileInput"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/*"
        class="file-input-hidden"
        @change="onInputChange"
      />
      <el-icon :size="48" class="drop-icon"><UploadFilled /></el-icon>
      <div class="drop-text">拖拽照片到此处，或点击选择</div>
      <p class="drop-tip">支持 JPG / PNG / HEIC / WebP，单文件最大 20MB</p>
    </div>

    <!-- Selected Files Preview Grid -->
    <div v-if="fileQueue.length > 0" class="preview-section">
      <div class="preview-header">
        <span class="preview-count">已选择 {{ fileQueue.length }} 张照片</span>
        <el-button v-if="!uploading" text type="danger" size="small" @click="clearAll">清空</el-button>
      </div>
      <div class="preview-grid">
        <div
          v-for="(item, i) in fileQueue"
          :key="i"
          class="preview-card"
          :class="{ 'is-uploading': item.status === 'uploading', 'is-error': item.status === 'error', 'is-done': item.status === 'done' }"
        >
          <img :src="item.previewUrl" class="preview-img" />
          <div class="preview-info">
            <span class="preview-name">{{ item.file.name }}</span>
            <span class="preview-size">{{ formatSize(item.file.size) }}</span>
          </div>
          <!-- Status overlay -->
          <div v-if="item.status === 'uploading'" class="status-overlay">
            <el-icon class="is-loading" :size="24"><Loading /></el-icon>
          </div>
          <div v-else-if="item.status === 'done'" class="status-overlay status-success">
            <el-icon :size="24"><CircleCheckFilled /></el-icon>
          </div>
          <div v-else-if="item.status === 'error'" class="status-overlay status-error">
            <el-icon :size="24"><CircleCloseFilled /></el-icon>
          </div>
          <!-- Remove button (only before/done/error, not during upload) -->
          <button
            v-if="item.status !== 'uploading'"
            class="remove-btn"
            @click="removeFile(i)"
          >
            <el-icon :size="16"><Close /></el-icon>
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Controls -->
    <div v-if="fileQueue.length > 0 && !uploading" class="upload-bar">
      <el-select v-model="targetAlbum" placeholder="选择相册" size="large" style="width:240px">
        <el-option v-for="a in albums" :key="a.id" :label="a.name" :value="a.id" />
      </el-select>
      <el-button type="primary" size="large" @click="startUpload" :disabled="!targetAlbum">
        上传 {{ pendingCount }} 张照片
      </el-button>
    </div>

    <!-- Upload Progress Bar -->
    <div v-if="uploading" class="progress-section">
      <el-progress :percentage="progress" :stroke-width="10" :color="'#06c'" />
      <p class="progress-detail">
        {{ doneCount }} / {{ totalCount }} 已完成
        <span v-if="errorCount > 0"> · {{ errorCount }} 失败</span>
      </p>
    </div>

    <!-- Done Summary -->
    <div v-if="uploadDone" class="done-section">
      <el-result
        icon="success"
        title="上传完成"
        :sub-title="`成功 ${doneCount - errorCount} / ${totalCount} 张`"
      >
        <template #extra>
          <el-button @click="resetAll">继续上传</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled, Loading, CircleCheckFilled, CircleCloseFilled, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getPresignedUrl, createPhoto } from '@/api/photos'
import { readExif } from '@/utils/exif'
import axios from 'axios'

const props = defineProps({
  albums: { type: Array, default: () => [] },
})
const emit = defineEmits(['uploaded'])

const fileInput = ref(null)
const fileQueue = ref([])
const targetAlbum = ref('')
const uploading = ref(false)
const uploadDone = ref(false)
const dragOver = ref(false)
const progress = ref(0)

const pendingCount = computed(() => fileQueue.value.filter(f => f.status === 'pending').length)
const totalCount = computed(() => fileQueue.value.length)
const doneCount = computed(() => fileQueue.value.filter(f => f.status === 'done').length)
const errorCount = computed(() => fileQueue.value.filter(f => f.status === 'error').length)

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function triggerFileInput() {
  fileInput.value?.click()
}

function addFiles(files) {
  for (const f of files) {
    if (!f.type.startsWith('image/')) continue
    if (f.size > 20 * 1024 * 1024) {
      ElMessage.error(`${f.name} 超过 20MB 限制`)
      continue
    }
    fileQueue.value.push({
      file: f,
      previewUrl: URL.createObjectURL(f),
      status: 'pending',
    })
  }
}

function onInputChange(e) {
  addFiles(e.target.files)
  e.target.value = ''
}

function onDrop(e) {
  dragOver.value = false
  addFiles(e.dataTransfer.files)
}

function removeFile(i) {
  const item = fileQueue.value[i]
  if (item.previewUrl) URL.revokeObjectURL(item.previewUrl)
  fileQueue.value.splice(i, 1)
}

function clearAll() {
  for (const item of fileQueue.value) {
    if (item.previewUrl) URL.revokeObjectURL(item.previewUrl)
  }
  fileQueue.value = []
}

async function startUpload() {
  if (!targetAlbum.value) return
  uploading.value = true
  uploadDone.value = false
  progress.value = 0

  for (let i = 0; i < fileQueue.value.length; i++) {
    const item = fileQueue.value[i]
    if (item.status === 'done') continue
    item.status = 'uploading'

    try {
      const exifData = await readExif(item.file)
      const ext = item.file.name.split('.').pop() || 'jpg'
      const { data: presigned } = await getPresignedUrl(item.file.name, item.file.type || 'image/jpeg')

      await axios.put(presigned.upload_url, item.file, {
        headers: { 'Content-Type': item.file.type || 'image/jpeg' },
        timeout: 120000,
      })

      await createPhoto({
        album: targetAlbum.value,
        title: item.file.name.replace(/\.[^.]+$/, ''),
        oss_key: presigned.oss_key,
        width: 0,
        height: 0,
        file_size: item.file.size,
        taken_at: exifData.takenAt || null,
        latitude: exifData.latitude,
        longitude: exifData.longitude,
      })

      item.status = 'done'
    } catch (e) {
      console.error(`Upload failed for ${item.file.name}:`, e)
      item.status = 'error'
    }

    progress.value = Math.round(((i + 1) / fileQueue.value.length) * 100)
  }

  uploading.value = false
  uploadDone.value = true

  const ok = doneCount.value
  const err = errorCount.value
  if (err > 0) {
    ElMessage.warning(`上传完成：${ok} 成功，${err} 失败`)
  } else {
    ElMessage.success(`${ok} 张照片上传成功`)
  }
  emit('uploaded')
}

function resetAll() {
  clearAll()
  uploadDone.value = false
  progress.value = 0
}
</script>

<style scoped>
.upload-zone-wrapper {
  max-width: 680px;
}

/* ---- Drop Zone ---- */
.drop-zone {
  border: 2px dashed #c7c7cc;
  border-radius: 16px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  background: rgba(255, 255, 255, 0.4);
}
.drop-zone:hover,
.drop-zone.is-dragover {
  border-color: #06c;
  background: rgba(0, 102, 204, 0.04);
}
.file-input-hidden {
  display: none;
}
.drop-icon {
  color: #86868b;
}
.drop-text {
  margin-top: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #1d1d1f;
}
.drop-tip {
  margin-top: 8px;
  font-size: 13px;
  color: #86868b;
}

/* ---- Preview Section ---- */
.preview-section {
  margin-top: 24px;
}
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.preview-count {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
}
.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
}
.preview-card {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  background: #f5f5f7;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: opacity 0.2s;
}
.preview-card.is-uploading {
  opacity: 0.7;
}
.preview-card.is-error {
  border-color: #ff3b30;
}
.preview-card.is-done {
  border-color: #34c759;
}
.preview-img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}
.preview-info {
  padding: 6px 8px;
}
.preview-name {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #1d1d1f;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.preview-size {
  display: block;
  font-size: 11px;
  color: #86868b;
  margin-top: 2px;
}

/* Status overlays */
.status-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.7);
  color: #86868b;
}
.status-success {
  color: #34c759;
  background: rgba(52, 199, 89, 0.12);
}
.status-error {
  color: #ff3b30;
  background: rgba(255, 59, 48, 0.1);
}

/* Remove button */
.remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}
.preview-card:hover .remove-btn {
  opacity: 1;
}
.remove-btn:hover {
  background: rgba(0, 0, 0, 0.7);
}

/* ---- Upload Bar ---- */
.upload-bar {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  align-items: center;
}

/* ---- Progress ---- */
.progress-section {
  margin-top: 24px;
}
.progress-detail {
  margin-top: 10px;
  font-size: 14px;
  color: #86868b;
}

/* ---- Done ---- */
.done-section {
  margin-top: 32px;
}
</style>
