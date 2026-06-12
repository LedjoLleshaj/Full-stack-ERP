from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import call_command

from erp.models import Inventory, Product

pytestmark = pytest.mark.django_db

LOW_STOCK_URL = "/api/v1/inventory/low-stock/"


def make_product(name, reorder_level=0, reorder_quantity=0, stock=None, is_active=True):
    product = Product.objects.create(
        name=name,
        category="Cat",
        price=Decimal("10.00"),
        description="d",
        reorder_level=reorder_level,
        reorder_quantity=reorder_quantity,
        is_active=is_active,
    )
    if stock is not None:
        Inventory.objects.create(prod=product, quantity=stock)
    return product


class TestProductReorderFields:
    def test_product_has_reorder_fields_with_zero_defaults(self):
        product = Product.objects.create(
            name="Reorder Prod",
            category="Cat",
            price=Decimal("10.00"),
            description="d",
        )
        assert product.reorder_level == 0
        assert product.reorder_quantity == 0

    def test_product_reorder_fields_persist(self):
        product = Product.objects.create(
            name="Reorder Prod 2",
            category="Cat",
            price=Decimal("10.00"),
            description="d",
            reorder_level=10,
            reorder_quantity=50,
        )
        product.refresh_from_db()
        assert product.reorder_level == 10
        assert product.reorder_quantity == 50


class TestLowStockEndpoint:
    def test_requires_authentication(self, api_client):
        resp = api_client.get(LOW_STOCK_URL)
        assert resp.status_code == 401

    def test_product_at_or_below_reorder_level_included(self, authenticated_api_client):
        make_product("At level", reorder_level=5, reorder_quantity=20, stock=5)
        make_product("Below level", reorder_level=5, reorder_quantity=20, stock=2)

        resp = authenticated_api_client.get(LOW_STOCK_URL)

        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()]
        assert names == ["Below level", "At level"]  # most critical first

    def test_product_above_reorder_level_excluded(self, authenticated_api_client):
        make_product("Healthy", reorder_level=5, stock=6)

        resp = authenticated_api_client.get(LOW_STOCK_URL)

        assert resp.json() == []

    def test_product_without_inventory_record_treated_as_out_of_stock(self, authenticated_api_client):
        make_product("Never stocked", reorder_level=0)

        resp = authenticated_api_client.get(LOW_STOCK_URL)

        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Never stocked"
        assert data[0]["quantity"] == 0

    def test_inactive_product_excluded(self, authenticated_api_client):
        make_product("Deleted", reorder_level=5, stock=0, is_active=False)

        resp = authenticated_api_client.get(LOW_STOCK_URL)

        assert resp.json() == []

    def test_response_fields(self, authenticated_api_client):
        product = make_product("Fields", reorder_level=5, reorder_quantity=30, stock=3)

        resp = authenticated_api_client.get(LOW_STOCK_URL)

        item = resp.json()[0]
        assert item == {
            "id": product.id,
            "name": "Fields",
            "category": "Cat",
            "price": 10.0,
            "quantity": 3,
            "reorder_level": 5,
            "reorder_quantity": 30,
        }


class TestLegacyProductEndpoints:
    def test_get_products_includes_reorder_fields(self, authenticated_api_client):
        make_product("Legacy fields", reorder_level=7, reorder_quantity=25, stock=100)

        resp = authenticated_api_client.get("/erp/products")

        assert resp.status_code == 200
        item = resp.json()[0]
        assert item["reorder_level"] == 7
        assert item["reorder_quantity"] == 25

    def test_update_product_accepts_reorder_fields(self, authenticated_api_client):
        product = make_product("Updatable", stock=100)

        resp = authenticated_api_client.put(
            f"/erp/update-product/{product.id}",
            {"reorder_level": 12, "reorder_quantity": 40},
            format="json",
        )

        assert resp.status_code == 200
        product.refresh_from_db()
        assert product.reorder_level == 12
        assert product.reorder_quantity == 40


class TestCheckStockLevelsCommand:
    def test_warns_for_each_low_stock_product(self, caplog):
        make_product("Low A", reorder_level=5, reorder_quantity=20, stock=2)
        make_product("Healthy", reorder_level=5, stock=50)

        out = StringIO()
        with caplog.at_level("WARNING"):
            call_command("check_stock_levels", stdout=out)

        output = out.getvalue()
        assert "Low A" in output
        assert "Healthy" not in output
        assert any("Low A" in record.message for record in caplog.records)

    def test_reports_ok_when_no_low_stock(self):
        make_product("Healthy", reorder_level=5, stock=50)

        out = StringIO()
        call_command("check_stock_levels", stdout=out)

        assert "0 product" in out.getvalue() or "No products" in out.getvalue()
