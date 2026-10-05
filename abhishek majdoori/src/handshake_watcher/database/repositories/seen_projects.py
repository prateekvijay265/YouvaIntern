"""
handshake_watcher.database.repositories.seen_projects
======================================================

Repository for the ``seen_projects`` deduplication table.

``seen_projects`` is a lightweight index over ``projects``. Every project
that has been processed by the monitoring engine has a row here.

The monitoring engine flow for each poll cycle is:
1. Scrape HTML → list of ProjectListing.
2. Call :meth:`get_all_seen_ids` → frozenset of already-processed IDs.
3. Diff scraped against seen → new_projects.
4. For each new project:
   a. ``ProjectRepository.save(project)``    — persist full data.
   b. ``SeenProjectsRepository.mark_seen(project_id)`` — record seen status.
   c. ``NotificationManager.notify(project)`` — dispatch notification.
5. Call :meth:`mark_notification_sent` after successful dispatch.

CRUD summary
------------
- :meth:`mark_seen`              — Insert a project_id as seen.
- :meth:`mark_seen_batch`        — Bulk mark seen in one transaction.
- :meth:`mark_notification_sent` — Set the notification_sent flag to True.
- :meth:`get_all_seen_ids`       — Fast frozenset of all seen IDs.
- :meth:`is_seen`                — Check a single project_id.
- :meth:`count`                  — Total seen project count.
- :meth:`clear_all`              — Reset the deduplication table.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from handshake_watcher.database.repositories.base import BaseRepository

if TYPE_CHECKING:
    from handshake_watcher.database.engine import DatabaseEngine

logger = logging.getLogger(__name__)


class SeenProjectsRepository(BaseRepository):
    """CRUD for the ``seen_projects`` deduplication table."""

    def __init__(self, engine: DatabaseEngine) -> None:
        super().__init__(engine)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------
    async def mark_seen(
        self,
        project_id: str,
        notification_sent: bool = False,
    ) -> bool:
        """
        Record that *project_id* has been processed.

        Uses ``INSERT OR IGNORE`` — safe to call multiple times for the
        same ID.

        Returns
        -------
        bool
            ``True`` if a new row was inserted, ``False`` if already seen.
        """
        cursor = await self._engine.execute(
            """
            INSERT OR IGNORE INTO seen_projects
                (project_id, first_seen_at, notification_sent)
            VALUES (?, ?, ?)
            """,
            (
                project_id,
                self._now(),
                self._bool_to_int(notification_sent),
            ),
        )
        return cursor.rowcount > 0

    async def mark_seen_batch(
        self,
        project_ids: list[str],
        notification_sent: bool = False,
    ) -> int:
        """
        Mark multiple project IDs as seen in a single transaction.

        Returns
        -------
        int
            The number of new rows inserted.
        """
        if not project_ids:
            return 0

        now = self._now()
        flag = self._bool_to_int(notification_sent)
        inserted = 0

        async with self._engine.transaction():
            for pid in project_ids:
                cursor = await self._engine.execute(
                    """
                    INSERT OR IGNORE INTO seen_projects
                        (project_id, first_seen_at, notification_sent)
                    VALUES (?, ?, ?)
                    """,
                    (pid, now, flag),
                )
                if cursor.rowcount > 0:
                    inserted += 1

        logger.debug("Batch marked %d/%d ID(s) as seen.", inserted, len(project_ids))
        return inserted

    async def mark_notification_sent(self, project_id: str) -> None:
        """Set ``notification_sent = 1`` for the given project."""
        await self._engine.execute(
            "UPDATE seen_projects SET notification_sent = 1 WHERE project_id = ?",
            (project_id,),
        )

    async def clear_all(self) -> int:
        """
        Delete all rows from ``seen_projects``.

        After this call, every project will appear "new" on the next poll.

        Returns
        -------
        int
            The number of rows deleted.
        """
        cursor = await self._engine.execute("DELETE FROM seen_projects")
        count = cursor.rowcount
        logger.warning("Seen-projects table cleared (%d row(s) removed).", count)
        return count

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------
    async def get_all_seen_ids(self) -> frozenset[str]:
        """
        Return all seen project IDs as an immutable frozenset.

        This is the primary deduplication mechanism used by the monitoring
        engine. frozenset enables O(1) membership tests.
        """
        rows = await self._engine.fetch_all(
            "SELECT project_id FROM seen_projects"
        )
        return frozenset(row[0] for row in rows)

    async def is_seen(self, project_id: str) -> bool:
        """Return ``True`` if *project_id* has been marked as seen."""
        row = await self._engine.fetch_one(
            "SELECT 1 FROM seen_projects WHERE project_id = ?",
            (project_id,),
        )
        return row is not None

    async def notification_was_sent(self, project_id: str) -> bool:
        """Return ``True`` if a notification has been dispatched for *project_id*."""
        row = await self._engine.fetch_one(
            "SELECT notification_sent FROM seen_projects WHERE project_id = ?",
            (project_id,),
        )
        if row is None:
            return False
        return self._int_to_bool(row[0])

    async def count(self) -> int:
        """Return the total number of seen project IDs."""
        result = await self._engine.scalar("SELECT COUNT(*) FROM seen_projects")
        return int(result or 0)

    async def count_notified(self) -> int:
        """Return the number of projects for which a notification was sent."""
        result = await self._engine.scalar(
            "SELECT COUNT(*) FROM seen_projects WHERE notification_sent = 1"
        )
        return int(result or 0)
