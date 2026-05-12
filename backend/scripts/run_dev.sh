#!/usr/bin/env bash
# Backend dev server başlatıcı
set -e
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || {
  echo "⚠ venv yok. İlk önce: python3 -m venv .venv && pip install -r requirements.txt"
  exit 1
}
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
