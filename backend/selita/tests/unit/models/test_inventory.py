"""
Unit tests for Inventory model.
"""

from django.test import TestCase
from decimal import Decimal
from selita.models import Inventory, Product


class InventoryModelTests(TestCase):
    """Tests for the Inventory model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.product = Product.objects.create(
            name='Test Fish', category='Fish',
            price=Decimal('10.00'), description='Test product'
        )
    
    def test_inventory_creation(self):
        """Test creating an inventory item."""
        inventory = Inventory.objects.create(
            prod=self.product,
            quantity=100
        )
        self.assertEqual(inventory.prod, self.product)
        self.assertEqual(inventory.quantity, 100)
        self.assertIsNotNone(inventory.restock_date)
    
    def test_inventory_product_relationship(self):
        """Test inventory links to product correctly."""
        inventory = Inventory.objects.create(
            prod=self.product,
            quantity=50
        )
        self.assertEqual(inventory.prod.name, 'Test Fish')
        self.assertEqual(inventory.prod.category, 'Fish')
    
    def test_inventory_quantity_update(self):
        """Test updating inventory quantity."""
        inventory = Inventory.objects.create(
            prod=self.product,
            quantity=100
        )
        
        inventory.quantity = 75
        inventory.save()
        inventory.refresh_from_db()
        
        self.assertEqual(inventory.quantity, 75)
    
    def test_inventory_str(self):
        """Test inventory string representation."""
        inventory = Inventory.objects.create(
            prod=self.product,
            quantity=100
        )
        str_repr = str(inventory)
        self.assertIn('Test Fish', str_repr)
        self.assertIn('100', str_repr)
    
    def test_inventory_ordering(self):
        """Test inventory ordered by -restock_date."""
        product2 = Product.objects.create(
            name='Another Fish', category='Fish',
            price=Decimal('12.00'), description=''
        )
        
        i1 = Inventory.objects.create(prod=self.product, quantity=100)
        i2 = Inventory.objects.create(prod=product2, quantity=50)
        
        inventories = list(Inventory.objects.all())
        # Newest first
        self.assertEqual(inventories[0].id, i2.id)
        self.assertEqual(inventories[1].id, i1.id)
