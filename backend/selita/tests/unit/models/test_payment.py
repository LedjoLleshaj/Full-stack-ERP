"""
Unit tests for Payment model.
"""

from decimal import Decimal
from django.test import TestCase
from selita.models import Payment, Transaction, Account, Client


class PaymentModelTests(TestCase):
    """Tests for the Payment model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.db_client = Client.objects.create(
            firstname='Test', lastname='Client',
            phone='+355 69 123', address='Address', city='Tirana'
        )
        cls.transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=cls.db_client,
            total_amount=Decimal('100.00'),
            currency='EUR'
        )
        cls.account = Account.objects.create(
            account_name='Cash EUR',
            account_type='CASH',
            currency='EUR'
        )
    
    def test_payment_creation(self):
        """Test creating a payment."""
        payment = Payment.objects.create(
            transaction=self.transaction,
            account=self.account,
            amount=Decimal('50.00'),
            currency='EUR',
            payment_method='CASH'
        )
        self.assertEqual(payment.transaction, self.transaction)
        self.assertEqual(payment.account, self.account)
        self.assertEqual(payment.amount, Decimal('50.00'))
        self.assertEqual(payment.payment_method, 'CASH')
        self.assertIsNotNone(payment.payment_date)
    
    def test_payment_method_choices(self):
        """Test payment method choices."""
        for method in ['CASH', 'CARD']:
            payment = Payment.objects.create(
                transaction=self.transaction,
                account=self.account,
                amount=Decimal('25.00'),
                currency='EUR',
                payment_method=method
            )
            self.assertEqual(payment.payment_method, method)
    
    def test_payment_with_currency_conversion(self):
        """Test payment with original currency fields."""
        payment = Payment.objects.create(
            transaction=self.transaction,
            account=self.account,
            amount=Decimal('92.00'),
            currency='EUR',
            original_amount=Decimal('100.00'),
            original_currency='USD',
            exchange_rate=Decimal('0.920000'),
            payment_method='CARD'
        )
        self.assertEqual(payment.original_amount, Decimal('100.00'))
        self.assertEqual(payment.original_currency, 'USD')
        self.assertEqual(payment.exchange_rate, Decimal('0.920000'))
    
    def test_payment_str(self):
        """Test payment string representation."""
        payment = Payment.objects.create(
            transaction=self.transaction,
            account=self.account,
            amount=Decimal('75.00'),
            currency='EUR',
            payment_method='CASH'
        )
        expected = f'Payment {payment.id} - 75.00 EUR'
        self.assertEqual(str(payment), expected)
    
    def test_payment_ordering(self):
        """Test payments ordered by -payment_date."""
        p1 = Payment.objects.create(
            transaction=self.transaction, account=self.account,
            amount=Decimal('30.00'), currency='EUR', payment_method='CASH'
        )
        p2 = Payment.objects.create(
            transaction=self.transaction, account=self.account,
            amount=Decimal('40.00'), currency='EUR', payment_method='CARD'
        )
        
        payments = list(Payment.objects.all())
        # Newest first
        self.assertEqual(payments[0].id, p2.id)
        self.assertEqual(payments[1].id, p1.id)
