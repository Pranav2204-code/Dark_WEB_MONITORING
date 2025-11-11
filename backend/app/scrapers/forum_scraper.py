"""
Scraper for dark web forums
"""
from typing import List, Optional
from datetime import datetime
from loguru import logger
import re

from .base_scraper import BaseScraper
from ..models import ThreatCreate, DataSource, ThreatType, ThreatSeverity


class ForumScraper(BaseScraper):
    """
    Scraper for dark web forums that may contain threat intelligence

    This is a template that can be customized for specific forums
    """

    def __init__(self, forum_url: str, forum_name: str):
        """
        Initialize forum scraper

        Args:
            forum_url: Base URL of the forum
            forum_name: Name of the forum
        """
        super().__init__(DataSource.FORUM, forum_name)
        self.forum_url = forum_url
        self.threads_per_page = 20

    async def scrape(self) -> List[ThreatCreate]:
        """
        Scrape recent forum threads for threats

        Returns:
            List of discovered threats
        """
        threats = []
        errors = 0

        try:
            # Get list of recent threads
            threads = await self.get_recent_threads()
            logger.info(f"[{self.source_name}] Found {len(threads)} recent threads")

            # Process each thread
            for thread in threads[:50]:  # Limit to 50 most recent
                try:
                    thread_threats = await self.scrape_thread(thread)
                    threats.extend(thread_threats)
                except Exception as e:
                    logger.error(f"[{self.source_name}] Error processing thread {thread.get('url')}: {e}")
                    errors += 1

        except Exception as e:
            logger.error(f"[{self.source_name}] Scraping error: {e}")
            errors += 1

        self.log_stats(len(threats), errors)
        return threats

    async def get_recent_threads(self) -> List[dict]:
        """
        Get list of recent forum threads

        Returns:
            List of thread metadata dictionaries
        """
        threads = []

        try:
            # Fetch forum index page
            html = await self.fetch_page(self.forum_url)
            if not html:
                return threads

            soup = self.parse_html(html)

            # Extract thread links (adjust selectors for actual forum)
            thread_elements = soup.select("div.thread-item, tr.thread-row")

            for element in thread_elements:
                # Extract thread metadata
                title_elem = element.select_one("a.thread-title, td.thread-title a")
                if not title_elem:
                    continue

                thread_url = title_elem.get("href", "")
                if not thread_url.startswith("http"):
                    thread_url = self.forum_url + thread_url

                thread_data = {
                    "title": title_elem.get_text(strip=True),
                    "url": thread_url,
                    "author": self.extract_text(element, "span.author, td.author"),
                    "replies": self.extract_text(element, "span.replies, td.replies"),
                    "views": self.extract_text(element, "span.views, td.views"),
                }

                threads.append(thread_data)

        except Exception as e:
            logger.error(f"[{self.source_name}] Error getting threads: {e}")

        return threads

    async def scrape_thread(self, thread_meta: dict) -> List[ThreatCreate]:
        """
        Scrape individual forum thread

        Args:
            thread_meta: Thread metadata dictionary

        Returns:
            List of threats found in thread
        """
        threats = []

        try:
            url = thread_meta.get("url")
            if not url:
                return threats

            html = await self.fetch_page(url)
            if not html:
                return threats

            soup = self.parse_html(html)

            # Extract posts from thread
            posts = soup.select("div.post, div.message")

            for post in posts:
                # Extract post content
                content_elem = post.select_one("div.post-content, div.message-body")
                if not content_elem:
                    continue

                content = content_elem.get_text(strip=True)

                # Check if post contains relevant threat intelligence
                if not self.is_threat_related(content):
                    continue

                # Extract post metadata
                author = self.extract_text(post, "span.author, div.author-name")
                post_date = self.extract_text(post, "span.post-date, div.post-time")

                # Check for specific threat indicators
                has_credentials = self.contains_credentials(content)
                has_malware = self.contains_malware_indicators(content)
                has_exploit = self.contains_exploit_indicators(content)
                has_data_breach = self.contains_breach_indicators(content)

                if has_credentials or has_malware or has_exploit or has_data_breach:
                    logger.info(f"[{self.source_name}] Found threat in thread: {thread_meta['title']}")

                    # Determine threat type and severity
                    if has_credentials:
                        threat_type = ThreatType.CREDENTIAL_LEAK
                        severity = ThreatSeverity.CRITICAL
                    elif has_data_breach:
                        threat_type = ThreatType.DATA_BREACH
                        severity = ThreatSeverity.HIGH
                    elif has_malware:
                        threat_type = ThreatType.MALWARE
                        severity = ThreatSeverity.HIGH
                    elif has_exploit:
                        threat_type = ThreatType.EXPLOIT
                        severity = ThreatSeverity.HIGH
                    else:
                        threat_type = ThreatType.OTHER
                        severity = ThreatSeverity.MEDIUM

                    threat = self.create_threat(
                        title=thread_meta["title"],
                        content=content[:5000],  # Limit content size
                        url=url,
                        author=author,
                        posted_at=self.parse_date(post_date),
                        threat_type=threat_type,
                        severity=severity,
                    )
                    threats.append(threat)

        except Exception as e:
            logger.error(f"[{self.source_name}] Error scraping thread: {e}")

        return threats

    def is_threat_related(self, content: str) -> bool:
        """
        Check if content is related to threat intelligence

        Args:
            content: Post content

        Returns:
            True if threat-related
        """
        content_lower = content.lower()

        threat_keywords = [
            "database", "dump", "leak", "breach", "hacked", "stolen",
            "password", "credential", "login", "account",
            "malware", "ransomware", "trojan", "exploit",
            "vulnerability", "0day", "zero-day",
            "credit card", "cvv", "fullz", "ssn",
            "sell", "selling", "sale", "buy", "buying",
        ]

        return any(keyword in content_lower for keyword in threat_keywords)

    def contains_credentials(self, content: str) -> bool:
        """Check if content contains credential dumps"""
        # Look for email:password patterns
        pattern = r'[\w\.-]+@[\w\.-]+\.[\w]+:[\S]+'
        matches = re.findall(pattern, content)
        return len(matches) >= 5

    def contains_malware_indicators(self, content: str) -> bool:
        """Check if content contains malware indicators"""
        content_lower = content.lower()
        indicators = ["malware", "trojan", "rat", "backdoor", "ransomware", "crypter"]
        return any(indicator in content_lower for indicator in indicators)

    def contains_exploit_indicators(self, content: str) -> bool:
        """Check if content contains exploit indicators"""
        content_lower = content.lower()
        indicators = ["exploit", "vulnerability", "0day", "zero-day", "cve-", "rce", "sql injection"]
        return any(indicator in content_lower for indicator in indicators)

    def contains_breach_indicators(self, content: str) -> bool:
        """Check if content contains data breach indicators"""
        content_lower = content.lower()
        indicators = ["database", "dump", "breach", "leaked", "stolen data", "hack"]
        count = sum(1 for indicator in indicators if indicator in content_lower)
        return count >= 2

    def parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime

        Args:
            date_str: Date string

        Returns:
            Datetime object or None
        """
        if not date_str:
            return None

        try:
            from dateutil import parser
            return parser.parse(date_str)
        except Exception:
            return None
