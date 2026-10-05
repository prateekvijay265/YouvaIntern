"""
tests/conftest.py

Shared pytest fixtures available to all test modules.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from handshake_watcher.models import ProjectListing


# ---------------------------------------------------------------------------
# Plyer stub — prevent any real OS notification calls in tests
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True, scope="session")
def mock_plyer_notification() -> None:
    """
    Replace the plyer module with a MagicMock for the entire test session.

    This prevents real Windows balloon-tip notifications from firing during
    tests, which would cause Shell_NotifyIconW thread exceptions in headless
    / CI environments.
    """
    import sys

    fake_notification = MagicMock()
    fake_plyer = ModuleType("plyer")
    fake_plyer.notification = fake_notification  # type: ignore[attr-defined]

    # Only inject if plyer is not already a proper stub
    real_plyer = sys.modules.get("plyer")
    sys.modules["plyer"] = fake_plyer
    yield
    # Restore
    if real_plyer is not None:
        sys.modules["plyer"] = real_plyer
    else:
        sys.modules.pop("plyer", None)

# ---------------------------------------------------------------------------
# Settings fixture — always uses a test .env so real credentials are never read
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:  # type: ignore[return]
    """
    Clear the settings LRU cache before and after every test.

    This ensures that environment-variable overrides set in individual tests
    do not bleed into neighbouring tests.
    """
    from handshake_watcher.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def minimal_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Provide the minimum environment variables required to instantiate Settings.
    """
    monkeypatch.setenv("HANDSHAKE_BASE_URL", "https://app.joinhandshake.example.com")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("POLL_INTERVAL_SECONDS", "30")


# ---------------------------------------------------------------------------
# Sample domain objects
# ---------------------------------------------------------------------------
@pytest.fixture()
def sample_project() -> ProjectListing:
    """A minimal valid ProjectListing for use in unit tests."""
    return ProjectListing(
        project_id="test-001",
        title="Test AI Project",
        url="https://app.joinhandshake.example.com/projects/001",
        company="ACME Corp",
        location="Remote",
        deadline="2026-08-31",
    )


@pytest.fixture()
def sample_project_list() -> list[ProjectListing]:
    """A list of three distinct ProjectListings."""
    return [
        ProjectListing(project_id=f"proj-{i}", title=f"Project {i}")
        for i in range(1, 4)
    ]


# ---------------------------------------------------------------------------
# Filesystem fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    """Return a path to a temporary state JSON file with two pre-existing IDs."""
    p = tmp_path / "seen_projects.json"
    p.write_text(
        json.dumps({"seen_ids": ["existing-001", "existing-002"], "last_updated": "2026-01-01T00:00:00+00:00"}),
        encoding="utf-8",
    )
    return p


@pytest.fixture()
def empty_state_file(tmp_path: Path) -> Path:
    """Return a path to a temporary directory where no state file yet exists."""
    return tmp_path / "state" / "seen_projects.json"
