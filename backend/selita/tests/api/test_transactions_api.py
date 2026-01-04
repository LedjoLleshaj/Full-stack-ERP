"""
API tests for transaction endpoints.

Tests transaction CRUD operations and payment queries.
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Transaction, Client, Supplier, Users


class TransactionAPITests(APITestCase):
    """Tests for transaction API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.user = Users.objects.create(
            username='testuser', password='password123',
            email='test@example.com', firstname='Test',
            lastname='User', role='admin'
        )
        cls.db_client = Client.objects.create(
            firstname='John', lastname='Doe',
            phone='+355 69 111 2222',
            address='123 Main St', city='Tirana'
        )
        cls.supplier = Supplier.objects.create(
            firstname='Fish', lastname='Co', address='Harbor'
        )
    
    def setUp(self):
        """Authenticate for each test."""
        self.client.force_authenticate(user=self.user)
        
        self.transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=self.db_client,
            total_amount=Decimal('150.00'),
            currency='EUR',
            status='PENDING'
        )
    
    def test_get_transactions_list(self):
        """Test listing all transactions."""
        response = self.client.get('/selita/transactions')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_single_transaction(self):
        """Test retrieving a specific transaction."""
        response = self.client.get(f'/selita/transaction/{self.transaction.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction_type'], 'SALE')
    
    def test_get_transaction_not_found(self):
        """Test retrieving non-existent transaction returns 404."""
        response = self.client.get('/selita/transaction/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_transaction_payments(self):
        """Test getting payments for a transaction."""
        response = self.client.get(f'/selita/transaction-payments/{self.transaction.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_add_transaction(self):
        """Test creating a new transaction."""
        data = {
            'transaction_type': 'SALE',
            'client': self.db_client.id,
            'total_amount': '200.00',
            'currency': 'EUR',
            'status': 'PENDING'
        }
        response = self.client.post('/selita/add-transaction', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_update_transaction(self):
        """Test updating a transaction."""
        data = {
            'transaction_type': 'SALE',
            'client': self.db_client.id,
            'total_amount': '175.00',
            'currency': 'EUR',
            'status': 'PARTIAL'
        }
        response = self.client.put(
            f'/selita/update-transaction/{self.transaction.id}',
            data, format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_transaction(self):
        """Test deleting a transaction."""
        response = self.client.delete(f'/selita/delete-transaction/{self.transaction.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transaction.objects.count(), 0)
    
    def test_delete_transaction_not_found(self):
        """Test deleting non-existent transaction returns 404."""
        response = self.client.delete('/selita/delete-transaction/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
