"""
handshake_watcher.tray.icon
=============================

System-tray icon integration via ``pystray``.

The tray icon gives the user a visible indicator that the watcher is
running silently in the background.  Right-clicking the icon exposes:

  * "Open Handshake"  — opens the projects page in the default browser
  * "Quit"            — calls *shutdown_callback* to stop the watcher

Design decisions
----------------
* ``pystray`` runs its own event loop in a daemon thread, so it does
  not block the asyncio event loop running the watcher.
* We create a minimal placeholder icon programmatically if the bundled
  ``assets/icon.png`` is not found, so the app never crashes on startup
  due to a missing asset.
"""

from __future__ import annotations

import logging
import threading
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from handshake_watcher.config.settings import Settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# pystray / Pillow — optional at import time; required at runtime
# ---------------------------------------------------------------------------
try:
    import pystray
    from PIL import Image, ImageDraw

    _HAS_PYSTRAY = True
except ImportError:  # pragma: no cover
    _HAS_PYSTRAY = False

# Default icon bundled with the package (assets/ directory)
_DEFAULT_ICON_PATH = Path(__file__).parent.parent.parent.parent / "assets" / "icon.png"


def _create_fallback_icon() -> "Image.Image":
    """
    Generate a simple coloured circle as a placeholder system-tray icon.

    Used when ``assets/icon.png`` is not present.
    """
    from PIL import Image, ImageDraw  # noqa: PLC0415 — only when pystray is available

    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, size - 4, size - 4], fill="#3B82F6")  # blue circle
    return img


class TrayIcon:
    """
    Manages the Windows system-tray icon for Handshake Project Watcher.

    Parameters
    ----------
    settings:
        Resolved application settings.
    shutdown_callback:
        A zero-argument callable invoked when the user chooses "Quit"
        from the tray menu. Typically calls ``WatcherService.stop()`` and
        cancels the asyncio task.
    """

    def __init__(
        self,
        settings: Settings,
        shutdown_callback: Callable[[], None],
    ) -> None:
        self._settings = settings
        self._shutdown_callback = shutdown_callback
        self._icon: "pystray.Icon | None" = None

    def run_detached(self) -> None:
        """
        Start the tray icon in a daemon thread so it does not block the
        main asyncio event loop.
        """
        if not _HAS_PYSTRAY:
            logger.warning(
                "pystray / Pillow not installed; system-tray icon disabled."
            )
            return

        thread = threading.Thread(target=self._run, daemon=True, name="tray-icon")
        thread.start()
        logger.info("System-tray icon started in daemon thread.")

    def stop(self) -> None:
        """Remove the tray icon and stop the pystray loop."""
        if self._icon is not None:
            self._icon.stop()
            logger.info("System-tray icon stopped.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _run(self) -> None:
        """Build and run the pystray icon (blocking — runs in daemon thread)."""
        from pystray import Icon, Menu, MenuItem  # noqa: PLC0415

        icon_image = self._load_icon()
        menu = Menu(
            MenuItem("Open Handshake", self._on_open, default=True),
            Menu.SEPARATOR,
            MenuItem("Quit", self._on_quit),
        )
        self._icon = Icon(
            name="handshake-watcher",
            icon=icon_image,
            title="Handshake Project Watcher",
            menu=menu,
        )
        self._icon.run()

    def _load_icon(self) -> "Image.Image":
        """Load the application icon, falling back to a generated one."""
        from PIL import Image  # noqa: PLC0415

        if _DEFAULT_ICON_PATH.is_file():
            try:
                return Image.open(_DEFAULT_ICON_PATH).convert("RGBA")
            except OSError:
                logger.debug("Could not load icon from %s; using fallback.", _DEFAULT_ICON_PATH)
        return _create_fallback_icon()

    def _on_open(self, icon: object, item: object) -> None:  # noqa: ARG002
        """Open the Handshake projects page in the default browser."""
        url = self._settings.projects_url
        logger.info("Opening browser to %s", url)
        webbrowser.open(url)

    def _on_quit(self, icon: object, item: object) -> None:  # noqa: ARG002
        """Invoke the shutdown callback and stop the tray icon."""
        logger.info("Quit requested from system tray.")
        self._shutdown_callback()
        if self._icon is not None:
            self._icon.stop()
