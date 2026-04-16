"""
scraper.py — Fetches and summarizes reference site content.
"""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup


class SiteScraper:
    """Scrapes reference websites to extract design-relevant content."""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def scrape(self, url: str, max_chars: int = 3000) -> str:
        """
        Fetch a URL and return a text summary of its design-relevant content.
        Extracts: title, meta description, headings, nav items, CTA text, footer.
        """
        try:
            resp = requests.get(url, headers=self.HEADERS, timeout=15)
            resp.raise_for_status()
            return self._parse(resp.text, url, max_chars)
        except Exception as e:
            return f"[Could not scrape {url}: {e}]"

    def scrape_multiple(self, urls: list[str]) -> list[str]:
        return [self.scrape(url) for url in urls]

    def _parse(self, html: str, url: str, max_chars: int) -> str:
        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts, styles, SVG noise
        for tag in soup(["script", "style", "svg", "noscript"]):
            tag.decompose()

        parts = [f"URL: {url}"]

        # Title
        title = soup.find("title")
        if title:
            parts.append(f"Title: {title.get_text(strip=True)}")

        # Meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            parts.append(f"Description: {meta.get('content', '')[:200]}")

        # Headings (design intent signals)
        headings = []
        for tag in soup.find_all(["h1", "h2", "h3"])[:12]:
            text = tag.get_text(strip=True)
            if text:
                headings.append(f"{tag.name.upper()}: {text}")
        if headings:
            parts.append("Headings:\n" + "\n".join(headings))

        # Navigation items
        nav = soup.find("nav")
        if nav:
            nav_items = [
                a.get_text(strip=True)
                for a in nav.find_all("a")
                if a.get_text(strip=True)
            ][:10]
            if nav_items:
                parts.append("Navigation: " + " | ".join(nav_items))

        # CTA buttons
        buttons = []
        for btn in soup.find_all(["button", "a"], class_=re.compile(r"btn|cta|button", re.I))[:5]:
            text = btn.get_text(strip=True)
            if text:
                buttons.append(text)
        if buttons:
            parts.append("CTA Buttons: " + " | ".join(buttons))

        # Color hints from inline styles
        style_blocks = soup.find_all("style")
        css_text = " ".join(s.get_text() for s in style_blocks)
        hex_colors = list(set(re.findall(r"#[0-9a-fA-F]{6}", css_text)))[:8]
        if hex_colors:
            parts.append("CSS Colors found: " + " ".join(hex_colors))

        result = "\n".join(parts)
        return result[:max_chars]
