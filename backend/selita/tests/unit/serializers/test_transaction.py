"""
Unit tests for TransactionSerializer.
"""
from decimal import Decimal
from django.test import TestCase
from selita.serializers import TransactionSerializer
from selita.models import Transaction, Client


class TransactionSerializerTests(TestCase):
    """Tests for TransactionSerializer."""
    
    @classmethod
    def setUpTestData(cls):
        cls.db_client = Client.objects.create(
            firstname='Test', lastname='Client',
            phone='+355 69 123', address='Addr', city='City'
        )
    
    def test_transaction_serialization(self):
        """Test serializing a transaction instance."""
        transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=self.db_client,
            total_amount=Decimal('100.00'),
            currency='EUR'
        )
        serializer = TransactionSerializer(instance=transaction)
        data = serializer.data
        
        self.assertEqual(data['transaction_type'], 'SALE')
        self.assertEqual(Decimal(data['total_amount']), Decimal('100.00'))
        self.assertIn('created_date', data)
