from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from erp.constants import TransactionStatus, TransactionType
from erp.models import Inventory, Payment, Sales, Transaction
from erp.tests.base import ErpTestCase


class TestMultiItemCreateSale(ErpTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from erp.models import Product
        cls.product_b = Product.objects.create(
            name="Test Product B",
            category="Test Category",
            category_fk=cls.category,
            price=Decimal("10.00"),
            description="Second test product",
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.create_inventory(self.product, quantity=100)
        self.create_inventory(self.product_b, quantity=50)

    def test_create_multi_item_sale(self):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 5},
                {"prod": self.product_b.id, "prod_price": 10.00, "quantity": 3},
            ],
        }
        response = self.api.post("/erp/create-sale", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertIn("transaction_id", data)
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(float(data["total_amount"]), 105.00)

        tx = Transaction.objects.get(id=data["transaction_id"])
        self.assertEqual(tx.transaction_type, TransactionType.SALE)
        self.assertEqual(tx.status, TransactionStatus.PENDING)
        self.assertEqual(tx.sales.count(), 2)

        inv_a = Inventory.objects.get(prod=self.product)
        inv_b = Inventory.objects.get(prod=self.product_b)
        self.assertEqual(inv_a.quantity, 95)
        self.assertEqual(inv_b.quantity, 47)

    def test_create_multi_item_with_tax_and_discount(self):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {
                    "prod": self.product.id,
                    "prod_price": 10.00,
                    "quantity": 10,
                    "tax_rate_id": self.tax_rate.id,
                    "discount_type": "PERCENT",
                    "discount_value": 10,
                },
                {
                    "prod": self.product_b.id,
                    "prod_price": 20.00,
                    "quantity": 2,
                },
            ],
        }
        response = self.api.post("/erp/create-sale", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Item 1: subtotal=100, discount=10, discounted=90, tax=18, line_total=108
        # Item 2: subtotal=40, no discount, no tax, line_total=40
        # Grand total: 148
        self.assertEqual(float(response.data["total_amount"]), 148.00)

    def test_create_multi_item_with_payment(self):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 2},
            ],
            "payment": {
                "amount": 30.00,
                "currency": "EUR",
                "payment_method": "CASH",
            },
        }
        response = self.api.post("/erp/create-sale", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tx = Transaction.objects.get(id=response.data["transaction_id"])
        self.assertEqual(tx.status, TransactionStatus.COMPLETED)
        self.assertEqual(Payment.objects.filter(transaction=tx).count(), 1)

    def test_create_sale_empty_items_rejected(self):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [],
        }
        response = self.api.post("/erp/create-sale", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sale_insufficient_inventory(self):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 999},
            ],
        }
        response = self.api.post("/erp/create-sale", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_sale_missing_client_rejected(self):
        payload = {
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 1},
            ],
        }
        response = self.api.post("/erp/create-sale", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_backward_compat_single_item(self):
        """Single-item payload still works fine"""
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 1},
            ],
        }
        response = self.api.post("/erp/create-sale", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["items"]), 1)


class TestTransactionDetails(ErpTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from erp.models import Product
        cls.product_b = Product.objects.create(
            name="Test Product B Det",
            category="Test Category",
            category_fk=cls.category,
            price=Decimal("10.00"),
            description="Second test product for details",
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.create_inventory(self.product, quantity=100)
        self.create_inventory(self.product_b, quantity=50)

    def test_get_details_by_transaction_id(self):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 5},
                {"prod": self.product_b.id, "prod_price": 10.00, "quantity": 3},
            ],
        }
        create_resp = self.api.post("/erp/create-sale", payload, format="json")
        tx_id = create_resp.data["transaction_id"]

        response = self.api.get(f"/erp/sale-details/{tx_id}")
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data["items"]), 2)
        self.assertIn("transaction", data)
        self.assertIn("client", data)
        self.assertIn("payment_summary", data)
        self.assertEqual(float(data["payment_summary"]["total_amount"]), 105.00)

    def test_get_details_returns_404_for_nonexistent(self):
        response = self.api.get("/erp/sale-details/99999")
        self.assertEqual(response.status_code, 404)

    def test_get_details_includes_payments(self):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 2},
            ],
            "payment": {"amount": 30.00, "currency": "EUR", "payment_method": "CASH"},
        }
        create_resp = self.api.post("/erp/create-sale", payload, format="json")
        tx_id = create_resp.data["transaction_id"]

        response = self.api.get(f"/erp/sale-details/{tx_id}")
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data["payments"]), 1)
        self.assertEqual(float(data["payment_summary"]["total_paid"]), 30.00)
        self.assertEqual(float(data["payment_summary"]["remaining"]), 0.00)


