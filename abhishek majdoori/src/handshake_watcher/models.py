"""
handshake_watcher.models
=========================

Shared, immutable domain dataclasses used across every layer of the
application. Keeping models in one place prevents circular imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class ProjectListing:
    """
    An immutable snapshot of a single project as it appears on the
    Handshake projects listing page.

    All fields except *project_id* and *title* are optional because the
    page layout may vary or certain metadata may not always be present.

    Attributes
    ----------
    project_id:
        Unique identifier extracted from the project URL or a page element.
        Used for deduplication.
    title:
        Display title of the project.
    url:
        Full URL to the project detail page (if parseable).
    company:
        Name of the company or organisation posting the project.
    location:
        Location string as displayed on the listing (may be "Remote").
    deadline:
        Application deadline, if shown on the listing page.
    posted_at:
        ISO timestamp string when the project was first seen by the watcher.
        Set by the scraper at parse time, not extracted from the page.
    """

    project_id: str
    title: str
    url: str | None = None
    company: str | None = None
    location: str | None = None
    deadline: str | None = None
    posted_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def __str__(self) -> str:
        parts = [f"[{self.project_id}] {self.title}"]
        if self.company:
            parts.append(f"by {self.company}")
        if self.location:
            parts.append(f"({self.location})")
        return " ".join(parts)
