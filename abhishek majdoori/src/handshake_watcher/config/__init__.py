"""
handshake_watcher.config
========================

Typed, environment-driven configuration using pydantic-settings.

All application settings are loaded once at startup from:
  1. Environment variables (highest priority)
  2. A `.env` file in the working directory
  3. Defaults defined in the Settings model (lowest priority)

Usage
-----
    from handshake_watcher.config import get_settings

    settings = get_settings()
    print(settings.poll_interval_seconds)
"""

from handshake_watcher.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
