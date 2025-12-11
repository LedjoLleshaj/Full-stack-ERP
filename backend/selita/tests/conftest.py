"""
Pytest configuration for the Selita test suite.

This file is optional and only needed if you choose to use pytest instead of Django's test runner.
"""

import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """Custom database setup for pytest."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def api_client():
    """Fixture for Django REST framework API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, django_user_model):
    """Fixture for authenticated API client."""
    user = django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client


# Add more fixtures as needed
