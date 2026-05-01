# 个人相册网站设计文档

日期：2026-05-01

## 1. 项目概述

一个公网部署的个人相册网站。支持手机端/桌面端上传照片，按相册、时间线、地点三种维度浏览展示。

## 2. 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 4.x + Django REST Framework |
| 前端框架 | Vue 3 + Vite + Element Plus |
| 数据库 | SQLite（开发）→ PostgreSQL（生产） |
| 对象存储 | 阿里云 OSS |
| 地理编码 | 高德地图 Web 服务 API |
| 反向代理 | Nginx + Gunicorn |
| PWA | manifest.json + Service Worker |
| 部署 | 阿里云 ECS / 轻量应用服务器 |

## 3. 系统架构

```
浏览器 (手机/桌面) → HTTPS → Nginx
                               ├── /static/   → Vue SPA 静态文件
                               ├── /api/      → Gunicorn → Django
                               └── /admin/    → Django Admin

Django → PostgreSQL（元数据）
Django → 高德 API（地理编码）
浏览器 → 阿里云 OSS（直传照片，通过 Presigned URL）
```

**关键设计决策**：
- Vue SPA build 产物放在 Django STATIC_ROOT 下，Nginx 直接提供
- 照片上传走 OSS 直传，不经 Django，不占服务器带宽
- 缩略图使用 OSS 图片处理（`?x-oss-process=image/resize,w_400` 实时缩放）

## 4. 数据模型

### Album（相册）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | CharField(100) | 相册名称 |
| description | TextField | 描述 |
| cover | FK → Photo (nullable) | 封面照片 |
| sort_order | IntegerField | 排序权重 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### Photo（照片）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| album | FK → Album | 所属相册 |
| title | CharField(200) | 照片标题 |
| oss_key | CharField(500) | OSS 对象 key |
| width | Integer | 宽度 |
| height | Integer | 高度 |
| file_size | BigInteger | 文件大小（字节） |
| taken_at | DateTime (nullable) | EXIF 拍摄时间 |
| latitude | Float (nullable) | EXIF GPS 纬度 |
| longitude | Float (nullable) | EXIF GPS 经度 |
| location | FK → Location (nullable) | 归属地点 |
| uploaded_at | DateTime | 上传时间 |

### Location（地点）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | CharField(200) | 显示名（如"杭州市"） |
| latitude | Float | 聚合中心纬度 |
| longitude | Float | 聚合中心经度 |
| city | CharField | 城市 |
| province | CharField | 省份 |
| country | CharField | 国家 |

## 5. REST API

公开接口（无需认证）：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/albums/ | 相册列表 |
| GET | /api/albums/{id}/ | 相册详情（含照片列表） |
| GET | /api/photos/?ordering=-taken_at | 时间线分页 |
| GET | /api/locations/ | 地点列表（按照片数量排序） |
| GET | /api/locations/{id}/photos/ | 某地点的所有照片 |

管理接口（需 JWT 认证）：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login/ | 管理员登录，返回 JWT |
| POST | /api/albums/ | 创建相册 |
| PUT/PATCH | /api/albums/{id}/ | 更新相册 |
| DELETE | /api/albums/{id}/ | 删除相册 |
| POST | /api/upload/presigned/ | 获取 OSS Presigned URL |
| POST | /api/photos/ | 保存照片元数据 |
| DELETE | /api/photos/{id}/ | 删除照片 |

## 6. 上传流程

```
[前端] 选择照片 → 读取 EXIF（GPS + 拍摄时间）
      → POST /api/upload/presigned/ 获取上传 URL
      → PUT 直接上传到 OSS
      → POST /api/photos/ 保存元数据（含坐标）
           → Django 调用高德反向地理编码
           → 将城市与已有 Location 匹配或创建新 Location
           → 关联 photo.location
```

## 7. 前端路由

| 路径 | 页面 | 说明 |
|------|------|------|
| / | 首页 | 最近上传照片 + 各相册封面概览 |
| /albums | 相册列表 | 网格卡片 |
| /albums/:id | 相册详情 | 照片瀑布流 + 上传入口 |
| /timeline | 时间线 | 按月份分组瀑布流 |
| /locations | 地点列表 | 城市卡片网格 |
| /locations/:id | 地点照片 | 该城市所有照片 |
| /admin | 管理页 | 登录 / 上传 / 管理 |

## 8. 核心前端组件

| 组件 | 功能 |
|------|------|
| PhotoGrid | Masonry 瀑布流照片网格（基于 Element Plus + CSS columns） |
| PhotoCard | 单张照片卡片，悬浮显示标题/日期/地点 |
| Lightbox | 全屏灯箱，左右滑动切换、双指缩放 |
| UploadZone | 拖拽/点选上传，多文件并发，进度条 |
| AlbumCard | 相册封面卡片，显示名称/照片数 |
| LocationCard | 地点封面卡片，显示城市名/照片数 |

## 9. PWA 支持

- `manifest.json`：图标、名称、主题色、全屏模式
- Service Worker：缓存静态资源，已浏览照片离线可用
- 响应式断点：<768px 手机 / 768-1024px 平板 / >1024px 桌面

## 10. 部署清单

- 阿里云 ECS 或轻量应用服务器（1C2G 起步）
- 域名 + Let's Encrypt SSL 证书
- 阿里云 OSS Bucket（私有读写）
- 高德地图 Web 服务 API Key
- Nginx + Gunicorn + PostgreSQL
- 环境变量注入：SECRET_KEY、OSS_ACCESS_KEY、AMAP_API_KEY 等

## 11. 安全措施

- OSS Bucket 设为私有，仅通过 Presigned URL 访问（有效期 60s）
- 所有 API Key / Secret 通过环境变量注入，不提交仓库
- Django SECRET_KEY 独立随机生成
- 管理接口统一要求 JWT，有效期 7 天
- Nginx 配置 rate limiting 防暴力破解登录
- 上传文件校验：仅允许图片格式，限制单文件最大 20MB

## 12. 不纳入范围

- 多人用户系统 / 注册登录
- 照片编辑 / 滤镜
- 评论 / 点赞
- 视频支持（仅照片）
- AI 人脸识别 / 自动标签
- CDN 加速
