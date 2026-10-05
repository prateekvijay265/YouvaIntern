"""
handshake_watcher.notifier.windows
=====================================

Windows desktop notification sender using ``plyer``.

Design decisions
----------------
* ``plyer.notification.notify()`` is called in a thread-safe manner via
  ``asyncio.get_event_loop().run_in_executor()`` from the watcher service,
  since plyer is a synchronous library.
* Notification text is truncated to 256 characters to respect Windows
  toast limits.
* All exceptions are caught and logged — a notification failure must never
  crash the watcher loop.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from handshake_watcher.models import ProjectListing

if TYPE_CHECKING:
    from handshake_watcher.config.settings import Settings

logger = logging.getLogger(__name__)

# Windows toast limits
_MAX_TITLE_LEN = 64
_MAX_MESSAGE_LEN = 256


class WindowsNotifier:
    """
    Sends Windows desktop toast notifications for new project listings.

    Parameters
    ----------
    settings:
        Resolved application settings. Uses ``notification_duration_seconds``.
    app_icon:
        Optional path to a ``.ico`` file for the toast icon.
    """

    def __init__(
        self,
        settings: Settings,
        app_icon: Path | None = None,
    ) -> None:
        self._duration = settings.notification_duration_seconds
        self._app_icon = str(app_icon) if app_icon else ""

    def send(self, project: ProjectListing) -> None:
        """
        Send a Windows toast notification for *project*.

        Parameters
        ----------
        project:
            The newly detected :class:`~handshake_watcher.models.ProjectListing`
            to announce.
        """
        title = self._format_title(project)
        message = self._format_message(project)

        logger.debug(
            "Sending notification: title=%r message=%r", title, message
        )

        try:
            from plyer import notification  # local import — optional dep

            notification.notify(
                title=title,
                message=message,
                app_name="Handshake Watcher",
                app_icon=self._app_icon,
                timeout=self._duration,
                toast=True,
            )
            logger.info("Notification sent for project: %s", project.project_id)
        except Exception:  # noqa: BLE001 — never crash the watcher
            logger.warning(
                "Failed to send notification for project %s",
                project.project_id,
                exc_info=True,
            )

    def send_batch(self, projects: list[ProjectListing]) -> None:
        """
        Send notifications for a list of new projects.

        Parameters
        ----------
        projects:
            Projects to announce. Each gets its own toast.
        """
        for project in projects:
            self.send(project)

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _format_title(project: ProjectListing) -> str:
        title = f"🔔 New Project: {project.title}"
        return title[:_MAX_TITLE_LEN]

    @staticmethod
    def _format_message(project: ProjectListing) -> str:
        parts: list[str] = []
        if project.company:
            parts.append(f"Company: {project.company}")
        if project.location:
            parts.append(f"Location: {project.location}")
        if project.deadline:
            parts.append(f"Deadline: {project.deadline}")
        message = "\n".join(parts) if parts else "Check Handshake for details."
        return message[:_MAX_MESSAGE_LEN]
