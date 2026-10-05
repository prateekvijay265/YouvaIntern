"""
handshake_watcher.database
===========================

Production SQLite database layer for the Handshake Project Watcher.

Tables
------
  projects          — Every project ever scraped from Handshake.
  seen_projects     — Lightweight deduplication index (project_id + flag).
  notifications     — Audit log of every notification dispatched.
  app_settings      — Persistent key-value configuration store.
  app_logs          — Recent structured log entries for the dashboard.
  statistics        — Named counters, gauges, and timing aggregates.
  poll_history      — Full record of every poll cycle.
  schema_migrations — Migration version tracking.

Public API
----------
    from handshake_watcher.database import DatabaseEngine
    from handshake_watcher.database.repositories import (
        ProjectRepository,
        SeenProjectsRepository,
        NotificationRepository,
        SettingsRepository,
        LogRepository,
        StatisticsRepository,
        PollHistoryRepository,
    )

    async with DatabaseEngine(db_path) as engine:
        repo = ProjectRepository(engine)
        await repo.save(project)
"""

from handshake_watcher.database.engine import DatabaseEngine

__all__ = ["DatabaseEngine"]