class TestMultiItemUpdate(ErpTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from erp.models import Product
        cls.product_b = Product.objects.create(
            name="Test Product B Upd",
            category="Test Category",
            category_fk=cls.category,
            price=Decimal("10.00"),
            description="Second test product for update",
        )
        cls.product_c = Product.objects.create(
            name="Test Product C Upd",
            category="Test Category",
            category_fk=cls.category,
            price=Decimal("20.00"),
            description="Third test product",
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.create_inventory(self.product, quantity=100)
        self.create_inventory(self.product_b, quantity=50)
        self.create_inventory(self.product_c, quantity=30)

    def _create_sale(self, items):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": items,
        }
        resp = self.api.post("/erp/create-sale", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        return resp.data

    def test_update_modify_existing_item(self):
        sale = self._create_sale([
            {"prod": self.product.id, "prod_price": 15.00, "quantity": 5},
            {"prod": self.product_b.id, "prod_price": 10.00, "quantity": 3},
        ])
        tx_id = sale["transaction_id"]
        item_ids = [i["sale_id"] for i in sale["items"]]

        update_payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"id": item_ids[0], "prod": self.product.id, "prod_price": 15.00, "quantity": 10},
                {"id": item_ids[1], "prod": self.product_b.id, "prod_price": 10.00, "quantity": 3},
            ],
        }
        resp = self.api.put(f"/erp/update-sale/{tx_id}", update_payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(float(resp.data["total_amount"]), 180.00)

        from erp.models import Inventory
        inv = Inventory.objects.get(prod=self.product)
        self.assertEqual(inv.quantity, 90)  # 100 - 10

    def test_update_add_new_item(self):
        sale = self._create_sale([
            {"prod": self.product.id, "prod_price": 15.00, "quantity": 5},
        ])
        tx_id = sale["transaction_id"]
        item_id = sale["items"][0]["sale_id"]

        update_payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"id": item_id, "prod": self.product.id, "prod_price": 15.00, "quantity": 5},
                {"prod": self.product_b.id, "prod_price": 10.00, "quantity": 2},
            ],
        }
        resp = self.api.put(f"/erp/update-sale/{tx_id}", update_payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(float(resp.data["total_amount"]), 95.00)
        from erp.models import Transaction
        self.assertEqual(Transaction.objects.get(id=tx_id).sales.count(), 2)

    def test_update_remove_item(self):
        sale = self._create_sale([
            {"prod": self.product.id, "prod_price": 15.00, "quantity": 5},
            {"prod": self.product_b.id, "prod_price": 10.00, "quantity": 3},
        ])
        tx_id = sale["transaction_id"]
        item_ids = [i["sale_id"] for i in sale["items"]]

        update_payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"id": item_ids[0], "prod": self.product.id, "prod_price": 15.00, "quantity": 5},
            ],
        }
        resp = self.api.put(f"/erp/update-sale/{tx_id}", update_payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(float(resp.data["total_amount"]), 75.00)
        from erp.models import Transaction, Inventory
        self.assertEqual(Transaction.objects.get(id=tx_id).sales.count(), 1)
        inv_b = Inventory.objects.get(prod=self.product_b)
        self.assertEqual(inv_b.quantity, 50)  # restored

    def test_update_rejects_foreign_item_id(self):
        sale1 = self._create_sale([
            {"prod": self.product.id, "prod_price": 15.00, "quantity": 1},
        ])
        sale2 = self._create_sale([
            {"prod": self.product_b.id, "prod_price": 10.00, "quantity": 1},
        ])
        tx1_id = sale1["transaction_id"]
        foreign_item_id = sale2["items"][0]["sale_id"]

        update_payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"id": foreign_item_id, "prod": self.product.id, "prod_price": 15.00, "quantity": 1},
            ],
        }
        resp = self.api.put(f"/erp/update-sale/{tx1_id}", update_payload, format="json")
        self.assertEqual(resp.status_code, 400)


class TestMultiItemDelete(ErpTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from erp.models import Product
        cls.product_b = Product.objects.create(
            name="Test Product B Del",
            category="Test Category",
            category_fk=cls.category,
            price=Decimal("10.00"),
            description="Second test product for delete",
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.create_inventory(self.product, quantity=100)
        self.create_inventory(self.product_b, quantity=50)

    def test_delete_multi_item_sale(self):
        payload = {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 5},
                {"prod": self.product_b.id, "prod_price": 10.00, "quantity": 3},
            ],
        }
        resp = self.api.post("/erp/create-sale", payload, format="json")
        tx_id = resp.data["transaction_id"]

        del_resp = self.api.delete(f"/erp/delete-sale/{tx_id}")
        self.assertEqual(del_resp.status_code, 200)

        from erp.models import Transaction, Inventory
        self.assertFalse(Transaction.objects.filter(id=tx_id).exists())
        inv_a = Inventory.objects.get(prod=self.product)
        inv_b = Inventory.objects.get(prod=self.product_b)
        self.assertEqual(inv_a.quantity, 100)
        self.assertEqual(inv_b.quantity, 50)


class TestTransactionGroupedList(ErpTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        from erp.models import Product
        cls.product_b = Product.objects.create(
            name="Test Product B List",
            category="Test Category",
            category_fk=cls.category,
            price=Decimal("10.00"),
            description="Second test product for list",
        )

    def setUp(self):
        self.api = APIClient()
        self.api.force_authenticate(user=self.user)
        self.create_inventory(self.product, quantity=100)
        self.create_inventory(self.product_b, quantity=50)

    def test_sales_list_groups_by_transaction(self):
        # Create a 2-item sale
        self.api.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 15.00, "quantity": 5},
                {"prod": self.product_b.id, "prod_price": 10.00, "quantity": 3},
            ],
        }, format="json")

        response = self.api.get("/erp/salesinfo")
        self.assertEqual(response.status_code, 200)
        # Should be 1 row (1 transaction), not 2 rows
        self.assertEqual(len(response.data), 1)
        row = response.data[0]
        self.assertIn("products", row)
        self.assertEqual(row["item_count"], 2)
        self.assertEqual(float(row["total_amount"]), 105.00)
        self.assertIn("transaction_id", row)
        self.assertIn("client", row)
        self.assertIn("payment_status", row)

    def test_sales_list_row_structure(self):
        self.api.post("/erp/create-sale", {
            "client_id": self.client_obj.id,
            "currency": "EUR",
            "items": [
                {"prod": self.product.id, "prod_price": 10.00, "quantity": 2},
            ],
        }, format="json")

        response = self.api.get("/erp/salesinfo")
        self.assertEqual(response.status_code, 200)
        row = response.data[0]
        required_fields = ["transaction_id", "products", "item_count", "total_amount", "currency", "sale_date", "payment_status", "client"]
        for field in required_fields:
            self.assertIn(field, row, f"Missing field: {field}")
