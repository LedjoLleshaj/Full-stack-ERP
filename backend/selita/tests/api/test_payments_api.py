"""
API tests for payment endpoints.

Tests payment CRUD operations.
"""

from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from selita.models import Payment, Transaction, Account, Client, Users


class PaymentAPITests(APITestCase):
    """Tests for payment API endpoints."""
    
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
        cls.account = Account.objects.create(
            account_name='Cash EUR', account_type='CASH',
            currency='EUR', current_balance=Decimal('1000.00')
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
        self.payment = Payment.objects.create(
            transaction=self.transaction,
            account=self.account,
            amount=Decimal('50.00'),
            currency='EUR',
            payment_method='CASH'
        )
    
    def test_get_payments_list(self):
        """Test listing all payments."""
        response = self.client.get('/selita/payments')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_single_payment(self):
        """Test retrieving a specific payment."""
        response = self.client.get(f'/selita/payment/{self.payment.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['amount']), Decimal('50.00'))
    
    def test_get_payment_not_found(self):
        """Test retrieving non-existent payment returns 404."""
        response = self.client.get('/selita/payment/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_payment(self):
        """Test creating a new payment."""
        data = {
            'transaction': self.transaction.id,
            'account': self.account.id,
            'amount': '75.00',
            'currency': 'EUR',
            'payment_method': 'CASH'
        }
        response = self.client.post('/selita/add-payment', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_update_payment(self):
        """Test updating a payment."""
        data = {
            'transaction': self.transaction.id,
            'account': self.account.id,
            'amount': '60.00',
            'currency': 'EUR',
            'payment_method': 'CARD'
        }
        response = self.client.put(
            f'/selita/update-payment/{self.payment.id}',
            data, format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_payment(self):
        """Test deleting a payment."""
        response = self.client.delete(f'/selita/delete-payment/{self.payment.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Payment.objects.count(), 0)
    
    def test_delete_payment_not_found(self):
        """Test deleting non-existent payment returns 404."""
        response = self.client.delete('/selita/delete-payment/99999')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
