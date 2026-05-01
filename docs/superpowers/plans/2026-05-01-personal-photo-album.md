# 个人相册网站实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建一个公网部署的个人相册网站，支持手机/桌面端上传照片，按相册、时间线、地点三种维度浏览。

**Architecture:** Django + DRF 提供 REST API，Vue 3 SPA build 产物由 Nginx 直接提供，照片经 Presigned URL 直传阿里云 OSS，高德 API 做 GPS 反向地理编码。

**Tech Stack:** Django 4.x, DRF, Vue 3, Vite, Element Plus, Pinia, SQLite/PostgreSQL, 阿里云 OSS, 高德地图 API, Nginx, Gunicorn

**文件结构概览：**

```
D:\hkyPhoto\
├── backend/                    # Django 项目
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/                 # 项目配置 (settings, urls, wsgi)
│   ├── albums/                 # 相册 app
│   ├── photos/                 # 照片 app
│   ├── locations/              # 地点 app
│   └── auth_ext/               # JWT 认证
├── frontend/                   # Vue 3 项目
│   ├── src/
│   │   ├── api/                # API 请求层
│   │   ├── components/         # 通用组件
│   │   ├── views/              # 页面
│   │   ├── stores/             # Pinia 状态
│   │   ├── utils/              # EXIF / OSS 工具
│   │   └── router/index.js
│   └── public/
├── nginx/                      # Nginx 配置
├── scripts/                    # 部署脚本
├── .env.example
└── .gitignore
```

---

## Phase 1: 项目脚手架

### Task 1: Django 项目初始化

**Files:**
- Create: `D:\hkyPhoto\backend\manage.py`
- Create: `D:\hkyPhoto\backend\requirements.txt`
- Create: `D:\hkyPhoto\backend\config\__init__.py`
- Create: `D:\hkyPhoto\backend\config\settings.py`
- Create: `D:\hkyPhoto\backend\config\urls.py`
- Create: `D:\hkyPhoto\backend\config\wsgi.py`
- Create: `D:\hkyPhoto\backend\config\asgi.py`
- Create: `D:\hkyPhoto\.env.example`
- Create: `D:\hkyPhoto\.gitignore`

- [ ] **Step 1: 创建 .gitignore**

```
__pycache__/
*.py[cod]
*.sqlite3
.env
node_modules/
dist/
.vite/
*.log
.superpowers/
```

- [ ] **Step 2: 创建 .env.example**

```
SECRET_KEY=change-me-to-random-string
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
OSS_ACCESS_KEY_ID=your-oss-access-key
OSS_ACCESS_KEY_SECRET=your-oss-secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your-bucket
AMAP_API_KEY=your-amap-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
```

- [ ] **Step 3: 创建 requirements.txt**

```
Django>=4.2,<5.0
djangorestframework>=3.14
django-cors-headers>=4.0
djangorestframework-simplejwt>=5.3
Pillow>=10.0
oss2>=2.18
python-decouple>=3.8
gunicorn>=21.2
psycopg2-binary>=2.9
requests>=2.31
```

- [ ] **Step 4: 创建 backend/config/settings.py**

```python
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='dev-secret-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'albums',
    'photos',
    'locations',
    'auth_ext',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')
if DATABASE_URL.startswith('sqlite'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / DATABASE_URL.replace('sqlite:///', ''),
        }
    }
else:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = DEBUG

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 24,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# OSS 配置
OSS_ACCESS_KEY_ID = config('OSS_ACCESS_KEY_ID', default='')
OSS_ACCESS_KEY_SECRET = config('OSS_ACCESS_KEY_SECRET', default='')
OSS_ENDPOINT = config('OSS_ENDPOINT', default='oss-cn-hangzhou.aliyuncs.com')
OSS_BUCKET_NAME = config('OSS_BUCKET_NAME', default='')

# 高德地图
AMAP_API_KEY = config('AMAP_API_KEY', default='')

# 上传限制
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB
```

- [ ] **Step 5: 创建 backend/config/urls.py**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_ext.urls')),
    path('api/', include('albums.urls')),
    path('api/', include('photos.urls')),
    path('api/', include('locations.urls')),
]
```

- [ ] **Step 6: 创建 backend/config/wsgi.py**

```python
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
```

- [ ] **Step 7: 创建 backend/config/asgi.py**

```python
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
```

- [ ] **Step 8: 创建 backend/manage.py**

```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

- [ ] **Step 9: 初始化各 app 目录**

```bash
cd /d/hkyPhoto/backend
mkdir -p albums photos locations auth_ext static
touch albums/__init__.py photos/__init__.py locations/__init__.py auth_ext/__init__.py
```

- [ ] **Step 10: 安装依赖并验证**

```bash
cd /d/hkyPhoto/backend
pip install -r requirements.txt
cp ../.env.example .env
python manage.py migrate
python manage.py runserver
```

Expected: Django welcome page at http://127.0.0.1:8000/

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "feat: scaffold Django project with config and dependencies"
```

---

### Task 2: Vue 3 项目初始化

**Files:**
- Create: `D:\hkyPhoto\frontend\` (Vite scaffold)

- [ ] **Step 1: 用 Vite 创建 Vue 3 项目**

```bash
cd /d/hkyPhoto
npm create vite@latest frontend -- --template vue
cd frontend
npm install
```

- [ ] **Step 2: 安装依赖**

```bash
cd /d/hkyPhoto/frontend
npm install vue-router@4 pinia axios element-plus @element-plus/icons-vue exif-js
npm install -D @vitejs/plugin-pwa vite-plugin-pwa
```

- [ ] **Step 3: 配置 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/*.png'],
      manifest: {
        name: 'MyAlbum - 个人相册',
        short_name: 'MyAlbum',
        description: '个人照片展示',
        theme_color: '#1e293b',
        background_color: '#0f172a',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/.*\.oss-.*\.aliyuncs\.com\/.*/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'oss-images',
              expiration: { maxEntries: 200, maxAgeSeconds: 7 * 24 * 60 * 60 },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
```

- [ ] **Step 4: 创建 src 目录结构**

