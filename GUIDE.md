# MyAlbum — 部署与使用指南

## 项目概述

个人相册网站，支持手机 / 桌面端上传照片，按 **相册、时间线、地点** 三种维度浏览。前后端分离，照片直接上传到阿里云 OSS。

- 后端：Django 4.x + Django REST Framework + JWT
- 前端：Vue 3 + Element Plus + Pinia + PWA
- 存储：阿里云 OSS (Presigned URL 直传)
- 地图：高德 API (GPS 坐标 → 城市名)

---

## 一、你需要准备的账号和 Key

部署前需要获取以下外部服务的账号和 API Key：

| 服务 | 用途 | 获取地址 |
|------|------|----------|
| 阿里云 OSS | 照片存储 | https://oss.console.aliyun.com |
| 高德地图 API | GPS 反向地理编码 | https://lbs.amap.com |
| Let's Encrypt | 免费 SSL 证书 | https://letsencrypt.org |

---

## 二、必须替换的配置

### 2.1 `.env` 环境变量

复制 `.env.example` 为 `.env`，逐行填入真实值：

```bash
# 1. Django 密钥 — 必须替换为随机字符串 (≥50字符)
# 生成方式: python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=change-me-to-random-string

# 2. 调试模式 — 生产环境必须改为 False
DEBUG=False

# 3. 数据库 — SQLite 无需改动，PostgreSQL 改为:
# DATABASE_URL=postgres://user:password@host:5432/dbname
DATABASE_URL=sqlite:///db.sqlite3

# 4. 阿里云 OSS — 必须全部替换
OSS_ACCESS_KEY_ID=your-oss-access-key          # ← 替换为你的 AccessKey ID
OSS_ACCESS_KEY_SECRET=your-oss-secret          # ← 替换为你的 AccessKey Secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com       # ← 替换为你 Bucket 的地域 Endpoint
OSS_BUCKET_NAME=your-bucket                     # ← 替换为你的 Bucket 名称

# 5. 高德地图 — 必须替换
AMAP_API_KEY=your-amap-key                      # ← 替换为你的高德 Web API Key

# 6. 管理员账号 — 必须替换
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me                        # ← 替换为强密码
```

> 如果你改了 `ADMIN_USERNAME` / `ADMIN_PASSWORD`，创建管理员时不要用默认值 `admin / admin123`。

### 2.2 Nginx 配置 (`nginx/nginx.conf`)

| 位置 | 行 | 当前值 | 替换为 |
|------|------|--------|--------|
| 域名 | 6, 12, 15, 16 | `your-domain.com` | 你的真实域名 |
| SSL 证书路径 | 15 | `/etc/letsencrypt/live/your-domain.com/fullchain.pem` | 证书实际路径 |
| SSL 私钥路径 | 16 | `/etc/letsencrypt/live/your-domain.com/privkey.pem` | 私钥实际路径 |
| 静态文件目录 | 22 | `/path/to/backend/staticfiles/` | 项目 `backend/staticfiles/` 的实际路径 |
| 媒体文件目录 | 27 | `/path/to/backend/media/` | 项目 `backend/media/` 的实际路径 |

### 2.3 部署脚本 (`scripts/deploy.sh`)

| 位置 | 当前值 | 替换为 |
|------|--------|--------|
| Gunicorn 服务名 | `sudo systemctl restart gunicorn` | 你创建的 systemd 服务名（如 `myalbum`） |

创建 Gunicorn systemd 服务文件 `/etc/systemd/system/myalbum.service`：

```ini
[Unit]
Description=MyAlbum Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2.4 前端开发代理 (`frontend/vite.config.js`)

| 位置 | 当前值 | 说明 |
|------|--------|------|
| `server.proxy` | `http://127.0.0.1:8000` | 开发时 Django 后端地址，通常不用改 |

---

## 三、阿里云 OSS 配置指南

### 3.1 创建 Bucket

