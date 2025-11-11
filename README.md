# Dark Web Monitoring and Intelligence Platform

A comprehensive system for continuous monitoring of the dark web to detect stolen data, cybercriminal activity, and emerging threats.

## Features

- **Multi-Source Monitoring**: Track dark web forums, marketplaces, paste sites, and hidden services
- **Threat Intelligence**: Advanced NLP-based threat classification and analysis
- **Real-time Alerts**: Instant notifications for critical threats
- **Data Breach Detection**: Monitor for stolen credentials and sensitive data
- **IOC Extraction**: Automatically extract Indicators of Compromise
- **Interactive Dashboard**: Visualize threats and trends
- **REST API**: Integration-ready API for external systems
- **Customizable Monitoring**: Configure keywords, domains, and alert rules

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Dashboard (React)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  REST API (FastAPI)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │   Scraping   │  │  NLP Analysis │  │  Alert Engine   │  │
│  │    Engine    │──│    Engine     │──│                 │  │
│  │  (Tor-based) │  │  (spaCy/BERT) │  │                 │  │
│  └──────────────┘  └───────────────┘  └─────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│  Database Layer (MongoDB + PostgreSQL + Redis)              │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Celery
- **Scraping**: Scrapy, Tor (SOCKS5), Selenium
- **NLP**: spaCy, transformers, scikit-learn
- **Databases**: MongoDB, PostgreSQL, Redis
- **Frontend**: React, TypeScript, Material-UI
- **Deployment**: Docker, Docker Compose
- **Task Queue**: Celery with Redis

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Tor service (for dark web access)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Dark_WEB_MONITORING
```

2. Start the platform with Docker:
```bash
docker-compose up -d
```

3. Access the dashboard:
```
http://localhost:3000
```

4. Access the API:
```
http://localhost:8000/docs
```

### Manual Installation

1. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Install Tor:
```bash
# Ubuntu/Debian
sudo apt-get install tor

# macOS
brew install tor
```

4. Start services:
```bash
# Terminal 1 - Start Tor
tor

# Terminal 2 - Start Redis
redis-server

# Terminal 3 - Start API
cd backend
uvicorn app.main:app --reload

# Terminal 4 - Start Celery workers
cd backend
celery -A app.celery_worker worker --loglevel=info

# Terminal 5 - Start Celery beat (scheduler)
cd backend
celery -A app.celery_worker beat --loglevel=info

# Terminal 6 - Start frontend
cd frontend
npm install
npm start
```

## Configuration

### Monitoring Targets

Configure monitoring targets in `backend/config/monitoring_config.yaml`:

```yaml
targets:
  keywords:
    - "your-company-name"
    - "your-domain.com"
    - "executive-names"

  data_types:
    - credentials
    - credit_cards
    - personal_data
    - source_code

  sources:
    - dark_web_forums
    - paste_sites
    - marketplace
    - telegram
```

### Alert Rules

Configure alert rules in `backend/config/alert_rules.yaml`:

```yaml
rules:
  - name: "Credential Leak"
    severity: "critical"
    conditions:
      - type: "keyword_match"
        field: "content"
        value: "password|credentials"
      - type: "data_type"
        value: "credentials"

  - name: "Company Mention"
    severity: "high"
    conditions:
      - type: "keyword_match"
        field: "content"
        value: "your-company-name"
```

## API Usage

### Authentication

```bash
# Get API token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```

### Query Threats

```bash
# Get recent threats
curl -X GET http://localhost:8000/api/v1/threats \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get threats by severity
curl -X GET http://localhost:8000/api/v1/threats?severity=critical \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Monitoring Rule

```bash
curl -X POST http://localhost:8000/api/v1/rules \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monitor Executive Names",
    "keywords": ["john.doe", "jane.smith"],
    "severity": "high",
    "notification_channels": ["email", "slack"]
  }'
```

## Security Considerations

⚠️ **Important Security Notes**:

1. **Legal Compliance**: Ensure compliance with local laws regarding dark web monitoring
2. **Data Handling**: Implement proper data retention and privacy policies
3. **Access Control**: Use strong authentication and role-based access control
4. **Network Security**: Isolate the monitoring infrastructure
5. **Responsible Use**: Only monitor for defensive/protective purposes

## Features in Detail

### 1. Dark Web Scraping

- Tor-based anonymous scraping
- Support for .onion sites
- JavaScript-rendered content support
- Rate limiting and anti-detection
- Rotating user agents and circuits

### 2. Threat Intelligence

- Entity extraction (emails, IPs, domains, hashes)
- Sentiment analysis
- Threat classification
- Actor attribution
- Trend analysis

### 3. Data Breach Detection

- Credential monitoring
- Credit card detection
- PII (Personally Identifiable Information) detection
- Source code leak detection

### 4. Alert System

- Multi-channel notifications (Email, Slack, Webhook)
- Severity-based prioritization
- False positive filtering
- Alert aggregation and deduplication

### 5. Dashboard

- Real-time threat feed
- Threat trends and analytics
- Geographical distribution
- Actor profiles
- Custom reports

## Development

### Project Structure

```
Dark_WEB_MONITORING/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core functionality
│   │   ├── models/           # Database models
│   │   ├── scrapers/         # Scraping engines
│   │   ├── nlp/              # NLP processors
│   │   ├── alerting/         # Alert system
│   │   └── utils/            # Utilities
│   ├── config/               # Configuration files
│   ├── tests/                # Test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   └── utils/            # Utilities
│   └── package.json
├── docker-compose.yml
└── README.md
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Disclaimer

This platform is intended for legitimate security research and defensive purposes only. Users are responsible for ensuring compliance with applicable laws and regulations. The developers assume no liability for misuse of this tool.

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See `/docs` directory

## Roadmap

- [ ] Machine learning-based threat prediction
- [ ] Automated takedown coordination
- [ ] Threat actor tracking and profiling
- [ ] Integration with threat intelligence feeds
- [ ] Mobile application
- [ ] Advanced visualization and reporting
- [ ] Multi-tenancy support