```bash
cd /d/hkyPhoto/frontend/src
mkdir -p api components views stores utils router
rm -rf assets components/HelloWorld.vue style.css
```

- [ ] **Step 5: 创建 src/main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { size: 'default' })

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

- [ ] **Step 6: 创建 src/App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 7: 创建 router/index.js（骨架）**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/albums', name: 'albums', component: () => import('@/views/AlbumListView.vue') },
  { path: '/albums/:id', name: 'album-detail', component: () => import('@/views/AlbumDetailView.vue') },
  { path: '/timeline', name: 'timeline', component: () => import('@/views/TimelineView.vue') },
  { path: '/locations', name: 'locations', component: () => import('@/views/LocationListView.vue') },
  { path: '/locations/:id', name: 'location-detail', component: () => import('@/views/LocationDetailView.vue') },
  { path: '/admin', name: 'admin', component: () => import('@/views/AdminView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

- [ ] **Step 8: 创建所有 views 占位文件**

```bash
cd /d/hkyPhoto/frontend/src/views
for f in HomeView AlbumListView AlbumDetailView TimelineView LocationListView LocationDetailView AdminView; do
  echo "<template><div>$f</div></template>" > "${f}.vue"
done
```

- [ ] **Step 9: 验证开发服务器**

```bash
cd /d/hkyPhoto/frontend
npm run dev
```

Expected: Vue dev server running, accessible in browser.

- [ ] **Step 10: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Vue 3 project with router, pinia, element-plus"
```

---

## Phase 2: 后端 Model & API

### Task 3: Album Model + Admin + API

**Files:**
- Create: `D:\hkyPhoto\backend\albums\models.py`
- Create: `D:\hkyPhoto\backend\albums\admin.py`
- Create: `D:\hkyPhoto\backend\albums\serializers.py`
- Create: `D:\hkyPhoto\backend\albums\views.py`
- Create: `D:\hkyPhoto\backend\albums\urls.py`

- [ ] **Step 1: 创建 Album model**

```python
# backend/albums/models.py
import uuid
from django.db import models

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    cover = models.ForeignKey('photos.Photo', on_delete=models.SET_NULL, null=True, blank=True, related_name='cover_of')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name

    @property
    def photo_count(self):
        return self.photos.count()
```

- [ ] **Step 2: 创建 Album admin**

```python
# backend/albums/admin.py
from django.contrib import admin
from .models import Album

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'created_at']
    search_fields = ['name']
```

- [ ] **Step 3: 创建 Album serializer**

```python
# backend/albums/serializers.py
from rest_framework import serializers
from .models import Album

class AlbumListSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ['id', 'name', 'description', 'cover_url', 'photo_count', 'sort_order', 'created_at', 'updated_at']

    def get_cover_url(self, obj):
        if obj.cover:
            return obj.cover.thumbnail_url
        first = obj.photos.first()
        return first.thumbnail_url if first else None

class AlbumDetailSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'name', 'description', 'photo_count', 'sort_order', 'created_at', 'updated_at']

class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['name', 'description', 'sort_order']
```

- [ ] **Step 4: 创建 Album views**

```python
# backend/albums/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .models import Album
from .serializers import AlbumListSerializer, AlbumDetailSerializer, AlbumCreateSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'list':
            return AlbumListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return AlbumCreateSerializer
        return AlbumDetailSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['get'])
    def photos(self, request, id=None):
        album = self.get_object()
        from photos.serializers import PhotoListSerializer
        photos = album.photos.all().order_by('-taken_at', '-uploaded_at')
        page = self.paginate_queryset(photos)
        if page is not None:
            return self.get_paginated_response(PhotoListSerializer(page, many=True).data)
        return Response(PhotoListSerializer(photos, many=True).data)
```

- [ ] **Step 5: 创建 Album urls**

```python
# backend/albums/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlbumViewSet

router = DefaultRouter()
router.register('albums', AlbumViewSet, basename='album')

urlpatterns = [
    path('', include(router.urls)),
]
```

- [ ] **Step 6: Makemigrations & migrate**

```bash
cd /d/hkyPhoto/backend
python manage.py makemigrations albums
python manage.py migrate
```

Expected: `albums_album` table created.

- [ ] **Step 7: Commit**

```bash
git add backend/albums/
git commit -m "feat: add Album model with admin, serializers, and API"
```

---

### Task 4: Location Model + Admin

**Files:**
- Create: `D:\hkyPhoto\backend\locations\models.py`
- Create: `D:\hkyPhoto\backend\locations\admin.py`

- [ ] **Step 1: 创建 Location model**

```python
# backend/locations/models.py
import uuid
from django.db import models

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=100, blank=True, default='')
    province = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['country', 'province', 'city']

    def __str__(self):
        return self.name

    @property
    def photo_count(self):
        return self.photos.count()
```

- [ ] **Step 2: 创建 Location admin**

```python
# backend/locations/admin.py
from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'province', 'country']
    search_fields = ['name', 'city']
```

- [ ] **Step 3: Makemigrations & migrate**

```bash
cd /d/hkyPhoto/backend
python manage.py makemigrations locations
python manage.py migrate
```

- [ ] **Step 4: Commit**

```bash
git add backend/locations/
git commit -m "feat: add Location model and admin"
```

---

### Task 5: Photo Model + Admin

**Files:**
- Create: `D:\hkyPhoto\backend\photos\models.py`
- Create: `D:\hkyPhoto\backend\photos\admin.py`
- Create: `D:\hkyPhoto\backend\photos\utils.py`

- [ ] **Step 1: 创建 OSS 工具函数**

```python
# backend/photos/utils.py
import oss2
from django.conf import settings

def get_oss_bucket():
    auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
    return oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)

def generate_presigned_url(oss_key, expires=60, process=None):
    bucket = get_oss_bucket()
    params = {}
    if process:
        params['x-oss-process'] = process
    return bucket.sign_url('GET', oss_key, expires, params=params)

def get_thumbnail_url(oss_key, size=400):
    return generate_presigned_url(oss_key, process=f'image/resize,w_{size}')
