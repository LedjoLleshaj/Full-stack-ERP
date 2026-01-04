"""
API tests for supplier endpoints.

Tests CRUD operations on supplier resources.
"""

from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Supplier, Users


class SupplierAPITests(APITestCase):
    """Tests for supplier API endpoints."""
    
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
        
        self.supplier = Supplier.objects.create(
            firstname='Fish', lastname='Supplier',
            phone='+355 69 111 2222',
            email='fish@supplier.com',
            address='Harbor 1, Durres'
        )
    
    def test_get_suppliers_list(self):
        """Test listing all suppliers."""
        response = self.client.get('/selita/suppliers')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
    
    def test_get_single_supplier(self):
        """Test retrieving a specific supplier."""
        response = self.client.get(f'/selita/supplier/{self.supplier.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['firstname'], 'Fish')
    
    def test_get_supplier_not_found(self):
        """Test retrieving non-existent supplier returns 404."""
        response = self.client.get('/selita/supplier/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_supplier(self):
        """Test creating a new supplier."""
        data = {
            'firstname': 'Sea',
            'lastname': 'Foods',
            'phone': '+355 69 333 4444',
            'email': 'sea@foods.com',
            'address': 'Pier 5, Vlore'
        }
        response = self.client.post('/selita/add-supplier', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['firstname'], 'Sea')
        self.assertEqual(Supplier.objects.count(), 2)
    
    def test_update_supplier(self):
        """Test updating a supplier."""
        data = {
            'firstname': 'Updated',
            'lastname': 'Supplier',
            'phone': '+355 69 999 8888',
            'email': 'updated@supplier.com',
            'address': 'New Address'
        }
        response = self.client.put(
            f'/selita/update-supplier/{self.supplier.id}',
            data, format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['firstname'], 'Updated')
    
    def test_update_supplier_not_found(self):
        """Test updating non-existent supplier returns 404."""
        data = {
            'firstname': 'Test', 'lastname': 'Update',
            'phone': '123', 'email': '', 'address': 'Addr'
        }
        response = self.client.put('/selita/update-supplier/99999', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_supplier(self):
        """Test deleting a supplier."""
        response = self.client.delete(f'/selita/delete-supplier/{self.supplier.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Supplier.objects.count(), 0)
    
    def test_delete_supplier_not_found(self):
        """Test deleting non-existent supplier returns 404."""
        response = self.client.delete('/selita/delete-supplier/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
