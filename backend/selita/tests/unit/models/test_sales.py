"""
Unit tests for Sales model.
"""

from decimal import Decimal
from django.test import TestCase
from selita.models import Sales, Transaction, Product, Users, Client


class SalesModelTests(TestCase):
    """Tests for the Sales model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.db_client = Client.objects.create(
            firstname='Test', lastname='Client',
            phone='+355 69 123', address='Address', city='Tirana'
        )
        cls.product = Product.objects.create(
            name='Fresh Fish', category='Fish',
            price=Decimal('15.00'), description='Fresh catch'
        )
        cls.user = Users.objects.create(
            username='seller', password='pass123',
            email='seller@test.com', firstname='Seller',
            lastname='User', role='user'
        )
        cls.transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=cls.db_client,
            total_amount=Decimal('150.00'),
            currency='EUR'
        )
    
    def test_sale_creation(self):
        """Test creating a sale."""
        sale = Sales.objects.create(
            transaction=self.transaction,
            prod=self.product,
            prod_price=Decimal('15.00'),
            user=self.user,
            quantity=10
        )
        self.assertEqual(sale.transaction, self.transaction)
        self.assertEqual(sale.prod, self.product)
        self.assertEqual(sale.prod_price, Decimal('15.00'))
        self.assertEqual(sale.quantity, 10)
        self.assertIsNotNone(sale.sale_date)
    
    def test_sale_product_price_at_time(self):
        """Test that prod_price stores the price at time of sale."""
        # Create sale at current price
        sale = Sales.objects.create(
            transaction=self.transaction,
            prod=self.product,
            prod_price=Decimal('15.00'),
            user=self.user,
            quantity=5
        )
        
        # Update product price
        self.product.price = Decimal('20.00')
        self.product.save()
        
        # Sale should still have old price
        sale.refresh_from_db()
        self.assertEqual(sale.prod_price, Decimal('15.00'))
    
    def test_sale_str(self):
        """Test sale string representation."""
        sale = Sales.objects.create(
            transaction=self.transaction,
            prod=self.product,
            prod_price=Decimal('15.00'),
            user=self.user,
            quantity=5
        )
        str_repr = str(sale)
        self.assertIn('Fresh Fish', str_repr)
        self.assertIn('5', str_repr)
    
    def test_sale_ordering(self):
        """Test sales ordered by -sale_date."""
        s1 = Sales.objects.create(
            transaction=self.transaction, prod=self.product,
            prod_price=Decimal('15.00'), user=self.user, quantity=5
        )
        s2 = Sales.objects.create(
            transaction=self.transaction, prod=self.product,
            prod_price=Decimal('15.00'), user=self.user, quantity=3
        )
        
        sales = list(Sales.objects.all())
        # Newest first
        self.assertEqual(sales[0].id, s2.id)
        self.assertEqual(sales[1].id, s1.id)
    
    def test_sale_transaction_relationship(self):
        """Test sale links to transaction correctly."""
        sale = Sales.objects.create(
            transaction=self.transaction,
            prod=self.product,
            prod_price=Decimal('15.00'),
            user=self.user,
            quantity=10
        )
        self.assertEqual(sale.transaction.client, self.db_client)
        self.assertEqual(sale.transaction.total_amount, Decimal('150.00'))
