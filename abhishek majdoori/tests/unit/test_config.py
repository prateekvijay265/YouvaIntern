"""
tests/unit/test_config.py

Unit tests for handshake_watcher.config.settings.Settings.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from handshake_watcher.config.settings import Settings


class TestSettingsDefaults:
    """Settings should load cleanly with only the required field provided."""

    def test_defaults_are_applied(self, minimal_env: None) -> None:
        s = Settings()  # type: ignore[call-arg]
        # minimal_env overrides POLL_INTERVAL_SECONDS to 30
        assert s.poll_interval_seconds == 30
        assert s.browser_headless is True
        assert s.log_level == "DEBUG"  # minimal_env sets LOG_LEVEL=DEBUG
        assert s.browser_storage_state_path is None

    def test_projects_url_is_correctly_derived(self, minimal_env: None) -> None:
        s = Settings()  # type: ignore[call-arg]
        url = s.projects_url
        assert url.startswith("https://")
        assert url.endswith("/projects")

    def test_trailing_slash_stripped_from_projects_path(
        self, monkeypatch: pytest.MonkeyPatch, minimal_env: None
    ) -> None:
        monkeypatch.setenv("HANDSHAKE_PROJECTS_PATH", "/projects/")
        s = Settings()  # type: ignore[call-arg]
        assert not s.handshake_projects_path.endswith("/")


class TestSettingsValidation:
    """Invalid values should raise ValidationError at construction time."""

    def test_missing_base_url_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(handshake_base_url=None)  # type: ignore[arg-type]

    def test_poll_interval_too_low_raises(
        self, monkeypatch: pytest.MonkeyPatch, minimal_env: None
    ) -> None:
        monkeypatch.setenv("POLL_INTERVAL_SECONDS", "10")
        with pytest.raises(ValidationError):
            Settings()  # type: ignore[call-arg]

    def test_poll_interval_too_high_raises(
        self, monkeypatch: pytest.MonkeyPatch, minimal_env: None
    ) -> None:
        monkeypatch.setenv("POLL_INTERVAL_SECONDS", "99999")
        with pytest.raises(ValidationError):
            Settings()  # type: ignore[call-arg]

    def test_invalid_log_level_raises(
        self, monkeypatch: pytest.MonkeyPatch, minimal_env: None
    ) -> None:
        monkeypatch.setenv("LOG_LEVEL", "VERBOSE")
        with pytest.raises(ValidationError):
            Settings()  # type: ignore[call-arg]


class TestSettingsEnvironmentOverride:
    """Environment variables should override defaults correctly."""

    def test_poll_interval_override(
        self, monkeypatch: pytest.MonkeyPatch, minimal_env: None
    ) -> None:
        monkeypatch.setenv("POLL_INTERVAL_SECONDS", "120")
        s = Settings()  # type: ignore[call-arg]
        assert s.poll_interval_seconds == 120

    def test_empty_storage_state_path_becomes_none(
        self, monkeypatch: pytest.MonkeyPatch, minimal_env: None
    ) -> None:
        monkeypatch.setenv("BROWSER_STORAGE_STATE_PATH", "")
        s = Settings()  # type: ignore[call-arg]
        assert s.browser_storage_state_path is None

    def test_headless_can_be_disabled(
        self, monkeypatch: pytest.MonkeyPatch, minimal_env: None
    ) -> None:
        monkeypatch.setenv("BROWSER_HEADLESS", "false")
        s = Settings()  # type: ignore[call-arg]
        assert s.browser_headless is False
