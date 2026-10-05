"""
handshake_watcher.scraper.projects
=====================================

Parse the Handshake AI Projects listing page HTML into a list of
:class:`~handshake_watcher.models.ProjectListing` dataclasses.

Design decisions
----------------
* BeautifulSoup + lxml parser for robustness against malformed HTML.
* All extraction is wrapped in ``try/except`` so a single broken project
  card never crashes the whole parse run — it is logged and skipped.
* The selectors here are intentionally written to be as loose as possible
  (look for known text patterns and ``data-*`` attributes) so they survive
  minor Handshake UI changes.

⚠️  Handshake's HTML structure may change at any time.  When it does,
    update only the ``_extract_*`` private methods below without touching
    the public ``parse_projects`` contract.
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any

from bs4 import BeautifulSoup, Tag

from handshake_watcher.models import ProjectListing

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------
_WHITESPACE_RE = re.compile(r"\s+")


def _clean(text: str | None) -> str | None:
    """Collapse consecutive whitespace and strip; return None if empty."""
    if text is None:
        return None
    cleaned = _WHITESPACE_RE.sub(" ", text).strip()
    return cleaned or None


def _derive_id(title: str, url: str | None) -> str:
    """
    Derive a stable project ID when the page does not expose one explicitly.

    Uses a short SHA-256 hex digest of ``title + url`` so that re-scrapes
    of the same project always produce the same ID.
    """
    raw = f"{title}::{url or ''}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def parse_projects(html: str) -> list[ProjectListing]:
    """
    Parse *html* and return a list of :class:`ProjectListing` objects.

    Parameters
    ----------
    html:
        Raw HTML string of the Handshake projects listing page.

    Returns
    -------
    list[ProjectListing]
        Parsed project listings. Empty list if no projects were found or
        all project cards raised parsing errors.
    """
    soup = BeautifulSoup(html, "lxml")
    cards = _find_project_cards(soup)
    logger.debug("Found %d project card(s) in HTML.", len(cards))

    listings: list[ProjectListing] = []
    for card in cards:
        try:
            listing = _parse_card(card)
            if listing is not None:
                listings.append(listing)
        except Exception:  # noqa: BLE001 — log and skip; never crash
            logger.warning("Failed to parse a project card; skipping.", exc_info=True)

    logger.info("Parsed %d valid project listing(s).", len(listings))
    return listings


# ---------------------------------------------------------------------------
# Private helpers — update these when Handshake's HTML structure changes
# ---------------------------------------------------------------------------
def _find_project_cards(soup: BeautifulSoup) -> list[Tag]:
    """
    Locate all project card elements within the parsed document.

    Handshake renders projects as a list of <li> or <article> elements.
    This method tries multiple selectors in order of specificity and returns
    the first non-empty match.

    Returns an empty list if no cards are found.
    """
    # Attempt 1: data attribute often used in React/SPA apps (data-hook="project-*")
    cards: list[Tag] = soup.find_all(attrs={"data-hook": re.compile(r"project", re.I)})
    if cards:
        return cards

    # Attempt 2: common card class naming conventions
    for class_pattern in ("project-card", "job-card", "opportunity-card"):
        cards = soup.find_all(class_=re.compile(class_pattern, re.I))
        if cards:
            return cards

    # Attempt 3: list-item children of a results container
    results = soup.find(id=re.compile(r"results|projects|opportunities", re.I))
    if isinstance(results, Tag):
        cards = results.find_all("li")
        if cards:
            return cards

    # Attempt 4: all <article> elements
    cards = soup.find_all("article")
    if cards:
        return cards

    # Attempt 5: <li> elements that carry any data-id / data-job-id attribute
    # (common in React SPAs; also matches our test fixtures)
    for data_attr in ("data-id", "data-job-id", "data-opportunity-id", "data-project-id"):
        cards = soup.find_all("li", attrs={data_attr: True})
        if cards:
            return cards

    # Attempt 6: bare <li> elements anywhere (widest net; last resort)
    cards = soup.find_all("li")
    return cards


def _parse_card(card: Tag) -> ProjectListing | None:
    """
    Extract fields from a single project card ``Tag``.

    Returns None if a required field (title) cannot be found.
    """
    title = _extract_title(card)
    if title is None:
        logger.debug("Card has no title; skipping: %.80s", card.get_text()[:80])
        return None

    url = _extract_url(card)
    project_id = _extract_id(card) or _derive_id(title, url)
    company = _extract_company(card)
    location = _extract_location(card)
    deadline = _extract_deadline(card)

    return ProjectListing(
        project_id=project_id,
        title=title,
        url=url,
        company=company,
        location=location,
        deadline=deadline,
        posted_at=datetime.now(tz=timezone.utc),
    )


def _extract_title(card: Tag) -> str | None:
    """Find the project title within a card element."""
    # Prefer heading tags
    for tag in ("h1", "h2", "h3", "h4"):
        heading = card.find(tag)
        if isinstance(heading, Tag):
            return _clean(heading.get_text())

    # Fall back to any element with a "title" role or class
    title_el = card.find(class_=re.compile(r"title|heading|name", re.I))
    if isinstance(title_el, Tag):
        return _clean(title_el.get_text())

    # Last resort: first anchor text
    anchor = card.find("a")
    if isinstance(anchor, Tag):
        return _clean(anchor.get_text())

    return None


def _extract_url(card: Tag) -> str | None:
    """Extract the project detail URL from the first anchor in the card."""
    anchor = card.find("a", href=True)
    if not isinstance(anchor, Tag):
        return None
    href: Any = anchor.get("href", "")
    if not isinstance(href, str) or not href:
        return None
    # Make relative URLs absolute if needed
    if href.startswith("/"):
        # The base URL is not available here; the watcher layer should resolve
        return href
    return href


def _extract_id(card: Tag) -> str | None:
    """
    Try to extract a native project ID from the card markup.

    Handshake often embeds IDs in ``data-id``, ``data-job-id``, or the
    URL path (``/projects/12345``).
    """
    for attr in ("data-id", "data-job-id", "data-opportunity-id", "data-project-id"):
        value = card.get(attr)
        if isinstance(value, str) and value.strip():
            return value.strip()

    # Try to parse from anchor href  e.g. /projects/12345
    url = _extract_url(card)
    if url:
        m = re.search(r"/(?:projects|jobs|opportunities)/(\d+)", url)
        if m:
            return m.group(1)

    return None


def _extract_company(card: Tag) -> str | None:
    """Extract the company / organisation name from the card."""
    for pattern in (r"company", r"employer", r"organization", r"org"):
        el = card.find(class_=re.compile(pattern, re.I))
        if isinstance(el, Tag):
            return _clean(el.get_text())
    return None


def _extract_location(card: Tag) -> str | None:
    """Extract the location string from the card."""
    el = card.find(class_=re.compile(r"location|city|place", re.I))
    if isinstance(el, Tag):
        return _clean(el.get_text())
    return None


def _extract_deadline(card: Tag) -> str | None:
    """Extract the application deadline from the card, if shown."""
    el = card.find(class_=re.compile(r"deadline|apply.by|due", re.I))
    if isinstance(el, Tag):
        return _clean(el.get_text())
    return None
