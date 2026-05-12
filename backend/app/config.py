"""Ortam değişkenleri ve uygulama ayarları."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Tüm env değişkenleri burada tanımlı ve type-safe."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # === Database ===
    database_url: str = "postgresql://fenlife:fenlife@localhost:5432/fenlife_analytics"

    # === Anthropic ===
    anthropic_api_key: str = ""

    # === Dizinler ===
    data_dir: Path = Path("./sample-data")
    output_dir: Path = Path("./app/report/_output")

    # === Rapor ===
    # Hard minimum: en az 1 dosya gerekli (0 dosya reddedilir)
    min_exam_count: int = 1
    # Öneri eşiği: bu sayının altında kullanıcıya bilgilendirici uyarı gösterilir
    recommended_exam_count: int = 5
    report_template_path: Path = Path("./app/report/templates/fenlife_base.docx")

    # === Ortam ===
    environment: str = "development"
    frontend_origin: str = "http://localhost:3000"
    log_level: str = "INFO"

    def ensure_dirs(self) -> None:
        """Çıktı dizinlerinin var olduğundan emin ol."""
        self.output_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
