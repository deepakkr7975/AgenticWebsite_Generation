"""
screenshotter.py — Selenium-based visual reviewer for the generated Next.js site.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
    _HAS_WDM = True
except ImportError:
    _HAS_WDM = False


class Screenshotter:
    """
    Takes full-page screenshots of a running local Next.js dev server
    using headless Chrome via Selenium.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        width: int = 1440,
        height: int = 900,
        screenshots_dir: str = "screenshots",
    ):
        self.base_url = base_url.rstrip("/")
        self.width = width
        self.height = height
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self._driver: webdriver.Chrome | None = None

    # ─────────────────────────────────────────────
    #  Driver management
    # ─────────────────────────────────────────────

    def _get_driver(self) -> webdriver.Chrome:
        if self._driver is not None:
            return self._driver

        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument(f"--window-size={self.width},{self.height}")
        opts.add_argument("--hide-scrollbars")

        if _HAS_WDM:
            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=opts)
        else:
            self._driver = webdriver.Chrome(options=opts)

        return self._driver

    def quit(self):
        if self._driver:
            self._driver.quit()
            self._driver = None

    # ─────────────────────────────────────────────
    #  Screenshot methods
    # ─────────────────────────────────────────────

    def screenshot_route(self, route: str, iteration: int) -> str:
        """
        Navigate to a route and take a full-page screenshot.
        Returns the path to the saved screenshot PNG.
        """
        driver = self._get_driver()
        url = self.base_url + route
        driver.get(url)

        # Wait for body to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception:
            pass

        # Extra wait for JS hydration
        time.sleep(2)

        # Scroll to capture lazy-loaded content (optional full-page trick)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(0.5)

        # Save screenshot
        safe_route = route.strip("/").replace("/", "_") or "home"
        filename = f"iter{iteration}_{safe_route}.png"
        filepath = str(self.screenshots_dir / filename)
        driver.save_screenshot(filepath)
        return filepath

    def screenshot_all_routes(
        self, routes: list[str], iteration: int
    ) -> dict[str, str]:
        """
        Screenshot multiple routes. Returns {route: filepath} mapping.
        """
        results: dict[str, str] = {}
        for route in routes:
            try:
                path = self.screenshot_route(route, iteration)
                results[route] = path
                print(f"  📸 Screenshotted {route} → {path}")
            except Exception as e:
                print(f"  ⚠️  Failed to screenshot {route}: {e}")
        return results

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.quit()
