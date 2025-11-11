"""
NLP-based threat intelligence analyzer
"""
import re
from typing import List, Dict, Optional, Tuple
from loguru import logger

from ..models import ThreatIntelligence, Entity, IOC


class ThreatAnalyzer:
    """
    Analyzes threat content using NLP to extract intelligence
    """

    def __init__(self):
        """Initialize threat analyzer"""
        self.nlp = None
        self.sentiment_analyzer = None
        self._initialize_models()

    def _initialize_models(self):
        """Initialize NLP models"""
        try:
            import spacy
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
                self.nlp = None

            # Initialize sentiment analyzer
            try:
                from textblob import TextBlob
                self.sentiment_analyzer = TextBlob
                logger.info("Sentiment analyzer initialized")
            except ImportError:
                logger.warning("TextBlob not available for sentiment analysis")
                self.sentiment_analyzer = None

        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")

    async def analyze(self, text: str, title: str = "") -> ThreatIntelligence:
        """
        Perform comprehensive threat intelligence analysis

        Args:
            text: Text content to analyze
            title: Optional title

        Returns:
            ThreatIntelligence object
        """
        combined_text = f"{title} {text}"

        # Extract entities
        entities = self.extract_entities(combined_text)

        # Extract IOCs
        iocs = self.extract_iocs(combined_text)

        # Analyze sentiment
        sentiment, sentiment_score = self.analyze_sentiment(text)

        # Detect language
        language = self.detect_language(text)

        # Extract keywords
        keywords = self.extract_keywords(combined_text)

        # Generate tags
        tags = self.generate_tags(combined_text, entities, iocs)

        return ThreatIntelligence(
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            language=language,
            keywords=keywords,
            entities=entities,
            iocs=iocs,
            tags=tags,
        )

    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities from text

        Args:
            text: Text to analyze

        Returns:
            List of extracted entities
        """
        entities = []

        if self.nlp:
            try:
                doc = self.nlp(text[:100000])  # Limit text size
                for ent in doc.ents:
                    entities.append(
                        Entity(
                            type=ent.label_,
                            value=ent.text,
                            confidence=0.8,  # spaCy doesn't provide confidence scores by default
                        )
                    )
            except Exception as e:
                logger.error(f"Entity extraction failed: {e}")

        # Also extract custom entities
        custom_entities = self._extract_custom_entities(text)
        entities.extend(custom_entities)

        # Deduplicate
        seen = set()
        unique_entities = []
        for entity in entities:
            key = (entity.type, entity.value.lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities[:50]  # Limit to top 50

    def _extract_custom_entities(self, text: str) -> List[Entity]:
        """
        Extract custom entities using regex patterns

        Args:
            text: Text to analyze

        Returns:
            List of entities
        """
        entities = []

        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append(Entity(type="EMAIL", value=match.group(), confidence=0.95))

        # Phone numbers
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
        for match in re.finditer(phone_pattern, text):
            entities.append(Entity(type="PHONE", value=match.group(), confidence=0.9))

        # Bitcoin addresses
        btc_pattern = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
        for match in re.finditer(btc_pattern, text):
            entities.append(Entity(type="BITCOIN_ADDRESS", value=match.group(), confidence=0.85))

        return entities

    def extract_iocs(self, text: str) -> List[IOC]:
        """
        Extract Indicators of Compromise (IOCs)

        Args:
            text: Text to analyze

        Returns:
            List of IOCs
        """
        iocs = []

        # IP addresses (IPv4)
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        for match in re.finditer(ip_pattern, text):
            ip = match.group()
            if self._is_valid_ip(ip):
                iocs.append(IOC(type="ipv4", value=ip, confidence=0.9))

        # Domains
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        for match in re.finditer(domain_pattern, text):
            domain = match.group()
            if not self._is_common_domain(domain):
                iocs.append(IOC(type="domain", value=domain, confidence=0.8))

        # URLs
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        for match in re.finditer(url_pattern, text):
            iocs.append(IOC(type="url", value=match.group(), confidence=0.95))

        # File hashes (MD5, SHA1, SHA256)
        md5_pattern = r'\b[a-fA-F0-9]{32}\b'
        sha1_pattern = r'\b[a-fA-F0-9]{40}\b'
        sha256_pattern = r'\b[a-fA-F0-9]{64}\b'

        for match in re.finditer(sha256_pattern, text):
            iocs.append(IOC(type="sha256", value=match.group(), confidence=0.95))

        for match in re.finditer(sha1_pattern, text):
            if not any(ioc.value == match.group() for ioc in iocs):
                iocs.append(IOC(type="sha1", value=match.group(), confidence=0.9))

        for match in re.finditer(md5_pattern, text):
            if not any(ioc.value == match.group() for ioc in iocs):
                iocs.append(IOC(type="md5", value=match.group(), confidence=0.85))

        # Deduplicate
        seen = set()
        unique_iocs = []
        for ioc in iocs:
            if ioc.value.lower() not in seen:
                seen.add(ioc.value.lower())
                unique_iocs.append(ioc)

        return unique_iocs[:100]  # Limit to top 100

    def _is_valid_ip(self, ip: str) -> bool:
        """Check if IP address is valid and not private"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False

            # Check each octet
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False

            # Exclude private/reserved IPs
            first = int(parts[0])
            if first in [0, 10, 127] or (first == 172 and 16 <= int(parts[1]) <= 31) or (first == 192 and int(parts[1]) == 168):
                return False

            return True
        except:
            return False

    def _is_common_domain(self, domain: str) -> bool:
        """Check if domain is a common legitimate domain"""
        common_domains = [
            'google.com', 'facebook.com', 'twitter.com', 'youtube.com',
            'linkedin.com', 'instagram.com', 'github.com', 'stackoverflow.com',
            'wikipedia.org', 'reddit.com', 'example.com', 'test.com'
        ]
        return domain.lower() in common_domains

    def analyze_sentiment(self, text: str) -> Tuple[Optional[str], Optional[float]]:
        """
        Analyze sentiment of text

        Args:
            text: Text to analyze

        Returns:
            Tuple of (sentiment_label, sentiment_score)
        """
        if not self.sentiment_analyzer:
            return None, None

        try:
            blob = self.sentiment_analyzer(text[:5000])  # Limit text size
            polarity = blob.sentiment.polarity

            # Classify sentiment
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"

            return sentiment, polarity

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return None, None

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of text

        Args:
            text: Text to analyze

        Returns:
            Language code (e.g., 'en', 'es')
        """
        try:
            from textblob import TextBlob
            blob = TextBlob(text[:1000])
            return blob.detect_language()
        except Exception:
            return "en"  # Default to English

    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        Extract important keywords from text

        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords

        Returns:
            List of keywords
        """
        if not self.nlp:
            return self._simple_keyword_extraction(text, max_keywords)

        try:
            doc = self.nlp(text[:50000])

            # Extract nouns and proper nouns
            keywords = []
            for token in doc:
                if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 3:
                    keywords.append(token.text.lower())

            # Count frequencies
            from collections import Counter
            word_freq = Counter(keywords)

            # Return top keywords
            return [word for word, _ in word_freq.most_common(max_keywords)]

        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return self._simple_keyword_extraction(text, max_keywords)

    def _simple_keyword_extraction(self, text: str, max_keywords: int) -> List[str]:
        """Simple keyword extraction without NLP"""
        words = re.findall(r'\b\w{4,}\b', text.lower())
        from collections import Counter
        word_freq = Counter(words)
        return [word for word, _ in word_freq.most_common(max_keywords)]

    def generate_tags(self, text: str, entities: List[Entity], iocs: List[IOC]) -> List[str]:
        """
        Generate tags for categorization

        Args:
            text: Text content
            entities: Extracted entities
            iocs: Extracted IOCs

        Returns:
            List of tags
        """
        tags = set()

        text_lower = text.lower()

        # Threat type tags
        if 'ransomware' in text_lower or 'ransom' in text_lower:
            tags.add('ransomware')
        if 'malware' in text_lower or 'virus' in text_lower or 'trojan' in text_lower:
            tags.add('malware')
        if 'phishing' in text_lower or 'phish' in text_lower:
            tags.add('phishing')
        if 'ddos' in text_lower or 'denial of service' in text_lower:
            tags.add('ddos')
        if 'exploit' in text_lower or 'vulnerability' in text_lower:
            tags.add('exploit')
        if 'breach' in text_lower or 'leak' in text_lower or 'dump' in text_lower:
            tags.add('data-breach')
        if 'credential' in text_lower or 'password' in text_lower or 'login' in text_lower:
            tags.add('credentials')

        # Data type tags
        if 'credit card' in text_lower or 'cvv' in text_lower:
            tags.add('financial')
        if 'ssn' in text_lower or 'social security' in text_lower:
            tags.add('pii')
        if any(e.type == 'EMAIL' for e in entities):
            tags.add('contains-emails')
        if any(ioc.type in ['ipv4', 'ipv6'] for ioc in iocs):
            tags.add('contains-ips')
        if any(ioc.type in ['md5', 'sha1', 'sha256'] for ioc in iocs):
            tags.add('contains-hashes')

        return list(tags)


# Global analyzer instance
threat_analyzer = ThreatAnalyzer()
