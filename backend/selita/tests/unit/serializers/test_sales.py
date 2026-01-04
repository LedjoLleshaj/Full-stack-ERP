"""
Unit tests for SalesSerializer.
"""
from decimal import Decimal
from django.test import TestCase
from selita.serializers import SalesSerializer
from selita.models import Sales, Transaction, Product, Users, Client


class SalesSerializerTests(TestCase):
    """Tests for SalesSerializer."""
    
    @classmethod
    def setUpTestData(cls):
        cls.db_client = Client.objects.create(
            firstname='Test', lastname='Client',
            phone='+355 69 456', address='Addr', city='City'
        )
        cls.product = Product.objects.create(
            name='Test Fish', category='Fish',
            price=Decimal('15.00'), description='Fresh'
        )
        cls.user = Users.objects.create(
            username='seller', password='pass',
            email='seller@test.com', firstname='Seller',
            lastname='User', role='user'
        )
        cls.transaction = Transaction.objects.create(
            transaction_type='SALE', client=cls.db_client,
            total_amount=Decimal('150.00'), currency='EUR'
        )
    
    def test_sales_serialization(self):
        """Test serializing a sales instance."""
        sale = Sales.objects.create(
            transaction=self.transaction,
            prod=self.product,
            prod_price=Decimal('15.00'),
            user=self.user,
            quantity=10
        )
        serializer = SalesSerializer(instance=sale)
        data = serializer.data
        
        self.assertEqual(data['quantity'], 10)
        self.assertEqual(Decimal(data['prod_price']), Decimal('15.00'))
        self.assertIn('sale_date', data)
    
    def test_sales_sale_date_read_only(self):
        """Test that sale_date is read-only."""
        data = {
            'transaction': self.transaction.id,
            'prod': self.product.id,
            'prod_price': '15.00',
            'user': self.user.id,
            'quantity': 5,
            'sale_date': '2020-01-01T00:00:00Z'
        }
        serializer = SalesSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        sale = serializer.save()
        self.assertNotEqual(sale.sale_date.year, 2020)