```

- [ ] **Step 2: 创建 Photo model**

```python
# backend/photos/models.py
import uuid
from django.db import models
from .utils import get_thumbnail_url

class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey('albums.Album', on_delete=models.CASCADE, related_name='photos')
    title = models.CharField(max_length=200, blank=True, default='')
    oss_key = models.CharField(max_length=500)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    taken_at = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_at', '-uploaded_at']

    def __str__(self):
        return self.title or f'Photo {self.id}'

    @property
    def thumbnail_url(self):
        return get_thumbnail_url(self.oss_key, 400)

    @property
    def full_url(self):
        from .utils import generate_presigned_url
        return generate_presigned_url(self.oss_key, 3600)
```

- [ ] **Step 3: 创建 Photo admin**

```python
# backend/photos/admin.py
from django.contrib import admin
from .models import Photo

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'taken_at', 'uploaded_at']
    list_filter = ['album', 'location']
    search_fields = ['title']
```

- [ ] **Step 4: 更新 Album model 的 cover 字段**

由于 Album 引用了 Photo，需要确保 Album 的 cover 字段与 Photo FK 兼容。此时 `albums/models.py` 中的 `cover = models.ForeignKey('photos.Photo', ...)` 已经是指向 `photos.Photo` 的字符串引用，无需修改。

- [ ] **Step 5: Makemigrations & migrate**

```bash
cd /d/hkyPhoto/backend
python manage.py makemigrations photos
python manage.py migrate
```

- [ ] **Step 6: Commit**

```bash
git add backend/photos/
git commit -m "feat: add Photo model with OSS utility helpers"
```

---

### Task 6: JWT 认证

**Files:**
- Create: `D:\hkyPhoto\backend\auth_ext\views.py`
- Create: `D:\hkyPhoto\backend\auth_ext\urls.py`
- Create: `D:\hkyPhoto\backend\auth_ext\serializers.py`

- [ ] **Step 1: 创建 serializer**

```python
# backend/auth_ext/serializers.py
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
```

- [ ] **Step 2: 创建 login view**

```python
# backend/auth_ext/views.py
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password'],
    )
    if user is None:
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })
```

- [ ] **Step 3: 创建 urls**

```python
# backend/auth_ext/urls.py
from django.urls import path
from .views import login_view

urlpatterns = [
    path('login/', login_view, name='auth-login'),
]
```

- [ ] **Step 4: 创建初始管理员用户**

```bash
cd /d/hkyPhoto/backend
python manage.py createsuperuser --username admin --email admin@example.com
```

- [ ] **Step 5: 验证登录 API**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

Expected: `{"access":"...", "refresh":"..."}`

- [ ] **Step 6: Commit**

```bash
git add backend/auth_ext/
git commit -m "feat: add JWT login endpoint"
```

---

### Task 7: OSS Presigned URL 上传端点

**Files:**
- Create: `D:\hkyPhoto\backend\photos\views.py` (上传相关部分)
- Create: `D:\hkyPhoto\backend\photos\urls.py`
- Create: `D:\hkyPhoto\backend\photos\serializers.py`

- [ ] **Step 1: 创建 photo serializers**

```python
# backend/photos/serializers.py
from rest_framework import serializers
from .models import Photo

class PhotoListSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.URLField(read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, default=None)

    class Meta:
        model = Photo
        fields = ['id', 'album', 'title', 'thumbnail_url', 'width', 'height',
                  'taken_at', 'location_name', 'latitude', 'longitude', 'uploaded_at']

class PhotoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'album', 'title', 'oss_key', 'width', 'height',
                  'file_size', 'taken_at', 'latitude', 'longitude']

class PresignedUrlSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=500)
    content_type = serializers.CharField(default='image/jpeg')
```

- [ ] **Step 2: 创建 PhotoViewSet（含 presigned URL 和 create）**

```python
# backend/photos/views.py
import uuid
from datetime import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Photo
from .serializers import PhotoListSerializer, PhotoCreateSerializer, PresignedUrlSerializer
from .utils import get_oss_bucket, generate_presigned_url

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all().select_related('album', 'location')
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ('create',):
            return PhotoCreateSerializer
        return PhotoListSerializer

    def get_permissions(self):
        if self.action in ('create', 'destroy', 'presigned_url'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 支持 ?album_id=xxx 和 ?location_id=xxx 过滤
        album_id = request.query_params.get('album_id')
        location_id = request.query_params.get('location_id')
        if album_id:
            queryset = queryset.filter(album_id=album_id)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        # 默认时间线排序
        ordering = request.query_params.get('ordering', '-taken_at')
        queryset = queryset.order_by(ordering)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(PhotoListSerializer(page, many=True).data)
        return Response(PhotoListSerializer(queryset, many=True).data)

    @action(detail=False, methods=['post'])
    def presigned_url(self, request):
        serializer = PresignedUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filename = serializer.validated_data['filename']
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'jpg'
        oss_key = f"photos/{datetime.now().strftime('%Y/%m')}/{uuid.uuid4().hex}.{ext}"
        bucket = get_oss_bucket()
        url = bucket.sign_url('PUT', oss_key, 300, headers={'Content-Type': serializer.validated_data['content_type']})
        return Response({'oss_key': oss_key, 'upload_url': url})

    def perform_create(self, serializer):
        photo = serializer.save()
        # 如果有经纬度，调用高德反向地理编码
        if photo.latitude and photo.longitude:
            self._assign_location(photo)

    def _assign_location(self, photo):
        import requests
        from locations.models import Location
        try:
            resp = requests.get('https://restapi.amap.com/v3/geocode/regeo', params={
                'key': settings.AMAP_API_KEY,
                'location': f'{photo.longitude},{photo.latitude}',
                'extensions': 'base',
            }, timeout=5)
            data = resp.json()
            if data['status'] == '1' and data['regeocode']:
                addr = data['regeocode']['addressComponent']
                city = addr.get('city', '') or addr.get('province', '')
                province = addr.get('province', '')
                country = addr.get('country', '')
                name_parts = [country, province, city]
                name = ''.join(p for p in name_parts if p) or '未知地点'

                location, _ = Location.objects.get_or_create(
                    name=name,
                    defaults={
                        'latitude': photo.latitude,
                        'longitude': photo.longitude,
                        'city': city,
                        'province': province,
                        'country': country,
                    }
                )
                photo.location = location
                photo.save(update_fields=['location'])
        except Exception:
            pass
```

- [ ] **Step 3: 创建 photos urls**

```python
# backend/photos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PhotoViewSet

router = DefaultRouter()
router.register('photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
]
```

- [ ] **Step 4: Commit**

```bash
git add backend/photos/
git commit -m "feat: add OSS presigned URL endpoint and photo upload API with geocoding"
```

---

### Task 8: Location API

**Files:**
- Create: `D:\hkyPhoto\backend\locations\serializers.py`
- Create: `D:\hkyPhoto\backend\locations\views.py`
- Create: `D:\hkyPhoto\backend\locations\urls.py`

- [ ] **Step 1: 创建 Location serializer**

```python
# backend/locations/serializers.py
from rest_framework import serializers
from .models import Location

class LocationListSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(read_only=True)
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'province', 'country', 'photo_count', 'cover_url']

    def get_cover_url(self, obj):
        first = obj.photos.first()
        return first.thumbnail_url if first else None

