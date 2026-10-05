"""
handshake_watcher.cli
======================

Command-line interface entry-point.

Provides the ``handshake-watcher`` console script declared in
``pyproject.toml``. Sub-commands:

  start        — Launch the watcher (default)
  config show  — Print current configuration (secrets redacted)
  state clear  — Wipe the seen-project state file
  --version    — Print version and exit

Public API
----------
    from handshake_watcher.cli import main

    main()   # called by the installed console script
"""

from handshake_watcher.cli.main import main

__all__ = ["main"]
