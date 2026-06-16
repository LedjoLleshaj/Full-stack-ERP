from rest_framework import status
from rest_framework.test import APIClient

from erp.tests.base import ErpTestCase


class DiscountCreateTests(ErpTestCase):

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.create_inventory(quantity=100)

    def _sale_payload(self, **overrides):
        base = {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "15.00",
            "quantity": 10,
            "user": self.user.id,
            "currency": "EUR",
        }
        base.update(overrides)
        return base

    def test_create_sale_no_discount(self):
        resp = self.api.post("/erp/create-sale", self._sale_payload(), format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["discount_amount"] == 0
        assert resp.data["total_amount"] == 150.0

    def test_create_sale_percent_discount(self):
        resp = self.api.post(
            "/erp/create-sale",
            self._sale_payload(discount_type="PERCENT", discount_value="10"),
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["discount_amount"] == 15.0  # 10% of 150
        assert resp.data["total_amount"] == 135.0

    def test_create_sale_fixed_discount(self):
        resp = self.api.post(
            "/erp/create-sale",
            self._sale_payload(discount_type="FIXED", discount_value="25"),
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["discount_amount"] == 25.0
        assert resp.data["total_amount"] == 125.0

    def test_percent_discount_with_tax(self):
        resp = self.api.post(
            "/erp/create-sale",
            self._sale_payload(
                discount_type="PERCENT",
                discount_value="20",
                tax_rate_id=self.tax_rate.id,
            ),
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        # subtotal=150, discount=30, discounted=120, tax=24 (20%), total=144
        assert resp.data["discount_amount"] == 30.0
        assert resp.data["tax_amount"] == 24.0
        assert resp.data["total_amount"] == 144.0

    def test_fixed_discount_with_tax(self):
        resp = self.api.post(
            "/erp/create-sale",
            self._sale_payload(
                discount_type="FIXED",
                discount_value="50",
                tax_rate_id=self.tax_rate.id,
            ),
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        # subtotal=150, discount=50, discounted=100, tax=20, total=120
        assert resp.data["discount_amount"] == 50.0
        assert resp.data["tax_amount"] == 20.0
        assert resp.data["total_amount"] == 120.0

    def test_percent_over_100_rejected(self):
        resp = self.api.post(
            "/erp/create-sale",
            self._sale_payload(discount_type="PERCENT", discount_value="150"),
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_fixed_over_subtotal_rejected(self):
        resp = self.api.post(
            "/erp/create-sale",
            self._sale_payload(discount_type="FIXED", discount_value="200"),
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_discount_type_rejected(self):
        resp = self.api.post(
            "/erp/create-sale",
            self._sale_payload(discount_type="BOGUS", discount_value="10"),
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class DiscountDetailsTests(ErpTestCase):

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.create_inventory(quantity=100)

    def test_details_include_discount_fields(self):
        resp = self.api.post(
            "/erp/create-sale",
            {
                "client_id": self.client_obj.id,
                "prod": self.product.id,
                "prod_price": "20.00",
                "quantity": 5,
                "user": self.user.id,
                "currency": "EUR",
                "discount_type": "PERCENT",
                "discount_value": "10",
            },
            format="json",
        )
        sale_id = resp.data["sale_id"]

        details = self.api.get(f"/erp/sale-details/{sale_id}")
        assert details.status_code == status.HTTP_200_OK
        assert details.data["discount_type"] == "PERCENT"
        assert details.data["discount_value"] == 10.0
        assert details.data["discount_amount"] == 10.0  # 10% of 100


class DiscountUpdateTests(ErpTestCase):

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.create_inventory(quantity=100)

    def _create_sale(self, **extra):
        payload = {
            "client_id": self.client_obj.id,
            "prod": self.product.id,
            "prod_price": "10.00",
            "quantity": 10,
            "user": self.user.id,
            "currency": "EUR",
        }
        payload.update(extra)
        resp = self.api.post("/erp/create-sale", payload, format="json")
        return resp.data["sale_id"]

    def test_add_discount_to_existing_sale(self):
        sale_id = self._create_sale()
        resp = self.api.put(
            f"/erp/update-sale/{sale_id}",
            {
                "prod": self.product.id,
                "quantity": 10,
                "prod_price": "10.00",
                "user": self.user.id,
                "currency": "EUR",
                "discount_type": "FIXED",
                "discount_value": "20",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["total_amount"] == 80.0

    def test_remove_discount_from_sale(self):
        sale_id = self._create_sale(discount_type="PERCENT", discount_value="10")
        resp = self.api.put(
            f"/erp/update-sale/{sale_id}",
            {
                "prod": self.product.id,
                "quantity": 10,
                "prod_price": "10.00",
                "user": self.user.id,
                "currency": "EUR",
                "discount_type": None,
                "discount_value": "0",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["total_amount"] == 100.0
