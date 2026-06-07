"""
Real-world accounting consistency tests.

Tests verify:
- Payment method changes (CASH ↔ CARD) update correct accounts
- Multi-payment scenarios with correct account balances
- Atomicity of delete operations (rollback on failure)
- Full workflow balance validation
"""

from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from erp.constants import TransactionStatus, TransactionType
from erp.models import (
    Account,
    Client,
    ExchangeRate,
    Inventory,
    Payment,
    Product,
    Restock,
    Sales,
    Supplier,
    Transaction,
    User,
)
from erp.services.payment_service import PaymentService


class PaymentMethodChangeTests(TestCase):
    """Tests for payment method changes (CASH ↔ CARD)"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass',
            firstname='Test', lastname='User', role='ADMIN',
        )
        self.client.force_authenticate(user=self.user)
        
        # Create accounts for both CASH and BANK (CARD)
        self.cash_eur = Account.objects.create(
            account_name="Cash EUR", account_type="CASH", 
            currency="EUR", current_balance=Decimal("1000.00")
        )
        self.bank_eur = Account.objects.create(
            account_name="Bank EUR", account_type="BANK", 
            currency="EUR", current_balance=Decimal("5000.00")
        )
        
        # Create test client
        self.client_obj = Client.objects.create(
            firstname="Test", lastname="Client", 
            phone="123456", address="Addr", city="City"
        )
        
    def test_update_payment_cash_to_card(self):
        """Changing payment from CASH to CARD should move money between accounts"""
        # Create a sale transaction
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("100.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        
        # Create initial CASH payment
        result = PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("100.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        payment = Payment.objects.get(id=result["payment_id"])
        
        # Verify initial state
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        initial_cash = self.cash_eur.current_balance  # 1000 + 100 = 1100
        initial_bank = self.bank_eur.current_balance  # 5000
        
        self.assertEqual(initial_cash, Decimal("1100.00"))
        self.assertEqual(initial_bank, Decimal("5000.00"))
        
        # Change payment method from CASH to CARD
        PaymentService.update_payment(
            payment=payment,
            amount=Decimal("100.00"),
            currency="EUR",
            payment_method="CARD",
            notes="Changed to card"
        )
        
        # Verify: CASH account decreased, BANK account increased
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        
        # CASH: 1100 - 100 = 1000 (original)
        self.assertEqual(self.cash_eur.current_balance, Decimal("1000.00"),
            "CASH account should be back to original after switching to CARD")
        
        # BANK: 5000 + 100 = 5100
        self.assertEqual(self.bank_eur.current_balance, Decimal("5100.00"),
            "BANK account should increase when payment switched to CARD")
    
    def test_update_payment_card_to_cash(self):
        """Changing payment from CARD to CASH should move money between accounts"""
        # Create a sale transaction
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("200.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        
        # Create initial CARD payment
        result = PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("200.00"),
            payment_currency="EUR",
            payment_method="CARD"
        )
        payment = Payment.objects.get(id=result["payment_id"])
        
        # Initial state
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, Decimal("1000.00"))
        self.assertEqual(self.bank_eur.current_balance, Decimal("5200.00"))  # 5000 + 200
        
        # Change to CASH
        PaymentService.update_payment(
            payment=payment,
            amount=Decimal("200.00"),
            currency="EUR",
            payment_method="CASH",
            notes="Changed to cash"
        )
        
        # Verify accounts
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        
        self.assertEqual(self.cash_eur.current_balance, Decimal("1200.00"),
            "CASH account should increase when payment switched from CARD")
        self.assertEqual(self.bank_eur.current_balance, Decimal("5000.00"),
            "BANK account should be back to original")
        
    def test_update_payment_method_for_purchase(self):
        """Test payment method change for PURCHASE (money out)"""
        supplier = Supplier.objects.create(
            firstname="Sup", lastname="Plier", address="Addr"
        )
        
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=supplier,
            total_amount=Decimal("150.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        
        # Create CASH payment (money out)
        result = PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("150.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        payment = Payment.objects.get(id=result["payment_id"])
        
        # Initial state
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, Decimal("850.00"))  # 1000 - 150
        self.assertEqual(self.bank_eur.current_balance, Decimal("5000.00"))
        
        # Change to CARD
        PaymentService.update_payment(
            payment=payment,
            amount=Decimal("150.00"),
            currency="EUR",
            payment_method="CARD"
        )
        
        # Verify
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        
        self.assertEqual(self.cash_eur.current_balance, Decimal("1000.00"),
            "CASH account restored when purchase payment moved to CARD")
        self.assertEqual(self.bank_eur.current_balance, Decimal("4850.00"),
            "BANK account should deduct purchase payment")


class MultiPaymentAccountingTests(TestCase):
    """Tests for sales/restocks with multiple payments"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass',
            firstname='Test', lastname='User', role='admin',
        )
        self.full_user = self.user
        self.client.force_authenticate(user=self.user)
        
        # Create all 6 accounts per schema
        self.cash_eur = Account.objects.create(
            account_name="Cash EUR", account_type="CASH", 
            currency="EUR", current_balance=Decimal("1000.00")
        )
        self.cash_lek = Account.objects.create(
            account_name="Cash LEK", account_type="CASH", 
            currency="LEK", current_balance=Decimal("100000.00")
        )
        self.bank_eur = Account.objects.create(
            account_name="Bank EUR", account_type="BANK", 
            currency="EUR", current_balance=Decimal("5000.00")
        )
        self.bank_lek = Account.objects.create(
            account_name="Bank LEK", account_type="BANK", 
            currency="LEK", current_balance=Decimal("500000.00")
        )
        
        # Exchange rates
        ExchangeRate.objects.create(from_currency="EUR", to_currency="LEK", rate=Decimal("100.00"))
        ExchangeRate.objects.create(from_currency="LEK", to_currency="EUR", rate=Decimal("0.01"))
        
        # Test data
        self.client_obj = Client.objects.create(
            firstname="Test", lastname="Client", 
            phone="123", address="A", city="C"
        )
        self.product = Product.objects.create(
            name="Fish", category="Fresh", price=Decimal("50.00"), description="D"
        )
        Inventory.objects.create(prod=self.product, quantity=100)

    def test_multiple_payments_total_balance(self):
        """Sale with 3 payments across different methods and currencies"""
        # Create sale for 300 EUR
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("300.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        
        # Store initial balances
        initial_balances = {
            'cash_eur': self.cash_eur.current_balance,
            'cash_lek': self.cash_lek.current_balance,
            'bank_eur': self.bank_eur.current_balance,
        }
        
        # Payment 1: 100 EUR CASH
        PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("100.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        
        # Payment 2: 100 EUR CARD
        PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("100.00"),
            payment_currency="EUR",
            payment_method="CARD"
        )
        
        # Payment 3: 10000 LEK CASH (= 100 EUR)
        PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("10000.00"),
            payment_currency="LEK",
            payment_method="CASH"
        )
        
        # Verify all account balances
        self.cash_eur.refresh_from_db()
        self.cash_lek.refresh_from_db()
        self.bank_eur.refresh_from_db()
        transaction.refresh_from_db()
        
        self.assertEqual(self.cash_eur.current_balance, 
                         initial_balances['cash_eur'] + Decimal("100.00"),
                         "CASH EUR should increase by 100")
        self.assertEqual(self.bank_eur.current_balance, 
                         initial_balances['bank_eur'] + Decimal("100.00"),
                         "BANK EUR should increase by 100")
        self.assertEqual(self.cash_lek.current_balance, 
                         initial_balances['cash_lek'] + Decimal("10000.00"),
                         "CASH LEK should increase by 10000")
        
        self.assertEqual(transaction.status, TransactionStatus.COMPLETED)

    def test_delete_sale_multiple_payments_reversal(self):
        """Delete sale with multiple payments reverses ALL correctly"""
        # Create sale
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("200.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product,
            prod_price=Decimal("100.00"),
            quantity=Decimal("2"),
            user=self.full_user
        )
        
        # Store true initial balances
        initial_cash_eur = self.cash_eur.current_balance
        initial_bank_eur = self.bank_eur.current_balance
        
        # Add 2 payments
        PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("100.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        PaymentService.create_payment(
            transaction=transaction,
            amount=Decimal("100.00"),
            payment_currency="EUR",
            payment_method="CARD"
        )
        
        # Verify payments added
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, initial_cash_eur + Decimal("100.00"))
        self.assertEqual(self.bank_eur.current_balance, initial_bank_eur + Decimal("100.00"))
        
        # Delete sale via API
        response = self.client.delete(f'/erp/delete-sale/{sale.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payments_reversed'], 2)
        
        # Verify ALL accounts restored
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        
        self.assertEqual(self.cash_eur.current_balance, initial_cash_eur,
            "CASH EUR should be restored to initial")
        self.assertEqual(self.bank_eur.current_balance, initial_bank_eur,
            "BANK EUR should be restored to initial")


