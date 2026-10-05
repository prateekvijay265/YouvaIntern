"""Smoke-test script to verify all imports and basic functionality."""
import sys

sys.path.insert(0, "src")

errors = []

# 1. Top-level package
try:
    from handshake_watcher import __version__
    print(f"[OK] handshake_watcher.__version__ = {__version__!r}")
except Exception as e:
    errors.append(f"handshake_watcher: {e}")

# 2. Models
try:
    from handshake_watcher.models import ProjectListing
    p = ProjectListing(project_id="smoke-1", title="Smoke Test")
    print(f"[OK] models.ProjectListing: {p}")
except Exception as e:
    errors.append(f"models: {e}")

# 3. Config
try:
    from handshake_watcher.config.settings import Settings, get_settings
    print("[OK] config.settings imported")
except Exception as e:
    errors.append(f"config.settings: {e}")

# 4. Logging config
try:
    from handshake_watcher.logging_config import setup_logging
    print("[OK] logging_config.setup_logging imported")
except Exception as e:
    errors.append(f"logging_config: {e}")

# 5. Scraper
try:
    from handshake_watcher.scraper.projects import parse_projects, _clean, _derive_id
    html = "<html><body><ul><li data-id='p1'><h3>Test Project</h3><a href='/projects/1'>L</a></li></ul></body></html>"
    results = parse_projects(html)
    assert len(results) == 1
    assert results[0].project_id == "p1"
    assert results[0].title == "Test Project"
    assert _clean("  hello  world  ") == "hello world"
    assert len(_derive_id("Test", None)) == 16
    print(f"[OK] scraper.parse_projects: found {len(results)} project(s)")
except Exception as e:
    errors.append(f"scraper: {e}")

# 6. State store
try:
    from handshake_watcher.state.store import StateStore
    print("[OK] state.StateStore imported")
except Exception as e:
    errors.append(f"state: {e}")

# 7. Notifier
try:
    from handshake_watcher.notifier.windows import WindowsNotifier, _MAX_TITLE_LEN, _MAX_MESSAGE_LEN
    print(f"[OK] notifier.WindowsNotifier imported (max_title={_MAX_TITLE_LEN}, max_msg={_MAX_MESSAGE_LEN})")
except Exception as e:
    errors.append(f"notifier: {e}")

# 8. Watcher service
try:
    from handshake_watcher.watcher.service import WatcherService
    print("[OK] watcher.WatcherService imported")
except Exception as e:
    errors.append(f"watcher: {e}")

# 9. Browser session
try:
    from handshake_watcher.browser.session import BrowserSession
    print("[OK] browser.BrowserSession imported")
except Exception as e:
    errors.append(f"browser: {e}")

# 10. Tray icon
try:
    from handshake_watcher.tray.icon import TrayIcon
    print("[OK] tray.TrayIcon imported")
except Exception as e:
    errors.append(f"tray: {e}")

# 11. CLI
try:
    from handshake_watcher.cli.main import main, _build_parser
    parser = _build_parser()
    print("[OK] cli.main imported and parser built")
except Exception as e:
    errors.append(f"cli: {e}")

# Summary
print()
if errors:
    print(f"FAILED — {len(errors)} error(s):")
    for err in errors:
        print(f"  [FAIL] {err}")
    sys.exit(1)
else:
    print(f"ALL {11} IMPORT CHECKS PASSED")
    sys.exit(0)
