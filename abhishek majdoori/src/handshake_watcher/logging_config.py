"""
handshake_watcher.logging_config
=================================

Centralised logging configuration for the entire application.

Features
--------
* Console handler   — Colourised output using ``colorlog``.
* File handler      — Rotating file log with configurable size and backup count.
* Single call-site  — All other modules simply use ``logging.getLogger(__name__)``.

Usage
-----
    from handshake_watcher.logging_config import setup_logging
    from handshake_watcher.config import get_settings

    setup_logging(get_settings())
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from handshake_watcher.config.settings import Settings

try:
    import colorlog

    _HAS_COLORLOG = True
except ImportError:  # pragma: no cover
    _HAS_COLORLOG = False

# ---------------------------------------------------------------------------
# Module-level logger (used internally by this module only)
# ---------------------------------------------------------------------------
_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Log format strings
# ---------------------------------------------------------------------------
_CONSOLE_FORMAT_COLOR = (
    "%(log_color)s%(asctime)s%(reset)s | "
    "%(log_color)s%(levelname)-8s%(reset)s | "
    "%(cyan)s%(name)s%(reset)s | "
    "%(message)s"
)
_CONSOLE_FORMAT_PLAIN = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_FILE_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def setup_logging(settings: Settings) -> None:
    """
    Configure the root logger according to *settings*.

    Call this **once** at application start-up, before any other module
    imports that perform logging.

    Parameters
    ----------
    settings:
        The resolved application :class:`~handshake_watcher.config.Settings`.
    """
    numeric_level: int = logging.getLevelName(settings.log_level)
    if not isinstance(numeric_level, int):  # pragma: no cover
        raise ValueError(f"Invalid log level: {settings.log_level!r}")

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Avoid adding duplicate handlers if called more than once (e.g. in tests)
    root.handlers.clear()

    # -----------------------------------------------------------------------
    # Console handler
    # -----------------------------------------------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)

    if _HAS_COLORLOG:
        console_formatter = colorlog.ColoredFormatter(
            _CONSOLE_FORMAT_COLOR,
            datefmt=_DATE_FORMAT,
            log_colors={
                "DEBUG": "white",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            reset=True,
            style="%",
        )
    else:
        console_formatter = logging.Formatter(
            _CONSOLE_FORMAT_PLAIN, datefmt=_DATE_FORMAT
        )

    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    # -----------------------------------------------------------------------
    # Rotating file handler
    # -----------------------------------------------------------------------
    log_path: Path = settings.log_file_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(numeric_level)
    file_formatter = logging.Formatter(_FILE_FORMAT, datefmt=_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    root.addHandler(file_handler)

    # -----------------------------------------------------------------------
    # Silence overly chatty third-party loggers at WARNING or above
    # -----------------------------------------------------------------------
    for noisy_logger_name in (
        "playwright",
        "asyncio",
        "urllib3",
        "httpx",
    ):
        logging.getLogger(noisy_logger_name).setLevel(
            max(numeric_level, logging.WARNING)
        )

    _logger.debug(
        "Logging configured. level=%s file=%s",
        settings.log_level,
        log_path,
    )
