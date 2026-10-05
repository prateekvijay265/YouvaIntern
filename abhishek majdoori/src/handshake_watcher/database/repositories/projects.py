"""
handshake_watcher.database.repositories.projects
=================================================

Repository for the ``projects`` table.

The ``projects`` table stores complete metadata for every project ever
scraped from Handshake. Each project is uniquely identified by its
``project_id`` (the natural key from the Handshake page).

CRUD summary
------------
- :meth:`save`          — INSERT or IGNORE a single project.
- :meth:`save_batch`    — Bulk INSERT or IGNORE (one transaction).
- :meth:`find_by_id`    — Fetch a project by its natural key.
- :meth:`get_recent`    — Fetch the N most recently seen projects.
- :meth:`get_all_ids`   — Return a frozenset of all known project IDs.
- :meth:`count`         — Total number of projects stored.
- :meth:`clear_all`     — Delete all rows (used by state-clear command).
- :meth:`mark_inactive` — Soft-delete a project.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from handshake_watcher.database.repositories.base import BaseRepository
from handshake_watcher.models import ProjectListing

if TYPE_CHECKING:
    from handshake_watcher.database.engine import DatabaseEngine

logger = logging.getLogger(__name__)


class ProjectRepository(BaseRepository):
    """CRUD for the ``projects`` table."""

    def __init__(self, engine: DatabaseEngine) -> None:
        super().__init__(engine)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------
    async def save(
        self,
        project: ProjectListing,
        poll_run_id: str | None = None,
    ) -> bool:
        """
        Insert *project* into the database.

        Uses ``INSERT OR IGNORE`` — if the project_id already exists the
        row is left unchanged and ``False`` is returned.

        Returns
        -------
        bool
            ``True`` if a new row was inserted, ``False`` if it already existed.
        """
        cursor = await self._engine.execute(
            """
            INSERT OR IGNORE INTO projects
                (project_id, title, url, company, location, deadline,
                 posted_at, first_seen_at, poll_run_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                project.project_id,
                project.title,
                project.url,
                project.company,
                project.location,
                project.deadline,
                project.posted_at.isoformat(),
                self._now(),
                poll_run_id,
            ),
        )
        inserted = cursor.rowcount > 0
        if inserted:
            logger.debug("Project saved: %s", project.project_id)
        return inserted

    async def save_batch(
        self,
        projects: list[ProjectListing],
        poll_run_id: str | None = None,
    ) -> int:
        """
        Insert a batch of projects in a single transaction.

        Returns
        -------
        int
            The number of new rows actually inserted (ignoring duplicates).
        """
        if not projects:
            return 0

        now = self._now()
        rows = [
            (
                p.project_id,
                p.title,
                p.url,
                p.company,
                p.location,
                p.deadline,
                p.posted_at.isoformat(),
                now,
                poll_run_id,
            )
            for p in projects
        ]

        inserted = 0
        async with self._engine.transaction():
            for row in rows:
                cursor = await self._engine.execute(
                    """
                    INSERT OR IGNORE INTO projects
                        (project_id, title, url, company, location, deadline,
                         posted_at, first_seen_at, poll_run_id, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    row,
                )
                if cursor.rowcount > 0:
                    inserted += 1

        logger.debug(
            "Batch saved %d/%d project(s).", inserted, len(projects)
        )
        return inserted

    async def mark_inactive(self, project_id: str) -> None:
        """Soft-delete a project by setting ``is_active = 0``."""
        await self._engine.execute(
            "UPDATE projects SET is_active = 0 WHERE project_id = ?",
            (project_id,),
        )

    async def clear_all(self) -> int:
        """
        Delete all rows from the ``projects`` table.

        Also removes dependent ``seen_projects`` rows via CASCADE.

        Returns
        -------
        int
            The number of rows deleted.
        """
        cursor = await self._engine.execute("DELETE FROM projects")
        count = cursor.rowcount
        logger.warning("All %d project(s) cleared from database.", count)
        return count

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------
    async def find_by_id(self, project_id: str) -> ProjectListing | None:
        """
        Return the :class:`ProjectListing` with the given ID, or ``None``.
        """
        row = await self._engine.fetch_one(
            "SELECT * FROM projects WHERE project_id = ?",
            (project_id,),
        )
        return self._row_to_listing(row) if row else None

    async def get_recent(self, limit: int = 20) -> list[ProjectListing]:
        """
        Return up to *limit* projects ordered by ``first_seen_at`` descending.
        """
        rows = await self._engine.fetch_all(
            "SELECT * FROM projects ORDER BY first_seen_at DESC LIMIT ?",
            (limit,),
        )
        return [self._row_to_listing(r) for r in rows]

    async def get_all_ids(self) -> frozenset[str]:
        """
        Return a frozenset of all project IDs in the database.

        This is the primary deduplication check used by the monitoring engine.
        The frozenset enables O(1) membership tests.
        """
        rows = await self._engine.fetch_all(
            "SELECT project_id FROM projects"
        )
        return frozenset(row[0] for row in rows)

    async def count(self) -> int:
        """Return the total number of projects in the database."""
        result = await self._engine.scalar("SELECT COUNT(*) FROM projects")
        return int(result or 0)

    async def count_active(self) -> int:
        """Return the number of active (not soft-deleted) projects."""
        result = await self._engine.scalar(
            "SELECT COUNT(*) FROM projects WHERE is_active = 1"
        )
        return int(result or 0)

    # ------------------------------------------------------------------
    # Private mapper
    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_listing(row: object) -> ProjectListing:
        """Convert a DB row (aiosqlite.Row) to a :class:`ProjectListing`."""
        import aiosqlite  # noqa: PLC0415
        r: aiosqlite.Row = row  # type: ignore[assignment]
        raw_posted = r["posted_at"]
        dt = datetime.fromisoformat(raw_posted)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return ProjectListing(
            project_id=r["project_id"],
            title=r["title"],
            url=r["url"],
            company=r["company"],
            location=r["location"],
            deadline=r["deadline"],
            posted_at=dt,
        )
