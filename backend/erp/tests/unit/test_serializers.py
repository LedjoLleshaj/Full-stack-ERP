"""
Unit tests for serializers.

Tests serializer validation, data transformation, and custom fields.
"""

from django.test import TestCase
from erp.serializers import (
    ClientSerializer, ProductSerializer, CategorySerializer,
    SaleSerializer
)
from erp.tests.base import ErpTestCase


class ClientSerializerTests(ErpTestCase):
    """Tests for the ClientSerializer."""
    
    def test_client_serialization(self):
        """Test serializing a client."""
        serializer = ClientSerializer(instance=self.client)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Client')
        self.assertEqual(data['contact_info'], 'test@client.com')
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_client_deserialization(self):
        """Test deserializing client data."""
        data = {
            'name': 'Deserialized Client',
            'contact_info': 'deserialized@example.com'
        }
        serializer = ClientSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        client = serializer.save()
        self.assertEqual(client.name, 'Deserialized Client')


class ProductSerializerTests(ErpTestCase):
    """Tests for the ProductSerializer."""
    
    def test_product_serialization(self):
        """Test serializing a product."""
        serializer = ProductSerializer(instance=self.product)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Product')
        self.assertEqual(float(data['selling_price']), 15.00)
        self.assertIn('category', data)


# TODO: Add more serializer tests:
# - SaleSerializer tests
# - PaymentSerializer tests
# - InventorySerializer tests
# - Complex validation scenarios
# - Nested serializers
# - Custom field tests
