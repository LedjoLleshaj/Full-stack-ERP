from rest_framework.test import APITestCase
from rest_framework import status
from erp.models import User, Client, Product, Account, Transaction, Sales, Payment, Supplier, Inventory
from erp.constants import TransactionStatus, TransactionType
from decimal import Decimal
from django.utils import timezone


class AccountingConsistencyTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testadmin",
            password="testpassword",
            email="test@example.com",
            firstname="Test",
            lastname="User",
            role="ADMIN",
        )
        self.client.force_authenticate(user=self.user)
        
        # Create Client & Supplier
        self.client_obj = Client.objects.create(firstname="John", lastname="Doe", phone="123", address="Tirana", city="TR")
        self.supplier_obj = Supplier.objects.create(firstname="Sup", lastname="Plier", phone="456", address="Durres")
        
        # Create Accounts
        self.cash_eur = Account.objects.create(account_name="Cash EUR", currency="EUR", account_type="CASH", current_balance=Decimal("1000.00"))
        
        # Create Product
        self.product = Product.objects.create(
            name="Test Fish", 
            price=Decimal("10.00"), 
            category="Fresh",
            description="Tasty"
        )
        Inventory.objects.create(prod=self.product, quantity=100) # Initial Inventory
        
    def test_delete_sale_reverses_accounting(self):
        """Test that deleting a paid sale reverses account balance and inventory"""
        
        # 1. Create Sale (10 units @ 10 EUR = 100 EUR)
        sale = Sales.objects.create(
            transaction=Transaction.objects.create(
                transaction_type=TransactionType.SALE,
                client=self.client_obj,
                total_amount=Decimal("100.00"),
                currency="EUR",
                status=TransactionStatus.PENDING
            ),
            prod=self.product,
            prod_price=Decimal("10.00"),
            quantity=Decimal("10.00"),
            user=self.user
        )
        transaction = sale.transaction
        
        # 2. Pay 100 EUR
        Payment.objects.create(
            transaction=transaction,
            account=self.cash_eur,
            amount=Decimal("100.00"),
            currency="EUR",
            payment_method="CASH"
        )
        # Update Account State manually (simulate service)
        self.cash_eur.current_balance += Decimal("100.00") 
        self.cash_eur.save()
        
        # Update Inventory manually (simulate service)
        inv = Inventory.objects.get(prod=self.product)
        inv.quantity -= 10
        inv.save()
        
        # Verify state before delete
        self.cash_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, Decimal("1100.00")) # 1000 + 100
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, 90) # 100 - 10
        
        # 3. Call Delete Endpoint
        response = self.client.delete(f'/erp/delete-sale/{sale.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Verify Reversals
        self.cash_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, Decimal("1000.00")) # Reversed 100
        
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, 100) # Reversed 10
        
        # Verify records deleted
        self.assertFalse(Sales.objects.filter(id=sale.id).exists())
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())
        self.assertFalse(Payment.objects.filter(transaction=transaction).exists())

    def test_update_sale_simplified_currency_logic(self):
        """Test update logic: Allow ONLY if new_total >= total_paid. No payment conversion."""
        
        # 1. Create Sale (100 EUR)
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.client_obj,
            total_amount=Decimal("100.00"),
            currency="EUR",
            status=TransactionStatus.PARTIAL
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product,
            prod_price=Decimal("10.00"),
            quantity=Decimal("10.00"),
            user=self.user
        )
        # Pay 50 EUR
        payment = Payment.objects.create(
            transaction=transaction,
            account=self.cash_eur,
            amount=Decimal("50.00"),
            currency="EUR",
            payment_method="CASH"
        )
        # self.cash_eur.current_balance += 50 (Not needed for this test logic)
        
        # 2. Update to LEK (Higher Value)
        # 10000 LEK > 50 (Nominal). Allow.
        update_data = {
            "prod": self.product.id,
            "quantity": 10.0,
            "prod_price": 1000.0, # 1000 * 10 = 10000 Total
            "currency": "LEK"
        }
        
        response = self.client.put(f'/erp/update-sale/{sale.id}', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify Transaction Updated
        transaction.refresh_from_db()
        self.assertEqual(transaction.currency, "LEK")
        self.assertEqual(transaction.total_amount, Decimal("10000.00"))
        self.assertEqual(transaction.status, TransactionStatus.PARTIAL) # 10000 > 50
        
        # Verify Payment NOT changed
        payment.refresh_from_db()
        self.assertEqual(payment.currency, "EUR")
        self.assertEqual(payment.amount, Decimal("50.00"))
        
        # 3. Update to LOWER value (Fail case)
        # Try to update to 40 EUR. 40 < 50. Should FAIL.
        error_data = {
            "prod": self.product.id,
            "quantity": 4.0,
            "prod_price": 10.0, # 40 Total
            "currency": "EUR"
        }
        response = self.client.put(f'/erp/update-sale/{sale.id}', error_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Already paid", response.data['error'])