class LocationDetailSerializer(serializers.ModelSerializer):
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'province', 'country', 'photo_count', 'latitude', 'longitude']
```

- [ ] **Step 2: 创建 Location views**

```python
# backend/locations/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Location
from .serializers import LocationListSerializer, LocationDetailSerializer
from photos.serializers import PhotoListSerializer

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'list':
            return LocationListSerializer
        return LocationDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return sorted(qs, key=lambda loc: loc.photo_count, reverse=True)

    @action(detail=True, methods=['get'])
    def photos(self, request, id=None):
        location = self.get_object()
        photos = location.photos.all().order_by('-taken_at', '-uploaded_at')
        page = self.paginate_queryset(photos)
        if page is not None:
            return self.get_paginated_response(PhotoListSerializer(page, many=True).data)
        return Response(PhotoListSerializer(photos, many=True).data)
```

- [ ] **Step 3: 创建 Location urls**

```python
# backend/locations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet

router = DefaultRouter()
router.register('locations', LocationViewSet, basename='location')

urlpatterns = [
    path('', include(router.urls)),
]
```

- [ ] **Step 4: Commit**

```bash
git add backend/locations/
git commit -m "feat: add Location list/detail API with photo count"
```

---

## Phase 3: 前端实现

### Task 9: API 客户端层 + Pinia Stores

**Files:**
- Create: `D:\hkyPhoto\frontend\src\api\index.js`
- Create: `D:\hkyPhoto\frontend\src\api\albums.js`
- Create: `D:\hkyPhoto\frontend\src\api\photos.js`
- Create: `D:\hkyPhoto\frontend\src\api\locations.js`
- Create: `D:\hkyPhoto\frontend\src\api\auth.js`
- Create: `D:\hkyPhoto\frontend\src\stores\auth.js`
- Create: `D:\hkyPhoto\frontend\src\stores\albums.js`

- [ ] **Step 1: 创建 axios 实例**

```javascript
// frontend/src/api/index.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
    }
    return Promise.reject(err)
  }
)

export default api
```

- [ ] **Step 2: 创建 auth API**

```javascript
// frontend/src/api/auth.js
import api from './index'

export function login(username, password) {
  return api.post('/auth/login/', { username, password })
}
```

- [ ] **Step 3: 创建 albums API**

```javascript
// frontend/src/api/albums.js
import api from './index'

export function getAlbums() {
  return api.get('/albums/')
}

export function getAlbum(id) {
  return api.get(`/albums/${id}/`)
}

export function getAlbumPhotos(id, page = 1) {
  return api.get(`/albums/${id}/photos/`, { params: { page } })
}

export function createAlbum(data) {
  return api.post('/albums/', data)
}

export function updateAlbum(id, data) {
  return api.patch(`/albums/${id}/`, data)
}

export function deleteAlbum(id) {
  return api.delete(`/albums/${id}/`)
}
```

- [ ] **Step 4: 创建 photos API**

```javascript
// frontend/src/api/photos.js
import api from './index'

export function getPhotos(params = {}) {
  return api.get('/photos/', { params })
}

export function getTimelinePhotos(page = 1) {
  return api.get('/photos/', { params: { ordering: '-taken_at', page } })
}

export function getPresignedUrl(filename, contentType) {
  return api.post('/photos/presigned_url/', { filename, content_type: contentType })
}

export function createPhoto(data) {
  return api.post('/photos/', data)
}

export function deletePhoto(id) {
  return api.delete(`/photos/${id}/`)
}
```

- [ ] **Step 5: 创建 locations API**

```javascript
// frontend/src/api/locations.js
import api from './index'

export function getLocations() {
  return api.get('/locations/')
}

export function getLocationPhotos(id, page = 1) {
  return api.get(`/locations/${id}/photos/`, { params: { page } })
}
```

- [ ] **Step 6: 创建 auth store**

```javascript
// frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    const { data } = await loginApi(username, password)
    token.value = data.access
    localStorage.setItem('token', data.access)
  }

  function logout() {
    token.value = ''
    localStorage.removeItem('token')
  }

  return { token, isAuthenticated, login, logout }
})
```

- [ ] **Step 7: 创建 albums store**

```javascript
// frontend/src/stores/albums.js
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
```

- [ ] **Step 8: Commit**

```bash
git add frontend/src/api/ frontend/src/stores/
git commit -m "feat: add API client layer and Pinia auth/albums stores"
```

---

### Task 10: 布局组件 (AppHeader + RouterView)

**Files:**
- Create: `D:\hkyPhoto\frontend\src\components\AppHeader.vue`

- [ ] **Step 1: 创建 AppHeader**

```vue
<!-- frontend/src/components/AppHeader.vue -->
<template>
  <el-header class="app-header">
    <div class="header-inner">
      <router-link to="/" class="logo">📷 MyAlbum</router-link>
      <nav class="nav-links">
        <router-link to="/albums">相册</router-link>
        <router-link to="/timeline">时间线</router-link>
        <router-link to="/locations">地点</router-link>
        <router-link to="/admin">管理</router-link>
      </nav>
    </div>
  </el-header>
