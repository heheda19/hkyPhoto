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
