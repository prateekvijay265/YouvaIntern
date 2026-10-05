"""
Handshake Project Watcher
=========================

A production-ready Windows desktop application that monitors the Handshake AI
Projects page and notifies the user when a new project becomes available.

This package is intentionally **read-only** — it will never submit forms,
click buttons, or perform any action on the user's behalf.

Package layout
--------------
handshake_watcher/
├── browser/       — Playwright session management
├── cli/           — argparse entry-point
├── config/        — pydantic-settings configuration
├── notifier/      — Windows desktop notifications
├── scraper/       — HTML parsing → typed dataclasses
├── state/         — Persistent seen-project ID store
├── tray/          — System-tray icon and menu
└── watcher/       — Polling-loop orchestration
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("handshake-project-watcher")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"

__all__ = ["__version__"]
