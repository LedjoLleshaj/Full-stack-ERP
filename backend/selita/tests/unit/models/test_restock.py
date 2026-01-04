"""
Unit tests for Restock model.
"""

from decimal import Decimal
from django.test import TestCase
from selita.models import Restock, Transaction, Product, Supplier


class RestockModelTests(TestCase):
    """Tests for the Restock model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.supplier = Supplier.objects.create(
            firstname='Fish', lastname='Supplier', address='Harbor 1'
        )
        cls.product = Product.objects.create(
            name='Salmon', category='Fish',
            price=Decimal('18.00'), description='Atlantic salmon'
        )
        cls.transaction = Transaction.objects.create(
            transaction_type='PURCHASE',
            supplier=cls.supplier,
            total_amount=Decimal('500.00'),
            currency='EUR',
            status='COMPLETED'
        )
    
    def test_restock_creation(self):
        """Test creating a restock."""
        restock = Restock.objects.create(
            transaction=self.transaction,
            prod=self.product,
            quantity=50,
            restock_price=Decimal('10.00')
        )
        self.assertEqual(restock.transaction, self.transaction)
        self.assertEqual(restock.prod, self.product)
        self.assertEqual(restock.quantity, 50)
        self.assertEqual(restock.restock_price, Decimal('10.00'))
        self.assertIsNotNone(restock.restock_date)
    
    def test_restock_price_tracking(self):
        """Test that restock_price tracks purchase cost per unit."""
        restock = Restock.objects.create(
            transaction=self.transaction,
            prod=self.product,
            quantity=100,
            restock_price=Decimal('8.50')
        )
        
        # Total cost = quantity * restock_price
        total_cost = restock.quantity * restock.restock_price
        self.assertEqual(total_cost, Decimal('850.00'))
    
    def test_restock_str(self):
        """Test restock string representation."""
        restock = Restock.objects.create(
            transaction=self.transaction,
            prod=self.product,
            quantity=25,
            restock_price=Decimal('12.00')
        )
        str_repr = str(restock)
        self.assertIn('Salmon', str_repr)
        self.assertIn('25', str_repr)
        self.assertIn('12.00', str_repr)
    
    def test_restock_ordering(self):
        """Test restocks ordered by -restock_date."""
        r1 = Restock.objects.create(
            transaction=self.transaction, prod=self.product,
            quantity=50, restock_price=Decimal('10.00')
        )
        r2 = Restock.objects.create(
            transaction=self.transaction, prod=self.product,
            quantity=30, restock_price=Decimal('11.00')
        )
        
        restocks = list(Restock.objects.all())
        # Newest first
        self.assertEqual(restocks[0].id, r2.id)
        self.assertEqual(restocks[1].id, r1.id)
    
    def test_restock_transaction_relationship(self):
        """Test restock links to purchase transaction."""
        restock = Restock.objects.create(
            transaction=self.transaction,
            prod=self.product,
            quantity=50,
            restock_price=Decimal('10.00')
        )
        self.assertEqual(restock.transaction.supplier, self.supplier)
        self.assertEqual(restock.transaction.transaction_type, 'PURCHASE')
