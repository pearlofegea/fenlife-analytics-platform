"""SQLAlchemy engine ve session yönetimi."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # stale connection'ları önler
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI Depends() ile kullanılır — her request için ayrı session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
