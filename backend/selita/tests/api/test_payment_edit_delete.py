from rest_framework.test import APITestCase
from decimal import Decimal
from django.utils import timezone
from selita.models import Transaction, Payment, Account, Client, Product, Supplier, Restock
from selita.services.payment_service import PaymentService
from selita.constants import TransactionType, TransactionStatus

class PaymentEditDeleteTest(APITestCase):
    def setUp(self):
        # Create common data
        self.client_obj = Client.objects.create(firstname="Test", lastname="Client")
        self.product = Product.objects.create(name="Test Product", price=Decimal("100.00"))
        self.account = Account.objects.create(
            account_name="Cash EUR", 
            account_type="CASH", 
            currency="EUR", 
            current_balance=Decimal("1000.00")
        )
        
        # Create a sale
        self.sale = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("200.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )

    def test_update_payment_sale(self):
        initial_balance = self.account.current_balance
        
        # Create initial payment
        payment_data = PaymentService.create_payment(
            transaction=self.sale,
            amount=Decimal("100.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        payment = Payment.objects.get(id=payment_data["payment_id"])
        
        self.account.refresh_from_db()
        self.sale.refresh_from_db()
        
        self.assertEqual(self.account.current_balance, initial_balance + Decimal("100.00"))
        self.assertEqual(self.sale.status, TransactionStatus.PARTIAL)
        
        # Update payment: 100 -> 150
        PaymentService.update_payment(payment, Decimal("150.00"), "Updated notes")
        
        self.account.refresh_from_db()
        self.sale.refresh_from_db()
        
        self.assertEqual(self.account.current_balance, initial_balance + Decimal("150.00"))
        self.assertEqual(self.sale.status, TransactionStatus.PARTIAL)
        
        # Update payment: 150 -> 200 (Complete)
        PaymentService.update_payment(payment, Decimal("200.00"), "Full payment")
        
        self.account.refresh_from_db()
        self.sale.refresh_from_db()
        
        self.assertEqual(self.account.current_balance, initial_balance + Decimal("200.00"))
        self.assertEqual(self.sale.status, TransactionStatus.COMPLETED)
        self.assertIsNotNone(self.sale.completed_date)

    def test_delete_payment_sale(self):
        initial_balance = self.account.current_balance
        
        # Create payment
        payment_data = PaymentService.create_payment(
            transaction=self.sale,
            amount=Decimal("200.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        payment = Payment.objects.get(id=payment_data["payment_id"])
        
        self.account.refresh_from_db()
        self.sale.refresh_from_db()
        
        self.assertEqual(self.account.current_balance, initial_balance + Decimal("200.00"))
        self.assertEqual(self.sale.status, TransactionStatus.COMPLETED)
        
        # Delete payment
        PaymentService.delete_payment(payment)
        
        self.account.refresh_from_db()
        self.sale.refresh_from_db()
        
        self.assertEqual(self.account.current_balance, initial_balance)
        self.assertEqual(self.sale.status, TransactionStatus.PENDING)
        self.assertIsNone(self.sale.completed_date)
        self.assertFalse(Payment.objects.filter(id=payment.id).exists())

    def test_update_payment_restock(self):
        # Setup restock
        supplier = Supplier.objects.create(firstname="Supp", lastname="Lier")
        account = self.account # Reuse account from setUp
        
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=supplier,
            total_amount=Decimal("500.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        
        # Create restock record
        Restock.objects.create(
            transaction=transaction,
            prod=self.product,
            quantity=10, 
            restock_price=Decimal("50.00")
        )
        
        initial_balance = account.current_balance
        
        # Create payment
        payment_data = PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("200.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        payment = Payment.objects.get(id=payment_data["payment_id"])
        
        account.refresh_from_db()
        self.assertEqual(account.current_balance, initial_balance - Decimal("200.00"))
        
        # Update payment: 200 -> 300
        PaymentService.update_payment(payment, Decimal("300.00"))
        
        account.refresh_from_db()
        transaction.refresh_from_db()
        
        self.assertEqual(account.current_balance, initial_balance - Decimal("300.00"))
        self.assertEqual(transaction.status, TransactionStatus.PARTIAL)
