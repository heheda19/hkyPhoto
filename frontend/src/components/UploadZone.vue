<template>
  <div>
    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :limit="20"
      multiple
      drag
      accept="image/*"
      :before-upload="() => false"
      :on-change="handleFileSelect"
      :file-list="fileList"
      list-type="picture-card"
      class="upload-zone"
    >
      <el-icon :size="40"><UploadFilled /></el-icon>
      <div class="upload-text">点击或拖拽照片到此区域</div>
      <template #tip>
        <div class="upload-tip">支持 JPG/PNG/HEIC，单文件最大 20MB</div>
      </template>
    </el-upload>

    <div v-if="fileList.length > 0 && !uploading" class="upload-actions">
      <el-select v-model="targetAlbum" placeholder="选择相册" style="width:200px">
        <el-option v-for="a in albums" :key="a.id" :label="a.name" :value="a.id" />
      </el-select>
      <el-button type="primary" @click="startUpload" :disabled="!targetAlbum">
        上传 {{ fileList.length }} 张照片
      </el-button>
    </div>

    <div v-if="uploading" class="upload-progress">
      <el-progress :percentage="progress" :stroke-width="8" />
      <p class="progress-text">正在上传 {{ completed }}/{{ fileList.length }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getPresignedUrl, createPhoto } from '@/api/photos'
import { readExif } from '@/utils/exif'
import axios from 'axios'

const props = defineProps({
  albums: { type: Array, default: () => [] },
})
const emit = defineEmits(['uploaded'])

const uploadRef = ref(null)
const fileList = ref([])
const targetAlbum = ref('')
const uploading = ref(false)
const progress = ref(0)
const completed = ref(0)

function handleFileSelect(file) {
  if (file.size > 20 * 1024 * 1024) {
    ElMessage.error(`${file.name} 超过 20MB 限制`)
    return
  }
  fileList.value.push(file)
}

async function startUpload() {
  if (!targetAlbum.value) return
  uploading.value = true
  completed.value = 0
  progress.value = 0
  const total = fileList.value.length

  for (let i = 0; i < fileList.value.length; i++) {
    const file = fileList.value[i].raw || fileList.value[i]
    try {
      const exifData = await readExif(file)
      const ext = file.name.split('.').pop() || 'jpg'
      const { data: presigned } = await getPresignedUrl(file.name, file.type || 'image/jpeg')

      await axios.put(presigned.upload_url, file, {
        headers: { 'Content-Type': file.type || 'image/jpeg' },
        timeout: 120000,
      })

      await createPhoto({
        album: targetAlbum.value,
        title: file.name.replace(/\.[^.]+$/, ''),
        oss_key: presigned.oss_key,
        width: 0,
        height: 0,
        file_size: file.size,
        taken_at: exifData.takenAt || null,
        latitude: exifData.latitude,
        longitude: exifData.longitude,
      })

      completed.value++
      progress.value = Math.round((completed.value / total) * 100)
    } catch (e) {
      console.error(`Upload failed for ${file.name}:`, e)
      ElMessage.error(`${file.name} 上传失败`)
    }
  }

  ElMessage.success(`成功上传 ${completed.value} 张照片`)
  fileList.value = []
  uploadRef.value?.clearFiles()
  uploading.value = false
  emit('uploaded')
}
</script>

<style scoped>
.upload-zone { width: 100%; }
.upload-text { color: #64748b; font-size: 14px; margin-top: 8px; }
.upload-tip { color: #94a3b8; font-size: 12px; margin-top: 8px; }
.upload-actions { margin-top: 16px; display: flex; gap: 12px; align-items: center; }
.upload-progress { margin-top: 20px; }
.progress-text { color: #64748b; font-size: 13px; margin-top: 8px; }
</style>
