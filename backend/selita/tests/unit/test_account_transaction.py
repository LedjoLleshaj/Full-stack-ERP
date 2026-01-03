"""
Unit tests for AccountTransaction model.
"""

from decimal import Decimal
from django.test import TestCase
from selita.models import AccountTransaction, Account, Payment, Transaction, Client


class AccountTransactionModelTests(TestCase):
    """Tests for the AccountTransaction model."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.account = Account.objects.create(
            account_name='Cash EUR',
            account_type='CASH',
            currency='EUR',
            current_balance=Decimal('1000.00')
        )
        cls.db_client = Client.objects.create(
            firstname='Test', lastname='Client',
            phone='+355 69 123', address='Address', city='Tirana'
        )
        cls.transaction = Transaction.objects.create(
            transaction_type='SALE',
            client=cls.db_client,
            total_amount=Decimal('100.00'),
            currency='EUR'
        )
        cls.payment = Payment.objects.create(
            transaction=cls.transaction,
            account=cls.account,
            amount=Decimal('100.00'),
            currency='EUR',
            payment_method='CASH'
        )
    
    def test_account_transaction_deposit(self):
        """Test creating a DEPOSIT account transaction."""
        acct_trans = AccountTransaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('500.00'),
            balance_after=Decimal('1500.00')
        )
        self.assertEqual(acct_trans.account, self.account)
        self.assertEqual(acct_trans.transaction_type, 'DEPOSIT')
        self.assertEqual(acct_trans.amount, Decimal('500.00'))
        self.assertEqual(acct_trans.balance_after, Decimal('1500.00'))
        self.assertIsNotNone(acct_trans.transaction_date)
    
    def test_account_transaction_withdrawal(self):
        """Test creating a WITHDRAWAL account transaction."""
        acct_trans = AccountTransaction.objects.create(
            account=self.account,
            transaction_type='WITHDRAWAL',
            amount=Decimal('200.00'),
            balance_after=Decimal('800.00')
        )
        self.assertEqual(acct_trans.transaction_type, 'WITHDRAWAL')
        self.assertEqual(acct_trans.amount, Decimal('200.00'))
        self.assertEqual(acct_trans.balance_after, Decimal('800.00'))
    
    def test_account_transaction_transfer(self):
        """Test creating a TRANSFER account transaction."""
        acct_trans = AccountTransaction.objects.create(
            account=self.account,
            transaction_type='TRANSFER',
            amount=Decimal('300.00'),
            balance_after=Decimal('700.00'),
            notes='Transfer to bank account'
        )
        self.assertEqual(acct_trans.transaction_type, 'TRANSFER')
        self.assertEqual(acct_trans.notes, 'Transfer to bank account')
    
    def test_account_transaction_with_payment(self):
        """Test account transaction linked to a payment."""
        acct_trans = AccountTransaction.objects.create(
            account=self.account,
            payment=self.payment,
            transaction_type='DEPOSIT',
            amount=Decimal('100.00'),
            balance_after=Decimal('1100.00')
        )
        self.assertEqual(acct_trans.payment, self.payment)
        self.assertEqual(acct_trans.payment.amount, Decimal('100.00'))
    
    def test_account_transaction_balance_tracking(self):
        """Test that balance_after tracks account state."""
        # Deposit
        t1 = AccountTransaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('500.00'),
            balance_after=Decimal('1500.00')
        )
        
        # Withdrawal
        t2 = AccountTransaction.objects.create(
            account=self.account,
            transaction_type='WITHDRAWAL',
            amount=Decimal('200.00'),
            balance_after=Decimal('1300.00')
        )
        
        self.assertEqual(t1.balance_after, Decimal('1500.00'))
        self.assertEqual(t2.balance_after, Decimal('1300.00'))
    
    def test_account_transaction_str(self):
        """Test account transaction string representation."""
        acct_trans = AccountTransaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('250.00'),
            balance_after=Decimal('1250.00')
        )
        expected = 'DEPOSIT - 250.00 (Balance: 1250.00)'
        self.assertEqual(str(acct_trans), expected)
    
    def test_account_transaction_ordering(self):
        """Test account transactions ordered by -transaction_date."""
        t1 = AccountTransaction.objects.create(
            account=self.account, transaction_type='DEPOSIT',
            amount=Decimal('100.00'), balance_after=Decimal('1100.00')
        )
        t2 = AccountTransaction.objects.create(
            account=self.account, transaction_type='WITHDRAWAL',
            amount=Decimal('50.00'), balance_after=Decimal('1050.00')
        )
        
        transactions = list(AccountTransaction.objects.all())
        # Newest first
        self.assertEqual(transactions[0].id, t2.id)
        self.assertEqual(transactions[1].id, t1.id)
    
    def test_account_transaction_optional_payment(self):
        """Test that payment is optional."""
        acct_trans = AccountTransaction.objects.create(
            account=self.account,
            transaction_type='DEPOSIT',
            amount=Decimal('100.00'),
            balance_after=Decimal('1100.00')
        )
        self.assertIsNone(acct_trans.payment)
