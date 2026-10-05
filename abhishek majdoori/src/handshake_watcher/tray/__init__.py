"""
handshake_watcher.tray
=======================

System-tray icon and menu using ``pystray``.

The tray icon gives the user a visual indicator that the watcher is running
and provides a right-click menu with options to open the Handshake page and
quit the application.

Public API
----------
    from handshake_watcher.tray import TrayIcon

    icon = TrayIcon(settings, shutdown_callback)
    icon.run_detached()   # runs pystray in a daemon thread
"""

from handshake_watcher.tray.icon import TrayIcon

__all__ = ["TrayIcon"]
