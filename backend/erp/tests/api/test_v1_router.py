from decimal import Decimal

import pytest

from erp.models import Client, Product


@pytest.mark.django_db
def test_products_list_paginated(authenticated_api_client):
    for i in range(30):
        Product.objects.create(name=f"Prod{i}", category="Cat", price=Decimal("10.00"), description="d")
    resp = authenticated_api_client.get("/api/v1/products/")
    assert resp.status_code == 200
    data = resp.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] == 30
    assert len(data["results"]) == 25  # page_size default


@pytest.mark.django_db
def test_products_page_2(authenticated_api_client):
    for i in range(30):
        Product.objects.create(name=f"Prod{i}", category="Cat", price=Decimal("10.00"), description="d")
    resp = authenticated_api_client.get("/api/v1/products/?page=2")
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 5


@pytest.mark.django_db
def test_suppliers_crud(authenticated_api_client):
    # Create
    resp = authenticated_api_client.post("/api/v1/suppliers/", {
        "firstname": "John", "lastname": "Doe", "address": "123 St"
    }, format="json")
    assert resp.status_code == 201
    pk = resp.json()["id"]
    # Read
    resp = authenticated_api_client.get(f"/api/v1/suppliers/{pk}/")
    assert resp.status_code == 200
    assert resp.json()["firstname"] == "John"
    # Update
    resp = authenticated_api_client.patch(f"/api/v1/suppliers/{pk}/", {"firstname": "Jane"}, format="json")
    assert resp.status_code == 200
    assert resp.json()["firstname"] == "Jane"
    # Delete
    resp = authenticated_api_client.delete(f"/api/v1/suppliers/{pk}/")
    assert resp.status_code == 204


@pytest.mark.django_db
def test_clients_list(authenticated_api_client):
    Client.objects.create(firstname="A", lastname="B", phone="111", address="x", city="Y")
    resp = authenticated_api_client.get("/api/v1/clients/")
    assert resp.status_code == 200
    assert resp.json()["count"] == 1


@pytest.mark.django_db
def test_unauthenticated_rejected():
    from rest_framework.test import APIClient
    client = APIClient()
    resp = client.get("/api/v1/products/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_legacy_routes_still_work(authenticated_api_client):
    Product.objects.create(name="Legacy", category="Cat", price=Decimal("10.00"), description="d")
    resp = authenticated_api_client.get("/erp/products")
    assert resp.status_code == 200
