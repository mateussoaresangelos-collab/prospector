"""Public business information enrichment module."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup

from prospector.models.lead import Lead


class BusinessInfoFinder:
    """Enrich a lead with public business information from the web."""

    def __init__(self, timeout: int = 15) -> None:
        """Initialize the finder with request settings."""
        self.timeout = timeout
        self.session = requests.Session()

    def enrich(self, lead: Lead) -> Lead:
        """Enrich the lead with publicly available business information."""
        if not lead.name.strip():
            return lead

        if lead.website.strip():
            self._enrich_from_website(lead)
            return lead

        search_results = self._search_public_sources(lead)
        for strategy in search_results:
            if self._apply_strategy(lead, strategy):
                break

        return lead

    def _enrich_from_website(self, lead: Lead) -> None:
        """Extract public contact data from a known website."""
        try:
            response = self.session.get(
                lead.website,
                timeout=self.timeout,
                verify=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
        except (requests.Timeout, requests.SSLError, requests.RequestException):
            return

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        lead.email = lead.email or self._extract_email(soup, html)
        lead.instagram = lead.instagram or self._extract_social_link(soup, "instagram")
        lead.linkedin = lead.linkedin or self._extract_social_link(soup, "linkedin")
        lead.facebook = lead.facebook or self._extract_social_link(soup, "facebook")
        lead.whatsapp = lead.whatsapp or self._extract_whatsapp(soup, html)

    def _search_public_sources(self, lead: Lead) -> list[dict[str, Any]]:
        """Search public sources for a lead using open web search endpoints."""
        query = f"{lead.name} {lead.city}".strip()
        if not query:
            return []

        encoded_query = quote(query)
        search_url = f"https://duckduckgo.com/html/?q={encoded_query}"

        try:
            response = self.session.get(
                search_url,
                timeout=self.timeout,
                verify=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
        except (requests.Timeout, requests.SSLError, requests.RequestException):
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[dict[str, Any]] = []

        for link in soup.select("a.result__a")[:5]:
            href = link.get("href")
            if href:
                results.append({"url": href, "source": "duckduckgo"})

        return results

    def _apply_strategy(self, lead: Lead, strategy: dict[str, Any]) -> bool:
        """Apply a single enrichment strategy to the lead."""
        url = strategy.get("url", "")
        if not url:
            return False

        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                verify=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            response.raise_for_status()
        except (requests.Timeout, requests.SSLError, requests.RequestException):
            return False

        soup = BeautifulSoup(response.text, "html.parser")
        lead.website = lead.website or self._extract_website(soup, url)
        lead.email = lead.email or self._extract_email(soup, response.text)
        lead.instagram = lead.instagram or self._extract_social_link(soup, "instagram")
        lead.linkedin = lead.linkedin or self._extract_social_link(soup, "linkedin")
        lead.facebook = lead.facebook or self._extract_social_link(soup, "facebook")
        lead.whatsapp = lead.whatsapp or self._extract_whatsapp(soup, response.text)

        return any(
            [
                lead.website,
                lead.email,
                lead.instagram,
                lead.linkedin,
                lead.facebook,
                lead.whatsapp,
            ]
        )

    def _extract_website(self, soup: BeautifulSoup, page_url: str) -> str:
        """Extract a website URL from a page."""
        for tag in soup.find_all(["a", "link"], href=True):
            href = tag.get("href", "")
            if self._is_probable_website(href):
                return urljoin(page_url, href)
        return ""

    def _extract_social_link(self, soup: BeautifulSoup, platform: str) -> str:
        """Extract a social link from the page HTML."""
        for tag in soup.find_all(["a"], href=True):
            href = tag.get("href", "")
            if platform.lower() in href.lower():
                return href
        return ""

    def _extract_email(self, soup: BeautifulSoup, html: str) -> str:
        """Extract an email address from the page content."""
        pattern = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        for match in pattern.finditer(html):
            return match.group(0)
        return ""

    def _extract_whatsapp(self, soup: BeautifulSoup, html: str) -> str:
        """Extract a WhatsApp link or number from the page content."""
        pattern = re.compile(r"wa\.me/[0-9]+|whatsapp\.com/send\?phone=[0-9]+")
        for match in pattern.finditer(html):
            return match.group(0)
        return ""

    def _is_probable_website(self, href: str) -> bool:
        """Return whether a link looks like a website URL."""
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            return False
        if href.startswith(("http://", "https://")):
            return True
        return False
