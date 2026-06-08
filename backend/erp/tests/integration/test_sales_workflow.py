from decimal import Decimal

from erp.constants import TransactionStatus
from erp.services.payment_service import PaymentService
from erp.tests.base import ErpTestCase


class SalesWorkflowTests(ErpTestCase):

    def setUp(self):
        self.inventory = self.create_inventory(quantity=100)

    def test_complete_sale_with_payment(self):
        sale = self.create_sale(quantity=10)
        transaction = sale.transaction
        total = transaction.total_amount

        payment_data = PaymentService.create_payment(
            transaction=transaction,
            amount=total,
            payment_currency="EUR",
            payment_method="CASH",
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionStatus.COMPLETED)
        self.assertEqual(Decimal(str(payment_data["remaining"])), Decimal("0.00"))

    def test_partial_payment_workflow(self):
        sale = self.create_sale(quantity=10)
        transaction = sale.transaction

        PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("50.00"),
            payment_currency="EUR",
            payment_method="CASH",
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionStatus.PARTIAL)

        PaymentService.create_payment(
            transaction=transaction,
            amount=transaction.total_amount - Decimal("50.00"),
            payment_currency="EUR",
            payment_method="CASH",
        )

        transaction.refresh_from_db()
        self.assertEqual(transaction.status, TransactionStatus.COMPLETED)
