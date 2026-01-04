"""
Unit tests for InventorySerializer.
"""
from decimal import Decimal
from django.test import TestCase
from selita.serializers import InventorySerializer
from selita.models import Inventory, Product


class InventorySerializerTests(TestCase):
    """Tests for InventorySerializer."""
    
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            name='Salmon', category='Fish',
            price=Decimal('18.00'), description='Atlantic'
        )
    
    def test_inventory_serialization(self):
        """Test serializing an inventory instance."""
        inventory = Inventory.objects.create(
            prod=self.product,
            quantity=100
        )
        serializer = InventorySerializer(instance=inventory)
        data = serializer.data
        
        self.assertEqual(data['quantity'], 100)
        self.assertIn('restock_date', data)
    
    def test_inventory_restock_date_read_only(self):
        """Test that restock_date is read-only."""
        data = {
            'prod': self.product.id,
            'quantity': 50,
            'restock_date': '2020-01-01T00:00:00Z'
        }
        serializer = InventorySerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        inventory = serializer.save()
        self.assertNotEqual(inventory.restock_date.year, 2020)
