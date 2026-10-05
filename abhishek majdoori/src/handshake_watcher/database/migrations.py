"""
handshake_watcher.database.migrations
=======================================

Schema migration system for SQLite.

Each migration is a versioned, description-tagged unit of SQL that runs
exactly once in ascending version order. The ``schema_migrations`` table
tracks which versions have been applied.

Design
------
- **Idempotent**: Running ``run_pending()`` on an up-to-date database is a
  no-op. It is safe to call on every application startup.
- **Forward-only**: Only ``up_sql`` is required. ``down_sql`` is recorded
  for documentation purposes but rollback is not implemented (SQLite does
  not support transactional DDL rollback reliably).
- **Transactional**: Each migration runs inside its own transaction. If the
  SQL fails, the transaction is rolled back and the error propagates.
- **Ordered**: Migrations are applied in strict ascending version order.

Adding a new migration
----------------------
Append a new :class:`Migration` to :data:`ALL_MIGRATIONS` with the next
sequential version number. Never edit or delete existing migrations.

    Migration(
        version=2,
        description="Add column projects.tags",
        up_sql=\"\"\"
            ALTER TABLE projects ADD COLUMN tags TEXT;
        \"\"\",
    )
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from handshake_watcher.database.schema import INITIAL_SCHEMA_DDL

if TYPE_CHECKING:
    from handshake_watcher.database.engine import DatabaseEngine

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Migration:
    """
    A single, versioned schema change.

    Attributes
    ----------
    version:
        Monotonically increasing integer. Must be unique across all migrations.
    description:
        Human-readable description stored in ``schema_migrations``.
    up_sql:
        One or more semicolon-separated SQL statements to apply.
    down_sql:
        Optional reverse SQL (for documentation only; not executed).
    """

    version: int
    description: str
    up_sql: str
    down_sql: str = field(default="-- no rollback defined")


# ---------------------------------------------------------------------------
# Migration registry — append new migrations here; NEVER edit existing ones
# ---------------------------------------------------------------------------
ALL_MIGRATIONS: list[Migration] = [
    Migration(
        version=1,
        description="Initial schema: projects, seen_projects, notifications, "
                    "app_settings, app_logs, statistics, poll_history, indexes",
        up_sql="\n".join(INITIAL_SCHEMA_DDL),
        down_sql=(
            "DROP TABLE IF EXISTS poll_history;\n"
            "DROP TABLE IF EXISTS statistics;\n"
            "DROP TABLE IF EXISTS app_logs;\n"
            "DROP TABLE IF EXISTS app_settings;\n"
            "DROP TABLE IF EXISTS notifications;\n"
            "DROP TABLE IF EXISTS seen_projects;\n"
            "DROP TABLE IF EXISTS projects;\n"
            "DROP TABLE IF EXISTS schema_migrations;\n"
        ),
    ),
    # ---- future migrations go here ----
    # Migration(
    #     version=2,
    #     description="Add projects.tags column",
    #     up_sql="ALTER TABLE projects ADD COLUMN tags TEXT;",
    # ),
]


class MigrationManager:
    """
    Applies pending schema migrations to the database.

    Parameters
    ----------
    engine:
        An initialised (but not yet migrated) :class:`DatabaseEngine`.
    """

    def __init__(self, engine: DatabaseEngine) -> None:
        self._engine = engine

    async def run_pending(self) -> None:
        """
        Apply all migrations whose version exceeds the current schema version.

        This method is idempotent — safe to call every time the application
        starts. It creates the ``schema_migrations`` table if it does not
        already exist, then applies any unapplied migrations in order.
        """
        # Bootstrap: ensure the tracking table exists before querying it
        await self._bootstrap()

        current_version = await self._current_version()
        pending = [m for m in ALL_MIGRATIONS if m.version > current_version]

        if not pending:
            logger.debug(
                "Schema is up to date (version=%d).", current_version
            )
            return

        logger.info(
            "Applying %d pending migration(s). Current version: %d.",
            len(pending),
            current_version,
        )

        for migration in sorted(pending, key=lambda m: m.version):
            await self._apply(migration)

        final_version = await self._current_version()
        logger.info("Schema migration complete. Version: %d.", final_version)

    async def current_version(self) -> int:
        """Return the currently applied schema version (0 if none)."""
        return await self._current_version()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    async def _bootstrap(self) -> None:
        """
        Create the ``schema_migrations`` tracking table unconditionally.

        This DDL must execute even before migration 1 is applied, so we
        run it directly rather than as part of a migration.
        """
        from handshake_watcher.database.schema import CREATE_SCHEMA_MIGRATIONS
        conn = self._engine.connection
        await conn.execute(CREATE_SCHEMA_MIGRATIONS)
        await conn.commit()

    async def _current_version(self) -> int:
        """Query the highest applied migration version."""
        conn = self._engine.connection
        async with conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM schema_migrations"
        ) as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def _apply(self, migration: Migration) -> None:
        """
        Execute *migration* inside a transaction.

        Each SQL statement in ``up_sql`` is executed sequentially. On failure
        the whole transaction rolls back and ``MigrationError`` is raised.
        """
        logger.info(
            "Applying migration v%d: %s", migration.version, migration.description
        )
        conn = self._engine.connection

        # aiosqlite isolation_level=None → manual transaction management
        await conn.execute("BEGIN")
        try:
            # Split on semicolons; skip blank statements
            statements = [
                s.strip()
                for s in migration.up_sql.split(";")
                if s.strip()
            ]
            for stmt in statements:
                await conn.execute(stmt)

            await conn.execute(
                "INSERT INTO schema_migrations (version, description, applied_at) "
                "VALUES (?, ?, ?)",
                (
                    migration.version,
                    migration.description,
                    datetime.now(tz=timezone.utc).isoformat(),
                ),
            )
            await conn.commit()
            logger.debug("Migration v%d applied successfully.", migration.version)
        except Exception:
            await conn.rollback()
            logger.error(
                "Migration v%d failed. Transaction rolled back.",
                migration.version,
                exc_info=True,
            )
            raise
