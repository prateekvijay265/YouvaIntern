"""
handshake_watcher.database.repositories
=========================================

Repository classes for every database table.

Each repository is injected with a :class:`~handshake_watcher.database.DatabaseEngine`
and provides typed async CRUD methods. No raw SQL outside these classes.

Public API
----------
    from handshake_watcher.database.repositories import (
        ProjectRepository,
        SeenProjectsRepository,
        NotificationRepository,
        SettingsRepository,
        LogRepository,
        StatisticsRepository,
        PollHistoryRepository,
    )
"""

from handshake_watcher.database.repositories.history import PollHistoryRepository
from handshake_watcher.database.repositories.logs import LogRepository
from handshake_watcher.database.repositories.notifications import NotificationRepository
from handshake_watcher.database.repositories.projects import ProjectRepository
from handshake_watcher.database.repositories.seen_projects import SeenProjectsRepository
from handshake_watcher.database.repositories.settings import SettingsRepository
from handshake_watcher.database.repositories.statistics import StatisticsRepository

__all__ = [
    "LogRepository",
    "NotificationRepository",
    "PollHistoryRepository",
    "ProjectRepository",
    "SeenProjectsRepository",
    "SettingsRepository",
    "StatisticsRepository",
]
