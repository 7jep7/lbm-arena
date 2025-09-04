# LBM Arena - Comprehensive Test Suite

This directory contains a complete, scalable test suite for the LBM Arena backend.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and shared fixtures
├── test_config.py              # Test configuration and settings
├── utils/                      # Test utilities and helpers
│   ├── __init__.py
│   ├── factories.py           # Model factories for test data generation
│   ├── fixtures.py            # Additional test fixtures
│   └── helpers.py             # Test helper functions
├── unit/                       # Unit tests (isolated component testing)
│   ├── __init__.py
│   ├── test_models/           # SQLAlchemy model tests
│   │   ├── __init__.py
│   │   ├── test_player.py
│   │   ├── test_game.py
│   │   └── test_move.py
│   ├── test_schemas/          # Pydantic schema validation tests
│   │   ├── __init__.py
│   │   ├── test_player_schemas.py
│   │   ├── test_game_schemas.py
│   │   └── test_api_schemas.py
│   ├── test_services/         # Business logic tests
│   │   ├── __init__.py
│   │   ├── test_chess_service.py
│   │   ├── test_poker_service.py
│   │   └── test_llm_service.py
│   └── test_core/             # Core functionality tests
│       ├── __init__.py
│       ├── test_config.py
│       └── test_database.py
├── integration/               # Integration tests (component interaction)
│   ├── __init__.py
│   ├── test_api/              # API endpoint integration tests
│   │   ├── __init__.py
│   │   ├── test_players_api.py
│   │   ├── test_games_api.py
│   │   └── test_chess_api.py
│   ├── test_database/         # Database integration tests
│   │   ├── __init__.py
│   │   ├── test_crud_operations.py
│   │   └── test_relationships.py
│   └── test_workflows/        # End-to-end workflow tests
│       ├── __init__.py
│       ├── test_game_creation.py
│       └── test_game_playing.py
├── performance/               # Performance and load tests
│   ├── __init__.py
│   ├── test_api_performance.py
│   └── test_database_performance.py
└── e2e/                       # End-to-end tests
    ├── __init__.py
    └── test_full_game_flow.py
```

## Testing Strategy

### 🎯 **Unit Tests**
- **Models**: Test SQLAlchemy model behavior, relationships, validations
- **Schemas**: Test Pydantic validation, serialization, edge cases
- **Services**: Test business logic in isolation with mocked dependencies
- **Core**: Test configuration, database connections, utilities

### 🔗 **Integration Tests**
- **API**: Test FastAPI endpoints with real database
- **Database**: Test complex queries, transactions, relationships
- **Workflows**: Test multi-component interactions

### ⚡ **Performance Tests**
- **API**: Load testing, response time validation
- **Database**: Query performance, connection pooling

### 🔄 **End-to-End Tests**
- **Complete Workflows**: Full game creation and playing scenarios
- **Real User Journeys**: From player creation to game completion

## Test Environment

### **Isolated Test Database**
- SQLite in-memory database for fast, isolated tests
- PostgreSQL test database for integration tests
- Automatic test data cleanup and reset

### **Mocking Strategy**
- Mock external dependencies (LLM APIs)
- Mock expensive operations in unit tests
- Use real implementations in integration tests

### **Test Data Management**
- Factory pattern for generating test data
- Fixtures for consistent test scenarios
- Automatic cleanup to prevent test pollution

## Running Tests

### **All Tests**
```bash
pytest
```

### **By Category**
```bash
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/performance/    # Performance tests only
pytest tests/e2e/           # End-to-end tests only
```

### **By Component**
```bash
pytest tests/unit/test_models/        # Model tests
pytest tests/unit/test_services/      # Service tests
pytest tests/integration/test_api/    # API tests
```

### **With Coverage**
```bash
pytest --cov=app --cov-report=html
```

### **Verbose Output**
```bash
pytest -v                    # Verbose
pytest -s                    # Show print statements
pytest -x                    # Stop on first failure
```

## Test Configuration

### **Environment Variables**
Tests use separate configuration to avoid affecting development/production:
- `TEST_DATABASE_URL` - Test database connection
- `TEST_REDIS_URL` - Test Redis connection
- `TEST_LLM_API_KEY` - Mock LLM API key

### **Test Settings**
- Fast execution with minimal I/O
- Deterministic test data
- Isolated test environment
- Comprehensive error reporting

## Best Practices

### ✅ **Writing Good Tests**
1. **Descriptive Names**: Test function names clearly describe what is being tested
2. **Arrange-Act-Assert**: Clear test structure
3. **Single Responsibility**: Each test tests one specific behavior
4. **Independent**: Tests don't depend on each other
5. **Fast**: Unit tests run quickly, integration tests are optimized

### ✅ **Test Data**
1. **Factories**: Use factories for generating test objects
2. **Minimal**: Create only the data needed for each test
3. **Realistic**: Test data reflects real-world scenarios
4. **Clean**: Automatic cleanup prevents test pollution

### ✅ **Assertions**
1. **Specific**: Assert exact expected values, not just "truthy"
2. **Comprehensive**: Test both success and failure cases
3. **Clear Messages**: Custom assertion messages for debugging

## Continuous Integration

### **Pre-commit Hooks**
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Runs before each commit:
# - Code formatting (black)
# - Import sorting (isort)
# - Linting (flake8)
# - Type checking (mypy)
# - Test suite (pytest)
```

### **CI Pipeline**
```yaml
# .github/workflows/tests.yml
# Runs on every push/PR:
# - Multiple Python versions
# - Multiple database backends
# - Full test suite with coverage
# - Performance regression testing
```

## Scalability

### **Adding New Tests**
1. Follow established patterns in existing tests
2. Use appropriate test category (unit/integration/e2e)
3. Leverage existing fixtures and factories
4. Maintain test isolation and independence

### **Test Maintenance**
1. Regular review and refactoring of test code
2. Update tests when adding new features
3. Remove obsolete tests when removing features
4. Keep test documentation updated

This testing framework is designed to:
- **Scale** with the project as it grows
- **Catch bugs** early in development
- **Document** expected behavior
- **Enable refactoring** with confidence
- **Maintain quality** through automation
