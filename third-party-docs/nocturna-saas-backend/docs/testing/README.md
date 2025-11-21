# Testing Guide

This guide explains how to run and write tests for the Nocturna SaaS Backend.

## Test Environment Setup

Before running tests, you need to set up the test environment:

```bash
make setup-test-env
```

This will:
1. Create test databases and schemas
2. Configure test environment variables
3. Set up test data

## Running Tests

### All Tests

```bash
make test
```

This will run all tests:
- Unit tests
- Integration tests
- Service tests
- API tests

### Test Coverage

```bash
make test-cov
```

This will run all tests with coverage report.

### Specific Test Categories

```bash
# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Service tests only
make test-service

# API tests only
make test-api
```

### Watch Mode

```bash
make test-watch
```

This will run tests in watch mode, automatically re-running when files change.

## Writing Tests

### Test Structure

Tests are organized in the `tests` directory:

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── services/       # Service tests
└── api/           # API tests
```

### Test Categories

1. **Unit Tests**
   - Test individual functions and classes
   - No external dependencies
   - Fast execution
   - Example: `tests/unit/test_llm_service.py`

2. **Integration Tests**
   - Test interaction between components
   - May use test databases
   - Slower execution
   - Example: `tests/integration/test_chart_service.py`

3. **Service Tests**
   - Test business logic services
   - May use mocks for external services
   - Example: `tests/services/test_interpretation_service.py`

4. **API Tests**
   - Test HTTP endpoints
   - Use FastAPI TestClient
   - Example: `tests/api/test_chart_endpoints.py`

### Test Fixtures

Common test fixtures are defined in `tests/conftest.py`:

```python
@pytest.fixture
async def db_session():
    """Database session fixture."""
    async with async_session() as session:
        yield session

@pytest.fixture
async def redis_client():
    """Redis client fixture."""
    async with Redis() as redis:
        yield redis

@pytest.fixture
async def clickhouse_client():
    """Clickhouse client fixture."""
    async with ClickhouseClient() as client:
        yield client
```

### Writing a Test

Example test for LLM service:

```python
import pytest
from src.services.llm import LLMService

@pytest.mark.asyncio
async def test_llm_service_generate():
    # Arrange
    service = LLMService()
    
    # Act
    response = await service.generate("Test prompt")
    
    # Assert
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
```

### Best Practices

1. **Test Naming**
   - Use descriptive names
   - Follow pattern: `test_<function>_<scenario>`
   - Example: `test_llm_service_generate_success`

2. **Test Organization**
   - One test file per module
   - Group related tests in classes
   - Use fixtures for common setup

3. **Assertions**
   - Use specific assertions
   - Test both success and failure cases
   - Verify side effects

4. **Mocking**
   - Mock external services
   - Use `unittest.mock` or `pytest-mock`
   - Example:
     ```python
     @pytest.fixture
     def mock_openai(mocker):
         return mocker.patch("openai.ChatCompletion.create")
     ```

5. **Database Tests**
   - Use transactions
   - Clean up after tests
   - Example:
     ```python
     @pytest.mark.asyncio
     async def test_create_chart(db_session):
         async with db_session.begin():
             # Test code here
     ```

## Test Data

Test data is managed in `tests/data/`:

```
tests/data/
├── charts/         # Chart test data
├── users/          # User test data
└── interpretations/ # Interpretation test data
```

### Loading Test Data

```python
from tests.data import load_test_data

@pytest.fixture
def test_chart():
    return load_test_data("charts/sample_chart.json")
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Merges to main branch
- Daily scheduled runs

### CI Configuration

See `.github/workflows/tests.yml` for CI configuration.

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check `.env.test` configuration
   - Verify test database exists
   - Check database permissions

2. **Redis Connection Issues**
   - Check Redis configuration
   - Verify Redis is running
   - Check Redis DB number

3. **Clickhouse Connection Issues**
   - Check Clickhouse configuration
   - Verify Clickhouse is running
   - Check database exists

4. **Test Failures**
   - Check test logs
   - Verify test data
   - Check environment variables

### Getting Help

If you encounter issues:
1. Check test logs
2. Review test configuration
3. Check environment setup
4. Open an issue on GitHub 