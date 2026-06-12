from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    fallback = "true" if default else "false"
    return os.getenv(name, fallback).lower() in ("1", "true", "yes")


def _env_csv(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings(BaseModel):
    database_url: str | None = Field(default=None)
    secret_key: str | None = Field(default=None)
    internal_auth_secret: str | None = Field(default=None)
    sql_echo: bool = False
    cors_origins: list[str] = Field(default_factory=list)
    port: int = 7860


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL"),
        secret_key=os.getenv("SECRET_KEY"),
        internal_auth_secret=os.getenv("INTERNAL_AUTH_SECRET"),
        sql_echo=_env_bool("SQL_ECHO", default=False),
        cors_origins=_env_csv("CORS_ORIGINS", "https://review-analyzer.vercel.app"),
        port=int(os.getenv("PORT", "7860")),
    )