</template>

<style scoped>
.app-header {
  background: #1e293b;
  border-bottom: 1px solid #334155;
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
}
.logo {
  color: #e2e8f0;
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
}
.nav-links {
  display: flex;
  gap: 4px;
}
.nav-links a {
  color: #94a3b8;
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
}
.nav-links a:hover,
.nav-links a.router-link-exact-active {
  color: #e2e8f0;
  background: #334155;
}
@media (max-width: 640px) {
  .logo { font-size: 16px; }
  .nav-links a { padding: 6px 10px; font-size: 12px; }
}
</style>
```

- [ ] **Step 2: 更新 App.vue**

```vue
<!-- frontend/src/App.vue -->
<template>
  <div class="app">
    <AppHeader />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import AppHeader from '@/components/AppHeader.vue'
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0f172a; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.app { min-height: 100vh; display: flex; flex-direction: column; }
.main-content { flex: 1; max-width: 1200px; width: 100%; margin: 0 auto; padding: 24px 16px; }
</style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/AppHeader.vue frontend/src/App.vue
git commit -m "feat: add AppHeader navigation and app layout"
```

---

### Task 11: PhotoCard + PhotoGrid 组件

**Files:**
- Create: `D:\hkyPhoto\frontend\src\components\PhotoCard.vue`
- Create: `D:\hkyPhoto\frontend\src\components\PhotoGrid.vue`

- [ ] **Step 1: 创建 PhotoCard**

```vue
<!-- frontend/src/components/PhotoCard.vue -->
<template>
  <div class="photo-card" @click="$emit('click')">
    <el-image
      :src="photo.thumbnail_url"
      fit="cover"
      lazy
      class="photo-image"
    >
      <template #placeholder>
        <div class="photo-placeholder" />
      </template>
    </el-image>
    <div class="photo-overlay">
      <span v-if="photo.title" class="photo-title">{{ photo.title }}</span>
      <span v-if="photo.location_name" class="photo-location">{{ photo.location_name }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ photo: { type: Object, required: true } })
defineEmits(['click'])
</script>

