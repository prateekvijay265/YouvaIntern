"""
tests/unit/test_state.py

Unit tests for handshake_watcher.state.store.StateStore.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from handshake_watcher.models import ProjectListing
from handshake_watcher.state.store import StateStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_settings(state_path: Path) -> MagicMock:
    """Return a minimal Settings mock pointing at *state_path*."""
    mock = MagicMock()
    mock.state_file_path = state_path
    return mock


def _make_project(pid: str) -> ProjectListing:
    return ProjectListing(project_id=pid, title=f"Project {pid}")


# ---------------------------------------------------------------------------
# StateStore — initial load
# ---------------------------------------------------------------------------
class TestStateStoreLoad:
    def test_starts_empty_when_no_file_exists(self, empty_state_file: Path) -> None:
        store = StateStore(_make_settings(empty_state_file))
        assert store.seen_count == 0

    def test_loads_existing_ids_from_file(self, state_file: Path) -> None:
        store = StateStore(_make_settings(state_file))
        assert store.seen_count == 2

    def test_corrupt_file_starts_with_empty_state(self, tmp_path: Path) -> None:
        corrupt = tmp_path / "state.json"
        corrupt.write_text("not valid json", encoding="utf-8")
        store = StateStore(_make_settings(corrupt))
        assert store.seen_count == 0


# ---------------------------------------------------------------------------
# StateStore — diff_and_update
# ---------------------------------------------------------------------------
class TestDiffAndUpdate:
    def test_all_new_projects_returned(self, empty_state_file: Path) -> None:
        store = StateStore(_make_settings(empty_state_file))
        projects = [_make_project("a"), _make_project("b")]
        new = store.diff_and_update(projects)
        assert len(new) == 2

    def test_existing_projects_not_returned(self, state_file: Path) -> None:
        store = StateStore(_make_settings(state_file))
        # Both IDs are pre-loaded from state_file fixture
        projects = [_make_project("existing-001"), _make_project("existing-002")]
        new = store.diff_and_update(projects)
        assert new == []

    def test_mixed_projects_returns_only_new(self, state_file: Path) -> None:
        store = StateStore(_make_settings(state_file))
        projects = [
            _make_project("existing-001"),  # already seen
            _make_project("brand-new-111"),  # new
        ]
        new = store.diff_and_update(projects)
        assert len(new) == 1
        assert new[0].project_id == "brand-new-111"

    def test_new_ids_persisted_after_update(self, empty_state_file: Path) -> None:
        store = StateStore(_make_settings(empty_state_file))
        store.diff_and_update([_make_project("saved-id")])
        # Reload from file
        store2 = StateStore(_make_settings(empty_state_file))
        assert store2.seen_count == 1
        # Running diff again should return empty (already persisted)
        new = store2.diff_and_update([_make_project("saved-id")])
        assert new == []

    def test_seen_count_increments(self, empty_state_file: Path) -> None:
        store = StateStore(_make_settings(empty_state_file))
        store.diff_and_update([_make_project("x")])
        assert store.seen_count == 1
        store.diff_and_update([_make_project("y")])
        assert store.seen_count == 2


# ---------------------------------------------------------------------------
# StateStore — clear
# ---------------------------------------------------------------------------
class TestStateClear:
    def test_clear_resets_seen_count(self, state_file: Path) -> None:
        store = StateStore(_make_settings(state_file))
        assert store.seen_count == 2
        store.clear()
        assert store.seen_count == 0

    def test_clear_persists_empty_state(self, state_file: Path) -> None:
        store = StateStore(_make_settings(state_file))
        store.clear()
        # Re-load and verify
        data = json.loads(state_file.read_text())
        assert data["seen_ids"] == []

    def test_after_clear_all_projects_are_new_again(self, state_file: Path) -> None:
        store = StateStore(_make_settings(state_file))
        store.clear()
        projects = [_make_project("existing-001")]
        new = store.diff_and_update(projects)
        assert len(new) == 1
