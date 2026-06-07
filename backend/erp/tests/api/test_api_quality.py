import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_unauthenticated_returns_error_envelope():
    """An unauthenticated request to a protected endpoint returns the error envelope."""
    client = APIClient()
    resp = client.get("/erp/users")
    assert resp.status_code == 401
    body = resp.json()
    assert "error" in body
    assert "message" in body["error"]
    assert "code" in body["error"]


@pytest.mark.django_db
def test_method_not_allowed_returns_error_envelope(authenticated_api_client):
    """A wrong HTTP method on a view returns the error envelope."""
    # /erp/users only allows GET
    resp = authenticated_api_client.delete("/erp/users")
    assert resp.status_code == 405
    body = resp.json()
    assert "error" in body
    assert "message" in body["error"]
    assert "code" in body["error"]


@pytest.mark.django_db
def test_schema_endpoint_accessible():
    client = APIClient()
    resp = client.get("/api/schema/", HTTP_ACCEPT="application/json")
    assert resp.status_code == 200
    body = resp.json()
    assert "openapi" in body


@pytest.mark.django_db
def test_docs_endpoint_accessible():
    client = APIClient()
    resp = client.get("/api/docs")
    assert resp.status_code == 200
