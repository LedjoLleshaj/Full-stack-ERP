import pytest
from rest_framework.test import APIClient

from erp.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def existing_user():
    return User.objects.create_user(
        username="existinguser",
        password="testpass123",
        email="existing@example.com",
        firstname="Existing",
        lastname="User",
        role="STAFF",
    )


@pytest.fixture
def authenticated_api_client(api_client, existing_user):
    api_client.force_authenticate(user=existing_user)
    return api_client
