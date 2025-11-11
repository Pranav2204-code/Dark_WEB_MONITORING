"""
Tests for NLP analysis functionality
"""
import pytest
from app.nlp.threat_analyzer import ThreatAnalyzer


class TestThreatAnalyzer:
    """Test threat analysis"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return ThreatAnalyzer()

    def test_extract_emails(self, analyzer):
        """Test email extraction"""
        text = "Contact me at john@example.com or admin@test.org for more info"
        entities = analyzer._extract_custom_entities(text)

        email_entities = [e for e in entities if e.type == "EMAIL"]
        assert len(email_entities) >= 2
        assert any("john@example.com" in e.value for e in email_entities)

    def test_extract_bitcoin_addresses(self, analyzer):
        """Test Bitcoin address extraction"""
        text = "Send payment to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        entities = analyzer._extract_custom_entities(text)

        btc_entities = [e for e in entities if e.type == "BITCOIN_ADDRESS"]
        assert len(btc_entities) >= 1

    def test_extract_ipv4(self, analyzer):
        """Test IPv4 extraction"""
        text = "Connect to 192.168.1.100 or 8.8.8.8 for testing"
        iocs = analyzer.extract_iocs(text)

        ip_iocs = [i for i in iocs if i.type == "ipv4"]
        # Note: Private IPs are filtered out
        assert len(ip_iocs) >= 1

    def test_extract_domains(self, analyzer):
        """Test domain extraction"""
        text = "Visit malicious-site.com or evil.org for downloads"
        iocs = analyzer.extract_iocs(text)

        domain_iocs = [i for i in iocs if i.type == "domain"]
        assert len(domain_iocs) >= 2

    def test_extract_hashes(self, analyzer):
        """Test hash extraction"""
        md5 = "5d41402abc4b2a76b9719d911017c592"
        sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        text = f"MD5: {md5} SHA256: {sha256}"

        iocs = analyzer.extract_iocs(text)

        hash_iocs = [i for i in iocs if i.type in ["md5", "sha256"]]
        assert len(hash_iocs) >= 2

    def test_extract_keywords(self, analyzer):
        """Test keyword extraction"""
        text = """
        This is a test document about malware analysis.
        We are analyzing malware samples and threat actors.
        The malware campaign targets financial institutions.
        """

        keywords = analyzer.extract_keywords(text, max_keywords=10)

        assert len(keywords) > 0
        # Common words should appear in keywords
        assert any(k in ["malware", "analysis", "test"] for k in keywords)

    def test_generate_tags(self, analyzer):
        """Test tag generation"""
        text = "New ransomware campaign targeting healthcare with phishing emails"
        entities = []
        iocs = []

        tags = analyzer.generate_tags(text, entities, iocs)

        assert "ransomware" in tags
        assert "phishing" in tags

    def test_is_valid_ip(self, analyzer):
        """Test IP validation"""
        assert analyzer._is_valid_ip("8.8.8.8") == True
        assert analyzer._is_valid_ip("192.168.1.1") == False  # Private IP
        assert analyzer._is_valid_ip("10.0.0.1") == False  # Private IP
        assert analyzer._is_valid_ip("256.1.1.1") == False  # Invalid
        assert analyzer._is_valid_ip("invalid") == False
