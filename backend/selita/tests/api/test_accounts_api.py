"""
API tests for account endpoints.

Tests CRUD operations on account resources.
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Account, Users


class AccountAPITests(APITestCase):
    """Tests for account API endpoints."""
    
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
        
        self.account = Account.objects.create(
            account_name='Cash EUR',
            account_type='CASH',
            currency='EUR',
            current_balance=Decimal('1000.00')
        )
    
    def test_get_accounts_list(self):
        """Test listing all accounts."""
        response = self.client.get('/selita/accounts')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
    
    def test_get_single_account(self):
        """Test retrieving a specific account."""
        response = self.client.get(f'/selita/account/{self.account.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account_name'], 'Cash EUR')
    
    def test_get_account_not_found(self):
        """Test retrieving non-existent account returns 404."""
        response = self.client.get('/selita/account/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_account(self):
        """Test creating a new account."""
        data = {
            'account_name': 'Bank USD',
            'account_type': 'BANK',
            'currency': 'USD',
            'current_balance': '5000.00'
        }
        response = self.client.post('/selita/add-account', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(Account.objects.count(), 2)
    
    def test_update_account(self):
        """Test updating an account."""
        data = {
            'account_name': 'Updated Account',
            'account_type': 'CASH',
            'currency': 'EUR',
            'current_balance': '2000.00'
        }
        response = self.client.put(
            f'/selita/update-account/{self.account.id}',
            data, format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_account(self):
        """Test deleting an account."""
        response = self.client.delete(f'/selita/delete-account/{self.account.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Account.objects.count(), 0)
    
    def test_delete_account_not_found(self):
        """Test deleting non-existent account returns 404."""
        response = self.client.delete('/selita/delete-account/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
