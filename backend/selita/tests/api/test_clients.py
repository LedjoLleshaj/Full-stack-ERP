"""
API tests for client endpoints.

Tests CRUD operations on client resources.
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Client, Users


class ClientAPITests(APITestCase):
    """Tests for client API endpoints."""
    
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
        
        # Create a test client
        self.test_client = Client.objects.create(
            firstname='John', lastname='Doe',
            phone='+355 69 111 2222',
            email='john@example.com',
            address='123 Main St', city='Tirana'
        )
    
    def test_get_clients_list(self):
        """Test listing all clients."""
        response = self.client.get('/selita/clients')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['firstname'], 'John')
    
    def test_get_clients_includes_unpaid_balance(self):
        """Test that client list includes unpaidBalance field."""
        response = self.client.get('/selita/clients')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unpaidBalance', response.data[0])
    
    def test_get_single_client(self):
        """Test retrieving a specific client."""
        response = self.client.get(f'/selita/client/{self.test_client.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['firstname'], 'John')
        self.assertEqual(response.data['lastname'], 'Doe')
        self.assertIn('unpaidBalance', response.data)
        self.assertIn('totalBought', response.data)
    
    def test_get_client_not_found(self):
        """Test retrieving non-existent client returns 404."""
        response = self.client.get('/selita/client/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_client(self):
        """Test creating a new client."""
        data = {
            'firstname': 'Jane',
            'lastname': 'Smith',
            'phone': '+355 69 333 4444',
            'email': 'jane@example.com',
            'address': '456 Oak Ave',
            'city': 'Durres'
        }
        response = self.client.post('/selita/add-client', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['firstname'], 'Jane')
        self.assertEqual(Client.objects.count(), 2)
    
    def test_add_client_without_email(self):
        """Test creating client without optional email."""
        data = {
            'firstname': 'No',
            'lastname': 'Email',
            'phone': '+355 69 555 6666',
            'address': '789 Pine Rd',
            'city': 'Vlore'
        }
        response = self.client.post('/selita/add-client', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['email'])
    
    def test_add_client_missing_required_fields(self):
        """Test creating client with missing fields returns error."""
        data = {'firstname': 'Incomplete'}
        response = self.client.post('/selita/add-client', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def test_update_client(self):
        """Test updating a client."""
        data = {
            'firstname': 'Johnny',
            'lastname': 'Updated',
            'phone': '+355 69 999 8888',
            'email': 'johnny@example.com',
            'address': 'New Address',
            'city': 'Shkoder'
        }
        response = self.client.post(
            f'/selita/update-client/{self.test_client.id}', 
            data, format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['firstname'], 'Johnny')
        
        # Verify in database
        self.test_client.refresh_from_db()
        self.assertEqual(self.test_client.city, 'Shkoder')
    
    def test_update_client_not_found(self):
        """Test updating non-existent client returns 404."""
        data = {
            'firstname': 'Test', 'lastname': 'Update',
            'phone': '123', 'email': '', 'address': 'Addr', 'city': 'City'
        }
        response = self.client.post('/selita/update-client/99999', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_client(self):
        """Test deleting a client."""
        response = self.client.delete(f'/selita/delete-client/{self.test_client.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Client.objects.count(), 0)
    
    def test_delete_client_not_found(self):
        """Test deleting non-existent client returns 404."""
        response = self.client.delete('/selita/delete-client/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_client_sales(self):
        """Test getting sales for a client."""
        response = self.client.get(f'/selita/client-sales/{self.test_client.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_client_sales_not_found(self):
        """Test getting sales for non-existent client returns 404."""
        response = self.client.get('/selita/client-sales/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ClientAPIUnauthenticatedTests(APITestCase):
    """Tests for client API without authentication."""
    
    def test_get_clients_requires_auth(self):
        """Test that listing clients requires authentication."""
        response = self.client.get('/selita/clients')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_add_client_allows_any(self):
        """Test that adding client works without auth (based on current API)."""
        data = {
            'firstname': 'New', 'lastname': 'Client',
            'phone': '+355 69 000 0000',
            'address': 'Test Address', 'city': 'Test City'
        }
        response = self.client.post('/selita/add-client', data, format='json')
        
        # addClient is currently @permission_classes commented out (AllowAny)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
