"""
Scraper for Telegram channels (public channels via web preview)
"""
from typing import List, Optional
from datetime import datetime
from loguru import logger

from .base_scraper import BaseScraper
from ..models import ThreatCreate, DataSource


class TelegramScraper(BaseScraper):
    """
    Scraper for public Telegram channels via web preview

    Note: This uses the public web preview. For full API access,
    you would need Telegram API credentials.
    """

    def __init__(self, channel_username: str):
        """
        Initialize Telegram scraper

        Args:
            channel_username: Telegram channel username (without @)
        """
        super().__init__(DataSource.TELEGRAM, f"@{channel_username}")
        self.channel_username = channel_username
        self.base_url = f"https://t.me/s/{channel_username}"

    async def scrape(self) -> List[ThreatCreate]:
        """
        Scrape Telegram channel for threats

        Returns:
            List of discovered threats
        """
        threats = []
        errors = 0

        try:
            logger.info(f"[{self.source_name}] Scraping Telegram channel")

            html = await self.fetch_page(self.base_url)
            if not html:
                logger.error(f"[{self.source_name}] Failed to fetch channel")
                return threats

            soup = self.parse_html(html)

            # Extract messages (Telegram web preview structure)
            messages = soup.select("div.tgme_widget_message")

            logger.info(f"[{self.source_name}] Found {len(messages)} messages")

            for message in messages[:100]:  # Last 100 messages
                try:
                    threat = await self.process_message(message)
                    if threat:
                        threats.append(threat)
                except Exception as e:
                    logger.error(f"[{self.source_name}] Error processing message: {e}")
                    errors += 1

        except Exception as e:
            logger.error(f"[{self.source_name}] Scraping error: {e}")
            errors += 1

        self.log_stats(len(threats), errors)
        return threats

    async def process_message(self, message_elem) -> Optional[ThreatCreate]:
        """
        Process individual Telegram message

        Args:
            message_elem: BeautifulSoup element for message

        Returns:
            ThreatCreate object if relevant
        """
        try:
            # Extract message text
            text_elem = message_elem.select_one("div.tgme_widget_message_text")
            if not text_elem:
                return None

            message_text = text_elem.get_text(strip=True)

            if not message_text or len(message_text) < 50:
                return None

            # Check if message is threat-related
            if not self.is_relevant(message_text):
                return None

            # Extract metadata
            author_elem = message_elem.select_one("span.tgme_widget_message_from_author")
            author = author_elem.get_text(strip=True) if author_elem else self.channel_username

            date_elem = message_elem.select_one("time")
            posted_at = None
            if date_elem and date_elem.get("datetime"):
                try:
                    from dateutil import parser
                    posted_at = parser.parse(date_elem.get("datetime"))
                except Exception:
                    pass

            # Get message URL
            link_elem = message_elem.select_one("a.tgme_widget_message_date")
            message_url = link_elem.get("href", "") if link_elem else self.base_url

            # Determine threat type and severity
            threat_type, severity = self.classify_threat(message_text, message_text)

            logger.info(f"[{self.source_name}] Found threat message")

            return self.create_threat(
                title=f"Telegram: {message_text[:100]}",
                content=message_text,
                url=message_url,
                author=author,
                posted_at=posted_at,
                threat_type=threat_type,
                severity=severity,
            )

        except Exception as e:
            logger.error(f"[{self.source_name}] Error processing message: {e}")

        return None


class TelegramChannelMonitor:
    """
    Monitor multiple Telegram channels
    """

    def __init__(self, channels: List[str]):
        """
        Initialize monitor for multiple channels

        Args:
            channels: List of channel usernames to monitor
        """
        self.scrapers = [TelegramScraper(channel) for channel in channels]

    async def scrape_all(self) -> List[ThreatCreate]:
        """
        Scrape all configured Telegram channels

        Returns:
            Combined list of threats from all channels
        """
        all_threats = []

        for scraper in self.scrapers:
            try:
                threats = await scraper.scrape()
                all_threats.extend(threats)
            except Exception as e:
                logger.error(f"Error scraping {scraper.source_name}: {e}")

        return all_threats
