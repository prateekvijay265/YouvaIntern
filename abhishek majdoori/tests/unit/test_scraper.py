"""
tests/unit/test_scraper.py

Unit tests for handshake_watcher.scraper.projects.parse_projects().

All tests operate on static HTML strings — no network, no browser.
"""

from __future__ import annotations

import pytest

from handshake_watcher.models import ProjectListing
from handshake_watcher.scraper.projects import parse_projects, _derive_id, _clean


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_card(
    *,
    title: str = "Test Project",
    company: str = "ACME",
    location: str = "Remote",
    href: str = "/projects/42",
    data_id: str = "42",
) -> str:
    return f"""
    <li data-id="{data_id}">
        <h3>{title}</h3>
        <a href="{href}">{title}</a>
        <span class="company">{company}</span>
        <span class="location">{location}</span>
    </li>
    """


def _wrap_cards(*cards: str) -> str:
    inner = "\n".join(cards)
    return f"<html><body><ul>{inner}</ul></body></html>"


# ---------------------------------------------------------------------------
# parse_projects
# ---------------------------------------------------------------------------
class TestParseProjects:
    def test_empty_html_returns_empty_list(self) -> None:
        result = parse_projects("<html><body></body></html>")
        assert result == []

    def test_single_card_parsed_correctly(self) -> None:
        html = _wrap_cards(_make_card(title="AI Research Role", company="DeepMind"))
        result = parse_projects(html)
        assert len(result) == 1
        listing = result[0]
        assert listing.title == "AI Research Role"
        assert listing.company == "DeepMind"

    def test_multiple_cards_all_parsed(self) -> None:
        html = _wrap_cards(
            _make_card(title="Project A", data_id="1"),
            _make_card(title="Project B", data_id="2"),
            _make_card(title="Project C", data_id="3"),
        )
        result = parse_projects(html)
        assert len(result) == 3

    def test_project_ids_are_unique(self) -> None:
        html = _wrap_cards(
            _make_card(title="Project A", data_id="1"),
            _make_card(title="Project B", data_id="2"),
        )
        result = parse_projects(html)
        ids = [p.project_id for p in result]
        assert len(ids) == len(set(ids))

    def test_returns_list_of_project_listing(self) -> None:
        html = _wrap_cards(_make_card())
        result = parse_projects(html)
        assert all(isinstance(p, ProjectListing) for p in result)

    def test_location_extracted(self) -> None:
        html = _wrap_cards(_make_card(location="San Francisco, CA"))
        result = parse_projects(html)
        assert result[0].location == "San Francisco, CA"

    def test_url_extracted(self) -> None:
        html = _wrap_cards(_make_card(href="/projects/99"))
        result = parse_projects(html)
        assert result[0].url == "/projects/99"

    def test_broken_card_does_not_crash_parser(self) -> None:
        # A card with completely missing content
        broken = "<li></li>"
        html = f"<html><body><ul>{broken}{_make_card(data_id='999')}</ul></body></html>"
        # Should not raise; broken card is skipped
        result = parse_projects(html)
        # The valid card should still parse
        assert any(p.project_id == "999" for p in result)


# ---------------------------------------------------------------------------
# _derive_id
# ---------------------------------------------------------------------------
class TestDeriveId:
    def test_same_inputs_produce_same_id(self) -> None:
        id1 = _derive_id("Test Project", "https://example.com/projects/1")
        id2 = _derive_id("Test Project", "https://example.com/projects/1")
        assert id1 == id2

    def test_different_titles_produce_different_ids(self) -> None:
        id1 = _derive_id("Project A", None)
        id2 = _derive_id("Project B", None)
        assert id1 != id2

    def test_id_is_16_hex_chars(self) -> None:
        result = _derive_id("Any Title", None)
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)


# ---------------------------------------------------------------------------
# _clean
# ---------------------------------------------------------------------------
class TestClean:
    def test_strips_whitespace(self) -> None:
        assert _clean("  hello world  ") == "hello world"

    def test_collapses_internal_whitespace(self) -> None:
        assert _clean("hello    world\n\t!") == "hello world !"

    def test_empty_string_returns_none(self) -> None:
        assert _clean("   ") is None

    def test_none_returns_none(self) -> None:
        assert _clean(None) is None
