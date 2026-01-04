"""
Unit tests for RestockSerializer.
"""
from decimal import Decimal
from django.test import TestCase
from selita.serializers import RestockSerializer
from selita.models import Restock, Transaction, Product, Supplier


class RestockSerializerTests(TestCase):
    """Tests for RestockSerializer."""
    
    @classmethod
    def setUpTestData(cls):
        cls.supplier = Supplier.objects.create(
            firstname='Fish', lastname='Co', address='Harbor'
        )
        cls.product = Product.objects.create(
            name='Tuna', category='Fish',
            price=Decimal('20.00'), description='Fresh'
        )
        cls.transaction = Transaction.objects.create(
            transaction_type='PURCHASE', supplier=cls.supplier,
            total_amount=Decimal('500.00'), currency='EUR',
            status='COMPLETED'
        )
    
    def test_restock_serialization(self):
        """Test serializing a restock instance."""
        restock = Restock.objects.create(
            transaction=self.transaction,
            prod=self.product,
            quantity=50,
            restock_price=Decimal('10.00')
        )
        serializer = RestockSerializer(instance=restock)
        data = serializer.data
        
        self.assertEqual(data['quantity'], 50)
        self.assertEqual(Decimal(data['restock_price']), Decimal('10.00'))
        self.assertIn('restock_date', data)
    
    def test_restock_restock_date_read_only(self):
        """Test that restock_date is read-only."""
        data = {
            'transaction': self.transaction.id,
            'prod': self.product.id,
            'quantity': 25,
            'restock_price': '12.00',
            'restock_date': '2020-01-01T00:00:00Z'
        }
        serializer = RestockSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        restock = serializer.save()
        self.assertNotEqual(restock.restock_date.year, 2020)
