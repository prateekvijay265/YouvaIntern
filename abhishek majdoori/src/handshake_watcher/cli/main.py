"""
handshake_watcher.cli.main
============================

Command-line entry-point for the ``handshake-watcher`` console script.

Sub-commands
------------
start            Start the watcher (default command)
config show      Print current configuration with secrets redacted
state clear      Wipe the seen-project state and start fresh
--version / -V   Print version and exit

Usage examples
--------------
    handshake-watcher start
    handshake-watcher start --log-level DEBUG
    handshake-watcher config show
    handshake-watcher state clear
    handshake-watcher --version
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import NoReturn

from handshake_watcher import __version__


def _build_parser() -> argparse.ArgumentParser:
    """Construct and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="handshake-watcher",
        description=(
            "Monitors the Handshake AI Projects page and notifies you "
            "when new projects appear. Never takes any action on your behalf."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # -----------------------------------------------------------------------
    # `start` sub-command
    # -----------------------------------------------------------------------
    start_cmd = sub.add_parser(
        "start",
        help="Start the project watcher (default).",
        description="Launch the Handshake Project Watcher polling loop.",
    )
    start_cmd.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Override the LOG_LEVEL from .env for this session.",
    )
    start_cmd.add_argument(
        "--no-tray",
        action="store_true",
        default=False,
        help="Disable the system-tray icon (useful for headless/CI environments).",
    )

    # -----------------------------------------------------------------------
    # `config` sub-command group
    # -----------------------------------------------------------------------
    config_cmd = sub.add_parser(
        "config",
        help="Inspect current configuration.",
    )
    config_sub = config_cmd.add_subparsers(dest="config_action", metavar="ACTION")
    config_sub.add_parser(
        "show",
        help="Print the resolved configuration (secrets redacted).",
    )

    # -----------------------------------------------------------------------
    # `state` sub-command group
    # -----------------------------------------------------------------------
    state_cmd = sub.add_parser(
        "state",
        help="Manage the seen-projects state store.",
    )
    state_sub = state_cmd.add_subparsers(dest="state_action", metavar="ACTION")
    state_sub.add_parser(
        "clear",
        help="Clear all seen-project IDs (triggers re-notification on next poll).",
    )

    return parser


def _cmd_start(args: argparse.Namespace) -> None:
    """Handle the ``start`` sub-command."""
    # Late imports so CLI --help is fast even without a .env file present
    import os  # noqa: PLC0415

    from handshake_watcher.config import get_settings  # noqa: PLC0415
    from handshake_watcher.logging_config import setup_logging  # noqa: PLC0415
    from handshake_watcher.tray import TrayIcon  # noqa: PLC0415
    from handshake_watcher.watcher import WatcherService  # noqa: PLC0415

    # Allow CLI override of log level
    if args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level
        get_settings.cache_clear()

    settings = get_settings()
    setup_logging(settings)

    service = WatcherService(settings)

    # Tray icon (optional)
    tray: TrayIcon | None = None
    if not args.no_tray:
        tray = TrayIcon(settings, shutdown_callback=service.stop)
        tray.run_detached()

    try:
        asyncio.run(service.run())
    finally:
        if tray is not None:
            tray.stop()


def _cmd_config_show() -> None:
    """Handle the ``config show`` sub-command."""
    from handshake_watcher.config import get_settings  # noqa: PLC0415

    settings = get_settings()
    # Print each field, masking anything that looks like a secret
    print("\nHandshake Project Watcher — Current Configuration\n" + "=" * 52)
    for name, value in settings.model_dump().items():
        display = str(value)
        print(f"  {name:<35} {display}")
    print()


def _cmd_state_clear() -> None:
    """Handle the ``state clear`` sub-command."""
    from handshake_watcher.config import get_settings  # noqa: PLC0415
    from handshake_watcher.state import StateStore  # noqa: PLC0415

    settings = get_settings()
    store = StateStore(settings)
    store.clear()
    print(f"State cleared. File: {settings.state_file_path}")


def main() -> NoReturn:
    """
    Entry-point for the ``handshake-watcher`` console script.

    Parses arguments, dispatches to the appropriate handler, and exits.
    """
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "start" or args.command is None:
        _cmd_start(args if args.command else parser.parse_args(["start"]))
    elif args.command == "config":
        if args.config_action == "show":
            _cmd_config_show()
        else:
            parser.parse_args(["config", "--help"])
    elif args.command == "state":
        if args.state_action == "clear":
            _cmd_state_clear()
        else:
            parser.parse_args(["state", "--help"])
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
