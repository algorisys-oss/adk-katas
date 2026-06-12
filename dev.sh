#!/usr/bin/env bash
# Run the full ADK Katas app: FastAPI backend + Vite/React frontend.
# Ctrl-C stops both. Run from anywhere: ./dev.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
BACKEND_PORT=8001

# --- one-time frontend deps -------------------------------------------------
if [ ! -d "frontend/node_modules" ]; then
  echo "📦 Installing frontend deps (first run)…"
  ( cd frontend && npm install )
fi

# --- API key heads-up (live chat only) --------------------------------------
if uv run python -c "from kata_helpers import has_api_key; import sys; sys.exit(0 if has_api_key() else 1)" 2>/dev/null; then
  echo "🔑 Gemini API key detected — live chat enabled."
else
  echo "⚠️  No Gemini API key — checks still work; live chat is disabled."
  echo "    Add GOOGLE_API_KEY to .env to enable it."
fi
echo

# --- start both -------------------------------------------------------------
echo "▶ backend  : http://localhost:$BACKEND_PORT          (FastAPI + ADK)"
echo "▶ frontend : http://localhost:5173 (or next free port — see Vite output below)"
echo

uv run uvicorn server:app --port "$BACKEND_PORT" --reload &
BACK=$!

# Vite uses port 5173 from vite.config.ts; it auto-bumps if that port is busy.
( cd frontend && npm run dev ) &
FRONT=$!

cleanup() {
  echo
  echo "stopping…"
  kill "$BACK" "$FRONT" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

wait
