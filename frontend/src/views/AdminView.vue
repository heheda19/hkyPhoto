<template>
  <div>
    <h2 class="page-title">管理</h2>

    <div v-if="!auth.isAuthenticated" class="login-box">
      <el-card header="管理员登录" class="login-card">
        <el-form @submit.prevent="doLogin">
          <el-form-item label="用户名">
            <el-input v-model="username" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="password" type="password" show-password />
          </el-form-item>
          <el-alert v-if="loginError" :title="loginError" type="error" show-icon :closable="false" style="margin-bottom:12px" />
          <el-button type="primary" native-type="submit" :loading="loggingIn" style="width:100%">登录</el-button>
        </el-form>
      </el-card>
    </div>

    <div v-else>
      <el-tabs v-model="tab">
        <el-tab-pane label="上传照片" name="upload">
          <UploadZone :albums="albumList" @uploaded="onUploaded" />
        </el-tab-pane>
        <el-tab-pane label="新建相册" name="album">
          <el-form @submit.prevent="createAlbum" class="album-form">
            <el-form-item label="名称">
              <el-input v-model="newAlbumName" required />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="newAlbumDesc" type="textarea" />
            </el-form-item>
            <el-button type="primary" native-type="submit">创建相册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getAlbums, createAlbum as createAlbumApi } from '@/api/albums'
import { ElMessage } from 'element-plus'
import UploadZone from '@/components/UploadZone.vue'

const auth = useAuthStore()
const username = ref('')
const password = ref('')
const loggingIn = ref(false)
const loginError = ref('')
const tab = ref('upload')
const albumList = ref([])
const newAlbumName = ref('')
const newAlbumDesc = ref('')

async function doLogin() {
  loggingIn.value = true
  loginError.value = ''
  try {
    await auth.login(username.value, password.value)
    ElMessage.success('登录成功')
    loadAlbums()
  } catch (e) {
    loginError.value = e.response?.data?.error || '登录失败'
  } finally {
    loggingIn.value = false
  }
}

async function loadAlbums() {
  try {
    const { data } = await getAlbums()
    albumList.value = data.results || data
  } catch (e) { /* ignore */ }
}

async function createAlbum() {
  if (!newAlbumName.value) return
  try {
    await createAlbumApi({ name: newAlbumName.value, description: newAlbumDesc.value })
    ElMessage.success('相册创建成功')
    newAlbumName.value = ''
    newAlbumDesc.value = ''
    loadAlbums()
    tab.value = 'upload'
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

function onUploaded() { /* refresh if needed */ }

onMounted(() => {
  if (auth.isAuthenticated) loadAlbums()
})
</script>

<style scoped>
.page-title { font-size: 28px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 28px; color: #1d1d1f; }
.login-box { padding: 40px 0; }
.login-card {
  max-width: 400px; margin: 60px auto;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}
.album-form { max-width: 400px; margin-top: 12px; }
</style>
