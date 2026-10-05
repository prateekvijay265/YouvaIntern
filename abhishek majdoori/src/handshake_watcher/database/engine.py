"""
handshake_watcher.database.engine
===================================

Async SQLite connection manager with automatic schema migration.

The :class:`DatabaseEngine` is the single entry point for all database
access. It owns the ``aiosqlite`` connection, applies pragmas, runs
migrations, and exposes convenience helpers used by every repository.

Usage
-----
    # As an async context manager (recommended):
    async with DatabaseEngine(db_path) as engine:
        repo = ProjectRepository(engine)
        await repo.save(project)

    # Or manually:
    engine = DatabaseEngine(db_path)
    await engine.initialize()
    try:
        ...
    finally:
        await engine.close()

Thread safety
-------------
aiosqlite is async-safe within a single asyncio event loop. Do NOT share a
:class:`DatabaseEngine` across threads. Create one engine per event loop.

Connection settings
-------------------
- ``isolation_level=None`` → autocommit mode. All transactions are managed
  explicitly using ``BEGIN`` / ``COMMIT`` / ``ROLLBACK``.
- WAL journal mode allows concurrent readers with a single writer.
- Foreign keys are enforced at the connection level.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiosqlite

from handshake_watcher.database.schema import CONNECTION_PRAGMAS

logger = logging.getLogger(__name__)


class DatabaseEngine:
    """
    Lifecycle manager for the aiosqlite connection.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file. Parent directories are created
        automatically during :meth:`initialize`.
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._connection: aiosqlite.Connection | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def initialize(self) -> None:
        """
        Open the database connection, apply pragmas, and run pending migrations.

        Safe to call on every application startup — migrations are idempotent.
        """
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Opening database: %s", self._db_path)

        # isolation_level=None → we manage transactions explicitly with BEGIN/COMMIT
        self._connection = await aiosqlite.connect(
            self._db_path,
            isolation_level=None,
        )
        # Return dict-like rows for named column access
        self._connection.row_factory = aiosqlite.Row

        await self._apply_pragmas()
        await self._run_migrations()

        logger.info("Database ready: %s", self._db_path)

    async def close(self) -> None:
        """Close the database connection gracefully."""
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
            logger.debug("Database connection closed.")

    # ------------------------------------------------------------------
    # Context-manager protocol
    # ------------------------------------------------------------------
    async def __aenter__(self) -> DatabaseEngine:
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Public helpers — used by repositories
    # ------------------------------------------------------------------
    @property
    def connection(self) -> aiosqlite.Connection:
        """Return the active connection; raises if not initialised."""
        if self._connection is None:
            raise RuntimeError(
                "DatabaseEngine is not initialised. Call initialize() first."
            )
        return self._connection

    async def execute(
        self,
        sql: str,
        params: tuple[Any, ...] | None = None,
    ) -> aiosqlite.Cursor:
        """
        Execute a single SQL statement and return its cursor.

        For INSERT/UPDATE/DELETE the cursor exposes ``lastrowid`` and
        ``rowcount``. For SELECT, use :meth:`fetch_one` or :meth:`fetch_all`.
        """
        return await self.connection.execute(sql, params or ())

    async def execute_many(
        self,
        sql: str,
        params_seq: list[tuple[Any, ...]],
    ) -> None:
        """Execute the same SQL statement for each tuple in *params_seq*."""
        await self.connection.executemany(sql, params_seq)

    async def fetch_one(
        self,
        sql: str,
        params: tuple[Any, ...] | None = None,
    ) -> aiosqlite.Row | None:
        """Return the first matching row, or ``None`` if no rows found."""
        async with self.connection.execute(sql, params or ()) as cursor:
            return await cursor.fetchone()

    async def fetch_all(
        self,
        sql: str,
        params: tuple[Any, ...] | None = None,
    ) -> list[aiosqlite.Row]:
        """Return all matching rows as a list."""
        async with self.connection.execute(sql, params or ()) as cursor:
            return await cursor.fetchall()

    async def scalar(
        self,
        sql: str,
        params: tuple[Any, ...] | None = None,
        default: Any = None,
    ) -> Any:
        """
        Return the first column of the first row, or *default* if no rows.

        Useful for COUNT / SUM / MAX / COALESCE queries.
        """
        row = await self.fetch_one(sql, params)
        return row[0] if row is not None else default

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        """
        Async context manager that wraps a block of SQL in a transaction.

        On success the transaction is committed; on exception it is rolled back.

        Example
        -------
            async with engine.transaction():
                await engine.execute("INSERT INTO projects ...", (...,))
                await engine.execute("INSERT INTO seen_projects ...", (...,))
        """
        conn = self.connection
        await conn.execute("BEGIN DEFERRED")
        try:
            yield
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    async def table_exists(self, table_name: str) -> bool:
        """Return True if *table_name* exists in the database."""
        row = await self.fetch_one(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return row is not None

    async def row_count(self, table_name: str) -> int:
        """Return the number of rows in *table_name*."""
        result: Any = await self.scalar(
            f"SELECT COUNT(*) FROM {table_name}"  # noqa: S608
        )
        return int(result or 0)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    async def _apply_pragmas(self) -> None:
        """Apply the standard set of performance and safety pragmas."""
        conn = self.connection
        for pragma in CONNECTION_PRAGMAS:
            await conn.execute(pragma)
        # WAL requires a commit to take effect
        await conn.commit()
        logger.debug("Database pragmas applied.")

    async def _run_migrations(self) -> None:
        """Delegate schema migration to :class:`MigrationManager`."""
        # Import here to avoid circular import (migrations imports engine)
        from handshake_watcher.database.migrations import MigrationManager  # noqa: PLC0415
        manager = MigrationManager(self)
        await manager.run_pending()