1. 登录 [OSS 控制台](https://oss.console.aliyun.com)
2. 创建 Bucket，权限选择 **私有**
3. 记录 Bucket 名称和所在 Region 的 Endpoint（如 `oss-cn-hangzhou.aliyuncs.com`）

### 3.2 配置跨域规则 (CORS)

在 Bucket 的「数据安全 → 跨域设置」中添加规则：

| 配置项 | 值 |
|--------|------|
| 来源 Origin | `https://你的域名` 和 `http://localhost:5173` (开发时) |
| 允许 Methods | `GET`, `PUT` |
| 允许 Headers | `Content-Type` |
| 暴露 Headers | `ETag` |

### 3.3 开启图片处理（缩略图功能依赖）

在 Bucket 的「数据处理 → 图片处理」中开启。项目用 `image/resize,w_400` 参数生成缩略图。

### 3.4 创建 AccessKey

1. RAM 控制台 → 用户 → 创建用户
2. 授权 `AliyunOSSFullAccess`
3. 记录 AccessKey ID 和 AccessKey Secret，填入 `.env`

---

## 四、高德地图 API 配置

1. 登录 [高德开放平台](https://lbs.amap.com)
2. 创建应用 → 添加 Key，服务平台选择 **Web 服务**
3. 开通 **逆地理编码** API
4. 将 Key 填入 `.env` 的 `AMAP_API_KEY`

---

## 五、本地开发

```bash
# 1. 配置环境
cp .env.example .env
# 编辑 .env 填入真实配置，开发时可保持 DEBUG=True

# 2. 启动后端 (http://127.0.0.1:8000)
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 3. 启动前端 (http://localhost:5173, 自动代理 /api 到后端)
cd frontend
npm install
npm run dev
```

> 前端 `npm run dev` 会自动将 `/api` 请求代理到后端 8000 端口，无需额外配置。

---

## 六、生产部署

```bash
# 1. 编辑 .env，确保 DEBUG=False

# 2. 一键部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

该脚本会依次：
1. 安装后端 Python 依赖
2. 构建前端并输出到 `backend/static/`
3. 运行 `collectstatic` + `migrate`
4. 重启 Gunicorn 和 Nginx

---

## 七、HTTPS 证书 (Let's Encrypt)

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot certonly --nginx -d your-domain.com

# 证书路径会自动生成在:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

---

## 八、文件结构

```
├── backend/                 # Django 后端
│   ├── config/              # 项目配置 (settings, urls, wsgi)
│   ├── albums/              # 相册 App
│   ├── photos/              # 照片 App (含 OSS 上传)
│   ├── locations/           # 地点 App (含高德地理编码)
│   ├── auth_ext/            # JWT 认证
│   └── static/              # 前端构建产物 (npm run build 自动生成)
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── api/             # axios API 层
│       ├── components/      # 组件 (PhotoCard, UploadZone, Lightbox…)
│       ├── views/           # 页面 (Home, Albums, Timeline, Admin…)
│       ├── stores/          # Pinia 状态管理
│       ├── router/          # Vue Router
│       └── utils/           # EXIF 工具
├── nginx/
│   └── nginx.conf           # Nginx 配置模板
├── scripts/
│   └── deploy.sh            # 一键部署脚本
├── .env.example             # 环境变量模板
└── GUIDE.md                 # 本文件
```

---

## 九、常见问题

**Q: 上传照片报错？**
A: 检查：(1) `.env` 中 OSS 配置是否正确；(2) OSS Bucket 是否设置了 CORS 跨域规则；(3) AccessKey 是否有 PutObject 权限。

**Q: 照片不显示地点信息？**
A: 照片需要有 GPS 坐标（手机拍照默认有）。检查 `.env` 中高德 API Key 是否正确，以及 API 是否开通了逆地理编码。

**Q: PWA 不生效？**
A: 需要 HTTPS 和生产构建（`npm run build`）。开发环境不启用 PWA。

**Q: 如何重置管理员密码？**
A: `cd backend && python manage.py changepassword admin`
