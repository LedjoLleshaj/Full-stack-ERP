"""
API tests for product endpoints.

Tests CRUD operations on product resources.
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Product, Users, Inventory


class ProductAPITests(APITestCase):
    """Tests for product API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = Users.objects.create(
            username='testuser', password='password123',
            email='test@example.com', firstname='Test',
            lastname='User', role='admin'
        )
    
    def setUp(self):
        """Authenticate for each test."""
        self.client.force_authenticate(user=self.user)
        
        self.product = Product.objects.create(
            name='Fresh Salmon',
            category='Fish',
            price=Decimal('15.00'),
            description='Atlantic salmon'
        )
    
    def test_get_products_list(self):
        """Test listing all products."""
        response = self.client.get('/selita/products')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
    
    def test_get_single_product(self):
        """Test retrieving a specific product."""
        response = self.client.get(f'/selita/product/{self.product.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Fresh Salmon')
    
    def test_get_product_not_found(self):
        """Test retrieving non-existent product returns 404."""
        response = self.client.get('/selita/product/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_product(self):
        """Test creating a new product."""
        data = {
            'name': 'Fresh Tuna',
            'category': 'Fish',
            'price': '18.50',
            'description': 'Bluefin tuna'
        }
        response = self.client.post('/selita/add-product', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('product_id', response.data)
        self.assertEqual(response.data['message'], 'Product added successfully!')
        self.assertEqual(Product.objects.count(), 2)
    
    def test_update_price(self):
        """Test updating a product's price."""
        # ProductSerializer requires all fields for update
        data = {
            'name': 'Fresh Salmon',
            'category': 'Fish',
            'price': '20.00',
            'description': 'Atlantic salmon'
        }
        response = self.client.put(
            f'/selita/update-price/{self.product.id}',
            data, format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, Decimal('20.00'))
    
    def test_get_product_categories(self):
        """Test getting product categories."""
        response = self.client.get('/selita/product-categories')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_product_names(self):
        """Test getting product names."""
        response = self.client.get('/selita/product-names')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_products_by_category(self):
        """Test getting products by category."""
        response = self.client.get('/selita/productbycategory/Fish')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_product_by_name(self):
        """Test getting product by name."""
        response = self.client.get('/selita/productbyname/Fresh Salmon')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_check_disponibility(self):
        """Test checking product availability."""
        # Create inventory for product
        Inventory.objects.create(prod=self.product, quantity=100)
        
        response = self.client.get(f'/selita/checkdisponibility/{self.product.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
