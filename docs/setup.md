# Kurulum (Mac / zsh / VS Code)

## Gereksinimler

- Python 3.11+ (`python3 --version`)
- Node.js 18+ (`node --version`)
- VS Code (önerilen eklentiler workspace açılınca teklif edilir)

## Adım adım

```bash
# 1. Repoyu aç
cd fenlife-analytics

# 2. Backend kur
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env içine ANTHROPIC_API_KEY ekle
cd ..

# 3. Frontend kur
cd frontend
npm install
cp .env.local.example .env.local
cd ..

# 4. VS Code'u workspace ile aç
code fenlife.code-workspace
```

## Çalıştırma

```bash
# Root'tan
make dev     # ikisi paralel
# veya ayrı ayrı
make backend
make frontend
```

Backend: http://localhost:8000 · http://localhost:8000/docs (Swagger)
Frontend: http://localhost:3000

## VS Code debug

`.vscode/launch.json` dört hazır config içerir:
- 🐍 FastAPI (debug)
- ⚛️ Next.js (debug)
- 🧪 Pytest (current file)
- 🔎 Parser (tek PDF test)

F5 ile başlat.
