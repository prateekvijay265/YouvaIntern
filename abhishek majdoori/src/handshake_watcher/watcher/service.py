"""
handshake_watcher.watcher.service
=====================================

Core polling-loop orchestration — the heart of the application.

Responsibilities
----------------
1. Use :class:`~handshake_watcher.browser.BrowserSession` to fetch the
   projects page HTML on every iteration.
2. Pass the HTML to :func:`~handshake_watcher.scraper.parse_projects`.
3. Feed the result to :class:`~handshake_watcher.state.StateStore` to
   identify new projects.
4. Delegate notification to :class:`~handshake_watcher.notifier.WindowsNotifier`.
5. Sleep for ``poll_interval_seconds`` and repeat.

Graceful shutdown
-----------------
The ``run()`` coroutine responds to ``asyncio.CancelledError`` and
``KeyboardInterrupt`` — either will cause a clean teardown.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from handshake_watcher.browser import BrowserSession
from handshake_watcher.notifier import WindowsNotifier
from handshake_watcher.scraper import parse_projects
from handshake_watcher.state import StateStore

if TYPE_CHECKING:
    from handshake_watcher.config.settings import Settings

logger = logging.getLogger(__name__)


class WatcherService:
    """
    Orchestrates the polling loop that monitors Handshake for new projects.

    Parameters
    ----------
    settings:
        Fully resolved application settings.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._state = StateStore(settings)
        self._notifier = WindowsNotifier(settings)
        self._running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def run(self) -> None:
        """
        Start the polling loop and block until cancelled or interrupted.

        The loop:
        1. Fetches the Handshake projects page.
        2. Parses project listings.
        3. Diffs against known state and sends notifications for new ones.
        4. Sleeps for ``poll_interval_seconds``.
        5. Goto 1.
        """
        self._running = True
        logger.info(
            "WatcherService started. Polling %s every %ds.",
            self._settings.projects_url,
            self._settings.poll_interval_seconds,
        )

        try:
            while self._running:
                await self._poll_once()
                logger.debug(
                    "Sleeping for %d seconds.", self._settings.poll_interval_seconds
                )
                await asyncio.sleep(self._settings.poll_interval_seconds)
        except asyncio.CancelledError:
            logger.info("WatcherService received cancellation signal. Shutting down.")
            raise  # must re-raise so the task is marked cancelled
        except KeyboardInterrupt:
            logger.info("WatcherService interrupted by user. Shutting down.")
        finally:
            self._running = False
            logger.info("WatcherService stopped.")

    def stop(self) -> None:
        """Request the polling loop to stop after the current sleep."""
        logger.info("Stop requested.")
        self._running = False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    async def _poll_once(self) -> None:
        """Execute a single poll cycle: fetch → parse → diff → notify."""
        logger.info("Poll cycle starting...")
        try:
            async with BrowserSession(self._settings) as session:
                html = await session.get_page_html(self._settings.projects_url)

            projects = parse_projects(html)
            logger.info("Scraped %d project(s) from page.", len(projects))

            new_projects = self._state.diff_and_update(projects)
            if new_projects:
                logger.info(
                    "Notifying user of %d new project(s).", len(new_projects)
                )
                self._notifier.send_batch(new_projects)
            else:
                logger.info("No new projects this poll.")

        except asyncio.CancelledError:
            raise  # propagate cancellation
        except Exception:  # noqa: BLE001 — log and continue loop
            logger.error(
                "Unhandled exception during poll cycle; will retry after sleep.",
                exc_info=True,
            )
