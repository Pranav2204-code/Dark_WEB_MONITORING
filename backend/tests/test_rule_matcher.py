"""
Tests for rule matching engine
"""
import pytest
from datetime import datetime
from app.core.rule_matcher import RuleMatcher
from app.models import (
    ThreatModel,
    MonitoringRule,
    RuleCondition,
    RuleConditionType,
    ThreatType,
    ThreatSeverity,
    DataSource,
    NotificationChannel,
)


class TestRuleMatcher:
    """Test rule matching functionality"""

    @pytest.fixture
    def matcher(self):
        """Create rule matcher instance"""
        return RuleMatcher()

    @pytest.fixture
    def sample_threat(self):
        """Create sample threat"""
        return ThreatModel(
            title="Stolen credentials for sale",
            content="Selling company@example.com credentials with password",
            url="https://example.onion/post/123",
            source=DataSource.FORUM,
            source_name="Dark Forum",
            threat_type=ThreatType.CREDENTIAL_LEAK,
            severity=ThreatSeverity.CRITICAL,
            author="darkuser",
            discovered_at=datetime.utcnow(),
        )

    def test_keyword_match_case_insensitive(self, matcher, sample_threat):
        """Test case-insensitive keyword matching"""
        rule = MonitoringRule(
            name="Test Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="credentials",
                    case_sensitive=False,
                )
            ],
            match_all=True,
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == True

    def test_keyword_match_case_sensitive(self, matcher, sample_threat):
        """Test case-sensitive keyword matching"""
        rule = MonitoringRule(
            name="Test Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="CREDENTIALS",  # Wrong case
                    case_sensitive=True,
                )
            ],
            match_all=True,
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == False

    def test_email_match_domain(self, matcher, sample_threat):
        """Test email domain matching"""
        rule = MonitoringRule(
            name="Email Domain Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.EMAIL_MATCH,
                    field="content",
                    value="@example.com",
                )
            ],
            match_all=True,
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == True

    def test_regex_match(self, matcher, sample_threat):
        """Test regex matching"""
        rule = MonitoringRule(
            name="Regex Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.REGEX_MATCH,
                    field="content",
                    value=r'\b[\w\.-]+@[\w\.-]+\.\w+\b',  # Email pattern
                )
            ],
            match_all=True,
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == True

    def test_multiple_conditions_match_all(self, matcher, sample_threat):
        """Test multiple conditions with AND logic"""
        rule = MonitoringRule(
            name="Multi Condition Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="credentials",
                ),
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="password",
                ),
            ],
            match_all=True,  # AND logic
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == True

    def test_multiple_conditions_match_any(self, matcher, sample_threat):
        """Test multiple conditions with OR logic"""
        rule = MonitoringRule(
            name="Multi Condition Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="nonexistent",  # Won't match
                ),
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="credentials",  # Will match
                ),
            ],
            match_all=False,  # OR logic
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == True

    def test_negation_condition(self, matcher, sample_threat):
        """Test negation logic"""
        rule = MonitoringRule(
            name="Negation Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="bitcoin",
                    negate=True,  # Should NOT contain bitcoin
                )
            ],
            match_all=True,
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == True

    def test_source_filtering(self, matcher, sample_threat):
        """Test source filtering"""
        rule = MonitoringRule(
            name="Source Filter Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="credentials",
                )
            ],
            match_all=True,
            sources=[DataSource.FORUM],  # Only match forum posts
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == True

    def test_disabled_rule(self, matcher, sample_threat):
        """Test that disabled rules don't match"""
        rule = MonitoringRule(
            name="Disabled Rule",
            enabled=False,  # Disabled
            conditions=[
                RuleCondition(
                    type=RuleConditionType.KEYWORD_MATCH,
                    field="content",
                    value="credentials",
                )
            ],
            match_all=True,
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == False

    def test_data_type_condition(self, matcher, sample_threat):
        """Test data type matching"""
        rule = MonitoringRule(
            name="Data Type Rule",
            enabled=True,
            conditions=[
                RuleCondition(
                    type=RuleConditionType.DATA_TYPE,
                    field="threat_type",
                    value=ThreatType.CREDENTIAL_LEAK,
                )
            ],
            match_all=True,
            severity=ThreatSeverity.HIGH,
            notification_channels=[NotificationChannel.DATABASE],
        )

        assert matcher.match(sample_threat, rule) == True
