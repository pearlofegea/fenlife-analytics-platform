"""Sağlık kontrol endpoint'i — frontend backend'e ulaşabildiğini kontrol eder."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basit ping — frontend'den bağlantı testi."""
    return {"status": "ok", "service": "fenlife-backend"}
