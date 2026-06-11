from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from erp.models import TaxRate, User
from erp.tests.base import ErpTestCase


class TestTaxRateAPI(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="taxuser",
            password="testpass123",
            firstname="Tax",
            lastname="Tester",
            role="ADMIN",
        )
        cls.tax_20 = TaxRate.objects.create(
            name="VAT 20%", rate=Decimal("20.00"), is_default=True
        )
        cls.tax_0 = TaxRate.objects.create(
            name="No Tax", rate=Decimal("0.00")
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_tax_rates(self):
        resp = self.client.get("/api/v1/tax-rates/")
        assert resp.status_code == 200
        results = resp.data["results"]
        assert len(results) == 2

    def test_create_tax_rate(self):
        resp = self.client.post("/api/v1/tax-rates/", {
            "name": "VAT 10%",
            "rate": "10.00",
        }, format="json")
        assert resp.status_code == 201
        assert resp.data["name"] == "VAT 10%"
        assert resp.data["rate"] == "10.00"
        assert resp.data["is_default"] is False
        assert resp.data["is_active"] is True

    def test_update_tax_rate(self):
        resp = self.client.patch(f"/api/v1/tax-rates/{self.tax_20.id}/", {
            "rate": "22.00",
        })
        assert resp.status_code == 200
        assert resp.data["rate"] == "22.00"

    def test_delete_tax_rate(self):
        tax = TaxRate.objects.create(name="Temp Tax", rate=Decimal("5.00"))
        resp = self.client.delete(f"/api/v1/tax-rates/{tax.id}/")
        assert resp.status_code == 204

    def test_inactive_tax_rates_hidden(self):
        TaxRate.objects.create(
            name="Old Tax", rate=Decimal("15.00"), is_active=False
        )
        resp = self.client.get("/api/v1/tax-rates/")
        names = [r["name"] for r in resp.data["results"]]
        assert "Old Tax" not in names


class TestSaleWithTax(ErpTestCase):

    def setUp(self):
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
        self.create_inventory(quantity=100)

    def test_create_sale_with_tax(self):
        resp = self.api_client.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "100.00",
            "quantity": 2,
            "user": self.user.id,
            "currency": "EUR",
            "tax_rate_id": self.tax_rate.id,
        })
        assert resp.status_code == 201
        assert resp.data["total_amount"] == 240.0  # 200 + 20% tax = 240
        assert resp.data["tax_amount"] == 40.0

    def test_create_sale_without_tax(self):
        resp = self.api_client.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "50.00",
            "quantity": 3,
            "user": self.user.id,
            "currency": "EUR",
        })
        assert resp.status_code == 201
        assert resp.data["total_amount"] == 150.0
        assert resp.data["tax_amount"] == 0.0

    def test_create_sale_with_zero_tax(self):
        resp = self.api_client.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "100.00",
            "quantity": 1,
            "user": self.user.id,
            "currency": "EUR",
            "tax_rate_id": self.tax_rate_zero.id,
        })
        assert resp.status_code == 201
        assert resp.data["total_amount"] == 100.0
        assert resp.data["tax_amount"] == 0.0


class TestSaleUpdateWithTax(ErpTestCase):

    def setUp(self):
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
        self.create_inventory(quantity=100)

    def test_update_sale_add_tax(self):
        resp = self.api_client.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "100.00",
            "quantity": 2,
            "user": self.user.id,
            "currency": "EUR",
        })
        sale_id = resp.data["sale_id"]

        resp = self.api_client.put(f"/erp/update-sale/{sale_id}", {
            "prod": self.product.id,
            "prod_price": "100.00",
            "quantity": 2,
            "user": self.user.id,
            "currency": "EUR",
            "tax_rate_id": self.tax_rate.id,
        })
        assert resp.status_code == 200
        assert resp.data["total_amount"] == 240.0

    def test_update_sale_remove_tax(self):
        resp = self.api_client.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "100.00",
            "quantity": 1,
            "user": self.user.id,
            "currency": "EUR",
            "tax_rate_id": self.tax_rate.id,
        })
        sale_id = resp.data["sale_id"]

        resp = self.api_client.put(f"/erp/update-sale/{sale_id}", {
            "prod": self.product.id,
            "prod_price": "100.00",
            "quantity": 1,
            "user": self.user.id,
            "currency": "EUR",
        })
        assert resp.status_code == 200
        assert resp.data["total_amount"] == 100.0


class TestSaleDetailsWithTax(ErpTestCase):

    def setUp(self):
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
        self.create_inventory(quantity=100)

    def test_sale_details_include_tax(self):
        resp = self.api_client.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "100.00",
            "quantity": 2,
            "user": self.user.id,
            "currency": "EUR",
            "tax_rate_id": self.tax_rate.id,
        })
        sale_id = resp.data["sale_id"]

        resp = self.api_client.get(f"/erp/sale-details/{sale_id}")
        assert resp.status_code == 200
        assert resp.data["tax_amount"] == 40.0
        assert resp.data["tax_rate_name"] == "VAT 20%"
        assert resp.data["tax_rate_percent"] == 20.0


class TestRestockWithTax(ErpTestCase):

    def setUp(self):
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

    def test_create_restock_with_tax(self):
        resp = self.api_client.post("/erp/add-restock", {
            "supplier_id": self.supplier.id,
            "prod": self.product.id,
            "quantity": 10,
            "restock_price": "500.00",
            "currency": "EUR",
            "tax_rate_id": self.tax_rate.id,
        })
        assert resp.status_code == 201
        from erp.models import Transaction
        transaction = Transaction.objects.get(id=resp.data["transaction_id"])
        assert transaction.total_amount == Decimal("600.00")

    def test_create_restock_without_tax(self):
        resp = self.api_client.post("/erp/add-restock", {
            "supplier_id": self.supplier.id,
            "prod": self.product.id,
            "quantity": 5,
            "restock_price": "200.00",
            "currency": "EUR",
        })
        assert resp.status_code == 201
        from erp.models import Transaction
        transaction = Transaction.objects.get(id=resp.data["transaction_id"])
        assert transaction.total_amount == Decimal("200.00")

    def test_update_restock_with_tax(self):
        resp = self.api_client.post("/erp/add-restock", {
            "supplier_id": self.supplier.id,
            "prod": self.product.id,
            "quantity": 5,
            "restock_price": "100.00",
            "currency": "EUR",
        })
        restock_id = resp.data["restock_id"]

        resp = self.api_client.put(f"/erp/update-restock/{restock_id}", {
            "prod": self.product.id,
            "quantity": 5,
            "restock_price": "100.00",
            "currency": "EUR",
            "tax_rate_id": self.tax_rate.id,
        })
        assert resp.status_code == 200
        assert resp.data["total_amount"] == 120.0


class TestSalesReportWithTax(ErpTestCase):

    def setUp(self):
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)
        self.create_inventory(quantity=100)

    def test_sales_report_includes_tax(self):
        self.api_client.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "100.00",
            "quantity": 2,
            "user": self.user.id,
            "currency": "EUR",
            "tax_rate_id": self.tax_rate.id,
        })

        resp = self.api_client.get("/erp/report/sales/")
        assert resp.status_code == 200
        assert len(resp.data) == 1
        row = resp.data[0]
        assert "TVSH" in row
        assert row["TVSH"] == 40.0
