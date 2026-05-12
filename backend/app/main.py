"""
FENlife Analytics — FastAPI uygulama başlangıcı.

Bu dosya:
- FastAPI uygulamasını yaratır
- CORS ayarlarını yapar
- Router'ları bağlar
- Sağlık kontrol endpoint'i

Dev çalıştırma:
    uvicorn app.main:app --reload --port 8000

Daha fazlası için: README.md
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, reports, students
from app.config import settings
from app.db.session import engine
from app.db import models  # noqa: F401 — metadata kayıt için import gerekli


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü — başlangıç ve kapanış."""
    # Startup: tablolar yoksa oluştur (migration uygulanmışsa no-op)
    # Production'da bu satır kaldırılır; yalnızca `alembic upgrade head` kullanılır.
    models.Base.metadata.create_all(bind=engine)
    print(f"🚀 FENlife Analytics backend — {settings.environment}")
    yield
    # Shutdown
    print("👋 Backend kapatılıyor...")


app = FastAPI(
    title="FENlife Analytics API",
    description="Akademik Gelişim ve Takip Planlama — backend servisi",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — frontend'in erişebilmesi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'lar
app.include_router(health.router, tags=["health"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(students.router, prefix="/api", tags=["students"])
# Swagger: /docs  |  ReDoc: /redoc


@app.get("/")
async def root():
    return {
        "service": "FENlife Analytics",
        "version": "0.1.0",
        "docs": "/docs",
    }
