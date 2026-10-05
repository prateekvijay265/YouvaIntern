"""
handshake_watcher.database.repositories.notifications
======================================================

Repository for the ``notifications`` audit log table.

Every time the notification manager dispatches a toast (or any other
adapter), a row is inserted here — regardless of whether the dispatch
succeeded. This provides a complete, tamper-evident audit trail.

CRUD summary
------------
- :meth:`save`              — Record a notification attempt.
- :meth:`find_by_id`        — Retrieve a single notification record.
- :meth:`get_for_project`   — All notifications for a given project_id.
- :meth:`get_recent`        — N most-recent notification records.
- :meth:`count_successful`  — Count of successful dispatches.
- :meth:`count_failed`      — Count of failed dispatches.
- :meth:`count`             — Total notification count.
- :meth:`clear_all`         — Delete all records (testing / reset).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from handshake_watcher.database.repositories.base import BaseRepository

if TYPE_CHECKING:
    import aiosqlite
    from handshake_watcher.database.engine import DatabaseEngine

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class NotificationRecord:
    """
    An immutable record of a single notification dispatch attempt.

    Attributes
    ----------
    notification_id:
        UUID string generated at dispatch time. Unique per row.
    project_id:
        The project for which the notification was sent.
    adapter_id:
        Which channel was used (e.g. ``"windows_toast"``).
    title:
        The notification title as displayed to the user.
    body:
        The notification body as displayed to the user.
    sent_at:
        UTC timestamp of the dispatch attempt.
    success:
        ``True`` if the adapter reported success.
    error_message:
        Error detail if ``success`` is ``False``, else ``None``.
    """

    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str | None = None
    adapter_id: str = "unknown"
    title: str = ""
    body: str = ""
    sent_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    success: bool = True
    error_message: str | None = None


class NotificationRepository(BaseRepository):
    """CRUD for the ``notifications`` audit table."""

    def __init__(self, engine: DatabaseEngine) -> None:
        super().__init__(engine)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------
    async def save(self, record: NotificationRecord) -> None:
        """
        Persist a notification record.

        Uses ``INSERT OR IGNORE`` on the ``notification_id`` unique key,
        so retrying a dispatch will not create duplicate rows.
        """
        await self._engine.execute(
            """
            INSERT OR IGNORE INTO notifications
                (notification_id, project_id, adapter_id, title, body,
                 sent_at, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.notification_id,
                record.project_id,
                record.adapter_id,
                record.title,
                record.body,
                record.sent_at.isoformat(),
                self._bool_to_int(record.success),
                record.error_message,
            ),
        )
        logger.debug(
            "Notification recorded: id=%s adapter=%s success=%s",
            record.notification_id,
            record.adapter_id,
            record.success,
        )

    async def clear_all(self) -> int:
        """
        Delete all notification records.

        Returns
        -------
        int
            Number of rows deleted.
        """
        cursor = await self._engine.execute("DELETE FROM notifications")
        count = cursor.rowcount
        logger.warning("Notifications table cleared (%d row(s) removed).", count)
        return count

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------
    async def find_by_id(self, notification_id: str) -> NotificationRecord | None:
        """Return the notification with the given UUID, or ``None``."""
        row = await self._engine.fetch_one(
            "SELECT * FROM notifications WHERE notification_id = ?",
            (notification_id,),
        )
        return self._row_to_record(row) if row else None

    async def get_for_project(self, project_id: str) -> list[NotificationRecord]:
        """Return all notification records for the given *project_id*."""
        rows = await self._engine.fetch_all(
            "SELECT * FROM notifications WHERE project_id = ? ORDER BY sent_at DESC",
            (project_id,),
        )
        return [self._row_to_record(r) for r in rows]

    async def get_recent(self, limit: int = 50) -> list[NotificationRecord]:
        """Return up to *limit* most recent notification records."""
        rows = await self._engine.fetch_all(
            "SELECT * FROM notifications ORDER BY sent_at DESC LIMIT ?",
            (limit,),
        )
        return [self._row_to_record(r) for r in rows]

    async def count(self) -> int:
        """Return total number of notification records."""
        result = await self._engine.scalar("SELECT COUNT(*) FROM notifications")
        return int(result or 0)

    async def count_successful(self) -> int:
        """Return the count of successful notification dispatches."""
        result = await self._engine.scalar(
            "SELECT COUNT(*) FROM notifications WHERE success = 1"
        )
        return int(result or 0)

    async def count_failed(self) -> int:
        """Return the count of failed notification dispatches."""
        result = await self._engine.scalar(
            "SELECT COUNT(*) FROM notifications WHERE success = 0"
        )
        return int(result or 0)

    # ------------------------------------------------------------------
    # Private mapper
    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_record(row: object) -> NotificationRecord:
        import aiosqlite as _aiosqlite  # noqa: PLC0415
        r: _aiosqlite.Row = row  # type: ignore[assignment]
        raw_dt = r["sent_at"]
        dt = datetime.fromisoformat(raw_dt)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return NotificationRecord(
            notification_id=r["notification_id"],
            project_id=r["project_id"],
            adapter_id=r["adapter_id"],
            title=r["title"],
            body=r["body"],
            sent_at=dt,
            success=bool(r["success"]),
            error_message=r["error_message"],
        )
