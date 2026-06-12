"""
Tests for Credit Notes / Returns.
"""

from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from erp.constants import TransactionStatus, TransactionType
from erp.models import (
    Account,
    Client,
    Inventory,
    Product,
    Sales,
    TaxRate,
    Transaction,
    User,
)
from erp.services.payment_service import PaymentError, PaymentService


class ReturnServiceTestCase(TestCase):
    """Tests for PaymentService.process_return()"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.com",
            firstname="Test",
            lastname="User",
            role="ADMIN",
        )

        self.test_client = Client.objects.create(
            firstname="John",
            lastname="Doe",
            phone="1234567890",
            address="123 Test St",
            city="Test City",
        )

        self.product = Product.objects.create(
            name="Apple",
            category="Fruit",
            price=Decimal("10.00"),
            description="Test apple",
        )

        Inventory.objects.create(prod=self.product, quantity=100)

        self.cash_eur = Account.objects.create(
            account_name="Cash EUR",
            account_type="CASH",
            currency="EUR",
            current_balance=Decimal("1000.00"),
        )

    def _create_sale_with_payment(self, quantity=10, price=Decimal("10.00"),
                                   paid=Decimal("0"), currency="EUR",
                                   tax_rate=None, tax_amount=Decimal("0")):
        """Helper: create a sale transaction with optional payment."""
        total = price * quantity + tax_amount
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=total,
            currency=currency,
            status=TransactionStatus.PENDING,
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product,
            prod_price=price,
            user=self.user,
            quantity=quantity,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
        )
        if paid > 0:
            PaymentService.create_payment(
                transaction=transaction,
                amount=paid,
                payment_currency=currency,
                payment_method="CASH",
            )
            transaction.refresh_from_db()
        return transaction, sale

    def test_partial_return_reduces_total(self):
        """Return 3 of 10 items, no refund needed (underpaid)."""
        transaction, sale = self._create_sale_with_payment(
            quantity=10, price=Decimal("10.00"), paid=Decimal("40.00")
        )

        result = PaymentService.process_return(
            original_transaction=transaction,
            return_items=[{"sale_line_id": sale.id, "quantity": 3}],
            refund_method="CASH",
            refund_currency="EUR",
            user=self.user,
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.total_amount, Decimal("70.00"))
        self.assertEqual(transaction.status, TransactionStatus.PARTIAL)
        self.assertEqual(result["refund_amount"], 0.0)
        self.assertEqual(result["return_value"], 30.0)

        # Inventory restored
        inv = Inventory.objects.get(prod=self.product)
        self.assertEqual(inv.quantity, 103)

    def test_return_completes_partial_sale(self):
        """Return enough that paid == new_total -> COMPLETED."""
        transaction, sale = self._create_sale_with_payment(
            quantity=10, price=Decimal("10.00"), paid=Decimal("40.00")
        )

        result = PaymentService.process_return(
            original_transaction=transaction,
            return_items=[{"sale_line_id": sale.id, "quantity": 6}],
            refund_method="CASH",
            refund_currency="EUR",
            user=self.user,
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.total_amount, Decimal("40.00"))
        self.assertEqual(transaction.status, TransactionStatus.COMPLETED)
        self.assertEqual(result["refund_amount"], 0.0)

    def test_return_triggers_refund(self):
        """Return on overpaid sale -> refund = overpaid amount."""
        transaction, sale = self._create_sale_with_payment(
            quantity=10, price=Decimal("10.00"), paid=Decimal("80.00")
        )

        initial_balance = Account.objects.get(id=self.cash_eur.id).current_balance

        result = PaymentService.process_return(
            original_transaction=transaction,
            return_items=[{"sale_line_id": sale.id, "quantity": 5}],
            refund_method="CASH",
            refund_currency="EUR",
            user=self.user,
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.total_amount, Decimal("50.00"))
        self.assertEqual(transaction.status, TransactionStatus.COMPLETED)
        self.assertEqual(result["refund_amount"], 30.0)

        # Account balance reduced by refund
        self.cash_eur.refresh_from_db()
        self.assertEqual(
            self.cash_eur.current_balance,
            initial_balance - Decimal("30.00"),
        )

    def test_full_return_marks_refunded(self):
        """Return all items on completed sale -> REFUNDED, full refund."""
        transaction, sale = self._create_sale_with_payment(
            quantity=10, price=Decimal("10.00"), paid=Decimal("100.00")
        )

        result = PaymentService.process_return(
            original_transaction=transaction,
            return_items=[{"sale_line_id": sale.id, "quantity": 10}],
            refund_method="CASH",
            refund_currency="EUR",
            user=self.user,
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.total_amount, Decimal("0.00"))
        self.assertEqual(transaction.status, TransactionStatus.REFUNDED)
        self.assertEqual(result["refund_amount"], 100.0)

    def test_cannot_return_more_than_sold(self):
        """Returning more than sold quantity raises error."""
        transaction, sale = self._create_sale_with_payment(quantity=10)

        with self.assertRaises(PaymentError):
            PaymentService.process_return(
                original_transaction=transaction,
                return_items=[{"sale_line_id": sale.id, "quantity": 11}],
                refund_method="CASH",
                refund_currency="EUR",
                user=self.user,
            )

    def test_cannot_return_cancelled_sale(self):
        """Returning on a cancelled sale raises error."""
        transaction, sale = self._create_sale_with_payment(quantity=10)
        transaction.status = TransactionStatus.CANCELLED
        transaction.save()

        with self.assertRaises(PaymentError):
            PaymentService.process_return(
                original_transaction=transaction,
                return_items=[{"sale_line_id": sale.id, "quantity": 5}],
                refund_method="CASH",
                refund_currency="EUR",
                user=self.user,
            )

    def test_cannot_return_already_refunded(self):
        """Returning on an already-refunded sale raises error."""
        transaction, sale = self._create_sale_with_payment(quantity=10)
        transaction.status = TransactionStatus.REFUNDED
        transaction.save()

        with self.assertRaises(PaymentError):
            PaymentService.process_return(
                original_transaction=transaction,
                return_items=[{"sale_line_id": sale.id, "quantity": 5}],
                refund_method="CASH",
                refund_currency="EUR",
                user=self.user,
            )

    def test_multiple_partial_returns(self):
        """Two partial returns, quantities tracked correctly."""
        transaction, sale = self._create_sale_with_payment(
            quantity=10, price=Decimal("10.00"), paid=Decimal("100.00")
        )

        # First return: 3 items
        PaymentService.process_return(
            original_transaction=transaction,
            return_items=[{"sale_line_id": sale.id, "quantity": 3}],
            refund_method="CASH",
            refund_currency="EUR",
            user=self.user,
        )
        transaction.refresh_from_db()
        self.assertEqual(transaction.total_amount, Decimal("70.00"))

        # Second return: 4 items
        PaymentService.process_return(
            original_transaction=transaction,
            return_items=[{"sale_line_id": sale.id, "quantity": 4}],
            refund_method="CASH",
            refund_currency="EUR",
            user=self.user,
        )
        transaction.refresh_from_db()
        self.assertEqual(transaction.total_amount, Decimal("30.00"))

        # Cannot return 4 more (only 3 remain)
        with self.assertRaises(PaymentError):
            PaymentService.process_return(
                original_transaction=transaction,
                return_items=[{"sale_line_id": sale.id, "quantity": 4}],
                refund_method="CASH",
                refund_currency="EUR",
                user=self.user,
            )

    def test_return_restores_inventory(self):
        """Inventory increases by returned quantity."""
        transaction, sale = self._create_sale_with_payment(quantity=10)

        inv_before = Inventory.objects.get(prod=self.product).quantity

        PaymentService.process_return(
            original_transaction=transaction,
            return_items=[{"sale_line_id": sale.id, "quantity": 7}],
            refund_method="CASH",
            refund_currency="EUR",
            user=self.user,
        )

        inv_after = Inventory.objects.get(prod=self.product).quantity
        self.assertEqual(inv_after, inv_before + 7)

    def test_return_with_tax(self):
        """Tax proportionally reduced on return."""
        tax_rate = TaxRate.objects.create(
            name="VAT 20%", rate=Decimal("20.00"), is_default=False
        )
        # 10 * 10 = 100, tax = 20, total = 120
        transaction, sale = self._create_sale_with_payment(
            quantity=10,
            price=Decimal("10.00"),
            paid=Decimal("120.00"),
            tax_rate=tax_rate,
            tax_amount=Decimal("20.00"),
        )

        # Return 5 items: subtotal 50, tax 10, return_value 60
        result = PaymentService.process_return(
            original_transaction=transaction,
            return_items=[{"sale_line_id": sale.id, "quantity": 5}],
            refund_method="CASH",
            refund_currency="EUR",
            user=self.user,
        )

        transaction.refresh_from_db()
        # new_total = 120 - 60 = 60, paid 120 -> refund 60
        self.assertEqual(transaction.total_amount, Decimal("60.00"))
        self.assertEqual(result["return_value"], 60.0)
        self.assertEqual(result["refund_amount"], 60.0)


class ReturnAPITestCase(TestCase):
    """Tests for return API endpoints."""

    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(
            username="testuser2",
            password="testpass123",
            email="test2@test.com",
            firstname="Test",
            lastname="User",
            role="ADMIN",
        )
        self.client_api.force_authenticate(user=self.user)

        self.test_client = Client.objects.create(
            firstname="Jane",
            lastname="Doe",
            phone="9876543210",
            address="456 Test Ave",
            city="Test City",
        )

        self.product = Product.objects.create(
            name="Orange",
            category="Fruit",
            price=Decimal("5.00"),
            description="Test orange",
        )

        Inventory.objects.create(prod=self.product, quantity=50)

        self.cash_eur = Account.objects.create(
            account_name="Cash EUR",
            account_type="CASH",
            currency="EUR",
            current_balance=Decimal("500.00"),
        )

    def _create_sale(self, quantity=10, price=Decimal("5.00"), paid=Decimal("50.00")):
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=price * quantity,
            currency="EUR",
            status=TransactionStatus.PENDING,
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product,
            prod_price=price,
            user=self.user,
            quantity=quantity,
        )
        if paid > 0:
            PaymentService.create_payment(
                transaction=transaction,
                amount=paid,
                payment_currency="EUR",
                payment_method="CASH",
            )
            transaction.refresh_from_db()
        return transaction, sale

    def test_create_return_endpoint(self):
        """POST /erp/create-return/<sale_id> creates a return."""
        # Sale of 10 items at 5.00 = 50.00, paid 20.00 (underpaid)
        # Returning 3 items (15.00 value): new_total=35, paid=20 -> refund=0
        transaction, sale = self._create_sale(quantity=10, paid=Decimal("20.00"))

        response = self.client_api.post(
            f"/erp/create-return/{sale.id}",
            {
                "items": [{"sale_line_id": sale.id, "quantity": 3}],
                "refund_method": "CASH",
                "refund_currency": "EUR",
                "notes": "Damaged",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["return_value"], 15.0)
        self.assertEqual(response.data["refund_amount"], 0.0)

    def test_create_return_with_refund(self):
        """Return triggers refund when overpaid."""
        transaction, sale = self._create_sale(quantity=10, paid=Decimal("50.00"))

        response = self.client_api.post(
            f"/erp/create-return/{sale.id}",
            {
                "items": [{"sale_line_id": sale.id, "quantity": 8}],
                "refund_method": "CASH",
                "refund_currency": "EUR",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["refund_amount"], 40.0)

    def test_get_sale_returns(self):
        """GET /erp/sale-returns/<sale_id> lists returns for a sale."""
        transaction, sale = self._create_sale(quantity=10, paid=Decimal("50.00"))

        self.client_api.post(
            f"/erp/create-return/{sale.id}",
            {
                "items": [{"sale_line_id": sale.id, "quantity": 3}],
                "refund_method": "CASH",
                "refund_currency": "EUR",
            },
            format="json",
        )

        response = self.client_api.get(f"/erp/sale-returns/{sale.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["items"][0]["quantity"], 3)

    def test_get_returns_list(self):
        """GET /erp/returns lists all return transactions."""
        transaction, sale = self._create_sale(quantity=10, paid=Decimal("50.00"))

        self.client_api.post(
            f"/erp/create-return/{sale.id}",
            {
                "items": [{"sale_line_id": sale.id, "quantity": 2}],
                "refund_method": "CASH",
                "refund_currency": "EUR",
            },
            format="json",
        )

        response = self.client_api.get("/erp/returns")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class SaleDetailsReturnInfoTestCase(TestCase):
    """Tests for return info in sale details endpoint."""

    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(
            username="testuser3",
            password="testpass123",
            email="test3@test.com",
            firstname="Test",
            lastname="User",
            role="ADMIN",
        )
        self.client_api.force_authenticate(user=self.user)

        self.test_client = Client.objects.create(
            firstname="Bob",
            lastname="Smith",
            phone="5551234567",
            address="789 Test Blvd",
            city="Test City",
        )

        self.product = Product.objects.create(
            name="Banana",
            category="Fruit",
            price=Decimal("8.00"),
            description="Test banana",
        )

        Inventory.objects.create(prod=self.product, quantity=50)

        Account.objects.create(
            account_name="Cash EUR",
            account_type="CASH",
            currency="EUR",
            current_balance=Decimal("500.00"),
        )

    def test_sale_details_includes_return_info(self):
        """getSaleDetails includes returns and already_returned per line."""
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=Decimal("80.00"),
            currency="EUR",
            status=TransactionStatus.PENDING,
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product,
            prod_price=Decimal("8.00"),
            user=self.user,
            quantity=10,
        )
        PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("80.00"),
            payment_currency="EUR",
            payment_method="CASH",
        )

        # Create a return of 3 items
        self.client_api.post(
            f"/erp/create-return/{sale.id}",
            {
                "items": [{"sale_line_id": sale.id, "quantity": 3}],
                "refund_method": "CASH",
                "refund_currency": "EUR",
            },
            format="json",
        )

        response = self.client_api.get(f"/erp/sale-details/{sale.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("returns", response.data)
        self.assertEqual(len(response.data["returns"]), 1)
        self.assertEqual(response.data["returns"][0]["items"][0]["quantity"], 3)
        self.assertEqual(response.data["already_returned"][str(self.product.id)], 3)

    def test_sales_list_excludes_returns(self):
        """getProductsFromSales filters out RETURN transactions."""
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=Decimal("80.00"),
            currency="EUR",
        )
        Sales.objects.create(
            transaction=transaction,
            prod=self.product,
            prod_price=Decimal("8.00"),
            user=self.user,
            quantity=10,
        )

        # Create a RETURN transaction
        return_tx = Transaction.objects.create(
            transaction_type=TransactionType.RETURN,
            client=self.test_client,
            total_amount=Decimal("24.00"),
            currency="EUR",
            original_transaction=transaction,
        )
        Sales.objects.create(
            transaction=return_tx,
            prod=self.product,
            prod_price=Decimal("8.00"),
            user=self.user,
            quantity=3,
        )

        response = self.client_api.get("/erp/salesinfo")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only the original sale should appear, not the return
        for s in response.data:
            sale_obj = Sales.objects.get(id=s["id"])
            self.assertNotEqual(
                sale_obj.transaction.transaction_type, TransactionType.RETURN
            )
