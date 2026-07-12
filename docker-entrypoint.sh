#!/bin/sh 
set -e
  # 如果环境变量 ALEMBIC_AUTO_MIGRATE 的值是 "true"，就执行 alembic upgrade head
  if [ "$ALEMBIC_AUTO_MIGRATE" = "true" ]; then
    alembic upgrade head
  fi
  # 最后执行 exec uvicorn app.main:app --host 0.0.0.0 --port 8000
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000