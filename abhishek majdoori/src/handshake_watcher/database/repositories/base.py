"""
handshake_watcher.database.repositories.base
=============================================

Abstract base repository with shared helpers.

All concrete repositories inherit from :class:`BaseRepository`. It
provides:
- A reference to the :class:`~handshake_watcher.database.DatabaseEngine`.
- ``_now()`` — timezone-aware UTC ISO-8601 timestamp for DB writes.
- ``_bool_to_int`` / ``_int_to_bool`` — SQLite boolean converters.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from handshake_watcher.database.engine import DatabaseEngine


class BaseRepository:
    """Shared base for all repository classes."""

    def __init__(self, engine: DatabaseEngine) -> None:
        self._engine = engine

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _now() -> str:
        """Current UTC time as an ISO-8601 string suitable for DB storage."""
        return datetime.now(tz=timezone.utc).isoformat()

    @staticmethod
    def _bool_to_int(value: bool) -> int:  # noqa: FBT001
        """Convert a Python bool to SQLite INTEGER 0/1."""
        return 1 if value else 0

    @staticmethod
    def _int_to_bool(value: int | None) -> bool:
        """Convert a SQLite INTEGER 0/1 to a Python bool."""
        return bool(value)

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        """Parse an ISO-8601 string from the DB into a timezone-aware datetime."""
        if value is None:
            return None
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            # Treat naive datetimes as UTC (legacy rows)
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
