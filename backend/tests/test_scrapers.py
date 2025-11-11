"""
Tests for scraping functionality
"""
import pytest
from app.scrapers.base_scraper import BaseScraper
from app.models import DataSource, ThreatType, ThreatSeverity


class TestBaseScraper:
    """Test base scraper functionality"""

    def test_classify_threat_credentials(self):
        """Test threat classification for credentials"""
        scraper = BaseScraper(DataSource.FORUM, "test")

        threat_type, severity = scraper.classify_threat(
            "Leaked database",
            "password dump with 10000 credentials"
        )

        assert threat_type == ThreatType.CREDENTIAL_LEAK
        assert severity == ThreatSeverity.CRITICAL

    def test_classify_threat_credit_card(self):
        """Test threat classification for credit cards"""
        scraper = BaseScraper(DataSource.MARKETPLACE, "test")

        threat_type, severity = scraper.classify_threat(
            "Credit card sale",
            "selling credit card numbers with cvv"
        )

        assert threat_type == ThreatType.CREDIT_CARD
        assert severity == ThreatSeverity.CRITICAL

    def test_classify_threat_malware(self):
        """Test threat classification for malware"""
        scraper = BaseScraper(DataSource.FORUM, "test")

        threat_type, severity = scraper.classify_threat(
            "New ransomware",
            "latest ransomware variant available"
        )

        assert threat_type == ThreatType.RANSOMWARE
        assert severity == ThreatSeverity.CRITICAL

    def test_classify_threat_exploit(self):
        """Test threat classification for exploits"""
        scraper = BaseScraper(DataSource.FORUM, "test")

        threat_type, severity = scraper.classify_threat(
            "Zero day vulnerability",
            "new 0day exploit for popular software"
        )

        assert threat_type == ThreatType.EXPLOIT
        assert severity == ThreatSeverity.HIGH

    def test_create_threat(self):
        """Test threat creation"""
        scraper = BaseScraper(DataSource.PASTE_SITE, "pastebin")

        threat = scraper.create_threat(
            title="Test Threat",
            content="Test content with sensitive data",
            url="https://example.com/test",
            author="anonymous"
        )

        assert threat.title == "Test Threat"
        assert threat.content == "Test content with sensitive data"
        assert threat.source == DataSource.PASTE_SITE
        assert threat.source_name == "pastebin"
