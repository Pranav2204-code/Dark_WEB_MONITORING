"""
Application configuration settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Dark Web Monitoring Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "darkweb_monitor"

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "darkweb_user"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "darkweb_monitor"
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Tor
    TOR_PROXY_HOST: str = "127.0.0.1"
    TOR_PROXY_PORT: int = 9050
    TOR_CONTROL_PORT: int = 9051
    TOR_PASSWORD: str = ""
    USE_TOR: bool = True

    # Scraping
    SCRAPING_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPING_DELAY_MIN: int = 2
    SCRAPING_DELAY_MAX: int = 5
    SCRAPING_TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 5

    # NLP
    NLP_MODEL: str = "en_core_web_sm"
    SENTIMENT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    USE_GPU: bool = False

    # Alerts
    ALERT_EMAIL_ENABLED: bool = True
    ALERT_SLACK_ENABLED: bool = False
    ALERT_WEBHOOK_ENABLED: bool = False

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@darkwebmonitor.com"
    ALERT_RECIPIENTS: List[str] = []

    # Slack
    SLACK_WEBHOOK_URL: str = ""
    SLACK_CHANNEL: str = "#security-alerts"

    # Webhook
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET: str = ""

    # Monitoring
    MONITOR_KEYWORDS: str = ""
    MONITOR_DOMAINS: str = ""
    MONITOR_EMAILS: str = ""

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Data Retention
    DATA_RETENTION_DAYS: int = 365
    CLEANUP_ENABLED: bool = True

    # Features
    ENABLE_AUTO_SCANNING: bool = True
    ENABLE_THREAT_INTELLIGENCE: bool = True
    ENABLE_IOC_EXTRACTION: bool = True
    ENABLE_ACTOR_PROFILING: bool = True

    # Scan Schedules
    SCAN_SCHEDULE_FORUMS: str = "0 */6 * * *"
    SCAN_SCHEDULE_PASTES: str = "0 */1 * * *"
    SCAN_SCHEDULE_MARKETPLACES: str = "0 */12 * * *"
    SCAN_SCHEDULE_TELEGRAM: str = "0 */2 * * *"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def async_postgres_url(self) -> str:
        """Get async PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def keywords_list(self) -> List[str]:
        """Get monitoring keywords as list"""
        return [k.strip() for k in self.MONITOR_KEYWORDS.split(",") if k.strip()]

    @property
    def domains_list(self) -> List[str]:
        """Get monitoring domains as list"""
        return [d.strip() for d in self.MONITOR_DOMAINS.split(",") if d.strip()]

    @property
    def emails_list(self) -> List[str]:
        """Get monitoring emails as list"""
        return [e.strip() for e in self.MONITOR_EMAILS.split(",") if e.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
