from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    allowed_origins: str = Field(default="http://localhost:5173", alias="ALLOWED_ORIGINS")
    sqlite_path: Path = Field(
        default=Path("D:/Codex/Finance/data/finance_quant_lab.sqlite3"),
        alias="SQLITE_PATH",
    )
    parquet_root: Path = Field(
        default=Path("D:/Codex/Finance/data/parquet"),
        alias="PARQUET_ROOT",
    )
    market_provider: str = Field(default="futu", alias="MARKET_PROVIDER")
    news_provider: str = Field(default="alpha_vantage", alias="NEWS_PROVIDER")
    futu_host: str = Field(default="127.0.0.1", alias="FUTU_HOST")
    futu_port: int = Field(default=11111, alias="FUTU_PORT")
    futu_sdk_appdata_path: Path = Field(
        default=Path("D:/Codex/Finance/data/futu-sdk-appdata"),
        alias="FUTU_SDK_APPDATA_PATH",
    )
    alpha_vantage_api_key: str = Field(default="", alias="ALPHA_VANTAGE_API_KEY")
    enable_fixture_mode: bool = Field(default=True, alias="ENABLE_FIXTURE_MODE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    settings.parquet_root.mkdir(parents=True, exist_ok=True)
    settings.futu_sdk_appdata_path.mkdir(parents=True, exist_ok=True)
    return settings
