# Contributing to Dark Web Monitoring Platform

Thank you for your interest in contributing to the Dark Web Monitoring Platform!

## Code of Conduct

This project adheres to responsible security research practices. All contributors must:

- Use the platform only for defensive security purposes
- Comply with all applicable laws and regulations
- Respect privacy and data protection requirements
- Not engage in illegal activities or unauthorized access

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/Dark_WEB_MONITORING.git`
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Set up development environment: `./scripts/setup.sh` (option 2 for dev setup)

## Development Guidelines

### Code Style

#### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable and function names

```python
# Good
async def analyze_threat(threat_content: str) -> ThreatIntelligence:
    """Analyze threat content using NLP."""
    pass

# Avoid
def analyze(c):
    pass
```

#### TypeScript/JavaScript

- Use ESLint and Prettier
- Prefer functional components with hooks
- Use TypeScript for type safety

```typescript
// Good
interface ThreatProps {
  id: string;
  severity: ThreatSeverity;
}

const ThreatCard: React.FC<ThreatProps> = ({ id, severity }) => {
  // component code
};

// Avoid
const ThreatCard = (props) => {
  // untyped component
};
```

### Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Test both success and failure cases

```python
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions and classes
- Update API documentation for endpoint changes

### Commit Messages

Use conventional commit format:

```
feat: add credential monitoring for paste sites
fix: resolve Tor connection timeout issue
docs: update deployment guide
test: add tests for NLP analyzer
refactor: improve database query performance
```

## Pull Request Process

1. **Update Documentation**: Ensure all changes are documented
2. **Add Tests**: Include tests for new functionality
3. **Update CHANGELOG.md**: Add entry under "Unreleased"
4. **Run Tests**: Ensure all tests pass
5. **Code Review**: Address reviewer feedback promptly

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings
```

## Feature Requests

Submit feature requests as GitHub issues with:

- Clear description of the feature
- Use case and benefits
- Potential implementation approach
- Any security implications

## Bug Reports

Include in bug reports:

- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or screenshots

## Security Issues

**Do not** create public issues for security vulnerabilities.

Instead, email: security@yourproject.com with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Code formatting
black app/
isort app/

# Linting
flake8 app/
mypy app/
```

### Frontend Development

```bash
cd frontend
npm install

# Run development server
npm run dev

# Run tests
npm test

# Lint and format
npm run lint
npm run format

# Type checking
npm run type-check
```

## Project Structure

```
Dark_WEB_MONITORING/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Data models
│   │   ├── scrapers/      # Scraping engines
│   │   ├── nlp/           # NLP analysis
│   │   ├── alerting/      # Alert system
│   │   └── utils/         # Utilities
│   ├── config/            # Configuration
│   └── tests/             # Tests
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Pages
│   │   ├── services/      # API services
│   │   └── utils/         # Utilities
│   └── public/            # Static files
└── docs/                  # Documentation
```

## Adding New Features

### New Data Source

1. Create scraper in `backend/app/scrapers/`
2. Extend `DataSource` enum in models
3. Add scraping task in `celery_worker.py`
4. Update documentation

### New Analysis Method

1. Add analyzer in `backend/app/nlp/`
2. Update `ThreatIntelligence` model if needed
3. Integrate into analysis pipeline
4. Add tests

### New Alert Channel

1. Extend notifier in `backend/app/alerting/`
2. Update `NotificationChannel` enum
3. Add configuration options
4. Update documentation

## Code Review Checklist

Reviewers should verify:

- [ ] Code follows project conventions
- [ ] All tests pass
- [ ] No security vulnerabilities introduced
- [ ] Documentation updated
- [ ] Error handling is appropriate
- [ ] No hardcoded credentials or secrets
- [ ] Logging is appropriate
- [ ] Performance considerations addressed

## Resources

- [Python Style Guide](https://pep8.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Best Practices](https://react.dev/learn)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
