"""
API tests for account transaction endpoints.

Tests account transaction CRUD operations (deposits, withdrawals, transfers).
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import AccountTransaction, Account, Users


class AccountTransactionAPITests(APITestCase):
    """Tests for account transaction API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = Users.objects.create(
            username='testuser', password='password123',
            email='test@example.com', firstname='Test',
            lastname='User', role='admin'
        )
        cls.account = Account.objects.create(
            account_name='Cash EUR', account_type='CASH',
            currency='EUR', current_balance=Decimal('1000.00')
        )
    
    def setUp(self):
        """Authenticate for each test."""
        self.client.force_authenticate(user=self.user)
        
        self.acct_trans = AccountTransaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('100.00'),
            balance_after=Decimal('1100.00')
        )
    
    def test_get_account_transactions_list(self):
        """Test listing all account transactions."""
        response = self.client.get('/selita/account-transactions')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_single_account_transaction(self):
        """Test retrieving a specific account transaction."""
        response = self.client.get(f'/selita/account-transaction/{self.acct_trans.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction_type'], 'DEPOSIT')
    
    def test_get_account_transaction_not_found(self):
        """Test retrieving non-existent account transaction returns 404."""
        response = self.client.get('/selita/account-transaction/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_transactions_by_account(self):
        """Test getting transactions for a specific account."""
        response = self.client.get(f'/selita/account-transactions/account/{self.account.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('transactions', response.data)
    
    def test_add_account_transaction(self):
        """Test creating a new account transaction."""
        data = {
            'account': self.account.id,
            'transaction_type': 'WITHDRAWAL',
            'amount': '50.00',
            'balance_after': '1050.00'
        }
        response = self.client.post('/selita/add-account-transaction', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_delete_account_transaction(self):
        """Test deleting an account transaction."""
        response = self.client.delete(f'/selita/delete-account-transaction/{self.acct_trans.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AccountTransaction.objects.count(), 0)
    
    def test_delete_account_transaction_not_found(self):
        """Test deleting non-existent account transaction returns 404."""
        response = self.client.delete('/selita/delete-account-transaction/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
