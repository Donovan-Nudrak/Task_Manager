#!/usr/bin/env python3

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).resolve().parents[2]


def _env_files() -> tuple[str, ...] | None:
    app_env = os.getenv("APP_ENV", "dev")
    files: list[str] = []
    extra = _ROOT / f".env.{app_env}"
    if extra.exists():
        files.append(str(extra))
    default_env = _ROOT / ".env"
    if default_env.exists():
        files.append(str(default_env))
    return tuple(files) if files else None


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "dev-secret-key"
    DEBUG: bool = True
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
