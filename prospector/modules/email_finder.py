"""Public email discovery module for leads."""

from __future__ import annotations

import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from prospector.models.lead import Lead


class EmailFinder:
    """Find public emails for a lead using layered strategies."""

    def __init__(self, timeout: int = 15) -> None:
        """Initialize the finder with request settings."""
        self.timeout = timeout
        self.session = requests.Session()

    def find(self, lead: Lead) -> Lead:
        """Find and update a public email for the lead."""
        if not lead.website.strip():
            return lead

        candidates = self._build_candidate_urls(lead.website)
        for url in candidates:
            email = self._search_email_from_url(url)
            if email:
                lead.email = email
                return lead

        return lead

    def find_email(self, lead: Lead) -> Lead:
        """Compatibility wrapper for the main workflow."""
        return self.find(lead)

    def _build_candidate_urls(self, website: str) -> list[str]:
        """Build a list of candidate URLs to inspect for emails."""
        cleaned = website.rstrip("/")
        return [
            cleaned,
            f"{cleaned}/contato",
            f"{cleaned}/contact",
            f"{cleaned}/sobre",
            f"{cleaned}/about",
        ]

    def _search_email_from_url(self, url: str) -> str | None:
        """Search a page for a public email address."""
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                verify=True,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
        except (
            requests.exceptions.SSLError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ):
            return None

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        for candidate in self._extract_candidates(soup, html):
            if self._is_valid_email(candidate):
                return candidate

        return ""

    def _extract_candidates(self, soup: BeautifulSoup, html: str) -> list[str]:
        """Extract candidate emails from a page."""
        candidates: list[str] = []

        for tag in soup.find_all(["a", "span", "p", "li", "div"], string=True):
            text = tag.get_text(" ", strip=True)
            if self._is_valid_email(text):
                candidates.append(text)

        for tag in soup.find_all(["a"], href=True):
            href = tag.get("href", "")
            if href.startswith("mailto:"):
                candidates.append(href.replace("mailto:", ""))

        for match in re.finditer(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html):
            candidates.append(match.group(0))

        return candidates

    def _is_valid_email(self, value: Any) -> bool:
        """Validate the format of an email address."""
        if not isinstance(value, str):
            return False
        return bool(re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value.strip()))
