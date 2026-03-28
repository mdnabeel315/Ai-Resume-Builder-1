"""
Config — Centralised settings loaded from environment / .env file.
All secrets live here. Never import os.environ directly elsewhere.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM
    gemini_api_key: str

    # App
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"

    # Rate limiting
    rate_limit_per_minute: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance. Call this everywhere."""
    return Settings()
