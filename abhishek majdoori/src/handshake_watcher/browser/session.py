"""
handshake_watcher.browser.session
===================================

Async context-manager that owns a Playwright Chromium browser instance.

Design decisions
----------------
* Single context per session — one browser, one context, one page at a time.
  The watcher is a sequential poller, not a concurrent scraper.
* Storage-state support — if ``settings.browser_storage_state_path`` is set,
  the context is initialised with saved cookies so the user stays logged in
  without re-authenticating on every start.
* Read-only contract — this class only navigates and reads; it never clicks,
  fills forms, or triggers side-effects. Every method name is a ``get_*``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Self

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

if TYPE_CHECKING:
    from handshake_watcher.config.settings import Settings

logger = logging.getLogger(__name__)


class BrowserSession:
    """
    Async context manager for a headless Chromium browser session.

    Usage
    -----
    .. code-block:: python

        async with BrowserSession(settings) as session:
            html = await session.get_page_html(url)
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------
    async def __aenter__(self) -> Self:
        await self._launch()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._close()

    # ------------------------------------------------------------------
    # Public read-only API
    # ------------------------------------------------------------------
    async def get_page_html(self, url: str) -> str:
        """
        Navigate to *url* and return the fully-rendered page HTML.

        The page is loaded once and its ``innerHTML`` returned.  No
        further interaction is performed.

        Parameters
        ----------
        url:
            The absolute URL to navigate to.

        Returns
        -------
        str
            Full HTML source of the rendered page.

        Raises
        ------
        playwright.async_api.TimeoutError
            If the page does not finish loading within the configured timeout.
        RuntimeError
            If the session has not been entered (i.e. used outside ``async with``).
        """
        page = self._require_page()
        logger.debug("Navigating to %s", url)
        await page.goto(url, timeout=self._settings.browser_timeout_ms, wait_until="networkidle")
        html: str = await page.content()
        logger.debug("Page loaded. HTML length=%d chars", len(html))
        return html

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    async def _launch(self) -> None:
        """Start the Playwright process, browser, and context."""
        logger.info(
            "Starting browser session (headless=%s)", self._settings.browser_headless
        )
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self._settings.browser_headless,
        )

        context_kwargs: dict[str, object] = {}
        storage_path: Path | None = self._settings.browser_storage_state_path
        if storage_path is not None:
            logger.info("Loading storage state from %s", storage_path)
            context_kwargs["storage_state"] = str(storage_path)

        self._context = await self._browser.new_context(**context_kwargs)
        self._context.set_default_timeout(self._settings.browser_timeout_ms)
        self._page = await self._context.new_page()
        logger.debug("Browser session ready.")

    async def _close(self) -> None:
        """Tear down the page, context, browser, and Playwright process."""
        logger.info("Closing browser session.")
        if self._page is not None:
            await self._page.close()
        if self._context is not None:
            await self._context.close()
        if self._browser is not None:
            await self._browser.close()
        if self._playwright is not None:
            await self._playwright.stop()

    def _require_page(self) -> Page:
        """Return the active page or raise if the session is not started."""
        if self._page is None:
            raise RuntimeError(
                "BrowserSession must be used as an async context manager: "
                "`async with BrowserSession(settings) as session:`"
            )
        return self._page
