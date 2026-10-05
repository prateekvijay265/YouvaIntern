"""
tests/unit/test_notifier.py

Unit tests for handshake_watcher.notifier.windows.WindowsNotifier.

plyer.notification.notify is mocked throughout — no actual OS notifications
are sent during testing.
"""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from handshake_watcher.models import ProjectListing
from handshake_watcher.notifier.windows import (
    WindowsNotifier,
    _MAX_MESSAGE_LEN,
    _MAX_TITLE_LEN,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_settings(duration: int = 5) -> MagicMock:
    mock = MagicMock()
    mock.notification_duration_seconds = duration
    return mock


def _make_project(**kwargs: object) -> ProjectListing:
    defaults = {
        "project_id": "test-notif-001",
        "title": "Test Project",
        "company": "Acme",
        "location": "Remote",
        "deadline": "2026-09-01",
    }
    defaults.update(kwargs)
    return ProjectListing(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# WindowsNotifier.send
# ---------------------------------------------------------------------------
class TestWindowsNotifierSend:
    def test_send_calls_notify(self) -> None:
        """plyer.notification.notify should be called once per send()."""
        notifier = WindowsNotifier(_make_settings())
        project = _make_project()

        # Build a fake plyer module with a notification sub-object
        fake_notification = MagicMock()
        fake_plyer = ModuleType("plyer")
        fake_plyer.notification = fake_notification  # type: ignore[attr-defined]

        with patch.dict(sys.modules, {"plyer": fake_plyer}):
            notifier.send(project)

        fake_notification.notify.assert_called_once()

    def test_send_does_not_raise_when_plyer_missing(self) -> None:
        """If plyer raises on import, send() should log a warning, not crash."""
        notifier = WindowsNotifier(_make_settings())
        project = _make_project()

        # Simulate ImportError by removing plyer from sys.modules
        saved = sys.modules.pop("plyer", None)
        try:
            # Should swallow the ImportError / AttributeError
            notifier.send(project)
        finally:
            if saved is not None:
                sys.modules["plyer"] = saved

    def test_send_batch_calls_send_for_each_project(self) -> None:
        """send_batch should call send() once per project."""
        notifier = WindowsNotifier(_make_settings())
        projects = [_make_project(project_id=f"p{i}", title=f"P{i}") for i in range(3)]
        call_count = 0

        def _mock_send(p: ProjectListing) -> None:
            nonlocal call_count
            call_count += 1

        notifier.send = _mock_send  # type: ignore[method-assign]
        notifier.send_batch(projects)
        assert call_count == 3


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
class TestNotificationFormatting:
    def test_title_is_truncated_to_max_length(self) -> None:
        long_title = "X" * 200
        project = _make_project(title=long_title)
        result = WindowsNotifier._format_title(project)
        assert len(result) <= _MAX_TITLE_LEN

    def test_message_is_truncated_to_max_length(self) -> None:
        long_company = "Acme " * 100
        project = _make_project(company=long_company)
        result = WindowsNotifier._format_message(project)
        assert len(result) <= _MAX_MESSAGE_LEN

    def test_title_includes_project_title(self) -> None:
        project = _make_project(title="My Awesome Project")
        result = WindowsNotifier._format_title(project)
        assert "My Awesome Project" in result

    def test_message_includes_company(self) -> None:
        project = _make_project(company="Skynet Labs")
        result = WindowsNotifier._format_message(project)
        assert "Skynet Labs" in result

    def test_message_fallback_when_no_metadata(self) -> None:
        project = ProjectListing(project_id="bare", title="Bare Project")
        result = WindowsNotifier._format_message(project)
        assert result  # non-empty fallback
