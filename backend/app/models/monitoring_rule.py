"""
Monitoring rule models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId

from .threat import PyObjectId, ThreatSeverity, ThreatType, DataSource


class RuleConditionType(str, Enum):
    """Types of rule conditions"""
    KEYWORD_MATCH = "keyword_match"
    REGEX_MATCH = "regex_match"
    DOMAIN_MATCH = "domain_match"
    EMAIL_MATCH = "email_match"
    IP_MATCH = "ip_match"
    HASH_MATCH = "hash_match"
    DATA_TYPE = "data_type"
    SOURCE = "source"
    SENTIMENT = "sentiment"


class RuleCondition(BaseModel):
    """Individual rule condition"""
    type: RuleConditionType
    field: str  # Field to check (content, title, url, etc.)
    value: str  # Value or pattern to match
    case_sensitive: bool = False
    negate: bool = False  # NOT condition


class NotificationChannel(str, Enum):
    """Notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DATABASE = "database"


class MonitoringRule(BaseModel):
    """Monitoring rule model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    # Basic Information
    name: str
    description: Optional[str] = None
    enabled: bool = True

    # Conditions
    conditions: List[RuleCondition]
    match_all: bool = True  # AND (True) or OR (False) logic

    # Classification
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    threat_type: Optional[ThreatType] = None

    # Filtering
    sources: Optional[List[DataSource]] = None  # Limit to specific sources
    exclude_sources: Optional[List[DataSource]] = None

    # Notifications
    notification_channels: List[NotificationChannel] = [NotificationChannel.DATABASE]
    notification_recipients: List[str] = []  # Email addresses or Slack users

    # Rate Limiting
    rate_limit_enabled: bool = False
    max_alerts_per_hour: int = 10

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None

    # Stats
    total_matches: int = 0
    total_alerts: int = 0
    last_triggered: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class MonitoringRuleCreate(BaseModel):
    """Schema for creating a monitoring rule"""
    name: str
    description: Optional[str] = None
    enabled: bool = True
    conditions: List[RuleCondition]
    match_all: bool = True
    severity: ThreatSeverity = ThreatSeverity.MEDIUM
    threat_type: Optional[ThreatType] = None
    sources: Optional[List[DataSource]] = None
    notification_channels: List[NotificationChannel] = [NotificationChannel.DATABASE]
    notification_recipients: List[str] = []


class MonitoringRuleUpdate(BaseModel):
    """Schema for updating a monitoring rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    conditions: Optional[List[RuleCondition]] = None
    match_all: Optional[bool] = None
    severity: Optional[ThreatSeverity] = None
    notification_channels: Optional[List[NotificationChannel]] = None
    notification_recipients: Optional[List[str]] = None


class MonitoringRuleResponse(BaseModel):
    """Response schema for monitoring rule"""
    id: str
    name: str
    description: Optional[str] = None
    enabled: bool
    severity: ThreatSeverity
    total_matches: int
    total_alerts: int
    last_triggered: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
