"""
Base test utilities and fixtures for the ERP test suite.

Provides common test utilities, fixtures, and helper functions.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from erp.models import (
    Client, Product, Category, Supplier, Account,
    Sale, Payment, Inventory, Restock
)

User = get_user_model()


class ErpTestCase(TestCase):
    """Base test case with common setup and utilities."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for the entire test case."""
        # Create a test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a test account
        cls.account = Account.objects.create(
            name='Test Account',
            balance=1000.00
        )
        
        # Create a test category
        cls.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create a test supplier
        cls.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_info='test@supplier.com'
        )
        
        # Create a test product
        cls.product = Product.objects.create(
            name='Test Product',
            category=cls.category,
            buying_price=10.00,
            selling_price=15.00,
            unit='kg'
        )
        
        # Create a test client
        cls.client = Client.objects.create(
            name='Test Client',
            contact_info='test@client.com'
        )
    
    def create_inventory(self, product=None, quantity=100):
        """Helper to create inventory."""
        if product is None:
            product = self.product
        
        return Inventory.objects.create(
            product=product,
            quantity=quantity,
            last_restocked=None
        )
    
    def create_sale(self, client=None, product=None, quantity=10):
        """Helper to create a sale."""
        if client is None:
            client = self.client
        if product is None:
            product = self.product
        
        return Sale.objects.create(
            client=client,
            product=product,
            quantity=quantity,
            unit_price=product.selling_price,
            total_price=quantity * product.selling_price
        )
