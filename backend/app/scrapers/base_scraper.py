"""
Base scraper class for dark web sources
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from loguru import logger

from .tor_client import tor_client
from ..models import ThreatModel, ThreatCreate, DataSource, ThreatType, ThreatSeverity


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers
    """

    def __init__(self, source: DataSource, source_name: str):
        """
        Initialize scraper

        Args:
            source: Type of data source
            source_name: Name of the specific source
        """
        self.source = source
        self.source_name = source_name
        self.tor_client = tor_client

    @abstractmethod
    async def scrape(self) -> List[ThreatCreate]:
        """
        Main scraping method - must be implemented by subclasses

        Returns:
            List of discovered threats
        """
        pass

    async def fetch_page(self, url: str, **kwargs) -> Optional[str]:
        """
        Fetch a page through Tor

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for tor_client.fetch()

        Returns:
            Page HTML content or None
        """
        logger.info(f"[{self.source_name}] Fetching: {url}")
        return await self.tor_client.fetch_text(url, **kwargs)

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content

        Args:
            html: HTML string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, "lxml")

    def extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """
        Extract text from HTML using CSS selector

        Args:
            soup: BeautifulSoup object
            selector: CSS selector

        Returns:
            Extracted text or None
        """
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None

    def extract_texts(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """
        Extract multiple texts from HTML using CSS selector

        Args:
            soup: BeautifulSoup object
            selector: CSS selector

        Returns:
            List of extracted texts
        """
        elements = soup.select(selector)
        return [el.get_text(strip=True) for el in elements]

    def classify_threat(self, title: str, content: str) -> tuple[ThreatType, ThreatSeverity]:
        """
        Basic threat classification based on keywords

        Args:
            title: Threat title
            content: Threat content

        Returns:
            Tuple of (ThreatType, ThreatSeverity)
        """
        text = (title + " " + content).lower()

        # Critical keywords
        if any(kw in text for kw in ["password", "credentials", "login", "dump", "breach"]):
            return ThreatType.CREDENTIAL_LEAK, ThreatSeverity.CRITICAL

        if any(kw in text for kw in ["credit card", "cvv", "card number", "fullz"]):
            return ThreatType.CREDIT_CARD, ThreatSeverity.CRITICAL

        if any(kw in text for kw in ["ransomware", "ransom", "encrypted"]):
            return ThreatType.RANSOMWARE, ThreatSeverity.CRITICAL

        # High severity keywords
        if any(kw in text for kw in ["database", "leak", "stolen", "hacked"]):
            return ThreatType.DATA_BREACH, ThreatSeverity.HIGH

        if any(kw in text for kw in ["malware", "trojan", "rat", "backdoor"]):
            return ThreatType.MALWARE, ThreatSeverity.HIGH

        if any(kw in text for kw in ["exploit", "vulnerability", "0day", "zero-day"]):
            return ThreatType.EXPLOIT, ThreatSeverity.HIGH

        if any(kw in text for kw in ["phishing", "phish", "fake login"]):
            return ThreatType.PHISHING, ThreatSeverity.HIGH

        # Medium severity
        if any(kw in text for kw in ["personal", "pii", "ssn", "passport"]):
            return ThreatType.PERSONAL_INFO, ThreatSeverity.MEDIUM

        if any(kw in text for kw in ["source code", "repository", "git", "github"]):
            return ThreatType.SOURCE_CODE, ThreatSeverity.MEDIUM

        if any(kw in text for kw in ["botnet", "bot", "zombie"]):
            return ThreatType.BOTNET, ThreatSeverity.MEDIUM

        # Default
        return ThreatType.OTHER, ThreatSeverity.LOW

    def create_threat(
        self,
        title: str,
        content: str,
        url: Optional[str] = None,
        author: Optional[str] = None,
        posted_at: Optional[datetime] = None,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[ThreatSeverity] = None,
    ) -> ThreatCreate:
        """
        Create a threat object

        Args:
            title: Threat title
            content: Threat content
            url: Source URL
            author: Author/poster
            posted_at: When it was posted
            threat_type: Type of threat (auto-classified if not provided)
            severity: Severity level (auto-classified if not provided)

        Returns:
            ThreatCreate object
        """
        # Auto-classify if not provided
        if threat_type is None or severity is None:
            auto_type, auto_severity = self.classify_threat(title, content)
            threat_type = threat_type or auto_type
            severity = severity or auto_severity

        return ThreatCreate(
            title=title,
            content=content,
            url=url,
            source=self.source,
            source_name=self.source_name,
            threat_type=threat_type,
            severity=severity,
            author=author,
            posted_at=posted_at,
        )

    async def validate_connection(self) -> bool:
        """
        Validate scraper can connect to source

        Returns:
            True if connection is valid
        """
        logger.info(f"[{self.source_name}] Validating connection...")
        return True

    def log_stats(self, threats_found: int, errors: int = 0):
        """
        Log scraping statistics

        Args:
            threats_found: Number of threats found
            errors: Number of errors encountered
        """
        logger.info(
            f"[{self.source_name}] Scraping complete - "
            f"Found: {threats_found} threats, Errors: {errors}"
        )
