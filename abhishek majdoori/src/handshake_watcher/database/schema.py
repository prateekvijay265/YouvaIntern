"""
handshake_watcher.database.schema
===================================

All SQL DDL statements as named constants.

Every table, index, and relationship is defined exactly once here.
Repositories never contain raw CREATE TABLE SQL — they reference these
constants. When the schema changes, only this file and
``migrations.py`` need to change.

Naming conventions
------------------
- Tables  : snake_case plural  (``projects``, ``poll_history``)
- PKs     : ``<singular>_id`` for natural keys; ``id`` INTEGER for auto-increment
- Dates   : TEXT in ISO-8601 format (``2026-07-21T17:00:00+00:00``)
- Booleans: INTEGER 0/1 (SQLite has no BOOLEAN type)
- JSON    : TEXT columns suffixed ``_json``
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Table: schema_migrations
# Tracks which migration versions have been applied. Always created first.
# ---------------------------------------------------------------------------
CREATE_SCHEMA_MIGRATIONS = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER PRIMARY KEY,
    description TEXT    NOT NULL,
    applied_at  TEXT    NOT NULL
);
"""

# ---------------------------------------------------------------------------
# Table: projects
# Full data for every project ever scraped from Handshake.
# project_id is the natural key extracted from the page (never auto-generated).
# ---------------------------------------------------------------------------
CREATE_PROJECTS = """
CREATE TABLE IF NOT EXISTS projects (
    project_id   TEXT PRIMARY KEY,
    title        TEXT    NOT NULL,
    url          TEXT,
    company      TEXT,
    location     TEXT,
    deadline     TEXT,
    posted_at    TEXT    NOT NULL,
    first_seen_at TEXT   NOT NULL,
    poll_run_id  TEXT,
    is_active    INTEGER NOT NULL DEFAULT 1
);
"""

# ---------------------------------------------------------------------------
# Table: seen_projects
# Lightweight deduplication index. One row per unique project_id.
# Foreign key references projects(project_id); if a project is deleted,
# the seen record is also removed (CASCADE).
# ---------------------------------------------------------------------------
CREATE_SEEN_PROJECTS = """
CREATE TABLE IF NOT EXISTS seen_projects (
    project_id        TEXT    PRIMARY KEY
                      REFERENCES projects(project_id) ON DELETE CASCADE,
    first_seen_at     TEXT    NOT NULL,
    notification_sent INTEGER NOT NULL DEFAULT 0
);
"""

# ---------------------------------------------------------------------------
# Table: notifications
# Audit log of every notification dispatched (one row per adapter per project).
# ---------------------------------------------------------------------------
CREATE_NOTIFICATIONS = """
CREATE TABLE IF NOT EXISTS notifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id TEXT    UNIQUE NOT NULL,
    project_id      TEXT    REFERENCES projects(project_id) ON DELETE SET NULL,
    adapter_id      TEXT    NOT NULL,
    title           TEXT    NOT NULL,
    body            TEXT    NOT NULL,
    sent_at         TEXT    NOT NULL,
    success         INTEGER NOT NULL DEFAULT 1,
    error_message   TEXT
);
"""

# ---------------------------------------------------------------------------
# Table: app_settings
# Persistent key-value store for runtime configuration overrides.
# value_type allows typed round-tripping: 'str', 'int', 'float', 'bool', 'json'
# ---------------------------------------------------------------------------
CREATE_APP_SETTINGS = """
CREATE TABLE IF NOT EXISTS app_settings (
    key         TEXT PRIMARY KEY,
    value       TEXT    NOT NULL,
    value_type  TEXT    NOT NULL DEFAULT 'str',
    description TEXT,
    updated_at  TEXT    NOT NULL
);
"""

# ---------------------------------------------------------------------------
# Table: app_logs
# Circular buffer of recent structured log entries for the dashboard panel.
# Entries older than the configured max_rows are pruned automatically.
# ---------------------------------------------------------------------------
CREATE_APP_LOGS = """
CREATE TABLE IF NOT EXISTS app_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    level       TEXT    NOT NULL,
    logger_name TEXT    NOT NULL,
    message     TEXT    NOT NULL,
    context_json TEXT,
    exception   TEXT,
    poll_run_id TEXT
);
"""

