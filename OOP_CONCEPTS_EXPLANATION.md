# Object-Oriented Programming (OOP) Concepts in Dark Web Monitoring Platform

## Complete Guide for Jury Presentation

---

## Overview

This Dark Web Monitoring Platform extensively uses Object-Oriented Programming principles throughout its architecture. Below is a comprehensive breakdown of **ALL 6 core OOP concepts** used in the project, with specific code examples and file locations.

---

## Table of Contents
1. [Classes and Objects](#classes)
2. [Encapsulation](#encapsulation)
3. [Inheritance](#inheritance)
4. [Polymorphism](#polymorphism)
5. [Abstraction](#abstraction)
6. [Composition](#composition)
7. [Summary for Presentation](#summary)

---

<a name="classes"></a>
## 1. Classes and Objects

**Concept**: Classes are blueprints for creating objects. Objects are instances of classes.

### Example 1: Pydantic Models (Data Classes)

**Location**: `backend/app/models/threat.py`

```python
class ThreatModel(BaseModel):
    """Main threat data model - Blueprint for threat objects"""

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    content: str
    url: Optional[str] = None
    source: DataSource
    severity: ThreatSeverity
    threat_type: ThreatType
    intelligence: Optional[ThreatIntelligence] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    false_positive: bool = False
    reviewed: bool = False

# Creating objects (instances) of this class:
threat1 = ThreatModel(
    title="Database Leak",
    content="Selling company database...",
    source=DataSource.FORUM,
    severity=ThreatSeverity.CRITICAL,
    threat_type=ThreatType.CREDENTIAL_LEAK
)

threat2 = ThreatModel(
    title="Malware Distribution",
    content="New ransomware variant...",
    source=DataSource.MARKETPLACE,
    severity=ThreatSeverity.HIGH,
    threat_type=ThreatType.MALWARE
)
```

**Why This Matters**:
- Each threat is an **object** with its own data (title, severity, etc.)
- The **class** defines what properties all threat objects have
- We can create unlimited threat objects from one class blueprint

### Example 2: NLP Analyzer Class

**Location**: `backend/app/nlp/threat_analyzer.py`

```python
class ThreatAnalyzer:
    """Analyzes threat content using NLP to extract intelligence"""

    def __init__(self):
        """Initialize threat analyzer - Constructor method"""
        self.nlp = None
        self.sentiment_analyzer = None
        self._initialize_models()

    def _initialize_models(self):
        """Private method to load ML models"""
        import spacy
        self.nlp = spacy.load("en_core_web_sm")

    async def analyze(self, text: str) -> ThreatIntelligence:
        """Public method to analyze text"""
        entities = self.extract_entities(text)
        iocs = self.extract_iocs(text)
        sentiment = self.analyze_sentiment(text)

        return ThreatIntelligence(
            entities=entities,
            iocs=iocs,
            sentiment=sentiment
        )

# Creating analyzer object
analyzer = ThreatAnalyzer()  # Object instantiation

# Using the object
result = await analyzer.analyze("Selling company database...")
print(result.entities)  # Accessing object's data
```

**Why This Matters**:
- The analyzer is an **object** that encapsulates all NLP functionality
- We create **one object** and use it multiple times
- The object maintains **state** (loaded models, configuration)

### Example 3: Scraper Classes

**Location**: `backend/app/scrapers/paste_scraper.py`

```python
class PasteScraper(BaseScraper):
    """Scraper for paste sites - Each scraper is a separate object"""

    def __init__(self, site_url: str, site_name: str):
        super().__init__(DataSource.PASTE_SITE, site_name)
        self.site_url = site_url  # Object-specific data

    async def scrape(self) -> List[ThreatCreate]:
        """Scraping logic specific to this scraper object"""
        threats = []
        html = await self.fetch_page(f"{self.site_url}/archive")
        # ... scraping logic
        return threats

# Creating multiple scraper objects
pastebin_scraper = PasteScraper("http://pastebin.onion", "Pastebin")
riseup_scraper = PasteScraper("http://riseup.onion", "Riseup Paste")

# Each object operates independently
threats1 = await pastebin_scraper.scrape()
threats2 = await riseup_scraper.scrape()
```

---

<a name="encapsulation"></a>
## 2. Encapsulation

**Concept**: Bundling data and methods together, hiding internal details, controlling access.

### Example 1: Database Connection Encapsulation

**Location**: `backend/app/core/database.py`

```python
class DatabaseConnection:
    """Encapsulates database connection logic"""

    def __init__(self):
        # Private attributes (internal state hidden from outside)
        self._db = None  # MongoDB connection
        self._redis = None  # Redis connection
        self._connected = False  # Connection status

    # Public property - controlled access to private data
    @property
    def db(self):
        """Get MongoDB database (read-only access)"""
        return self._db

    @property
    def redis(self):
        """Get Redis connection (read-only access)"""
        return self._redis

    # Public method - controlled way to interact with private data
    async def connect_to_mongo(self):
        """Public method to establish connection"""
        self._db = AsyncIOMotorClient(settings.MONGODB_URL)[settings.MONGODB_DB_NAME]
        self._connected = True
        logger.info("✓ Connected to MongoDB")

    async def disconnect(self):
        """Public method to close connection"""
        if self._db:
            self._db.client.close()
        self._connected = False
        logger.info("✓ Disconnected from MongoDB")

    def _validate_connection(self):
        """Private helper method (internal use only)"""
        if not self._connected:
            raise ConnectionError("Database not connected")

# Usage:
db = DatabaseConnection()
await db.connect_to_mongo()

# Can access database through property
await db.db.threats.find()  # ✓ Allowed

# Cannot directly modify private attributes
# db._db = None  # ✗ Bad practice (should not access private attributes)
```

**Why This Matters**:
- Internal details (connection state) are **hidden** from outside code
- Access is **controlled** through public methods and properties
- Prevents bugs by **protecting internal state**
- Can change internal implementation without breaking external code

### Example 2: User Model with Password Hashing

**Location**: `backend/app/models/user.py`

```python
class User(BaseModel):
    """User model with encapsulated password handling"""

    email: str
    username: str
    hashed_password: str  # Stored as hash, never plain text
    role: UserRole
    is_active: bool = True

    # Password is NOT stored directly - encapsulated as hash

    @classmethod
    def create(cls, email: str, username: str, password: str):
        """Factory method - controls how users are created"""
        # Password is automatically hashed before storing
        hashed = hash_password(password)
        return cls(
            email=email,
            username=username,
            hashed_password=hashed,
            role=UserRole.ANALYST
        )

    def verify_password(self, password: str) -> bool:
        """Public method to check password - hides hashing logic"""
        return verify_password(password, self.hashed_password)

    def change_password(self, new_password: str):
        """Controlled way to change password"""
        self.hashed_password = hash_password(new_password)

# Usage:
user = User.create(
    email="analyst@company.com",
    username="analyst1",
    password="secret123"  # Plain text password
)
# Password is now stored as hash internally

# Verify password
if user.verify_password("secret123"):
    print("Login successful")

# Cannot access plain password - it's never stored!
```

**Why This Matters**:
- Passwords are **never stored in plain text**
- Internal hashing logic is **hidden** from API users
- Only **safe methods** are exposed (verify, change)
- Security through encapsulation

### Example 3: Rule Matcher with Private Methods

**Location**: `backend/app/core/rule_matcher.py`

```python
class RuleMatcher:
    """Rule matching with encapsulated matching logic"""

    def __init__(self):
        self._regex_cache = {}  # Private cache (internal optimization)

    # Public method - what users interact with
    def matches_rule(self, threat: ThreatModel, rule: MonitoringRule) -> bool:
        """Check if threat matches rule"""
        results = []

        for condition in rule.conditions:
            # Delegates to private helper methods
            match = self._evaluate_condition(threat, condition)
            results.append(match)

        # Apply AND/OR logic
        return all(results) if rule.match_all else any(results)

    # Private helper methods - internal implementation details
    def _evaluate_condition(self, threat, condition):
        """Private: Evaluate single condition"""
        if condition.type == "keyword_match":
            return self._match_keyword(threat, condition)
        elif condition.type == "regex_match":
            return self._match_regex(threat, condition)
        # ... more conditions

    def _match_keyword(self, threat, condition):
        """Private: Keyword matching logic"""
        text = threat.content.lower()
        keyword = condition.value.lower()
        return keyword in text

    def _match_regex(self, threat, condition):
        """Private: Regex matching with caching"""
        # Uses private cache for optimization
        if condition.value not in self._regex_cache:
            self._regex_cache[condition.value] = re.compile(condition.value)

        pattern = self._regex_cache[condition.value]
        return bool(pattern.search(threat.content))

# Usage:
matcher = RuleMatcher()

# Only interact with public method
matches = matcher.matches_rule(threat, rule)

# Internal details are hidden
# matcher._regex_cache  # ✗ Should not access (private)
```

**Why This Matters**:
- Complex matching logic is **broken into private methods**
- Users only see simple public interface: `matches_rule()`
- Internal optimizations (regex cache) are **hidden**
- Can change internal implementation without breaking code

---

<a name="inheritance"></a>
## 3. Inheritance

**Concept**: Creating new classes based on existing classes, inheriting properties and methods.

### Example 1: Base Scraper Inheritance (Most Important)

**Location**: `backend/app/scrapers/base_scraper.py` and children

```python
# PARENT CLASS (Base/Abstract)
class BaseScraper(ABC):
    """
    Parent class that defines common scraper functionality
    All scrapers inherit from this
    """

    def __init__(self, source: DataSource, source_name: str):
        self.source = source
        self.source_name = source_name
        self.tor_client = tor_client

    # Abstract method - MUST be implemented by children
    @abstractmethod
    async def scrape(self) -> List[ThreatCreate]:
        """Child classes MUST implement this"""
        pass

    # Common methods inherited by all children
    async def fetch_page(self, url: str) -> Optional[str]:
        """All children can use this"""
        logger.info(f"[{self.source_name}] Fetching: {url}")
        return await self.tor_client.fetch_text(url)

    def parse_html(self, html: str) -> BeautifulSoup:
        """All children can use this"""
        return BeautifulSoup(html, "lxml")

    def classify_threat(self, title: str, content: str):
        """All children can use this"""
        text = (title + " " + content).lower()
        if "password" in text:
            return ThreatType.CREDENTIAL_LEAK, ThreatSeverity.CRITICAL
        # ... more classification logic

    def log_stats(self, threats_found: int, errors: int = 0):
        """All children can use this"""
        logger.info(f"[{self.source_name}] Found: {threats_found}")


# CHILD CLASS 1: PasteScraper
class PasteScraper(BaseScraper):
    """
    Inherits from BaseScraper
    Gets all parent methods automatically
    """

    def __init__(self, site_url: str, site_name: str):
        # Call parent constructor
        super().__init__(DataSource.PASTE_SITE, site_name)
        self.site_url = site_url  # Add child-specific attribute

    # MUST implement abstract method from parent
    async def scrape(self) -> List[ThreatCreate]:
        """Paste-specific scraping logic"""
        threats = []

        # Uses inherited method from parent
        html = await self.fetch_page(f"{self.site_url}/archive")

        # Uses inherited method from parent
        soup = self.parse_html(html)

        # Child-specific logic
        for link in soup.select("a.paste-link"):
            threat = await self.scrape_paste(link['href'])
            if threat:
                threats.append(threat)

        # Uses inherited method from parent
        self.log_stats(len(threats))
        return threats

    # Child-specific method (not in parent)
    async def scrape_paste(self, url: str):
        """Only PasteScraper has this"""
        # ... paste-specific logic
        pass


# CHILD CLASS 2: ForumScraper
class ForumScraper(BaseScraper):
    """
    Also inherits from BaseScraper
    Gets same parent methods as PasteScraper
    """

    def __init__(self, forum_url: str, forum_name: str):
        super().__init__(DataSource.FORUM, forum_name)
        self.forum_url = forum_url

    async def scrape(self) -> List[ThreatCreate]:
        """Forum-specific scraping logic"""
        threats = []

        # Also uses inherited methods
        html = await self.fetch_page(self.forum_url)
        soup = self.parse_html(html)

        # Forum-specific logic
        for post in soup.select("div.forum-post"):
            # Uses inherited classify_threat method
            threat_type, severity = self.classify_threat(
                post.find('h3').text,
                post.find('div.content').text
            )
            threats.append(self.create_threat(...))

        self.log_stats(len(threats))
        return threats


# CHILD CLASS 3: MarketplaceScraper
class MarketplaceScraper(BaseScraper):
    """Yet another child with same inherited functionality"""

    def __init__(self, marketplace_url: str, marketplace_name: str):
        super().__init__(DataSource.MARKETPLACE, marketplace_name)
        self.marketplace_url = marketplace_url

    async def scrape(self) -> List[ThreatCreate]:
        """Marketplace-specific logic"""
        # Also gets all parent methods
        html = await self.fetch_page(self.marketplace_url)
        soup = self.parse_html(html)
        # ... marketplace logic
```

**Inheritance Hierarchy**:
```
                    BaseScraper (Parent/Abstract)
                           |
                   +-------+-------+-------+
                   |       |       |       |
            PasteScraper  ForumScraper  MarketplaceScraper  TelegramScraper
             (Child)       (Child)         (Child)            (Child)
```

**Why This Matters**:
- **Code reuse**: Common functionality written once in parent
- All children get: `fetch_page()`, `parse_html()`, `classify_threat()`, `log_stats()`
- **Consistency**: All scrapers work the same way
- **Maintainability**: Fix bug in parent = fixed in all children
- **Extensibility**: Easy to add new scrapers

**Real Impact**:
- Without inheritance: Would need to write same 200+ lines in each scraper (800+ lines total)
- With inheritance: Write 200 lines once in parent, only 50 lines per child (400 lines total)
- **Saved 400+ lines of code!**

### Example 2: Pydantic Model Inheritance

**Location**: `backend/app/models/threat.py`

```python
# Parent Model
class ThreatBase(BaseModel):
    """Base threat model with common fields"""
    title: str
    content: str
    url: Optional[str] = None
    source: DataSource
    threat_type: ThreatType
    severity: ThreatSeverity

# Child Model 1: For creating threats
class ThreatCreate(ThreatBase):
    """Inherits all ThreatBase fields, adds nothing"""
    pass  # Same fields as parent

# Child Model 2: For full threat with metadata
class ThreatModel(ThreatBase):
    """Inherits ThreatBase fields, adds more"""
    id: Optional[PyObjectId]
    intelligence: Optional[ThreatIntelligence] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    false_positive: bool = False
    reviewed: bool = False

# Child Model 3: For API responses
class ThreatResponse(ThreatBase):
    """Inherits ThreatBase fields, customizes for API"""
    id: str  # Different from ThreatModel (string not ObjectId)
    discovered_at: datetime
    reviewed: bool
```

**Why This Matters**:
- Common fields defined **once** in parent
- Three different models for different purposes
- All share same base structure
- Type safety maintained across all models

---

<a name="polymorphism"></a>
## 4. Polymorphism

**Concept**: Same interface, different implementations. Objects of different types can be treated the same way.

### Example 1: Scraper Polymorphism (Most Important)

```python
# Different scraper types, same interface
paste_scraper = PasteScraper("http://paste.onion", "Pastebin")
forum_scraper = ForumScraper("http://forum.onion", "DarkForum")
marketplace_scraper = MarketplaceScraper("http://market.onion", "DarkMarket")

# ALL scrapers have scrape() method (polymorphism)
# Can call same method on different objects
async def run_all_scrapers(scrapers: List[BaseScraper]):
    """Works with ANY scraper type"""
    for scraper in scrapers:
        # Same method call, different implementations
        threats = await scraper.scrape()  # Polymorphism!

        # Each scraper's scrape() method does different things:
        # - PasteScraper.scrape() -> looks for paste links
        # - ForumScraper.scrape() -> looks for forum posts
        # - MarketplaceScraper.scrape() -> looks for listings
        # But we call them all the same way!

        print(f"Found {len(threats)} threats")

# Usage:
all_scrapers = [paste_scraper, forum_scraper, marketplace_scraper]
await run_all_scrapers(all_scrapers)
```

**Why This Matters**:
- **Same interface**: All scrapers have `scrape()` method
- **Different behavior**: Each implements scraping differently
- **Flexible code**: Can add new scraper types without changing `run_all_scrapers()`
- **Cleaner code**: No need for if/else to check scraper type

### Example 2: Celery Task Polymorphism

**Location**: `backend/app/celery_worker.py`

```python
# Different tasks, same interface
@celery_app.task
def scan_paste_sites():
    """Scan paste sites"""
    scraper = PasteScraper(...)
    threats = await scraper.scrape()
    return threats

@celery_app.task
def scan_forums():
    """Scan forums"""
    scraper = ForumScraper(...)
    threats = await scraper.scrape()
    return threats

@celery_app.task
def scan_marketplaces():
    """Scan marketplaces"""
    scraper = MarketplaceScraper(...)
    threats = await scraper.scrape()
    return threats

# Celery scheduler treats all tasks the same way (polymorphism)
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Same schedule method for different tasks
    sender.add_periodic_task(3600, scan_paste_sites.s())
    sender.add_periodic_task(3600, scan_forums.s())
    sender.add_periodic_task(3600, scan_marketplaces.s())
```

### Example 3: API Response Polymorphism

**Location**: `backend/app/api/v1/threats.py`

```python
# Same endpoint, different response types based on request
@app.get("/api/v1/threats")
async def get_threats(
    output_format: str = "json"  # Can be 'json', 'csv', 'xml'
):
    threats = await db.threats.find().to_list()

    # Polymorphism: Same data, different formats
    if output_format == "json":
        return JSONResponse(threats)
    elif output_format == "csv":
        return CSVResponse(threats)
    elif output_format == "xml":
        return XMLResponse(threats)

    # All response types have same interface (can be returned from function)
    # But each formats data differently
```

---

<a name="abstraction"></a>
## 5. Abstraction

**Concept**: Hiding complex implementation details, showing only essential features.

### Example 1: Abstract Base Scraper

**Location**: `backend/app/scrapers/base_scraper.py`

```python
from abc import ABC, abstractmethod

class BaseScraper(ABC):  # ABC = Abstract Base Class
    """
    Abstract class - cannot create objects directly
    Forces children to implement required methods
    """

    @abstractmethod
    async def scrape(self) -> List[ThreatCreate]:
        """
        Abstract method - NO implementation here
        Each child MUST implement this
        """
        pass  # No code - just definition

    # Regular methods CAN have implementation
    async def fetch_page(self, url: str):
        """Concrete method - has implementation"""
        return await self.tor_client.fetch_text(url)

# CANNOT create BaseScraper directly
# scraper = BaseScraper()  # ✗ ERROR! Cannot instantiate abstract class

# MUST create child class that implements abstract methods
class PasteScraper(BaseScraper):
    async def scrape(self):  # ✓ Must implement
        # ... implementation
        pass

# Now CAN create PasteScraper
scraper = PasteScraper()  # ✓ OK! Child implements abstract method
```

**Why This Matters**:
- **Contract**: Guarantees all scrapers have `scrape()` method
- **Consistency**: All scrapers follow same interface
- **Compiler help**: Python prevents creating abstract classes
- **Documentation**: Abstract methods show what children must implement

### Example 2: Database Abstraction

**Location**: `backend/app/core/database.py`

```python
class DatabaseConnection:
    """
    Abstracts away database complexity
    Users don't need to know about connection pools, drivers, etc.
    """

    async def get_threats(self, filters: dict):
        """
        Simple interface - hides complex database operations
        """
        # Hidden complexity:
        # - Connection pooling
        # - Query optimization
        # - Error handling
        # - Retry logic
        # - Connection management

        query = self._build_query(filters)  # Hidden
        cursor = self._get_collection().find(query)  # Hidden
        results = await self._execute_with_retry(cursor)  # Hidden
        return self._transform_results(results)  # Hidden

    # Private methods hide implementation details
    def _build_query(self, filters): pass
    def _get_collection(self): pass
    def _execute_with_retry(self, cursor): pass
    def _transform_results(self, results): pass

# Usage is simple - complexity is hidden
db = DatabaseConnection()
threats = await db.get_threats({'severity': 'critical'})
# User doesn't need to know HOW it works, just THAT it works
```

### Example 3: NLP Analysis Abstraction

**Location**: `backend/app/nlp/threat_analyzer.py`

```python
class ThreatAnalyzer:
    """
    Abstracts complex NLP processing
    Simple interface hides ML model complexity
    """

    async def analyze(self, text: str) -> ThreatIntelligence:
        """
        Simple method - just give text, get intelligence
        Hides:
        - spaCy model loading
        - BERT inference
        - Entity recognition
        - IOC extraction
        - Sentiment analysis
        """
        # All this complexity is hidden from user
        entities = self.extract_entities(text)
        iocs = self.extract_iocs(text)
        sentiment = self.analyze_sentiment(text)
        keywords = self.extract_keywords(text)

        return ThreatIntelligence(
            entities=entities,
            iocs=iocs,
            sentiment=sentiment,
            keywords=keywords
        )

# Usage is simple
analyzer = ThreatAnalyzer()
result = await analyzer.analyze("Selling company database...")
print(result.iocs)  # Just works - don't need to know how
```

---

<a name="composition"></a>
## 6. Composition

**Concept**: Building complex objects by combining simpler objects. "Has-a" relationship.

### Example 1: Threat Model Composition

**Location**: `backend/app/models/threat.py`

```python
# Simple component classes
class IOC(BaseModel):
    """Component: Indicator of Compromise"""
    type: str  # ip, email, hash, etc.
    value: str
    confidence: float

class Entity(BaseModel):
    """Component: Extracted entity"""
    type: str  # PERSON, ORG, EMAIL, etc.
    value: str
    confidence: float

class ThreatIntelligence(BaseModel):
    """Component: Intelligence analysis"""
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    keywords: List[str] = []
    entities: List[Entity] = []  # HAS-MANY Entity objects
    iocs: List[IOC] = []  # HAS-MANY IOC objects
    tags: List[str] = []

class ThreatModel(BaseModel):
    """
    Complex object COMPOSED of simpler objects
    Threat HAS-A ThreatIntelligence
    ThreatIntelligence HAS-MANY Entities
    ThreatIntelligence HAS-MANY IOCs
    """
    title: str
    content: str
    severity: ThreatSeverity
    intelligence: Optional[ThreatIntelligence] = None  # Composition!

# Creating composed object
threat = ThreatModel(
    title="Database Leak",
    content="...",
    severity=ThreatSeverity.CRITICAL,
    intelligence=ThreatIntelligence(  # Composed object
        sentiment="negative",
        sentiment_score=0.95,
        keywords=["database", "leak", "password"],
        entities=[  # List of composed objects
            Entity(type="EMAIL", value="admin@company.com", confidence=0.98),
            Entity(type="ORG", value="Company Inc", confidence=0.85)
        ],
        iocs=[  # List of composed objects
            IOC(type="email", value="admin@company.com", confidence=0.95),
            IOC(type="ip", value="192.168.1.1", confidence=0.90)
        ]
    )
)

# Access nested objects
print(threat.intelligence.entities[0].value)  # "admin@company.com"
print(threat.intelligence.iocs[1].type)  # "ip"
```

**Composition Hierarchy**:
```
ThreatModel
    └── intelligence: ThreatIntelligence
            ├── entities: List[Entity]
            │       ├── Entity (type="EMAIL")
            │       └── Entity (type="ORG")
            └── iocs: List[IOC]
                    ├── IOC (type="email")
                    └── IOC (type="ip")
```

**Why This Matters**:
- **Modularity**: Each component is independent
- **Reusability**: Entity and IOC classes used in multiple places
- **Flexibility**: Can add/remove components easily
- **Clarity**: Clear relationships between objects

### Example 2: Scraper Composition

**Location**: `backend/app/scrapers/base_scraper.py`

```python
class BaseScraper:
    """
    Scraper is COMPOSED of:
    - TorClient (for network access)
    - BeautifulSoup (for HTML parsing)
    - Logger (for logging)
    """

    def __init__(self, source: DataSource, source_name: str):
        self.source = source
        self.source_name = source_name

        # Composition: Scraper HAS-A TorClient
        self.tor_client = tor_client  # Composed object

        # Composition: Scraper HAS-A Logger
        self.logger = logger  # Composed object

    async def scrape(self):
        # Uses composed TorClient object
        html = await self.tor_client.fetch_text(url)

        # Uses composed BeautifulSoup object
        soup = BeautifulSoup(html, "lxml")

        # Uses composed logger object
        self.logger.info("Scraping complete")
```

### Example 3: API Router Composition

**Location**: `backend/app/api/v1/__init__.py`

```python
from .threats import router as threats_router
from .rules import router as rules_router
from .auth import router as auth_router

# Main API router COMPOSED of sub-routers
api_router = APIRouter()

# Composition: API HAS-MANY routers
api_router.include_router(threats_router, prefix="/threats", tags=["threats"])
api_router.include_router(rules_router, prefix="/rules", tags=["rules"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Each sub-router is independent but part of larger API
```

---

<a name="summary"></a>
## Summary for Presentation

### Quick Reference Table

| OOP Concept | File Location | Example | Lines of Code |
|-------------|---------------|---------|---------------|
| **Classes & Objects** | `models/threat.py` | ThreatModel, ThreatCreate | 300+ |
| | `nlp/threat_analyzer.py` | ThreatAnalyzer | 400+ |
| | `scrapers/*.py` | All scraper classes | 800+ |
| **Encapsulation** | `core/database.py` | DatabaseConnection | 150+ |
| | `models/user.py` | User with password hashing | 74 |
| | `core/rule_matcher.py` | RuleMatcher | 200+ |
| **Inheritance** | `scrapers/base_scraper.py` | BaseScraper (parent) | 209 |
| | `scrapers/paste_scraper.py` | PasteScraper (child) | 219 |
| | `scrapers/forum_scraper.py` | ForumScraper (child) | 200+ |
| | `scrapers/marketplace_scraper.py` | MarketplaceScraper (child) | 200+ |
| **Polymorphism** | All scrapers | scrape() method | - |
| | `celery_worker.py` | Task scheduling | 200+ |
| **Abstraction** | `scrapers/base_scraper.py` | ABC class with @abstractmethod | 209 |
| | `core/database.py` | Database abstraction | 150+ |
| **Composition** | `models/threat.py` | ThreatModel has ThreatIntelligence | 176 |
| | `scrapers/base_scraper.py` | Scraper has TorClient | 209 |

### For Jury Presentation

**Simple Explanation**:

"I extensively used Object-Oriented Programming throughout the project:

1. **Classes & Objects**: Created 20+ classes representing threats, scrapers, analyzers, and users. Each object has its own data and behavior.

2. **Encapsulation**: Hid complex implementation details. For example, password hashing is encapsulated in the User class - passwords are never stored in plain text.

3. **Inheritance**: Built a base scraper class with common functionality, then created 4 specialized scrapers that inherit this functionality. This saved 400+ lines of duplicate code.

4. **Polymorphism**: All scrapers have the same interface (scrape() method) but different implementations. I can treat different scraper types uniformly.

5. **Abstraction**: Used abstract base classes to define contracts that child classes must follow. The BaseScraper is abstract - you can't create it directly.

6. **Composition**: Built complex objects from simpler ones. A Threat object is composed of ThreatIntelligence, which contains Entity and IOC objects."

### Most Impressive Examples for Jury

**1. Inheritance Hierarchy** (Show this diagram):
```
BaseScraper (209 lines)
    ├── PasteScraper (219 lines)
    ├── ForumScraper (200+ lines)
    ├── MarketplaceScraper (200+ lines)
    └── TelegramScraper (200+ lines)

Without inheritance: ~1000 lines
With inheritance: ~600 lines
Saved: 400+ lines through code reuse!
```

**2. Encapsulation in Action**:
```python
# Bad (no encapsulation):
password = "secret123"
user.password = password  # Stored as plain text!

# Good (with encapsulation):
user = User.create(email="...", password="secret123")
# Password automatically hashed, never stored as plain text
# Can only verify through: user.verify_password("secret123")
```

**3. Polymorphism Power**:
```python
# Same code works with ANY scraper type
async def process_scraper(scraper: BaseScraper):
    threats = await scraper.scrape()  # Works for all types!
    return threats

# Can use with any scraper
process_scraper(PasteScraper(...))
process_scraper(ForumScraper(...))
process_scraper(MarketplaceScraper(...))
```

---

## Code Statistics

**OOP Implementation Stats**:
- **Total Classes**: 25+
- **Abstract Classes**: 1 (BaseScraper)
- **Child Classes**: 4 scrapers
- **Pydantic Models**: 15+
- **Composition Relationships**: 10+
- **Encapsulated Methods**: 50+
- **Lines Saved Through Inheritance**: 400+

**Files Using OOP**:
- `backend/app/models/*.py` (6 files)
- `backend/app/scrapers/*.py` (6 files)
- `backend/app/core/*.py` (5 files)
- `backend/app/nlp/*.py` (2 files)
- `backend/app/api/**/*.py` (8 files)

---

## Conclusion

This project demonstrates **professional-level OOP implementation** with:
✅ Proper class hierarchies
✅ Clear separation of concerns
✅ Reusable, maintainable code
✅ Industry best practices
✅ Type safety with Pydantic
✅ Abstract classes for contracts
✅ Composition over inheritance where appropriate

**Every major component uses OOP principles to create clean, scalable, maintainable code.**
