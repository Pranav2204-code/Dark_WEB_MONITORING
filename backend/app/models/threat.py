"""
Threat data models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class ThreatSeverity(str, Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatType(str, Enum):
    """Types of threats"""
    CREDENTIAL_LEAK = "credential_leak"
    DATA_BREACH = "data_breach"
    CREDIT_CARD = "credit_card"
    PERSONAL_INFO = "personal_info"
    SOURCE_CODE = "source_code"
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    PHISHING = "phishing"
    COMPANY_MENTION = "company_mention"
    EXECUTIVE_MENTION = "executive_mention"
    VULNERABILITY = "vulnerability"
    EXPLOIT = "exploit"
    BOTNET = "botnet"
    OTHER = "other"


class DataSource(str, Enum):
    """Dark web data sources"""
    FORUM = "forum"
    MARKETPLACE = "marketplace"
    PASTE_SITE = "paste_site"
    TELEGRAM = "telegram"
    CHAT_ROOM = "chat_room"
    HIDDEN_SERVICE = "hidden_service"
    OTHER = "other"


class IOC(BaseModel):
    """Indicator of Compromise"""
    type: str  # ip, domain, email, hash, url, etc.
    value: str
    confidence: float = Field(ge=0.0, le=1.0)


class Entity(BaseModel):
    """Extracted entity from NLP"""
    type: str  # PERSON, ORG, GPE, EMAIL, IP, etc.
    value: str
    confidence: float = Field(ge=0.0, le=1.0)


class ThreatIntelligence(BaseModel):
    """Threat intelligence analysis"""
    sentiment: Optional[str] = None  # positive, negative, neutral
    sentiment_score: Optional[float] = None
    language: Optional[str] = None
    keywords: List[str] = []
    entities: List[Entity] = []
    iocs: List[IOC] = []
    tags: List[str] = []


class ThreatModel(BaseModel):
    """Main threat data model"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    # Basic Information
    title: str
    content: str
    url: Optional[str] = None
    source: DataSource
    source_name: Optional[str] = None  # Specific forum/marketplace name

    # Classification
    threat_type: ThreatType
    severity: ThreatSeverity

    # Intelligence
    intelligence: Optional[ThreatIntelligence] = None

    # Metadata
    author: Optional[str] = None
    posted_at: Optional[datetime] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)

    # Tracking
    false_positive: bool = False
    reviewed: bool = False
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    # Alert
    alert_triggered: bool = False
    alert_sent: bool = False

    # Additional data
    raw_data: Optional[Dict[str, Any]] = None
    screenshots: List[str] = []

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class ThreatCreate(BaseModel):
    """Schema for creating a threat"""
    title: str
    content: str
    url: Optional[str] = None
    source: DataSource
    source_name: Optional[str] = None
    threat_type: ThreatType
    severity: ThreatSeverity
    author: Optional[str] = None
    posted_at: Optional[datetime] = None


class ThreatUpdate(BaseModel):
    """Schema for updating a threat"""
    title: Optional[str] = None
    severity: Optional[ThreatSeverity] = None
    false_positive: Optional[bool] = None
    reviewed: Optional[bool] = None
    reviewed_by: Optional[str] = None


class ThreatResponse(BaseModel):
    """Response schema for threat"""
    id: str
    title: str
    content: str
    url: Optional[str] = None
    source: DataSource
    source_name: Optional[str] = None
    threat_type: ThreatType
    severity: ThreatSeverity
    author: Optional[str] = None
    posted_at: Optional[datetime] = None
    discovered_at: datetime
    false_positive: bool
    reviewed: bool
    alert_triggered: bool

    class Config:
        from_attributes = True
