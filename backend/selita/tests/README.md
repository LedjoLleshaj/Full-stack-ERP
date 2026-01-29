# Selita Backend Tests

This directory contains all tests for the Selita backend application.

## Structure

```
tests/
├── __init__.py           # Package initialization
├── base.py               # Base test classes and utilities
├── conftest.py           # Pytest configuration (optional)
├── unit/                 # Unit tests
│   ├── __init__.py
│   ├── test_models.py
│   └── test_serializers.py
├── integration/          # Integration tests
│   ├── __init__.py
│   └── test_sales_workflow.py
└── api/                  # API endpoint tests
    ├── __init__.py
    ├── test_auth.py
    └── test_clients.py
```

## Running Tests

### Run all tests
```bash
python manage.py test
```

### Run specific test module
```bash
python manage.py test selita.tests.unit.test_models
```

### Run specific test class
```bash
python manage.py test selita.tests.unit.test_models.ClientModelTests
```

### Run specific test method
```bash
python manage.py test selita.tests.unit.test_models.ClientModelTests.test_client_creation
```

### Run tests with coverage
```bash
# Install coverage first
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

### Run tests with pytest (optional)
```bash
# Install pytest and pytest-django
pip install pytest pytest-django

# Run all tests
pytest

# Run specific test file
pytest selita/tests/unit/test_models.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=selita
```

## Test Categories

### Unit Tests (`unit/`)
Tests individual components in isolation:
- **Models**: Test model creation, validation, methods, and properties
- **Serializers**: Test serialization, deserialization, and validation
- **Utilities**: Test helper functions and custom validators

### Integration Tests (`integration/`)
Tests workflows and component interactions:
- **Sales Workflows**: Complete sales processes including inventory and payments
- **Payment Processing**: Multi-step payment scenarios
- **Inventory Management**: Stock tracking and restock workflows
- **Multi-model Interactions**: Complex business logic involving multiple models

### API Tests (`api/`)
Tests API endpoints and HTTP responses:
- **Authentication**: Login, logout, registration
- **CRUD Operations**: Create, Read, Update, Delete for all resources
- **Permissions**: Access control and authorization
- **Data Validation**: Request/response validation
- **Error Handling**: Edge cases and error responses

## Writing Tests

### Use the Base Test Class
```python
from selita.tests.base import SelitaTestCase

class MyModelTests(SelitaTestCase):
    def test_something(self):
        # self.user, self.client, self.product, etc. are available
        pass
```

### API Testing Pattern
```python
from rest_framework.test import APITestCase
from selita.tests.base import SelitaTestCase

class MyAPITests(APITestCase, SelitaTestCase):
    def setUp(self):
        super().setUpTestData()
        self.client.force_authenticate(user=self.user)
    
    def test_endpoint(self):
        response = self.client.get('/api/endpoint/')
        self.assertEqual(response.status_code, 200)
```

## TODO

Add tests for:
- [ ] Products API
- [ ] Sales API
- [ ] Payments API
- [ ] Inventory API
- [ ] Restocks API
- [ ] Suppliers API
- [ ] Accounts API
- [ ] Transactions API
- [ ] Reports API
- [ ] Users API
- [ ] All model edge cases
- [ ] All serializer validations
- [ ] Permission scenarios
- [ ] Error handling
- [ ] Performance tests
- [ ] Load tests

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Isolation**: Each test should be independent and not rely on others
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
4. **DRY**: Use base classes and helper methods to avoid repetition
5. **Coverage**: Aim for high test coverage, especially for critical business logic
6. **Documentation**: Add docstrings to explain complex test scenarios
7. **Fast Tests**: Keep unit tests fast; save slower tests for integration