# ---------------------------------------------------------------------------
# Table: statistics
# Named counters, gauges, and timing aggregates persisted across restarts.
# metric_type: 'counter' | 'gauge' | 'timing_sum' | 'timing_count'
# ---------------------------------------------------------------------------
CREATE_STATISTICS = """
CREATE TABLE IF NOT EXISTS statistics (
    metric_name TEXT    PRIMARY KEY,
    metric_type TEXT    NOT NULL,
    value       REAL    NOT NULL DEFAULT 0,
    updated_at  TEXT    NOT NULL
);
"""

# ---------------------------------------------------------------------------
# Table: poll_history
# One row per poll cycle. Enables failure-rate and duration analytics.
# ---------------------------------------------------------------------------
CREATE_POLL_HISTORY = """
CREATE TABLE IF NOT EXISTS poll_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_run_id   TEXT    UNIQUE NOT NULL,
    started_at    TEXT    NOT NULL,
    completed_at  TEXT,
    scraped_count INTEGER,
    new_count     INTEGER,
    duration_ms   INTEGER,
    success       INTEGER NOT NULL DEFAULT 0,
    error_type    TEXT,
    error_message TEXT
);
"""

# ---------------------------------------------------------------------------
# Indexes — all created after tables to avoid dependency ordering issues
# ---------------------------------------------------------------------------
INDEXES: list[str] = [
    # projects
    "CREATE INDEX IF NOT EXISTS idx_projects_first_seen ON projects(first_seen_at);",
    "CREATE INDEX IF NOT EXISTS idx_projects_company    ON projects(company);",
    "CREATE INDEX IF NOT EXISTS idx_projects_is_active  ON projects(is_active);",

    # poll_history
    "CREATE INDEX IF NOT EXISTS idx_poll_history_started_at ON poll_history(started_at);",
    "CREATE INDEX IF NOT EXISTS idx_poll_history_success    ON poll_history(success);",

    # notifications
    "CREATE INDEX IF NOT EXISTS idx_notifications_project_id ON notifications(project_id);",
    "CREATE INDEX IF NOT EXISTS idx_notifications_sent_at    ON notifications(sent_at);",
    "CREATE INDEX IF NOT EXISTS idx_notifications_adapter    ON notifications(adapter_id);",

    # app_logs
    "CREATE INDEX IF NOT EXISTS idx_app_logs_timestamp   ON app_logs(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_app_logs_level        ON app_logs(level);",
    "CREATE INDEX IF NOT EXISTS idx_app_logs_poll_run_id  ON app_logs(poll_run_id);",

    # statistics
    "CREATE INDEX IF NOT EXISTS idx_statistics_metric_type ON statistics(metric_type);",
]

# ---------------------------------------------------------------------------
# Ordered list of all DDL statements (tables first, indexes after)
# Used by MigrationManager for the initial schema migration.
# ---------------------------------------------------------------------------
INITIAL_SCHEMA_DDL: list[str] = [
    CREATE_SCHEMA_MIGRATIONS,
    CREATE_PROJECTS,
    CREATE_SEEN_PROJECTS,
    CREATE_NOTIFICATIONS,
    CREATE_APP_SETTINGS,
    CREATE_APP_LOGS,
    CREATE_STATISTICS,
    CREATE_POLL_HISTORY,
    *INDEXES,
]

# ---------------------------------------------------------------------------
# SQLite connection pragmas applied at every connect
# ---------------------------------------------------------------------------
CONNECTION_PRAGMAS: list[str] = [
    "PRAGMA journal_mode = WAL",        # enables concurrent readers
    "PRAGMA synchronous = NORMAL",      # durable enough, much faster than FULL
    "PRAGMA foreign_keys = ON",         # enforce referential integrity
    "PRAGMA cache_size = -8000",        # 8 MB page cache (negative = KiB)
    "PRAGMA temp_store = MEMORY",       # keep temp tables in RAM
    "PRAGMA mmap_size = 268435456",     # 256 MB memory-mapped I/O
]
