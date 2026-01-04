"""
Unit tests for PaymentSerializer.
"""
from decimal import Decimal
from django.test import TestCase
from selita.serializers import PaymentSerializer
from selita.models import Payment, Transaction, Account, Client


class PaymentSerializerTests(TestCase):
    """Tests for PaymentSerializer."""
    
    @classmethod
    def setUpTestData(cls):
        cls.db_client = Client.objects.create(
            firstname='Test', lastname='Client',
            phone='+355 69 789', address='Addr', city='City'
        )
        cls.transaction = Transaction.objects.create(
            transaction_type='SALE', client=cls.db_client,
            total_amount=Decimal('100.00'), currency='EUR'
        )
        cls.account = Account.objects.create(
            account_name='Cash', account_type='CASH', currency='EUR'
        )
    
    def test_payment_serialization(self):
        """Test serializing a payment instance."""
        payment = Payment.objects.create(
            transaction=self.transaction,
            account=self.account,
            amount=Decimal('50.00'),
            currency='EUR',
            payment_method='CASH'
        )
        serializer = PaymentSerializer(instance=payment)
        data = serializer.data
        
        self.assertEqual(Decimal(data['amount']), Decimal('50.00'))
        self.assertEqual(data['payment_method'], 'CASH')
        self.assertIn('payment_date', data)
