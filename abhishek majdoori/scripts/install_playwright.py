"""
scripts/install_playwright.py

One-shot helper that installs the Playwright Chromium browser binary.

Run this script once after `pip install -e ".[dev]"`:

    python scripts/install_playwright.py

This is equivalent to `playwright install chromium` but can be invoked
without the Playwright CLI being on PATH (useful in CI or fresh envs).
"""

from __future__ import annotations

import subprocess
import sys


def main() -> None:
    print("Installing Playwright Chromium browser binary...")
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=False,
    )
    if result.returncode != 0:
        print(
            "\n[ERROR] Playwright installation failed.\n"
            "Try running manually: playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(result.returncode)
    print("\nPlaywright Chromium installed successfully.")


if __name__ == "__main__":
    main()
