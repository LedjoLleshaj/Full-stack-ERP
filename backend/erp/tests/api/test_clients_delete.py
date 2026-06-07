
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from erp.models import Client, Transaction
from erp.constants import TransactionStatus, TransactionType, Currency

User = get_user_model()

class ClientDeletionTests(APITestCase):
    """Tests for client deletion restrictions."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.url = lambda pk: f'/erp/delete-client/{pk}'

    def test_delete_client_no_transactions(self):
        """Test deleting a client with no transactions."""
        # Create a fresh client with no transactions
        client = Client.objects.create(
            firstname="No",
            lastname="Transaction",
            phone="1234567890",
            address="Test Address",
            city="Test City"
        )
        
        response = self.client.delete(self.url(client.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify soft delete
        client.refresh_from_db()
        self.assertFalse(client.is_active)

    def test_delete_client_with_paid_transactions(self):
        """Test deleting a client with only paid transactions."""
        client = Client.objects.create(
            firstname="Paid",
            lastname="Client",
            phone="0987654321",
            address="Test Address",
            city="Test City"
        )
        
        # Create a completed transaction
        Transaction.objects.create(
            client=client,
            transaction_type=TransactionType.SALE,
            total_amount=100.00,
            currency=Currency.EUR,
            status=TransactionStatus.COMPLETED
        )
        
        response = self.client.delete(self.url(client.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        client.refresh_from_db()
        self.assertFalse(client.is_active)

    def test_delete_client_with_unpaid_transactions(self):
        """Test deleting a client with unpaid transactions should fail."""
        client = Client.objects.create(
            firstname="Unpaid",
            lastname="Client",
            phone="1122334455",
            address="Test Address",
            city="Test City"
        )
        
        # Create a pending transaction
        Transaction.objects.create(
            client=client,
            transaction_type=TransactionType.SALE,
            total_amount=100.00,
            currency=Currency.EUR,
            status=TransactionStatus.PENDING
        )
        
        response = self.client.delete(self.url(client.id))
        
        # Expect 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("unpaid transactions", str(response.data)) # Commented out until implemented
        
        # Verify client is still active
        client.refresh_from_db()
        self.assertTrue(client.is_active)

    def test_delete_client_with_partial_transactions(self):
        """Test deleting a client with partial transactions should fail."""
        client = Client.objects.create(
            firstname="Partial",
            lastname="Client",
            phone="5544332211",
            address="Test Address",
            city="Test City"
        )
        
        # Create a partial transaction
        Transaction.objects.create(
            client=client,
            transaction_type=TransactionType.SALE,
            total_amount=100.00,
            currency=Currency.EUR,
            status=TransactionStatus.PARTIAL
        )
        
        response = self.client.delete(self.url(client.id))
        
        # Expect 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify client is still active
        client.refresh_from_db()
        self.assertTrue(client.is_active)
