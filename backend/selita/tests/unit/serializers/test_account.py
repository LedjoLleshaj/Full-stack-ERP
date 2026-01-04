"""
Unit tests for AccountSerializer.
"""
from decimal import Decimal
from django.test import TestCase
from selita.serializers import AccountSerializer
from selita.models import Account


class AccountSerializerTests(TestCase):
    """Tests for AccountSerializer."""
    
    def test_account_serialization(self):
        """Test serializing an account instance."""
        account = Account.objects.create(
            account_name='Cash EUR',
            account_type='CASH',
            currency='EUR',
            current_balance=Decimal('1000.00')
        )
        serializer = AccountSerializer(instance=account)
        data = serializer.data
        
        self.assertEqual(data['account_name'], 'Cash EUR')
        self.assertEqual(data['account_type'], 'CASH')
        self.assertIn('created_date', data)
    
    def test_account_created_date_read_only(self):
        """Test that created_date is read-only."""
        data = {
            'account_name': 'New Account',
            'account_type': 'BANK',
            'currency': 'USD',
            'created_date': '2020-01-01T00:00:00Z'
        }
        serializer = AccountSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        account = serializer.save()
        self.assertNotEqual(account.created_date.year, 2020)
