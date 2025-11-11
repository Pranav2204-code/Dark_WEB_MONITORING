"""
Advanced rule matching engine for monitoring rules
"""
import re
from typing import List, Dict, Any, Optional
from loguru import logger

from ..models import (
    MonitoringRule,
    ThreatModel,
    RuleConditionType,
    NotificationChannel,
)


class RuleMatcher:
    """
    Advanced rule matching engine that evaluates threats against monitoring rules
    """

    def __init__(self):
        """Initialize rule matcher"""
        self.compiled_patterns: Dict[str, re.Pattern] = {}

    def match(self, threat: ThreatModel, rule: MonitoringRule) -> bool:
        """
        Check if a threat matches a monitoring rule

        Args:
            threat: Threat to evaluate
            rule: Monitoring rule to check against

        Returns:
            True if threat matches rule
        """
        if not rule.enabled:
            return False

        # Check source filtering
        if rule.sources and threat.source not in rule.sources:
            return False

        if rule.exclude_sources and threat.source in rule.exclude_sources:
            return False

        # Evaluate conditions
        results = []
        for condition in rule.conditions:
            result = self._evaluate_condition(threat, condition)
            results.append(result)

        # Apply match logic (AND/OR)
        if rule.match_all:
            return all(results)  # AND - all conditions must match
        else:
            return any(results)  # OR - at least one condition must match

    def _evaluate_condition(self, threat: ThreatModel, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition

        Args:
            threat: Threat to evaluate
            condition: Condition dictionary

        Returns:
            True if condition matches
        """
        try:
            condition_type = RuleConditionType(condition.get("type"))
            field = condition.get("field", "content")
            value = condition.get("value", "")
            case_sensitive = condition.get("case_sensitive", False)
            negate = condition.get("negate", False)

            # Get field value from threat
            field_value = self._get_field_value(threat, field)
            if field_value is None:
                return negate  # If field doesn't exist, return negation

            # Evaluate based on condition type
            if condition_type == RuleConditionType.KEYWORD_MATCH:
                result = self._match_keyword(field_value, value, case_sensitive)
            elif condition_type == RuleConditionType.REGEX_MATCH:
                result = self._match_regex(field_value, value, case_sensitive)
            elif condition_type == RuleConditionType.DOMAIN_MATCH:
                result = self._match_domain(field_value, value)
            elif condition_type == RuleConditionType.EMAIL_MATCH:
                result = self._match_email(field_value, value)
            elif condition_type == RuleConditionType.IP_MATCH:
                result = self._match_ip(field_value, value)
            elif condition_type == RuleConditionType.HASH_MATCH:
                result = self._match_hash(field_value, value)
            elif condition_type == RuleConditionType.DATA_TYPE:
                result = self._match_data_type(threat, value)
            elif condition_type == RuleConditionType.SOURCE:
                result = threat.source == value
            elif condition_type == RuleConditionType.SENTIMENT:
                result = self._match_sentiment(threat, value)
            else:
                logger.warning(f"Unknown condition type: {condition_type}")
                return False

            # Apply negation if specified
            return not result if negate else result

        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False

    def _get_field_value(self, threat: ThreatModel, field: str) -> Optional[str]:
        """Get field value from threat"""
        if field == "content":
            return threat.content
        elif field == "title":
            return threat.title
        elif field == "url":
            return threat.url or ""
        elif field == "author":
            return threat.author or ""
        elif field == "source_name":
            return threat.source_name or ""
        else:
            return getattr(threat, field, None)

    def _match_keyword(self, text: str, keyword: str, case_sensitive: bool) -> bool:
        """Match keyword in text"""
        if not case_sensitive:
            text = text.lower()
            keyword = keyword.lower()
        return keyword in text

    def _match_regex(self, text: str, pattern: str, case_sensitive: bool) -> bool:
        """Match regex pattern"""
        try:
            # Cache compiled patterns
            cache_key = f"{pattern}:{case_sensitive}"
            if cache_key not in self.compiled_patterns:
                flags = 0 if case_sensitive else re.IGNORECASE
                self.compiled_patterns[cache_key] = re.compile(pattern, flags)

            compiled_pattern = self.compiled_patterns[cache_key]
            return bool(compiled_pattern.search(text))
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            return False

    def _match_domain(self, text: str, domain: str) -> bool:
        """Match domain in text"""
        # Look for domain pattern
        domain_pattern = r'\b' + re.escape(domain) + r'\b'
        return bool(re.search(domain_pattern, text, re.IGNORECASE))

    def _match_email(self, text: str, email_pattern: str) -> bool:
        """Match email pattern"""
        # Support wildcards like @company.com
        if email_pattern.startswith("@"):
            # Match any email with this domain
            pattern = r'\b[\w\.-]+' + re.escape(email_pattern) + r'\b'
            return bool(re.search(pattern, text, re.IGNORECASE))
        else:
            # Exact email match
            pattern = r'\b' + re.escape(email_pattern) + r'\b'
            return bool(re.search(pattern, text, re.IGNORECASE))

    def _match_ip(self, text: str, ip_pattern: str) -> bool:
        """Match IP address"""
        # Support CIDR notation and wildcards
        if "*" in ip_pattern:
            # Convert wildcard to regex
            pattern = re.escape(ip_pattern).replace(r'\*', r'\d+')
            return bool(re.search(pattern, text))
        else:
            # Exact IP match
            return ip_pattern in text

    def _match_hash(self, text: str, hash_value: str) -> bool:
        """Match hash (MD5, SHA1, SHA256)"""
        return hash_value.lower() in text.lower()

    def _match_data_type(self, threat: ThreatModel, data_type: str) -> bool:
        """Match threat type"""
        return threat.threat_type == data_type

    def _match_sentiment(self, threat: ThreatModel, sentiment: str) -> bool:
        """Match sentiment"""
        if not threat.intelligence or not threat.intelligence.sentiment:
            return False
        return threat.intelligence.sentiment == sentiment

    async def find_matching_rules(
        self,
        threat: ThreatModel,
        rules: List[MonitoringRule]
    ) -> List[MonitoringRule]:
        """
        Find all rules that match a threat

        Args:
            threat: Threat to evaluate
            rules: List of monitoring rules

        Returns:
            List of matching rules
        """
        matching_rules = []

        for rule in rules:
            try:
                if self.match(threat, rule):
                    matching_rules.append(rule)
                    logger.info(f"Threat matched rule: {rule.name}")
            except Exception as e:
                logger.error(f"Error matching rule {rule.name}: {e}")

        return matching_rules

    def should_send_alert(
        self,
        rule: MonitoringRule,
        recent_alerts_count: int
    ) -> bool:
        """
        Check if alert should be sent based on rate limiting

        Args:
            rule: Monitoring rule
            recent_alerts_count: Number of recent alerts sent

        Returns:
            True if alert should be sent
        """
        if not rule.rate_limit_enabled:
            return True

        return recent_alerts_count < rule.max_alerts_per_hour


# Global rule matcher instance
rule_matcher = RuleMatcher()
