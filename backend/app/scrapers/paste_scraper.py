"""
Scraper for paste sites (Pastebin-like services)
"""
from typing import List, Optional
from datetime import datetime
from loguru import logger
import re

from .base_scraper import BaseScraper
from ..models import ThreatCreate, DataSource


class PasteScraper(BaseScraper):
    """
    Scraper for paste sites that may contain leaked data

    Note: This is a template scraper. Actual implementation would target
    specific paste sites on the dark web or clearnet.
    """

    def __init__(self, site_url: str, site_name: str):
        """
        Initialize paste scraper

        Args:
            site_url: Base URL of the paste site
            site_name: Name of the paste site
        """
        super().__init__(DataSource.PASTE_SITE, site_name)
        self.site_url = site_url

    async def scrape(self) -> List[ThreatCreate]:
        """
        Scrape recent pastes for threats

        Returns:
            List of discovered threats
        """
        threats = []
        errors = 0

        try:
            # Fetch recent pastes list
            recent_url = f"{self.site_url}/archive"
            html = await self.fetch_page(recent_url)

            if not html:
                logger.error(f"[{self.source_name}] Failed to fetch recent pastes")
                return threats

            soup = self.parse_html(html)

            # Extract paste links (adjust selectors based on actual site)
            paste_links = soup.select("a.paste-link")[:20]  # Last 20 pastes

            logger.info(f"[{self.source_name}] Found {len(paste_links)} recent pastes")

            # Process each paste
            for link in paste_links:
                try:
                    paste_url = link.get("href", "")
                    if not paste_url.startswith("http"):
                        paste_url = self.site_url + paste_url

                    threat = await self.scrape_paste(paste_url)
                    if threat:
                        threats.append(threat)

                except Exception as e:
                    logger.error(f"[{self.source_name}] Error processing paste: {e}")
                    errors += 1

        except Exception as e:
            logger.error(f"[{self.source_name}] Scraping error: {e}")
            errors += 1

        self.log_stats(len(threats), errors)
        return threats

    async def scrape_paste(self, url: str) -> Optional[ThreatCreate]:
        """
        Scrape individual paste

        Args:
            url: Paste URL

        Returns:
            ThreatCreate object if relevant content found
        """
        try:
            html = await self.fetch_page(url)
            if not html:
                return None

            soup = self.parse_html(html)

            # Extract paste content
            title = self.extract_text(soup, "h1.paste-title") or "Untitled Paste"
            content = self.extract_text(soup, "div.paste-content") or ""
            author = self.extract_text(soup, "span.paste-author") or "Anonymous"

            # Extract timestamp
            posted_at = None
            timestamp_text = self.extract_text(soup, "span.paste-date")
            if timestamp_text:
                posted_at = self.parse_timestamp(timestamp_text)

            # Check if paste contains sensitive data
            if not self.is_relevant(content):
                return None

            # Look for credentials pattern
            has_credentials = self.detect_credentials(content)
            has_credit_cards = self.detect_credit_cards(content)
            has_emails = self.detect_emails(content)

            # Only create threat if sensitive data detected
            if has_credentials or has_credit_cards or has_emails:
                logger.info(f"[{self.source_name}] Found sensitive data in paste: {title}")

                return self.create_threat(
                    title=title,
                    content=content[:5000],  # Limit content size
                    url=url,
                    author=author,
                    posted_at=posted_at,
                )

            return None

        except Exception as e:
            logger.error(f"[{self.source_name}] Error scraping paste {url}: {e}")
            return None

    def is_relevant(self, content: str) -> bool:
        """
        Check if paste content is relevant for monitoring

        Args:
            content: Paste content

        Returns:
            True if relevant
        """
        if not content or len(content) < 50:
            return False

        keywords = [
            "password", "email", "username", "login", "credentials",
            "database", "dump", "leak", "breach", "hacked",
            "credit card", "cvv", "ssn", "passport",
            "api key", "token", "secret", "private key",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in keywords)

    def detect_credentials(self, text: str) -> bool:
        """
        Detect credential patterns in text

        Args:
            text: Text to analyze

        Returns:
            True if credentials detected
        """
        # Pattern: email:password or username:password
        pattern = r'[\w\.-]+@[\w\.-]+\.[\w]+:[\w!@#$%^&*(),.?":{}|<>]+'
        matches = re.findall(pattern, text)
        return len(matches) > 5  # At least 5 credential pairs

    def detect_credit_cards(self, text: str) -> bool:
        """
        Detect credit card patterns in text

        Args:
            text: Text to analyze

        Returns:
            True if credit cards detected
        """
        # Pattern: 16-digit credit card numbers
        pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        matches = re.findall(pattern, text)
        return len(matches) > 3

    def detect_emails(self, text: str) -> bool:
        """
        Detect email addresses in text

        Args:
            text: Text to analyze

        Returns:
            True if significant emails detected
        """
        pattern = r'[\w\.-]+@[\w\.-]+\.[\w]+'
        matches = re.findall(pattern, text)
        return len(matches) > 10

    def parse_timestamp(self, timestamp_text: str) -> Optional[datetime]:
        """
        Parse timestamp from text

        Args:
            timestamp_text: Timestamp string

        Returns:
            Datetime object or None
        """
        try:
            # Try common formats
            # This would need to be customized based on actual site format
            from dateutil import parser
            return parser.parse(timestamp_text)
        except Exception:
            return None
