from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://agrolino:agrolino@localhost:5432/agrolino"
    session_secret: str = "dev-change-me-in-production-min-32-chars!!"
    environment: str = "development"
    session_cookie_secure: bool = False
    session_cookie_samesite: Literal["strict", "lax", "none"] = "strict"
    session_ttl_hours: int = 168  # 7 dias


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
