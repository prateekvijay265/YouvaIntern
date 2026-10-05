"""
handshake_watcher.browser
==========================

Playwright-based browser session management.

This sub-package owns the entire lifecycle of the headless Chromium
browser that the watcher uses to load Handshake pages:

  - Launching and closing the browser.
  - Managing the browser context (cookies, storage state).
  - Navigating to a URL and returning the rendered HTML.

The browser is intentionally exposed as a simple async context manager so
callers cannot forget to close it.

Public API
----------
    from handshake_watcher.browser import BrowserSession

    async with BrowserSession(settings) as session:
        html = await session.get_page_html(url)
"""

from handshake_watcher.browser.session import BrowserSession

__all__ = ["BrowserSession"]
