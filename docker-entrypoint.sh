#!/bin/sh
set -e

# Render 自动设置 PORT 环境变量，本地默认 8000
PORT="${PORT:-8000}"

echo "🚀 启动端口: $PORT"

if [ "$ALEMBIC_AUTO_MIGRATE" = "true" ]; then
  echo "📦 执行数据库迁移..."
  alembic upgrade head
fi

echo "✅ 启动 FastAPI 服务..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"