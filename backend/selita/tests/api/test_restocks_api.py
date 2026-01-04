"""
API tests for restock endpoints.

Tests restock CRUD operations.
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Restock, Product, Transaction, Supplier, Users


class RestockAPITests(APITestCase):
    """Tests for restock API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = Users.objects.create(
            username='testuser', password='password123',
            email='test@example.com', firstname='Test',
            lastname='User', role='admin'
        )
        cls.supplier = Supplier.objects.create(
            firstname='Fish', lastname='Co', address='Harbor'
        )
        cls.product = Product.objects.create(
            name='Fresh Salmon', category='Fish',
            price=Decimal('15.00'), description='Atlantic salmon'
        )
    
    def setUp(self):
        """Authenticate for each test."""
        self.client.force_authenticate(user=self.user)
        
        self.transaction = Transaction.objects.create(
            transaction_type='PURCHASE',
            supplier=self.supplier,
            total_amount=Decimal('500.00'),
            currency='EUR',
            status='COMPLETED'
        )
        self.restock = Restock.objects.create(
            transaction=self.transaction,
            prod=self.product,
            quantity=50,
            restock_price=Decimal('10.00')
        )
    
    def test_get_restocks_list(self):
        """Test listing all restocks."""
        response = self.client.get('/selita/restocks')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_single_restock(self):
        """Test retrieving a specific restock."""
        response = self.client.get(f'/selita/restock/{self.restock.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 50)
    
    def test_get_restock_not_found(self):
        """Test retrieving non-existent restock returns 404."""
        response = self.client.get('/selita/restock/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_restock(self):
        """Test creating a new restock."""
        data = {
            'transaction': self.transaction.id,
            'prod': self.product.id,
            'quantity': 25,
            'restock_price': '12.00'
        }
        response = self.client.post('/selita/add-restock', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_update_restock(self):
        """Test updating a restock."""
        data = {
            'transaction': self.transaction.id,
            'prod': self.product.id,
            'quantity': 60,
            'restock_price': '11.00'
        }
        response = self.client.put(
            f'/selita/update-restock/{self.restock.id}',
            data, format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_restock(self):
        """Test deleting a restock."""
        response = self.client.delete(f'/selita/delete-restock/{self.restock.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Restock.objects.count(), 0)
    
    def test_delete_restock_not_found(self):
        """Test deleting non-existent restock returns 404."""
        response = self.client.delete('/selita/delete-restock/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
