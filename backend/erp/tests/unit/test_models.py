"""
Unit tests for models.

Tests model creation, validation, methods, and properties.
"""

from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from erp.models import Client, Product, Category, Sale, Inventory
from erp.tests.base import ErpTestCase


class ClientModelTests(ErpTestCase):
    """Tests for the Client model."""
    
    def test_client_creation(self):
        """Test creating a client."""
        client = Client.objects.create(
            name='New Client',
            contact_info='newclient@example.com'
        )
        self.assertEqual(client.name, 'New Client')
        self.assertEqual(client.contact_info, 'newclient@example.com')
        self.assertIsNotNone(client.created_at)
    
    def test_client_str(self):
        """Test client string representation."""
        self.assertEqual(str(self.client), 'Test Client')


class ProductModelTests(ErpTestCase):
    """Tests for the Product model."""
    
    def test_product_creation(self):
        """Test creating a product."""
        product = Product.objects.create(
            name='New Product',
            category=self.category,
            buying_price=Decimal('20.00'),
            selling_price=Decimal('30.00'),
            unit='piece'
        )
        self.assertEqual(product.name, 'New Product')
        self.assertEqual(product.buying_price, Decimal('20.00'))
        self.assertEqual(product.selling_price, Decimal('30.00'))
    
    def test_product_str(self):
        """Test product string representation."""
        self.assertEqual(str(self.product), 'Test Product')


class CategoryModelTests(ErpTestCase):
    """Tests for the Category model."""
    
    def test_category_creation(self):
        """Test creating a category."""
        category = Category.objects.create(
            name='New Category',
            description='New category description'
        )
        self.assertEqual(category.name, 'New Category')
        self.assertEqual(category.description, 'New category description')
    
    def test_category_str(self):
        """Test category string representation."""
        self.assertEqual(str(self.category), 'Test Category')


class SaleModelTests(ErpTestCase):
    """Tests for the Sale model."""
    
    def test_sale_creation(self):
        """Test creating a sale."""
        sale = self.create_sale(quantity=5)
        self.assertEqual(sale.quantity, 5)
        self.assertEqual(sale.total_price, Decimal('75.00'))  # 5 * 15.00
    
    def test_sale_str(self):
        """Test sale string representation."""
        sale = self.create_sale()
        expected = f'Sale #{sale.id} - Test Client - Test Product'
        self.assertEqual(str(sale), expected)


class InventoryModelTests(ErpTestCase):
    """Tests for the Inventory model."""
    
    def test_inventory_creation(self):
        """Test creating inventory."""
        inventory = self.create_inventory(quantity=50)
        self.assertEqual(inventory.quantity, 50)
        self.assertEqual(inventory.product, self.product)
    
    def test_inventory_str(self):
        """Test inventory string representation."""
        inventory = self.create_inventory()
        expected = f'Test Product - 100 kg'
        self.assertEqual(str(inventory), expected)


# TODO: Add more model tests:
# - Payment model tests
# - Transaction model tests
# - Restock model tests
# - Account model tests
# - Supplier model tests
# - User model tests
