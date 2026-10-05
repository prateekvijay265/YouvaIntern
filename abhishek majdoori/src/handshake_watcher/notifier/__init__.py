"""
handshake_watcher.notifier
===========================

Windows desktop notification layer.

Wraps the ``plyer`` library's ``notification.notify()`` call behind a clean
interface. Plyer handles the platform-specific toast/tray mechanics; this
module adds project-specific formatting and error handling.

Public API
----------
    from handshake_watcher.notifier import WindowsNotifier

    notifier = WindowsNotifier(settings)
    notifier.send(project)
"""

from handshake_watcher.notifier.windows import WindowsNotifier

__all__ = ["WindowsNotifier"]
