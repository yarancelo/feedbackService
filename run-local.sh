#!/usr/bin/env bash
# One-command local run WITHOUT Docker: single process (FastAPI serves the API and
# the built SPA) on a local SQLite database. For the full production stack
# (PostgreSQL 18 + nginx, 4 containers) use `docker compose up --build` instead.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "==> Building frontend (Vite)"
cd "$ROOT/frontend"
npm install
npm run build

echo "==> Preparing backend"
cd "$ROOT/backend"
python3 -m venv .venv 2>/dev/null || true
# shellcheck disable=SC1091
. .venv/bin/activate
pip install -q -r requirements.txt

export PYTHONPATH="$ROOT/backend/src"
export DATABASE_URL="sqlite+pysqlite:///$ROOT/backend/feedback_local.db"
export SERVE_STATIC_DIR="$ROOT/frontend/dist"

echo
echo "==> App: http://localhost:8080   (admin / password)"
echo "    API: http://localhost:8080/api/health"
echo
exec uvicorn feedback_app.main:app --host 0.0.0.0 --port 8080
