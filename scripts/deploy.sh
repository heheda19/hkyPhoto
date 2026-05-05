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
