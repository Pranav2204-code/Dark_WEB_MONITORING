"""
Scraper for dark web marketplaces
"""
from typing import List, Optional
from datetime import datetime
from loguru import logger
import re

from .base_scraper import BaseScraper
from ..models import ThreatCreate, DataSource, ThreatType, ThreatSeverity


class MarketplaceScraper(BaseScraper):
    """
    Scraper for dark web marketplaces

    Monitors for stolen data, credentials, and other illicit goods
    """

    def __init__(self, marketplace_url: str, marketplace_name: str):
        """
        Initialize marketplace scraper

        Args:
            marketplace_url: Base URL of the marketplace
            marketplace_name: Name of the marketplace
        """
        super().__init__(DataSource.MARKETPLACE, marketplace_name)
        self.marketplace_url = marketplace_url

    async def scrape(self) -> List[ThreatCreate]:
        """
        Scrape marketplace listings for threats

        Returns:
            List of discovered threats
        """
        threats = []
        errors = 0

        try:
            # Get categories to monitor
            categories = [
                "data", "databases", "credentials", "accounts",
                "cards", "documents", "malware", "exploits"
            ]

            for category in categories:
                try:
                    category_threats = await self.scrape_category(category)
                    threats.extend(category_threats)
                except Exception as e:
                    logger.error(f"[{self.source_name}] Error scraping category {category}: {e}")
                    errors += 1

        except Exception as e:
            logger.error(f"[{self.source_name}] Scraping error: {e}")
            errors += 1

        self.log_stats(len(threats), errors)
        return threats

    async def scrape_category(self, category: str) -> List[ThreatCreate]:
        """
        Scrape specific marketplace category

        Args:
            category: Category to scrape

        Returns:
            List of threats from category
        """
        threats = []

        try:
            # Construct category URL
            category_url = f"{self.marketplace_url}/category/{category}"

            html = await self.fetch_page(category_url)
            if not html:
                return threats

            soup = self.parse_html(html)

            # Extract listings (adjust selectors for actual marketplace)
            listings = soup.select("div.listing, div.product, div.item")

            for listing in listings[:50]:  # Limit to 50 listings per category
                threat = await self.process_listing(listing, category)
                if threat:
                    threats.append(threat)

        except Exception as e:
            logger.error(f"[{self.source_name}] Error scraping category {category}: {e}")

        return threats

    async def process_listing(self, listing_elem, category: str) -> Optional[ThreatCreate]:
        """
        Process individual marketplace listing

        Args:
            listing_elem: BeautifulSoup element for listing
            category: Category of the listing

        Returns:
            ThreatCreate object if relevant
        """
        try:
            # Extract listing details
            title = self.extract_text(listing_elem, "h3.title, div.listing-title")
            description = self.extract_text(listing_elem, "div.description, p.desc")
            price = self.extract_text(listing_elem, "span.price, div.price")
            seller = self.extract_text(listing_elem, "span.seller, div.vendor")

            listing_url = listing_elem.select_one("a")
            url = listing_url.get("href", "") if listing_url else ""
            if url and not url.startswith("http"):
                url = self.marketplace_url + url

            if not title or not description:
                return None

            # Check if listing is relevant
            full_text = f"{title} {description}".lower()

            # Classify threat type based on content
            threat_type = ThreatType.OTHER
            severity = ThreatSeverity.MEDIUM

            if any(kw in full_text for kw in ["credential", "password", "login", "account"]):
                threat_type = ThreatType.CREDENTIAL_LEAK
                severity = ThreatSeverity.CRITICAL
            elif any(kw in full_text for kw in ["database", "dump", "records"]):
                threat_type = ThreatType.DATA_BREACH
                severity = ThreatSeverity.HIGH
            elif any(kw in full_text for kw in ["card", "cvv", "credit"]):
                threat_type = ThreatType.CREDIT_CARD
                severity = ThreatSeverity.CRITICAL
            elif any(kw in full_text for kw in ["malware", "trojan", "rat"]):
                threat_type = ThreatType.MALWARE
                severity = ThreatSeverity.HIGH
            elif any(kw in full_text for kw in ["exploit", "vulnerability", "0day"]):
                threat_type = ThreatType.EXPLOIT
                severity = ThreatSeverity.HIGH

            # Only create threat for high-value items
            if severity in [ThreatSeverity.CRITICAL, ThreatSeverity.HIGH]:
                logger.info(f"[{self.source_name}] Found relevant listing: {title}")

                content = f"""
Marketplace Listing: {title}

Category: {category}
Seller: {seller}
Price: {price}

Description:
{description}

This item was found on {self.source_name} marketplace.
                """.strip()

                return self.create_threat(
                    title=f"[{self.source_name}] {title}",
                    content=content,
                    url=url,
                    author=seller,
                    threat_type=threat_type,
                    severity=severity,
                )

        except Exception as e:
            logger.error(f"[{self.source_name}] Error processing listing: {e}")

        return None

    def extract_listing_details(self, html: str) -> dict:
        """
        Extract detailed information from listing page

        Args:
            html: Listing page HTML

        Returns:
            Dictionary of listing details
        """
        soup = self.parse_html(html)

        details = {
            "title": self.extract_text(soup, "h1.title, div.product-title"),
            "description": self.extract_text(soup, "div.description, div.product-desc"),
            "price": self.extract_text(soup, "span.price, div.product-price"),
            "seller": self.extract_text(soup, "span.seller, a.vendor"),
            "rating": self.extract_text(soup, "span.rating, div.vendor-rating"),
            "sales": self.extract_text(soup, "span.sales, div.sales-count"),
        }

        return details
