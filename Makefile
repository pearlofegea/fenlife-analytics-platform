.PHONY: help install backend frontend dev test lint clean

help:
	@echo "FENlife Analytics — Geliştirme Komutları"
	@echo ""
	@echo "  make install    İlk kurulum (backend venv + frontend node_modules)"
	@echo "  make backend    FastAPI dev server (http://localhost:8000)"
	@echo "  make frontend   Next.js dev server (http://localhost:3000)"
	@echo "  make dev        İkisini de paralel çalıştır"
	@echo "  make test       Backend testlerini çalıştır"
	@echo "  make lint       Ruff + ESLint + Prettier"
	@echo "  make clean      Cache ve build klasörlerini temizle"

install:
	@echo "→ Backend kuruluyor..."
	cd backend && python3 -m venv .venv && \
		.venv/bin/pip install --upgrade pip && \
		.venv/bin/pip install -r requirements.txt
	@echo "→ Frontend kuruluyor..."
	cd frontend && npm install
	@echo "✓ Kurulum tamam. VS Code'da 'fenlife.code-workspace' dosyasını aç."

backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --reload-dir app --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "→ Backend (8000) ve Frontend (3000) paralel başlatılıyor..."
	@trap 'kill 0' SIGINT; \
	(cd backend && .venv/bin/uvicorn app.main:app --reload --reload-dir app --port 8000) & \
	(cd frontend && npm run dev) & \
	wait

test:
	cd backend && .venv/bin/pytest tests/ -v

lint:
	cd backend && .venv/bin/ruff check app/ && .venv/bin/ruff format app/ --check
	cd frontend && npm run lint

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.next frontend/out
	@echo "✓ Temizlendi"
