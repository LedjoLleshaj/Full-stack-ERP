"""
Unit tests for ProductSerializer.
"""
from decimal import Decimal
from django.test import TestCase
from selita.serializers import ProductSerializer
from selita.models import Product


class ProductSerializerTests(TestCase):
    """Tests for ProductSerializer."""
    
    def test_product_serialization(self):
        """Test serializing a product instance."""
        product = Product.objects.create(
            name='Fresh Salmon', category='Fish',
            price=Decimal('15.00'), description='Atlantic salmon'
        )
        serializer = ProductSerializer(instance=product)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Fresh Salmon')
        self.assertEqual(data['category'], 'Fish')
        self.assertEqual(Decimal(data['price']), Decimal('15.00'))
    
    def test_product_deserialization_valid(self):
        """Test deserializing valid product data."""
        data = {
            'name': 'Tuna',
            'category': 'Fish',
            'price': '18.50',
            'description': 'Fresh tuna'
        }
        serializer = ProductSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.name, 'Tuna')
        self.assertEqual(product.price, Decimal('18.50'))
