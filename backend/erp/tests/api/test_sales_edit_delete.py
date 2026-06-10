"""
Tests for Sales API edit/delete endpoints.

Tests verify:
- Sale update with overpayment validation
- Sale delete with payment reversal
- Inventory adjustments
- Transaction status updates
"""

from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from erp.constants import TransactionStatus, TransactionType
from erp.models import Account, Client, Inventory, Payment, Product, Sales, Transaction, User


class SaleUpdateDeleteTestCase(TestCase):
    """Test suite for sale update and delete operations"""

    def setUp(self):
        """Set up test data"""
        self.client_api = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.com",
            firstname="Test",
            lastname="User",
            role="ADMIN",
        )
        self.client_api.force_authenticate(user=self.user)
        
        # Create test client
        self.test_client = Client.objects.create(
            firstname="John",
            lastname="Doe",
            phone="1234567890",
            address="123 Test St",
            city="Test City"
        )
        
        # Create test products
        self.product_a = Product.objects.create(
            name="Product A",
            category="Category A",
            price=Decimal("10.00"),
            description="Test product A"
        )
        self.product_b = Product.objects.create(
            name="Product B",
            category="Category B",
            price=Decimal("15.00"),
            description="Test product B"
        )
        
        # Add inventory
        Inventory.objects.create(prod=self.product_a, quantity=100)
        Inventory.objects.create(prod=self.product_b, quantity=100)
        
        # Create accounts for payments
        self.cash_eur = Account.objects.create(
            account_name="Cash EUR",
            account_type="CASH",
            currency="EUR",
            current_balance=Decimal("0.00")
        )
    
    def test_update_sale_quantity_increase(self):
        """Test increasing sale quantity"""
        # Create initial sale
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=Decimal("100.00"),  # 10 * 10
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product_a,
            prod_price=Decimal("10.00"),
            user=self.user,
            quantity=Decimal("10")
        )
        
        # Update to 15 quantity
        response = self.client_api.put(
            f'/erp/update-sale/{sale.id}',
            {
                'prod': self.product_a.id,
                'quantity': 15,
                'prod_price': '10.00',
                'user': self.user.id,
                'currency': 'EUR'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_amount'], 150.00)
        
        # Verify inventory
        inventory = Inventory.objects.filter(prod=self.product_a).first()
        # Initial: 100, update adds 5 more sold = 95 remaining
        self.assertEqual(inventory.quantity, 95)
    
    def test_update_sale_overpayment_blocked(self):
        """Test that reducing total below paid amount is blocked"""
        # Create sale with payment
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=Decimal("100.00"),
            currency="EUR",
            status=TransactionStatus.COMPLETED
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product_a,
            prod_price=Decimal("10.00"),
            user=self.user,
            quantity=Decimal("10")
        )
        Payment.objects.create(
            transaction=transaction,
            account=self.cash_eur,
            amount=Decimal("100.00"),
            currency="EUR",
            payment_method="CASH"
        )
        
        # Try to reduce quantity (would make total < paid)
        response = self.client_api.put(
            f'/erp/update-sale/{sale.id}',
            {
                'prod': self.product_a.id,
                'quantity': 5,  # Would make total = 50, but paid = 100
                'prod_price': '10.00',
                'user': self.user.id,
                'currency': 'EUR'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot reduce total", response.data['error'])
    
    def test_delete_sale_unpaid(self):
        """Test deleting an unpaid sale"""
        # Create unpaid sale
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=Decimal("100.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product_a,
            prod_price=Decimal("10.00"),
            user=self.user,
            quantity=Decimal("10")
        )
        
        # Get initial inventory
        initial_inventory = Inventory.objects.filter(prod=self.product_a).first().quantity
        
        # Delete sale
        response = self.client_api.delete(f'/erp/delete-sale/{sale.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payments_reversed'], 0)
        
        # Verify inventory restored
        final_inventory = Inventory.objects.filter(prod=self.product_a).first().quantity
        self.assertEqual(final_inventory, initial_inventory + 10)
        
        # Verify sale and transaction deleted
        self.assertFalse(Sales.objects.filter(id=sale.id).exists())
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())
    
    def test_delete_sale_with_payment(self):
        """Test deleting a paid sale reverses payment"""
        # Create sale with payment
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=Decimal("100.00"),
            currency="EUR",
            status=TransactionStatus.COMPLETED
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product_a,
            prod_price=Decimal("10.00"),
            user=self.user,
            quantity=Decimal("10")
        )
        Payment.objects.create(
            transaction=transaction,
            account=self.cash_eur,
            amount=Decimal("100.00"),
            currency="EUR",
            payment_method="CASH"
        )
        
        # Account should have +100
        self.cash_eur.current_balance += Decimal("100.00")
        self.cash_eur.save()
        self.cash_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, Decimal("100.00"))
        
        # Delete sale
        response = self.client_api.delete(f'/erp/delete-sale/{sale.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payments_reversed'], 1)
        self.assertEqual(response.data['total_reversed'], 100.00)
        
        # Verify account balance reversed
        self.cash_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, Decimal("0.00"))
    
    def test_update_sale_change_product(self):
        """Test changing product in a sale"""
        # Create sale
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=self.test_client,
            total_amount=Decimal("100.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=self.product_a,
            prod_price=Decimal("10.00"),
            user=self.user,
            quantity=Decimal("10")
        )
        
        # Get initial inventories
        inv_a_before = Inventory.objects.filter(prod=self.product_a).first().quantity
        inv_b_before = Inventory.objects.filter(prod=self.product_b).first().quantity
        
        # Change product from A to B
        response = self.client_api.put(
            f'/erp/update-sale/{sale.id}',
            {
                'prod': self.product_b.id,
                'quantity': 10,
                'prod_price': '15.00',
                'user': self.user.id,
                'currency': 'EUR'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify product A inventory restored
        inv_a_after = Inventory.objects.filter(prod=self.product_a).first().quantity
        self.assertEqual(inv_a_after, inv_a_before + 10)
        
        # Verify product B inventory reduced
        inv_b_after = Inventory.objects.filter(prod=self.product_b).first().quantity
        self.assertEqual(inv_b_after, inv_b_before - 10)
