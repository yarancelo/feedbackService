#!/bin/sh
set -e

echo "[entrypoint] applying database migrations (alembic upgrade head)..."
alembic upgrade head

echo "[entrypoint] starting API on :8080 ..."
exec uvicorn feedback_app.main:app --host 0.0.0.0 --port 8080
