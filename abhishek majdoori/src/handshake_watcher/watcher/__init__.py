"""
handshake_watcher.watcher
==========================

Polling-loop orchestration layer.

The :class:`WatcherService` ties together the browser, scraper, state store,
and notifier into a single ``run()`` coroutine that loops indefinitely,
sleeping for ``poll_interval_seconds`` between iterations.

Public API
----------
    from handshake_watcher.watcher import WatcherService

    service = WatcherService(settings)
    await service.run()      # blocks until cancelled / shutdown signal
"""

from handshake_watcher.watcher.service import WatcherService

__all__ = ["WatcherService"]
