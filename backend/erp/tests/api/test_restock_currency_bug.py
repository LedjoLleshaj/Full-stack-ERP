
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from erp.models import Restock, Product, Supplier, Transaction, Payment, Account, Inventory, ExchangeRate
from erp.constants import TransactionStatus, TransactionType
from django.contrib.auth.models import User

class RestockCurrencyBugTestCase(TestCase):
    """Test suite for reproducing restock currency inconsistency bugs"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        self.supplier = Supplier.objects.create(firstname="S", lastname="T", address="A")
        self.product = Product.objects.create(name="P", category="C", price=Decimal("10.00"), description="D")
        Inventory.objects.create(prod=self.product, quantity=100)
        
        # Create accounts
        self.cash_eur = Account.objects.create(account_name="Cash EUR", account_type="CASH", currency="EUR", current_balance=Decimal("1000.00"))
        self.cash_lek = Account.objects.create(account_name="Cash LEK", account_type="CASH", currency="LEK", current_balance=Decimal("100000.00"))
        
        # Set exchange rates matches schema (roughly)
        ExchangeRate.objects.create(from_currency='EUR', to_currency='LEK', rate=Decimal("100.00"))
        ExchangeRate.objects.create(from_currency='LEK', to_currency='EUR', rate=Decimal("0.01"))

    def test_reproduce_currency_change_delete_bug(self):
        """
        Reproduce: restock in euro 10euro gets change to lek 1000lek, 
        after deleting the account shows 1000euro which is wrong.
        """
        # 1. Create restock 10 EUR
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("10.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        restock = Restock.objects.create(
            transaction=transaction,
            prod=self.product,
            quantity=1,
            restock_price=Decimal("10.00")
        )
        
        # 2. Pay 10 EUR from EUR account
        payment = Payment.objects.create(
            transaction=transaction,
            account=self.cash_eur,
            amount=Decimal("10.00"),
            currency="EUR",
            payment_method="CASH"
        )
        self.cash_eur.current_balance -= Decimal("10.00")
        self.cash_eur.save()
        
        self.assertEqual(self.cash_eur.current_balance, Decimal("990.00"))
        
        # 3. Change restock to 1000 LEK
        response = self.client.put(
            f'/erp/update-restock/{restock.id}',
            {
                'prod': self.product.id,
                'quantity': 1,
                'restock_price': '1000.00',
                'currency': 'LEK'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Verify payment was converted to 1000 LEK in DB
        payment.refresh_from_db()
        self.assertEqual(payment.amount, Decimal("1000.00"))
        self.assertEqual(payment.currency, "LEK")
        
        # 5. Delete restock
        response = self.client.delete(f'/erp/delete-restock/{restock.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 6. Check EUR account balance
        # BUG: It should be 1000.00 (990 + 10).
        # Currently, it is likely 1990.00 (990 + 1000) because it reverses 1000 into EUR account!
        self.cash_eur.refresh_from_db()
        print(f"DEBUG: Balance after deletion: {self.cash_eur.current_balance}")
        
        # This assertion will FAIL before the fix
        self.assertEqual(self.cash_eur.current_balance, Decimal("1000.00"), 
                         f"EUR Account balance should be 1000.00, but got {self.cash_eur.current_balance}")

    def test_reproduce_delete_converted_payment_bug(self):
        """
        Reproduce: payment in LEK for EUR transaction. Delete payment.
        Verify LEK account is reversed correctly.
        """
        # 1. Create restock 10 EUR
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("10.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        restock = Restock.objects.create(transaction=transaction, prod=self.product, quantity=1, restock_price=Decimal("10.00"))
        
        # 2. Pay 1000 LEK (which is 10 EUR) from LEK account
        # In reality, PaymentService.create_payment would be used.
        # payment.amount = 10 (EUR), original_amount = 1000 (LEK)
        payment = Payment.objects.create(
            transaction=transaction,
            account=self.cash_lek,
            amount=Decimal("10.00"),
            currency="EUR",
            original_amount=Decimal("1000.00"),
            original_currency="LEK",
            payment_method="CASH"
        )
        self.cash_lek.current_balance -= Decimal("1000.00")
        self.cash_lek.save()
        
        self.assertEqual(self.cash_lek.current_balance, Decimal("99000.00"))
        
        # 3. Delete THIS payment via API? Or directly via PaymentService
        from erp.services.payment_service import PaymentService
        PaymentService.delete_payment(payment)
        
        # 4. Check LEK account balance
        # BUG: It should be 100000.00 (99000 + 1000).
        # Currently, it is likely 99010.00 (99000 + 10) because delete_payment uses payment.amount!
        self.cash_lek.refresh_from_db()
        print(f"DEBUG: LEK Balance after payment deletion: {self.cash_lek.current_balance}")
        
        # This assertion will FAIL before the fix
        self.assertEqual(self.cash_lek.current_balance, Decimal("100000.00"),
                         f"LEK Account balance should be 100000.00, but got {self.cash_lek.current_balance}")
