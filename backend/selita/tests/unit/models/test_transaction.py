"""
Unit tests for Transaction model.
"""

from decimal import Decimal
from django.test import TestCase
from selita.models import Transaction, Client, Supplier


class TransactionModelTests(TestCase):
    """Tests for the Transaction model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.db_client = Client.objects.create(
            firstname='Test', lastname='Client',
            phone='+355 69 111', address='Address', city='Tirana'
        )
        cls.supplier = Supplier.objects.create(
            firstname='Test', lastname='Supplier', address='Supplier Address'
        )
    
    def test_transaction_creation_sale(self):
        """Test creating a SALE transaction."""
        transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=self.db_client,
            total_amount=Decimal('150.00'),
            currency='EUR'
        )
        self.assertEqual(transaction.transaction_type, 'SALE')
        self.assertEqual(transaction.client, self.db_client)
        self.assertEqual(transaction.total_amount, Decimal('150.00'))
        self.assertEqual(transaction.status, 'PENDING')  # Default
        self.assertIsNotNone(transaction.created_date)
    
    def test_transaction_creation_purchase(self):
        """Test creating a PURCHASE transaction."""
        transaction = Transaction.objects.create(
            transaction_type='PURCHASE',
            supplier=self.supplier,
            total_amount=Decimal('500.00'),
            currency='EUR',
            status='COMPLETED'
        )
        self.assertEqual(transaction.transaction_type, 'PURCHASE')
        self.assertEqual(transaction.supplier, self.supplier)
        self.assertEqual(transaction.status, 'COMPLETED')
    
    def test_transaction_status_choices(self):
        """Test all status choices."""
        for status in ['PENDING', 'PARTIAL', 'COMPLETED', 'CANCELLED']:
            transaction = Transaction.objects.create(
                transaction_type='SALE',
                client=self.db_client,
                total_amount=Decimal('100.00'),
                currency='EUR',
                status=status
            )
            self.assertEqual(transaction.status, status)
    
    def test_transaction_default_status(self):
        """Test default status is PENDING."""
        transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=self.db_client,
            total_amount=Decimal('100.00'),
            currency='EUR'
        )
        self.assertEqual(transaction.status, 'PENDING')
    
    def test_transaction_str_with_invoice(self):
        """Test string representation with invoice number."""
        transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=self.db_client,
            total_amount=Decimal('100.00'),
            currency='EUR',
            invoice_number='INV-001'
        )
        self.assertEqual(str(transaction), 'SALE - INV-001')
    
    def test_transaction_str_without_invoice(self):
        """Test string representation without invoice number."""
        transaction = Transaction.objects.create(
            transaction_type='PURCHASE',
            supplier=self.supplier,
            total_amount=Decimal('100.00'),
            currency='EUR'
        )
        self.assertEqual(str(transaction), f'PURCHASE - {transaction.id}')
    
    def test_transaction_ordering(self):
        """Test transactions ordered by -created_date."""
        t1 = Transaction.objects.create(
            transaction_type='SALE', client=self.db_client,
            total_amount=Decimal('100.00'), currency='EUR'
        )
        t2 = Transaction.objects.create(
            transaction_type='SALE', client=self.db_client,
            total_amount=Decimal('200.00'), currency='EUR'
        )
        
        transactions = list(Transaction.objects.all())
        # Newest first
        self.assertEqual(transactions[0].id, t2.id)
        self.assertEqual(transactions[1].id, t1.id)
