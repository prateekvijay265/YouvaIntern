"""
handshake_watcher.scraper
==========================

HTML parsing layer — converts raw Handshake project page HTML into typed
:class:`~handshake_watcher.models.ProjectListing` dataclasses.

This layer knows nothing about the browser or the network; it only operates
on a plain HTML string. This makes it trivially unit-testable.

Public API
----------
    from handshake_watcher.scraper import parse_projects

    listings = parse_projects(html_string)
"""

from handshake_watcher.scraper.projects import parse_projects

__all__ = ["parse_projects"]