<style scoped>
.photo-card {
  break-inside: avoid;
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  background: #1e293b;
  transition: transform 0.2s;
}
.photo-card:hover { transform: scale(1.02); }
.photo-image {
  width: 100%;
  display: block;
}
.photo-placeholder {
  aspect-ratio: 4/3;
  background: #1e293b;
}
.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px 10px;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 12px;
}
.photo-card:hover .photo-overlay { opacity: 1; }
.photo-title { color: #fff; display: block; }
.photo-location { color: #94a3b8; font-size: 11px; }
</style>
```

- [ ] **Step 2: 创建 PhotoGrid**

```vue
<!-- frontend/src/components/PhotoGrid.vue -->
<template>
  <div v-if="photos.length === 0 && !loading" class="empty-state">
    <p>暂无照片</p>
  </div>
  <div v-else class="photo-grid">
    <PhotoCard
      v-for="photo in photos"
      :key="photo.id"
      :photo="photo"
      @click="$emit('photo-click', photo)"
    />
  </div>
  <div v-if="loading" class="loading-more">
    <el-icon class="is-loading"><Loading /></el-icon>
  </div>
  <div v-if="hasMore && !loading" class="load-more" @click="$emit('load-more')">
    <el-button text>加载更多</el-button>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'
import PhotoCard from './PhotoCard.vue'

defineProps({
  photos: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  hasMore: { type: Boolean, default: false },
})
defineEmits(['photo-click', 'load-more'])
</script>

<style scoped>
.photo-grid {
  columns: 4;
  column-gap: 12px;
}
@media (max-width: 1024px) { .photo-grid { columns: 3; } }
@media (max-width: 768px) { .photo-grid { columns: 2; } }
@media (max-width: 480px) { .photo-grid { columns: 2; column-gap: 8px; } }
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
  font-size: 16px;
}
.loading-more, .load-more {
  text-align: center;
  padding: 24px;
}
.load-more .el-button { color: #60a5fa; }
</style>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/PhotoCard.vue frontend/src/components/PhotoGrid.vue
git commit -m "feat: add PhotoCard and PhotoGrid components"
```

---

### Task 12: Lightbox 组件

**Files:**
- Create: `D:\hkyPhoto\frontend\src\components\Lightbox.vue`

- [ ] **Step 1: 创建 Lightbox**

```vue
<!-- frontend/src/components/Lightbox.vue -->
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
import { ref } from 'vue'
import { Close, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  photos: { type: Array, required: true },
  index: { type: Number, default: 0 },
})
defineEmits(['close', 'prev', 'next'])

const current = computed(() => props.photos[props.index] || null)

let touchStart = 0
function onTouchStart(e) { touchStart = e.touches[0].clientX }
function onTouchEnd(e) {
  const diff = touchStart - e.changedTouches[0].clientX
  if (Math.abs(diff) > 60) {
    diff > 0 ? $emit('next') : $emit('prev')
  }
}
</script>

<style scoped>
.lightbox-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.95);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.lightbox-toolbar {
  position: absolute; top: 0; left: 0; right: 0;
  padding: 12px 16px; display: flex; align-items: center; gap: 12px; color: #fff;
  background: linear-gradient(rgba(0,0,0,0.6), transparent);
}
.lightbox-title { flex: 1; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lightbox-counter { font-size: 13px; color: #94a3b8; }
.close-btn { color: #fff; background: transparent; border-color: #475569; }
.lightbox-body { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; padding: 60px 48px; }
.lightbox-img { max-width: 100%; max-height: 100%; }
.nav-btn {
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(255,255,255,0.1); border: none; color: #fff;
  width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 20px;
  display: flex; align-items: center; justify-content: center;
}
.nav-btn:hover { background: rgba(255,255,255,0.2); }
.nav-btn.prev { left: 12px; }
.nav-btn.next { right: 12px; }
@media (max-width: 640px) {
  .lightbox-body { padding: 50px 12px; }
  .nav-btn { width: 36px; height: 36px; }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/Lightbox.vue
git commit -m "feat: add Lightbox component with touch swipe support"
```

---

### Task 13: AlbumCard + AlbumListView

**Files:**
- Create: `D:\hkyPhoto\frontend\src\components\AlbumCard.vue`
- Update: `D:\hkyPhoto\frontend\src\views\AlbumListView.vue`

- [ ] **Step 1: 创建 AlbumCard**

```vue
<!-- frontend/src/components/AlbumCard.vue -->
<template>
  <router-link :to="`/albums/${album.id}`" class="album-card">
    <div class="album-cover">
      <el-image v-if="album.cover_url" :src="album.cover_url" fit="cover" />
      <div v-else class="album-cover-placeholder">
        <el-icon :size="32"><Picture /></el-icon>
      </div>
    </div>
    <div class="album-info">
      <h3>{{ album.name }}</h3>
      <span>{{ album.photo_count }} 张照片</span>
    </div>
  </router-link>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'
defineProps({ album: { type: Object, required: true } })
</script>

<style scoped>
.album-card {
  background: #1e293b;
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s;
  display: block;
}
.album-card:hover { transform: translateY(-4px); }
.album-cover {
  aspect-ratio: 4/3;
  background: #334155;
}
.album-cover .el-image { width: 100%; height: 100%; }
.album-cover-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  color: #64748b;
}
.album-info { padding: 12px 14px; }
.album-info h3 { font-size: 15px; margin-bottom: 4px; color: #e2e8f0; }
.album-info span { font-size: 12px; color: #94a3b8; }
</style>
```

- [ ] **Step 2: 创建 AlbumListView**

```vue
<!-- frontend/src/views/AlbumListView.vue -->
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
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/AlbumCard.vue frontend/src/views/AlbumListView.vue
git commit -m "feat: add AlbumCard and AlbumListView"
```

---

### Task 14: AlbumDetailView

**Files:**
- Update: `D:\hkyPhoto\frontend\src\views\AlbumDetailView.vue`

- [ ] **Step 1: 实现 AlbumDetailView**

```vue
<!-- frontend/src/views/AlbumDetailView.vue -->
<template>
  <div>
    <div class="page-header">
      <router-link to="/albums" class="back-link">← 返回相册</router-link>
      <h2 class="page-title">{{ album?.name }}</h2>
      <p v-if="album?.description" class="page-desc">{{ album.description }}</p>
    </div>

    <div v-if="photoError" class="error-msg">{{ photoError }}</div>

    <PhotoGrid
      :photos="photos"
      :loading="loading"
      :has-more="hasMore"
      @photo-click="openLightbox"
      @load-more="loadMore"
    />

    <Lightbox
      :visible="lightboxVisible"
      :photos="photos"
      :index="lightboxIndex"
      @close="lightboxVisible = false"
      @prev="lightboxIndex = Math.max(0, lightboxIndex - 1)"
      @next="lightboxIndex = Math.min(photos.length - 1, lightboxIndex + 1)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAlbum, getAlbumPhotos } from '@/api/albums'
import PhotoGrid from '@/components/PhotoGrid.vue'
import Lightbox from '@/components/Lightbox.vue'

const route = useRoute()
const album = ref(null)
const photos = ref([])
const loading = ref(true)
const hasMore = ref(false)
const page = ref(1)
const photoError = ref('')
const lightboxVisible = ref(false)
const lightboxIndex = ref(0)

async function loadPhotos() {
  loading.value = true
  photoError.value = ''
  try {
    const { data } = await getAlbumPhotos(route.params.id, page.value)
    photos.value = page.value === 1 ? data.results : [...photos.value, ...data.results]
    hasMore.value = !!data.next
  } catch (e) {
    photoError.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}

function loadMore() { page.value++; loadPhotos() }

function openLightbox(photo) {
  lightboxIndex.value = photos.value.findIndex(p => p.id === photo.id)
  lightboxVisible.value = true
}

onMounted(async () => {
  try {
    const { data } = await getAlbum(route.params.id)
    album.value = data
  } catch (e) { /* ignore */ }
  loadPhotos()
})
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.back-link { color: #60a5fa; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 12px; }
.page-title { font-size: 24px; font-weight: 700; }
.page-desc { color: #94a3b8; margin-top: 6px; font-size: 14px; }
.error-msg { color: #f87171; padding: 12px 0; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/AlbumDetailView.vue
git commit -m "feat: add AlbumDetailView with photo grid and lightbox"
```

---

### Task 15: TimelineView

**Files:**
- Update: `D:\hkyPhoto\frontend\src\views\TimelineView.vue`

- [ ] **Step 1: 实现 TimelineView**

```vue
<!-- frontend/src/views/TimelineView.vue -->
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/TimelineView.vue
git commit -m "feat: add TimelineView grouped by month"
```

---

### Task 16: LocationCard + Location Views

**Files:**
- Create: `D:\hkyPhoto\frontend\src\components\LocationCard.vue`
- Update: `D:\hkyPhoto\frontend\src\views\LocationListView.vue`
- Update: `D:\hkyPhoto\frontend\src\views\LocationDetailView.vue`

- [ ] **Step 1: 创建 LocationCard**

```vue
<!-- frontend/src/components/LocationCard.vue -->
<template>
  <router-link :to="`/locations/${location.id}`" class="location-card">
    <div class="location-cover">
      <el-image v-if="location.cover_url" :src="location.cover_url" fit="cover" />
      <div v-else class="cover-fallback">📍</div>
    </div>
    <div class="location-info">
      <h3>{{ location.city || location.name }}</h3>
      <span>{{ location.photo_count }} 张照片</span>
    </div>
  </router-link>
</template>

<script setup>
defineProps({ location: { type: Object, required: true } })
</script>

<style scoped>
.location-card {
  background: #1e293b; border-radius: 12px; overflow: hidden;
  text-decoration: none; color: inherit; display: block;
  transition: transform 0.2s;
}
.location-card:hover { transform: translateY(-4px); }
.location-cover { aspect-ratio: 16/10; background: #334155; }
.location-cover .el-image { width: 100%; height: 100%; }
.cover-fallback {
  width: 100%; height: 100%; display: flex; align-items: center;
  justify-content: center; font-size: 40px;
}
.location-info { padding: 12px 14px; }
.location-info h3 { font-size: 15px; margin-bottom: 4px; color: #e2e8f0; }
.location-info span { font-size: 12px; color: #94a3b8; }
</style>
```

- [ ] **Step 2: 实现 LocationListView**

```vue
<!-- frontend/src/views/LocationListView.vue -->
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
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 24px; color: #e2e8f0; }
.location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}
.loading, .empty-state { text-align: center; padding: 80px 20px; color: #64748b; }
</style>
```

- [ ] **Step 3: 实现 LocationDetailView**

```vue
<!-- frontend/src/views/LocationDetailView.vue -->
<template>
  <div>
    <router-link to="/locations" class="back-link">← 返回地点</router-link>
    <h2 class="page-title">📍 {{ location?.city || location?.name }}</h2>
    <p v-if="location?.province" class="page-desc">{{ location.province }}{{ location.country ? ' · ' + location.country : '' }}</p>

    <PhotoGrid
      :photos="photos"
      :loading="loading"
      :has-more="hasMore"
      @photo-click="openLightbox"
      @load-more="loadMore"
    />

    <Lightbox
      :visible="lightboxVisible"
      :photos="photos"
      :index="lightboxIndex"
      @close="lightboxVisible = false"
      @prev="lightboxIndex = Math.max(0, lightboxIndex - 1)"
      @next="lightboxIndex = Math.min(photos.length - 1, lightboxIndex + 1)"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getLocationPhotos } from '@/api/locations'
import PhotoGrid from '@/components/PhotoGrid.vue'
import Lightbox from '@/components/Lightbox.vue'

const route = useRoute()
const location = ref(null)
const photos = ref([])
const loading = ref(true)
const hasMore = ref(false)
const page = ref(1)
const lightboxVisible = ref(false)
const lightboxIndex = ref(0)

async function load() {
  loading.value = true
  try {
    const { data } = await getLocationPhotos(route.params.id, page.value)
    photos.value = page.value === 1 ? data.results : [...photos.value, ...data.results]
    hasMore.value = !!data.next
    if (page.value === 1 && data.results.length > 0) {
      location.value = {
        city: data.results[0]?.location_name || '',
        name: data.results[0]?.location_name || '',
      }
    }
  } finally {
    loading.value = false
  }
}

function loadMore() { page.value++; load() }
function openLightbox(photo) {
  lightboxIndex.value = photos.value.findIndex(p => p.id === photo.id)
  lightboxVisible.value = true
}

onMounted(() => load())
</script>

<style scoped>
.back-link { color: #60a5fa; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 12px; }
.page-title { font-size: 24px; font-weight: 700; }
.page-desc { color: #94a3b8; margin-top: 4px; margin-bottom: 20px; }
</style>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/LocationCard.vue frontend/src/views/LocationListView.vue frontend/src/views/LocationDetailView.vue
git commit -m "feat: add LocationCard, LocationListView, LocationDetailView"
```

---

### Task 17: UploadZone 组件 + AdminView

**Files:**
- Create: `D:\hkyPhoto\frontend\src\components\UploadZone.vue`
- Create: `D:\hkyPhoto\frontend\src\utils\exif.js`
- Update: `D:\hkyPhoto\frontend\src\views\AdminView.vue`

- [ ] **Step 1: 创建 EXIF 读取工具**

```javascript
// frontend/src/utils/exif.js
import EXIF from 'exif-js'

export function readExif(file) {
  return new Promise((resolve) => {
    EXIF.getData(file, function () {
      const lat = EXIF.getTag(this, 'GPSLatitude')
      const latRef = EXIF.getTag(this, 'GPSLatitudeRef')
      const lon = EXIF.getTag(this, 'GPSLongitude')
      const lonRef = EXIF.getTag(this, 'GPSLongitudeRef')
      const takenAt = EXIF.getTag(this, 'DateTimeOriginal')

      let latitude = null, longitude = null
      if (lat && lon) {
        latitude = dmsToDecimal(lat) * (latRef === 'S' ? -1 : 1)
        longitude = dmsToDecimal(lon) * (lonRef === 'W' ? -1 : 1)
      }

      let takenAtISO = null
      if (takenAt) {
        takenAtISO = takenAt.replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3')
      }

      resolve({ latitude, longitude, takenAt: takenAtISO })
    })
  })
}

function dmsToDecimal(dms) {
  return dms[0] + dms[1] / 60 + dms[2] / 3600
}
```

- [ ] **Step 2: 创建 UploadZone 组件**

```vue
<!-- frontend/src/components/UploadZone.vue -->
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
import { getAlbums } from '@/api/albums'
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
.upload-text { color: #94a3b8; font-size: 14px; margin-top: 8px; }
.upload-tip { color: #64748b; font-size: 12px; margin-top: 8px; }
.upload-actions { margin-top: 16px; display: flex; gap: 12px; align-items: center; }
.upload-progress { margin-top: 20px; }
.progress-text { color: #94a3b8; font-size: 13px; margin-top: 8px; }
</style>
```

- [ ] **Step 3: 实现 AdminView**

```vue
<!-- frontend/src/views/AdminView.vue -->
<template>
  <div>
    <h2 class="page-title">管理</h2>

    <div v-if="!auth.isAuthenticated" class="login-box">
      <el-card header="管理员登录" style="max-width:400px;margin:60px auto">
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
          <el-form @submit.prevent="createAlbum" style="max-width:400px;margin-top:12px">
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
.page-title { font-size: 24px; font-weight: 700; margin-bottom: 24px; color: #e2e8f0; }
.login-box { padding: 40px 0; }
</style>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/utils/exif.js frontend/src/components/UploadZone.vue frontend/src/views/AdminView.vue
git commit -m "feat: add UploadZone, EXIF reader, and AdminView with login"
```

---

### Task 18: HomeView 首页

**Files:**
- Update: `D:\hkyPhoto\frontend\src\views\HomeView.vue`

- [ ] **Step 1: 实现 HomeView**

```vue
<!-- frontend/src/views/HomeView.vue -->
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
        <router-link to="/timeline" class="see-all">查看全部 →</router-link>
      </div>
    </section>

    <section v-if="albums.length > 0" class="section">
      <h3 class="section-title">相册</h3>
      <div class="album-grid">
        <AlbumCard v-for="album in albums.slice(0, 6)" :key="album.id" :album="album" />
      </div>
      <div v-if="albums.length > 6" class="section-footer">
        <router-link to="/albums" class="see-all">查看全部 →</router-link>
      </div>
    </section>

    <section v-if="locations.length > 0" class="section">
      <h3 class="section-title">地点</h3>
      <div class="location-grid">
        <LocationCard v-for="loc in locations.slice(0, 6)" :key="loc.id" :location="loc" />
      </div>
      <div v-if="locations.length > 6" class="section-footer">
        <router-link to="/locations" class="see-all">查看全部 →</router-link>
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
.page-title { font-size: 28px; font-weight: 700; color: #e2e8f0; }
.page-subtitle { color: #94a3b8; margin-bottom: 32px; font-size: 15px; }
.section { margin-bottom: 40px; }
.section-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; border-left: 3px solid #3b82f6; padding-left: 10px; }
.section-footer { margin-top: 16px; text-align: right; }
.see-all { color: #60a5fa; text-decoration: none; font-size: 14px; }
.album-grid, .location-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/HomeView.vue
git commit -m "feat: add HomeView with recent photos, albums, and locations"
```

---

## Phase 4: 部署与构建

### Task 19: 构建配置与集成

**Files:**
- Modify: `D:\hkyPhoto\frontend\vite.config.js`
- Modify: `D:\hkyPhoto\backend\config\settings.py`

- [ ] **Step 1: 配置 Vite build 输出到 Django static 目录**

在 `vite.config.js` 中添加 build 配置：

```javascript
// 在 defineConfig 中添加:
build: {
  outDir: resolve(__dirname, '../backend/static'),
  emptyOutDir: true,
  assetsDir: 'assets',
},
```

- [ ] **Step 2: 配置 Django 回退视图以支持 SPA 路由**

在 `backend/config/urls.py` 中添加：

```python
from django.views.generic import TemplateView

# 在所有 urlpatterns 之后添加:
urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html')),
    re_path(r'^(?!api/|admin/|static/).*$', TemplateView.as_view(template_name='index.html')),
]
```

需要在 settings.py TEMPLATES['DIRS'] 中添加 static 目录：

```python
TEMPLATES[0]['DIRS'] = [BASE_DIR / 'static']
```

- [ ] **Step 3: 构建前端并验证**

```bash
cd /d/hkyPhoto/frontend
npm run build
```

Expected: `backend/static/` 目录中出现 index.html 和 assets/

- [ ] **Step 4: Commit**

```bash
git add frontend/vite.config.js backend/config/settings.py backend/config/urls.py
git commit -m "feat: configure Vite build output to Django static and SPA fallback"
```

---

### Task 20: Nginx 配置 & 部署脚本

**Files:**
- Create: `D:\hkyPhoto\nginx\nginx.conf`
- Create: `D:\hkyPhoto\scripts\deploy.sh`

- [ ] **Step 1: 创建 Nginx 配置**

```nginx
# nginx/nginx.conf
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 0;
    proxy_request_buffering off;

    location /static/ {
        alias /path/to/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/backend/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        location ~ ^/(api|admin)/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Rate limiting for login
    location /api/auth/login/ {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Rate limit zone
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
```

- [ ] **Step 2: 创建部署脚本**

```bash
#!/bin/bash
# scripts/deploy.sh
set -e

echo "=== 安装后端依赖 ==="
cd backend
pip install -r requirements.txt

echo "=== 构建前端 ==="
cd ../frontend
npm install
npm run build

echo "=== 收集静态文件 ==="
cd ../backend
python manage.py collectstatic --noinput
python manage.py migrate

echo "=== 重启服务 ==="
sudo systemctl restart gunicorn
sudo systemctl reload nginx

echo "=== 部署完成 ==="
```

- [ ] **Step 3: Commit**

```bash
git add nginx/ scripts/
git commit -m "feat: add Nginx config and deploy script"
```

---

### Task 21: README 与 最终验证

**Files:**
- Create: `D:\hkyPhoto\README.md`

- [ ] **Step 1: 创建 README.md**

```markdown
# MyAlbum - 个人相册网站

基于 Django + Vue 3 的个人相册网站，支持按相册、时间线、地点浏览照片。

## 技术栈

- 后端：Django 4.x + Django REST Framework
- 前端：Vue 3 + Element Plus + Pinia
- 存储：阿里云 OSS
- 地图：高德地图 API（反向地理编码）

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入实际配置
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 生产构建

```bash
cd frontend && npm run build
cd ../backend && python manage.py collectstatic
```

## 部署

参考 `nginx/nginx.conf` 和 `scripts/deploy.sh`
```

- [ ] **Step 2: 最终验证清单**

- [ ] 后端：`cd backend && python manage.py runserver` 正常启动
- [ ] 前端：`cd frontend && npm run dev` 正常启动
- [ ] API：`curl http://127.0.0.1:8000/api/albums/` 返回 JSON
- [ ] 构建：`cd frontend && npm run build` 成功

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README and finalize project"
```

---

## 附录：环境依赖清单

在运行项目前需要准备：

| 依赖 | 说明 |
|------|------|
| Python 3.10+ | Django 运行环境 |
| Node.js 18+ | Vue 前端构建 |
| 阿里云 OSS Bucket | 照片存储（私有读写） |
| 高德地图 API Key | 坐标→城市名转换 |
| pip / npm | 包管理器 |

## 附录：OSS Bucket 配置示例

1. 创建 Bucket，权限设为"私有"
2. 设置跨域规则（允许 PUT 方法，来源为你的域名）
3. 建议开启图片处理功能（用于缩略图）
