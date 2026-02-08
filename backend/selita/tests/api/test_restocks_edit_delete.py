"""
Tests for Restock API edit/delete endpoints.

Tests verify:
- Restock update with overpayment validation
- Restock delete with payment reversal
- Inventory adjustments
- Transaction status updates
"""

from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from selita.models import Restock, Product, Supplier, Transaction, Payment, Account, Inventory
from selita.constants import TransactionStatus, TransactionType


from django.contrib.auth.models import User

class RestockUpdateDeleteTestCase(TestCase):
    """Test suite for restock update and delete operations"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create and authenticate user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        # Create test supplier
        self.supplier = Supplier.objects.create(
            firstname="Supplier",
            lastname="Test",
            phone="9876543210",
            address="456 Supplier Ave"
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
        
        # Initialize inventory
        Inventory.objects.create(prod=self.product_a, quantity=0)
        Inventory.objects.create(prod=self.product_b, quantity=0)
        
        # Create account for payments
        self.cash_eur = Account.objects.create(
            account_name="Cash EUR",
            account_type="CASH",
            currency="EUR",
            current_balance=Decimal("1000.00")
        )
    
    def test_update_restock_quantity(self):
        """Test updating restock quantity"""
        # Create initial restock
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("200.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        restock = Restock.objects.create(
            transaction=transaction,
            prod=self.product_a,
            quantity=20,
            restock_price=Decimal("200.00")
        )
        
        # Get initial inventory
        inv_before = Inventory.objects.filter(prod=self.product_a).first().quantity
        
        # Update to 30 quantity
        response = self.client.put(
            f'/update-restock/{restock.id}',
            {
                'prod': self.product_a.id,
                'quantity': 30,
                'restock_price': '300.00',
                'currency': 'EUR'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_amount'], 300.00)
        
        # Verify inventory increased by 10
        inv_after = Inventory.objects.filter(prod=self.product_a).first().quantity
        self.assertEqual(inv_after, inv_before + 10)
    
    def test_update_restock_overpayment_blocked(self):
        """Test that reducing total below paid amount is blocked"""
        # Create restock with payment
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("200.00"),
            currency="EUR",
            status=TransactionStatus.COMPLETED
        )
        restock = Restock.objects.create(
            transaction=transaction,
            prod=self.product_a,
            quantity=20,
            restock_price=Decimal("200.00")
        )
        Payment.objects.create(
            transaction=transaction,
            account=self.cash_eur,
            amount=Decimal("200.00"),
            currency="EUR",
            payment_method="CASH"
        )
        
        # Try to reduce price (would make total < paid)
        response = self.client.put(
            f'/update-restock/{restock.id}',
            {
                'prod': self.product_a.id,
                'quantity': 20,
                'restock_price': '100.00',  # Reduce price, but already paid 200
                'currency': 'EUR'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot reduce total", response.data['message'])
    
    def test_delete_restock_unpaid(self):
        """Test deleting an unpaid restock"""
        # Create unpaid restock
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("200.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        restock = Restock.objects.create(
            transaction=transaction,
            prod=self.product_a,
            quantity=20,
            restock_price=Decimal("200.00")
        )
        
        # Get initial inventory
        initial_inventory = Inventory.objects.filter(prod=self.product_a).first().quantity
        
        # Delete restock
        response = self.client.delete(f'/delete-restock/{restock.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payments_reversed'], 0)
        
        # Verify inventory removed
        final_inventory = Inventory.objects.filter(prod=self.product_a).first().quantity
        self.assertEqual(final_inventory, initial_inventory - 20)
        
        # Verify restock and transaction deleted
        self.assertFalse(Restock.objects.filter(id=restock.id).exists())
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())
    
    def test_delete_restock_with_payment(self):
        """Test deleting a paid restock reverses payment"""
        # Create restock with payment
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("200.00"),
            currency="EUR",
            status=TransactionStatus.COMPLETED
        )
        restock = Restock.objects.create(
            transaction=transaction,
            prod=self.product_a,
            quantity=20,
            restock_price=Decimal("200.00")
        )
        Payment.objects.create(
            transaction=transaction,
            account=self.cash_eur,
            amount=Decimal("200.00"),
            currency="EUR",
            payment_method="CASH"
        )
        
        # Account should have -200 (PURCHASE means money out)
        initial_balance = self.cash_eur.current_balance
        self.cash_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, initial_balance - Decimal("200.00"))
        
        # Delete restock
        response = self.client.delete(f'/delete-restock/{restock.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payments_reversed'], 1)
        self.assertEqual(response.data['total_reversed'], 200.00)
        
        # Verify account balance reversed (money returned)
        self.cash_eur.refresh_from_db()
        self.assertEqual(self.cash_eur.current_balance, initial_balance)
    
    def test_update_restock_change_product(self):
        """Test changing product in a restock"""
        # Create restock for product A
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("200.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        restock = Restock.objects.create(
            transaction=transaction,
            prod=self.product_a,
            quantity=20,
            restock_price=Decimal("200.00")
        )
        
        # Get initial inventories
        inv_a_before = Inventory.objects.filter(prod=self.product_a).first().quantity
        inv_b_before = Inventory.objects.filter(prod=self.product_b).first().quantity
        
        # Change product from A to B
        response = self.client.put(
            f'/update-restock/{restock.id}',
            {
                'prod': self.product_b.id,
                'quantity': 20,
                'restock_price': '300.00',
                'currency': 'EUR'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify product A inventory removed
        inv_a_after = Inventory.objects.filter(prod=self.product_a).first().quantity
        self.assertEqual(inv_a_after, inv_a_before - 20)
        
    def test_delete_restock_blocked_if_sold(self):
        """Test blocking restock deletion if items already sold"""
        # Create restock of 100
        transaction = Transaction.objects.create(
            transaction_type=TransactionType.PURCHASE,
            supplier=self.supplier,
            total_amount=Decimal("1000.00"),
            currency="EUR",
            status=TransactionStatus.PENDING
        )
        restock = Restock.objects.create(
            transaction=transaction,
            prod=self.product_a,
            quantity=100,
            restock_price=Decimal("1000.00")
        )
        # Manually increase inventory (since we bypassed service in test setup previously, 
        # or rely on signal if any. Actually my test setup initialized to 0).
        # But wait, InventoryService.add_inventory would have been called in real API.
        # In this test case, I am creating objects directly, so I must manually set inventory.
        inv_obj = Inventory.objects.get(prod=self.product_a)
        inv_obj.quantity = 100
        inv_obj.save()
        
        # Now simulate a sale of 10 items (reducing inventory to 90)
        inv_obj.quantity = 90
        inv_obj.save()
        
        # Try to delete restock (which put 100 items). Should fail because only 90 avail.
        response = self.client.delete(f'/selita/delete-restock/{restock.id}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Furnizimi nuk mund të fshihet", response.data['error'])
        self.assertIn("90 janë në gjendje", response.data['error'])

