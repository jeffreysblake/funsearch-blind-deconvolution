# Testing Guide

Comprehensive testing guide for FunSearch framework.

---

## 🧪 Test Suite Overview

We have **3 types of tests**:
1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test API endpoints and workflows end-to-end
3. **Original Tests** - Google DeepMind's original tests for core algorithm

### Current Test Coverage

```
tests/
├── unit/                    # Unit tests (NEW)
│   ├── test_health.py       # Health endpoint tests
│   ├── test_projects_api.py # Projects API tests
│   ├── test_lm_studio.py    # LM Studio sampler tests
│   ├── test_docker_sandbox.py # Docker sandbox tests
│   └── test_detection.py    # Service detection tests
├── integration/             # Integration tests (NEW)
│   └── test_end_to_end.py   # Full workflow tests
└── implementation/          # Original Google tests
    ├── funsearch_test.py
    ├── programs_database_test.py
    ├── evaluator_test.py
    └── code_manipulation_test.py
```

**Test Statistics:**
- Unit tests: 5 files, ~30+ test cases
- Integration tests: 1 file, ~10+ test cases
- Original tests: 4 files, ~25+ test cases
- **Total: ~65+ test cases**

---

## 🚀 Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run complete test suite
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=backend --cov=config --cov-report=term-missing
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Original implementation tests
pytest implementation/

# Specific test file
pytest tests/unit/test_health.py

# Specific test function
pytest tests/unit/test_health.py::test_health_endpoint_returns_200
```

### Run Tests in Parallel

```bash
# Use pytest-xdist for parallel execution
pytest -n auto
```

### Run Tests with Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run tests that don't require Docker
pytest -m "not requires_docker"
```

---

## 📊 Coverage Reports

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=backend --cov=config --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=backend --cov=config --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=backend --cov=config --cov-report=xml
```

### Current Coverage Targets

- **Backend API**: Goal 80%+ coverage
- **Core Components**: Goal 90%+ coverage
- **Utilities**: Goal 70%+ coverage

---

## 🏗️ Writing New Tests

### Unit Test Template

```python
"""Tests for my_module."""

import pytest
from unittest.mock import Mock, patch

from backend.my_module import MyClass


@pytest.fixture
def my_fixture():
    """Create test fixture."""
    return MyClass()


def test_something(my_fixture):
    """Test that something works."""
    result = my_fixture.do_something()
    assert result == expected_value


@patch("backend.my_module.external_dependency")
def test_with_mock(mock_external):
    """Test with mocked dependency."""
    mock_external.return_value = "mocked"
    # ... test code
```

### Integration Test Template

```python
"""Integration tests for my workflow."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_workflow():
    """Test complete workflow."""
    # Step 1: Create resource
    create_response = client.post("/api/v1/resources", json={...})
    assert create_response.status_code == 201

    # Step 2: Retrieve resource
    resource_id = create_response.json()["id"]
    get_response = client.get(f"/api/v1/resources/{resource_id}")
    assert get_response.status_code == 200
```

### Test Markers

Add markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_test():
    pass


@pytest.mark.integration
def test_integration_test():
    pass


@pytest.mark.slow
def test_slow_test():
    pass


@pytest.mark.requires_docker
def test_docker_sandbox():
    pass


@pytest.mark.requires_lm_studio
def test_lm_studio_integration():
    pass
```

---

## 🐛 Testing Best Practices

### 1. Test Isolation

**DO:**
```python
@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
```

**DON'T:**
```python
# Sharing state between tests
global_db = create_database()  # ❌ Tests will interfere
```

### 2. Mock External Dependencies

**DO:**
```python
@patch("requests.get")
def test_api_call(mock_get):
    """Mock external API."""
    mock_get.return_value.json.return_value = {"data": "test"}
    # Test code that makes API call
```

**DON'T:**
```python
def test_api_call():
    """Actually calls external API."""
    response = requests.get("https://api.example.com")  # ❌ Flaky, slow
```

### 3. Clear Test Names

**DO:**
```python
def test_create_project_with_valid_data_returns_201():
    """Descriptive test name."""
    pass


def test_create_project_with_duplicate_name_returns_400():
    """Clear what's being tested."""
    pass
```

**DON'T:**
```python
def test_1():  # ❌ What does this test?
    pass
```

### 4. Test One Thing

**DO:**
```python
def test_health_endpoint_returns_200():
    """Test status code."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_structure():
    """Test response structure."""
    response = client.get("/health")
    data = response.json()
    assert "status" in data
```

**DON'T:**
```python
def test_health_endpoint():
    """Tests too many things."""  # ❌ Hard to debug failures
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["version"] == "0.1.0"
    # ... 20 more assertions
```

---

## 🔧 Testing Tools & Fixtures

### Database Fixtures

```python
# Use test database
@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)
```

### API Client Fixture

```python
@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)
```

### Mock LLM Fixture

```python
@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = Mock()
    llm.sample.return_value = ["test code"]
    return llm
```

---

## 🔍 Debugging Failed Tests

### Run with Verbose Output

```bash
pytest -vv tests/unit/test_health.py
```

### Run with Print Statements

```bash
pytest -s tests/unit/test_health.py
```

### Run with Debugger

```bash
pytest --pdb tests/unit/test_health.py
```

### Show Local Variables on Failure

```bash
pytest -l tests/unit/test_health.py
```

---

## 🤖 CI/CD Integration

Tests run automatically on:
- **Every push** to main/develop
- **Every pull request**

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: |
    pytest tests/unit/ -v --cov=backend
    pytest tests/integration/ -v
```

### Coverage Requirements

CI fails if coverage drops below:
- Overall: 70%
- Backend: 75%

---

## 📈 Test Metrics

### Expected Test Times

- Unit tests: ~5-10 seconds
- Integration tests: ~30-60 seconds
- All tests: ~1-2 minutes

### Performance Benchmarks

```bash
# Run with duration reporting
pytest --durations=10
```

---

## ✅ Pre-Commit Checklist

Before committing code:

- [ ] All tests pass: `pytest`
- [ ] Coverage maintained: `pytest --cov`
- [ ] Code formatted: `black backend/ config/ cli/`
- [ ] Imports sorted: `isort backend/ config/ cli/`
- [ ] Linting passes: `ruff check backend/ config/ cli/`
- [ ] Type checks pass: `mypy backend/ config/ cli/`

---

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)

---

## 🆘 Troubleshooting

### "Module not found"

```bash
# Install package in editable mode
pip install -e .
```

### "Database locked" errors

```bash
# Use separate test database
export DATABASE_URL="sqlite:///./test.db"
```

### Tests pass locally but fail in CI

- Check Python version compatibility (3.11 vs 3.12)
- Verify all dependencies in requirements.txt
- Check for platform-specific code (Windows vs Linux)

### Slow tests

```bash
# Profile test execution
pytest --profile

# Run only fast tests
pytest -m "not slow"
```

---

**Version**: 1.0
**Last Updated**: 2025-01-16
**Test Coverage**: ~65+ tests, growing