class AtomicityTests(TestCase):
    """Tests for atomic transaction behavior (rollback on failure)"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        self.supplier = Supplier.objects.create(
            firstname="Sup", lastname="Plier", address="Addr"
        )
        self.product = Product.objects.create(
            name="Fish", category="Fresh", price=Decimal("10.00"), description="D"
        )
        Inventory.objects.create(prod=self.product, quantity=50)  # Start with 50
        
        self.cash_eur = Account.objects.create(
            account_name="Cash EUR", account_type="CASH", 
            currency="EUR", current_balance=Decimal("1000.00")
        )

    def test_restock_delete_rollback_on_inventory_error(self):
        """
        If inventory reduction fails during restock delete,
        payment reversals MUST also be rolled back.
        """
        # Create restock of 100 units
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("500.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        restock = Restock.objects.create(
            transaction=transaction,
            prod=self.product,
            quantity=100,
            restock_price=Decimal("5.00")
        )
        
        # Add 100 to inventory (simulating restock effect)
        inv = Inventory.objects.get(prod=self.product)
        inv.quantity = 150  # 50 + 100
        inv.save()
        
        # Create payment
        Payment.objects.create(
            transaction=transaction,
            account=self.cash_eur,
            amount=Decimal("500.00"),
            currency="EUR",
            payment_method="CASH"
        )
        self.cash_eur.current_balance -= Decimal("500.00")  # 500 out
        self.cash_eur.save()
        
        initial_balance = self.cash_eur.current_balance  # 500
        
        # Simulate selling 60 items (inventory now 90)
        inv.quantity = 90
        inv.save()
        
        # Try to delete restock (needs 100, only have 90)
        response = self.client.delete(f'/erp/delete-restock/{restock.id}')
        
        # Should fail
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # CRITICAL: Verify payment was NOT reversed (atomicity)
        self.cash_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, initial_balance,
            "Account balance should remain unchanged after failed delete")
        
        # Verify restock still exists
        self.assertTrue(Restock.objects.filter(id=restock.id).exists())
        
        # Verify payment still exists
        self.assertEqual(Payment.objects.filter(transaction=transaction).count(), 1)


class FullWorkflowBalanceTests(TestCase):
    """End-to-end workflow testing final account balance correctness"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass',
            firstname='Test', lastname='User', role='admin',
        )
        self.full_user = self.user
        self.client.force_authenticate(user=self.user)
        
        # All 6 accounts starting at 0
        self.cash_eur = Account.objects.create(
            account_name="Cash EUR", account_type="CASH", 
            currency="EUR", current_balance=Decimal("0.00")
        )
        self.bank_eur = Account.objects.create(
            account_name="Bank EUR", account_type="BANK", 
            currency="EUR", current_balance=Decimal("0.00")
        )
        
        self.client_obj = Client.objects.create(
            firstname="Client", lastname="One", 
            phone="111", address="A", city="C"
        )
        self.supplier = Supplier.objects.create(
            firstname="Sup", lastname="One", address="A"
        )
        self.product = Product.objects.create(
            name="Salmon", category="Fish", price=Decimal("20.00"), description="D"
        )
        Inventory.objects.create(prod=self.product, quantity=0)

    def test_full_workflow_balance_validation(self):
        """
        Complete workflow:
        1. Restock 50 units @ 500 EUR (payment: 500 EUR CASH out)
        2. Sell 20 units @ 600 EUR (payment: 300 EUR CASH, 300 EUR CARD in)
        3. Delete the sale
        4. Verify final balances = only restock payment effect remains
        """
        # 1. Create Restock
        restock_tx = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("500.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        Restock.objects.create(
            transaction=restock_tx,
            prod=self.product,
            quantity=50,
            restock_price=Decimal("10.00")
        )
        inv = Inventory.objects.get(prod=self.product)
        inv.quantity = 50
        inv.save()
        
        # Pay for restock (500 EUR CASH out)
        PaymentService.create_payment(
            transaction=restock_tx,
            amount=Decimal("500.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        
        # Verify after restock payment
        self.cash_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, Decimal("-500.00"),
            "Cash should be -500 after paying for restock")
        
        # 2. Create Sale
        sale_tx = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("600.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        sale = Sales.objects.create(
            transaction=sale_tx,
            prod=self.product,
            prod_price=Decimal("30.00"),
            quantity=Decimal("20"),
            user=self.full_user
        )
        inv.quantity = 30  # 50 - 20
        inv.save()
        
        # Pay for sale (300 CASH + 300 CARD)
        PaymentService.create_payment(
            transaction=sale_tx,
            amount=Decimal("300.00"),
            payment_currency="EUR",
            payment_method="CASH"
        )
        PaymentService.create_payment(
            transaction=sale_tx,
            amount=Decimal("300.00"),
            payment_currency="EUR",
            payment_method="CARD"
        )
        
        # Verify after sale payments
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, Decimal("-200.00"),
            "Cash: -500 + 300 = -200")
        self.assertEqual(self.bank_eur.current_balance, Decimal("300.00"),
            "Bank: 0 + 300 = 300")
        
        # 3. Delete sale
        response = self.client.delete(f'/erp/delete-sale/{sale.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Final balance validation
        self.cash_eur.refresh_from_db()
        self.bank_eur.refresh_from_db()
        
        # Expected: Only restock payment remains
        # Cash: -500 (restock payment)
        # Bank: 0 (no remaining transactions)
        self.assertEqual(self.cash_eur.current_balance, Decimal("-500.00"),
            "Final CASH balance should reflect only restock payment")
        self.assertEqual(self.bank_eur.current_balance, Decimal("0.00"),
            "Final BANK balance should be zero after sale deletion")
        
        # Verify inventory restored
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, 50, "Inventory should be restored to 50")
        
        # Verify sum of all remaining payments equals account balances
        remaining_payments = Payment.objects.all()
        cash_payments = remaining_payments.filter(account=self.cash_eur)
        remaining_payments.filter(account=self.bank_eur)
        
        # For PURCHASE, payment reduces balance
        expected_cash = sum(
            -p.amount if p.transaction.transaction_type == TransactionType.PURCHASE 
            else p.amount 
            for p in cash_payments
        )
        
        self.assertEqual(self.cash_eur.current_balance, expected_cash,
            "Account balance should equal sum of payment effects")
