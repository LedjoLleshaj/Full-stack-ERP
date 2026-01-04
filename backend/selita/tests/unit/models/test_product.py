"""
Unit tests for Product model.
"""

from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from selita.models import Product


class ProductModelTests(TestCase):
    """Tests for the Product model."""
    
    def test_product_creation(self):
        """Test creating a product with all fields."""
        product = Product.objects.create(
            name='Salmon Fresh',
            category='Fish',
            price=Decimal('12.50'),
            description='Fresh Atlantic salmon'
        )
        self.assertEqual(product.name, 'Salmon Fresh')
        self.assertEqual(product.category, 'Fish')
        self.assertEqual(product.price, Decimal('12.50'))
        self.assertEqual(product.description, 'Fresh Atlantic salmon')
    
    def test_product_unique_name(self):
        """Test that product name must be unique."""
        Product.objects.create(
            name='Tuna', category='Fish',
            price=Decimal('15.00'), description='Fresh tuna'
        )
        
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                name='Tuna', category='Seafood',  # Same name
                price=Decimal('18.00'), description='Another tuna'
            )
    
    def test_product_str(self):
        """Test product string representation."""
        product = Product.objects.create(
            name='Shrimp', category='Seafood',
            price=Decimal('20.00'), description='Large shrimp'
        )
        self.assertEqual(str(product), 'Shrimp')
    
    def test_product_price_precision(self):
        """Test price supports 2 decimal places."""
        product = Product.objects.create(
            name='Cod', category='Fish',
            price=Decimal('8.99'), description='Fresh cod'
        )
        product.refresh_from_db()
        self.assertEqual(product.price, Decimal('8.99'))
    
    def test_product_ordering(self):
        """Test products ordered by category, name."""
        Product.objects.create(name='Zander', category='Fish', price=Decimal('10'), description='')
        Product.objects.create(name='Anchovy', category='Fish', price=Decimal('5'), description='')
        Product.objects.create(name='Lobster', category='Seafood', price=Decimal('50'), description='')
        
        products = list(Product.objects.all())
        # Fish category first (alphabetically before Seafood)
        self.assertEqual(products[0].name, 'Anchovy')
        self.assertEqual(products[1].name, 'Zander')
        self.assertEqual(products[2].category, 'Seafood')
    
    def test_product_update(self):
        """Test updating a product's fields."""
        product = Product.objects.create(
            name='Bass', category='Fish',
            price=Decimal('15.00'), description='Sea bass'
        )
        
        product.price = Decimal('18.00')
        product.description = 'Premium sea bass'
        product.save()
        product.refresh_from_db()
        
        self.assertEqual(product.price, Decimal('18.00'))
        self.assertEqual(product.description, 'Premium sea bass')
