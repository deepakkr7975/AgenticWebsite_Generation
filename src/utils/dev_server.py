"""
dev_server.py — Manages the Next.js dev server for visual review.
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import requests


class DevServerManager:
    """
    Starts and stops `npm run dev` for a Next.js project.
    Used during visual review to serve the generated site for screenshots.
    """

    def __init__(self, site_dir: str, port: int = 3001):
        self.site_dir = Path(site_dir)
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self._process: subprocess.Popen | None = None

    def start(self, timeout: int = 60) -> bool:
        """
        Install deps and start the dev server.
        Returns True if server started successfully.
        """
        # Install dependencies
        print(f"📦 Installing npm dependencies in {self.site_dir}...")
        result = subprocess.run(
            ["npm", "install", "--legacy-peer-deps"],
            cwd=self.site_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"⚠️  npm install warning: {result.stderr[:500]}")

        # Start dev server
        print(f"🚀 Starting Next.js dev server on port {self.port}...")
        env = os.environ.copy()
        env["PORT"] = str(self.port)
        self._process = subprocess.Popen(
            ["npm", "run", "dev", "--", "--port", str(self.port)],
            cwd=self.site_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        # Wait for server to be ready
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                resp = requests.get(self.base_url, timeout=3)
                if resp.status_code < 500:
                    print(f"✅ Dev server ready at {self.base_url}")
                    return True
            except Exception:
                pass
            time.sleep(2)

        print("❌ Dev server failed to start in time")
        self.stop()
        return False

    def stop(self):
        """Kill the dev server process."""
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
            print("🛑 Dev server stopped")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
