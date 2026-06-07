"""
API tests for client endpoints.

Tests CRUD operations on client resources.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from erp.models import Client
from erp.tests.base import ErpTestCase


class ClientAPITests(APITestCase, ErpTestCase):
    """Tests for client API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Call parent setUp to get test data
        super().setUpTestData()
        # Authenticate the test client
        self.client.force_authenticate(user=self.user)
    
    def test_list_clients(self):
        """Test listing all clients."""
        url = reverse('client-list')  # Adjust URL name as needed
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_retrieve_client(self):
        """Test retrieving a specific client."""
        url = reverse('client-detail', kwargs={'pk': self.client.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Client')
    
    def test_create_client(self):
        """Test creating a new client."""
        url = reverse('client-list')
        data = {
            'name': 'New API Client',
            'contact_info': 'newapi@client.com'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 2)  # 1 from setup + 1 new
    
    def test_update_client(self):
        """Test updating a client."""
        url = reverse('client-detail', kwargs={'pk': self.client.id})
        data = {
            'name': 'Updated Client Name',
            'contact_info': 'updated@client.com'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.refresh_from_db()
        self.assertEqual(self.client.name, 'Updated Client Name')
    
    def test_delete_client(self):
        """Test deleting a client."""
        url = reverse('client-detail', kwargs={'pk': self.client.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Client.objects.count(), 0)


# TODO: Add more client API tests:
# - Filtering tests
# - Pagination tests
# - Search tests
# - Permission tests (unauthenticated access)
