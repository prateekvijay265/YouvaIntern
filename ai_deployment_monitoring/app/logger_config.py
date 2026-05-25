"""
logger_config.py
----------------
Configures a structured JSON logger with both console and rotating-file
handlers. Import `get_logger` anywhere in the application.
"""

import logging
import logging.handlers
import os
import sys

from pythonjsonlogger import jsonlogger  # type: ignore

LOG_DIR = os.environ.get("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "api.log")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
MAX_BYTES = 10 * 1024 * 1024   # 10 MB per file
BACKUP_COUNT = 5


def _ensure_log_dir() -> None:
    """Create the log directory if it does not already exist."""
    os.makedirs(LOG_DIR, exist_ok=True)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Extend the base JSON formatter with a fixed `service` field."""

    def add_fields(self, log_record, record, message_dict):  # type: ignore[override]
        super().add_fields(log_record, record, message_dict)
        log_record["service"] = "iris-prediction-api"
        log_record["level"] = record.levelname


def get_logger(name: str) -> logging.Logger:
    """Return a logger instance wired to JSON console + rotating file handlers."""
    _ensure_log_dir()

    logger = logging.getLogger(name)
    if logger.handlers:
        # Avoid adding duplicate handlers when the module is re-imported
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    fmt = CustomJsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    # ── Console handler ────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    # ── Rotating file handler ──────────────────────────────────────────────
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger
