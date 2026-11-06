"""
ai_analyst/config.py
Centralised configuration loaded from environment variables via pydantic-settings.

Usage:
    from ai_analyst.config import settings
    settings.groq_api_key   # str
"""
from __future__ import annotations

from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration for the AI Analyst backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Groq ──────────────────────────────────────────────────
    groq_api_key: str = Field(
        default="",
        alias="GROQ_API_KEY",
        description="Groq platform API key (required for SQL generation).",
    )
    groq_model: str = Field(
        default="openai/gpt-oss-120b",
        alias="GROQ_MODEL",
        description="Groq model to use for SQL generation.",
    )
    groq_timeout: int = Field(
        default=30,
        alias="GROQ_TIMEOUT",
        description="HTTP timeout for Groq API calls in seconds.",
    )

    # ── Database ───────────────────────────────────────────────
    readonly_database_url: str = Field(
        default="",
        alias="READONLY_DATABASE_URL",
        description=(
            "PostgreSQL DSN for the DEDICATED READ-ONLY role. "
            "Must NOT be the postgres superuser. "
            "Create the role with scripts/setup_readonly_role.sql first."
        ),
    )

    # ── Execution safety ──────────────────────────────────────
    query_timeout_seconds: int = Field(
        default=3,
        alias="QUERY_TIMEOUT_SECONDS",
        description="Per-query PostgreSQL statement_timeout (seconds).",
    )
    max_result_rows: int = Field(
        default=100,
        alias="MAX_RESULT_ROWS",
        description="Maximum rows returned from any single query.",
    )

    # ── Internal flags ────────────────────────────────────────
    db_schema: str = "road_insight"

    @field_validator("groq_api_key")
    @classmethod
    def warn_missing_key(cls, v: str) -> str:
        if not v:
            import warnings
            warnings.warn(
                "GROQ_API_KEY is not set. SQL generation will fail. "
                "Copy .env.example to .env and fill in the value.",
                stacklevel=4,
            )
        return v

    @property
    def db_configured(self) -> bool:
        """True when the read-only DB URL looks like it has been configured."""
        url = self.readonly_database_url
        return bool(url) and "CHANGE_ME" not in url and "your_" not in url

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key) and "your_" not in self.groq_api_key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance (singleton)."""
    return Settings()


# Convenience re-export
settings: Settings = get_settings()

