"""
tests/integration/test_watcher.py

Integration tests for handshake_watcher.watcher.service.WatcherService.

The browser and notifier are mocked so no real network calls are made.
These tests verify the watcher's orchestration logic end-to-end.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handshake_watcher.models import ProjectListing
from handshake_watcher.watcher.service import WatcherService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_settings(state_path: Path) -> MagicMock:
    mock = MagicMock()
    mock.projects_url = "https://app.joinhandshake.example.com/projects"
    mock.poll_interval_seconds = 30
    mock.notification_duration_seconds = 5
    mock.state_file_path = state_path
    mock.browser_headless = True
    mock.browser_timeout_ms = 5000
    mock.browser_storage_state_path = None
    return mock


def _make_html_with_projects(*project_ids: str) -> str:
    cards = "".join(
        f'<li data-id="{pid}"><h3>Project {pid}</h3><a href="/projects/{pid}">Link</a></li>'
        for pid in project_ids
    )
    return f"<html><body><ul>{cards}</ul></body></html>"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@pytest.mark.integration
class TestWatcherServiceOrchestration:
    """Verify that WatcherService correctly ties together all sub-layers."""

    @pytest.mark.asyncio
    async def test_new_projects_trigger_notifications(self, tmp_path: Path) -> None:
        """When new projects appear, the notifier must be called."""
        state_path = tmp_path / "state" / "seen.json"
        settings = _make_settings(state_path)

        mock_html = _make_html_with_projects("proj-alpha", "proj-beta")

        notifier_calls: list[str] = []

        with (
            patch(
                "handshake_watcher.watcher.service.BrowserSession"
            ) as MockSession,
            patch(
                "handshake_watcher.watcher.service.WindowsNotifier"
            ) as MockNotifier,
        ):
            # Configure async context manager mock
            mock_session_instance = AsyncMock()
            mock_session_instance.get_page_html = AsyncMock(return_value=mock_html)
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)

            # Capture send_batch calls
            mock_notifier_instance = MagicMock()
            MockNotifier.return_value = mock_notifier_instance

            def _capture_batch(projects: list[ProjectListing]) -> None:
                notifier_calls.extend(p.project_id for p in projects)

            mock_notifier_instance.send_batch.side_effect = _capture_batch

            service = WatcherService(settings)
            await service._poll_once()

        assert "proj-alpha" in notifier_calls
        assert "proj-beta" in notifier_calls

    @pytest.mark.asyncio
    async def test_known_projects_do_not_retrigger_notifications(
        self, tmp_path: Path
    ) -> None:
        """Projects seen in a prior poll must not cause a second notification."""
        state_path = tmp_path / "state" / "seen.json"
        settings = _make_settings(state_path)
        mock_html = _make_html_with_projects("proj-alpha")

        with (
            patch("handshake_watcher.watcher.service.BrowserSession") as MockSession,
            patch("handshake_watcher.watcher.service.WindowsNotifier") as MockNotifier,
        ):
            mock_session_instance = AsyncMock()
            mock_session_instance.get_page_html = AsyncMock(return_value=mock_html)
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)

            mock_notifier_instance = MagicMock()
            MockNotifier.return_value = mock_notifier_instance

            service = WatcherService(settings)

            # First poll — should notify
            await service._poll_once()
            assert mock_notifier_instance.send_batch.call_count == 1

            # Second poll — same project, no new notification
            await service._poll_once()
            assert mock_notifier_instance.send_batch.call_count == 1

    @pytest.mark.asyncio
    async def test_poll_error_does_not_crash_service(self, tmp_path: Path) -> None:
        """An exception during a poll cycle must be caught and logged, not propagated."""
        state_path = tmp_path / "state" / "seen.json"
        settings = _make_settings(state_path)

        with patch("handshake_watcher.watcher.service.BrowserSession") as MockSession:
            MockSession.return_value.__aenter__ = AsyncMock(
                side_effect=RuntimeError("Connection failed")
            )
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)

            service = WatcherService(settings)
            # Should not raise
            await service._poll_once()

    @pytest.mark.asyncio
    async def test_run_stops_when_cancelled(self, tmp_path: Path) -> None:
        """asyncio.CancelledError must cleanly stop the watcher loop."""
        state_path = tmp_path / "state" / "seen.json"
        settings = _make_settings(state_path)
        settings.poll_interval_seconds = 9999  # long sleep so cancel triggers quickly

        with patch("handshake_watcher.watcher.service.BrowserSession") as MockSession:
            mock_session = AsyncMock()
            mock_session.get_page_html = AsyncMock(return_value="<html></html>")
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)

            service = WatcherService(settings)
            task = asyncio.create_task(service.run())
            await asyncio.sleep(0.05)  # let one iteration start
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass  # expected — task was cleanly cancelled
            assert task.done()
