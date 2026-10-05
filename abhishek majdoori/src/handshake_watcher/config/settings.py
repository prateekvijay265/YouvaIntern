"""
handshake_watcher.config.settings
===================================

Pydantic-settings model that loads all application configuration from
environment variables and / or a `.env` file.

Every field is documented with its purpose, unit, and allowed range where
applicable. Validation errors surface at startup — fail fast, fail loudly.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """
    Central configuration model for Handshake Project Watcher.

    Values are resolved in priority order:
      1. Explicit environment variables
      2. Values from the `.env` file
      3. Field defaults
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # silently ignore unknown env vars
        validate_default=True,
    )

    # -----------------------------------------------------------------------
    # Handshake connection
    # -----------------------------------------------------------------------
    handshake_base_url: AnyHttpUrl = Field(
        ...,
        description="Base URL of your Handshake instance, e.g. https://app.joinhandshake.com",
    )

    handshake_projects_path: str = Field(
        default="/projects",
        description="URL path appended to base URL to reach the projects listing page.",
        pattern=r"^/.*",
    )

    # -----------------------------------------------------------------------
    # Polling
    # -----------------------------------------------------------------------
    poll_interval_seconds: int = Field(
        default=60,
        ge=30,
        le=3600,
        description="Seconds between consecutive polls. Minimum 30 to be server-respectful.",
    )

    # -----------------------------------------------------------------------
    # Notifications
    # -----------------------------------------------------------------------
    notification_duration_seconds: int = Field(
        default=10,
        ge=1,
        le=60,
        description="How long each Windows toast notification stays on screen (seconds).",
    )

    # -----------------------------------------------------------------------
    # State persistence
    # -----------------------------------------------------------------------
    state_file_path: Path = Field(
        default=Path("state/seen_projects.json"),
        description="Path to the JSON file that persists seen-project IDs.",
    )

    # -----------------------------------------------------------------------
    # Logging
    # -----------------------------------------------------------------------
    log_level: LogLevel = Field(
        default="INFO",
        description="Logging verbosity: DEBUG | INFO | WARNING | ERROR | CRITICAL",
    )

    log_file_path: Path = Field(
        default=Path("logs/watcher.log"),
        description="Path to the rotating log file.",
    )

    log_max_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        ge=1024,
        description="Maximum log-file size in bytes before rotation.",
    )

    log_backup_count: int = Field(
        default=5,
        ge=0,
        le=100,
        description="Number of rotated backup log files to retain.",
    )

    # -----------------------------------------------------------------------
    # Browser (Playwright)
    # -----------------------------------------------------------------------
    browser_headless: bool = Field(
        default=True,
        description="Run Chromium in headless mode. Set False to see the browser.",
    )

    browser_timeout_ms: int = Field(
        default=30_000,
        ge=5_000,
        le=120_000,
        description="Page-load timeout in milliseconds.",
    )

    browser_storage_state_path: Path | None = Field(
        default=None,
        description=(
            "Optional path to a Playwright storage-state JSON file "
            "(cookies / local storage). Generates once via scripts/save_auth.py."
        ),
    )

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------
    @field_validator("handshake_projects_path")
    @classmethod
    def _strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    @model_validator(mode="after")
    def _ensure_state_and_log_dirs_exist(self) -> "Settings":
        """Create parent directories for state and log files if absent."""
        for path in (self.state_file_path, self.log_file_path):
            path.parent.mkdir(parents=True, exist_ok=True)
        return self

    @field_validator("browser_storage_state_path", mode="before")
    @classmethod
    def _coerce_empty_string_to_none(cls, v: object) -> object:
        """Treat empty-string env var as None (no storage state)."""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    # -----------------------------------------------------------------------
    # Derived properties
    # -----------------------------------------------------------------------
    @property
    def projects_url(self) -> str:
        """Full URL to the Handshake projects listing page."""
        base = str(self.handshake_base_url).rstrip("/")
        return f"{base}{self.handshake_projects_path}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the application settings singleton.

    The result is cached so that pydantic parses the environment exactly once.
    Call ``get_settings.cache_clear()`` in tests to reset state between runs.
    """
    settings = Settings()  # type: ignore[call-arg]
    logger.debug("Settings loaded: projects_url=%s", settings.projects_url)
    return settings
