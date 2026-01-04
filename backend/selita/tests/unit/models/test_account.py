"""
Unit tests for Account model.
"""

from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from selita.models import Account


class AccountModelTests(TestCase):
    """Tests for the Account model."""
    
    def test_account_creation_cash(self):
        """Test creating a CASH account."""
        account = Account.objects.create(
            account_name='Main Cash',
            account_type='CASH',
            currency='EUR'
        )
        self.assertEqual(account.account_name, 'Main Cash')
        self.assertEqual(account.account_type, 'CASH')
        self.assertEqual(account.currency, 'EUR')
        self.assertIsNotNone(account.created_date)
    
    def test_account_creation_bank(self):
        """Test creating a BANK account."""
        account = Account.objects.create(
            account_name='Business Bank',
            account_type='BANK',
            currency='USD',
            current_balance=Decimal('5000.00')
        )
        self.assertEqual(account.account_type, 'BANK')
        self.assertEqual(account.current_balance, Decimal('5000.00'))
    
    def test_account_default_balance(self):
        """Test that default balance is 0.00."""
        account = Account.objects.create(
            account_name='New Account',
            account_type='CASH',
            currency='LEK'
        )
        self.assertEqual(account.current_balance, Decimal('0.00'))
    
    def test_account_unique_type_currency(self):
        """Test unique constraint on account_type + currency."""
        Account.objects.create(account_name='Cash EUR', account_type='CASH', currency='EUR')
        
        with self.assertRaises(IntegrityError):
            Account.objects.create(account_name='Another Cash EUR', account_type='CASH', currency='EUR')
    
    def test_account_str(self):
        """Test account string representation."""
        account = Account.objects.create(
            account_name='Primary Account',
            account_type='BANK',
            currency='EUR'
        )
        self.assertEqual(str(account), 'Primary Account (EUR)')
    
    def test_account_ordering(self):
        """Test accounts ordered by account_type, currency."""
        Account.objects.create(account_name='Cash USD', account_type='CASH', currency='USD')
        Account.objects.create(account_name='Bank EUR', account_type='BANK', currency='EUR')
        Account.objects.create(account_name='Cash EUR', account_type='CASH', currency='EUR')
        
        accounts = list(Account.objects.all())
        self.assertEqual(accounts[0].account_type, 'BANK')
        self.assertEqual(accounts[1].account_type, 'CASH')
        self.assertEqual(accounts[1].currency, 'EUR')
        self.assertEqual(accounts[2].currency, 'USD')
