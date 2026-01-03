"""
Unit tests for serializers.

Tests serializer validation, serialization, and deserialization.
"""

from decimal import Decimal
from django.test import TestCase
from selita.serializers import (
    ClientSerializer, ProductSerializer, SupplierSerializer,
    AccountSerializer, TransactionSerializer, PaymentSerializer,
    InventorySerializer, SalesSerializer, RestockSerializer, UserSerializer
)
from selita.models import (
    Client, Product, Supplier, Account, Transaction, Payment,
    Inventory, Sales, Restock, Users
)


class ClientSerializerTests(TestCase):
    """Tests for ClientSerializer."""
    
    def test_client_serialization(self):
        """Test serializing a client instance."""
        client = Client.objects.create(
            firstname='John', lastname='Doe',
            phone='+355 69 111 2222',
            email='john@example.com',
            address='123 Main St', city='Tirana'
        )
        serializer = ClientSerializer(instance=client)
        data = serializer.data
        
        self.assertEqual(data['firstname'], 'John')
        self.assertEqual(data['lastname'], 'Doe')
        self.assertEqual(data['phone'], '+355 69 111 2222')
        self.assertIn('id', data)
    
    def test_client_deserialization_valid(self):
        """Test deserializing valid client data."""
        data = {
            'firstname': 'Jane',
            'lastname': 'Smith',
            'phone': '+355 69 333 4444',
            'address': '456 Oak Ave',
            'city': 'Durres'
        }
        serializer = ClientSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        client = serializer.save()
        self.assertEqual(client.firstname, 'Jane')
        self.assertEqual(client.city, 'Durres')
    
    def test_client_deserialization_missing_required(self):
        """Test deserialization with missing required fields."""
        data = {
            'firstname': 'John'
            # Missing lastname, phone, address, city
        }
        serializer = ClientSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('lastname', serializer.errors)
        self.assertIn('phone', serializer.errors)


class ProductSerializerTests(TestCase):
    """Tests for ProductSerializer."""
    
    def test_product_serialization(self):
        """Test serializing a product instance."""
        product = Product.objects.create(
            name='Fresh Salmon', category='Fish',
            price=Decimal('15.00'), description='Atlantic salmon'
        )
        serializer = ProductSerializer(instance=product)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Fresh Salmon')
        self.assertEqual(data['category'], 'Fish')
        self.assertEqual(Decimal(data['price']), Decimal('15.00'))
    
    def test_product_deserialization_valid(self):
        """Test deserializing valid product data."""
        data = {
            'name': 'Tuna',
            'category': 'Fish',
            'price': '18.50',
            'description': 'Fresh tuna'
        }
        serializer = ProductSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.name, 'Tuna')
        self.assertEqual(product.price, Decimal('18.50'))


class SupplierSerializerTests(TestCase):
    """Tests for SupplierSerializer."""
    
    def test_supplier_serialization(self):
        """Test serializing a supplier instance."""
        supplier = Supplier.objects.create(
            firstname='Fish', lastname='Co',
            phone='+355 69 555 6666',
            address='Harbor 1'
        )
        serializer = SupplierSerializer(instance=supplier)
        data = serializer.data
        
        self.assertEqual(data['firstname'], 'Fish')
        self.assertEqual(data['lastname'], 'Co')
    
    def test_supplier_deserialization_valid(self):
        """Test deserializing valid supplier data."""
        data = {
            'firstname': 'Sea',
            'lastname': 'Foods',
            'address': 'Pier 5'
        }
        serializer = SupplierSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        supplier = serializer.save()
        self.assertEqual(supplier.firstname, 'Sea')


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
            'created_date': '2020-01-01T00:00:00Z'  # Should be ignored
        }
        serializer = AccountSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        account = serializer.save()
        # created_date should NOT be 2020-01-01
        self.assertNotEqual(account.created_date.year, 2020)


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


class UserSerializerTests(TestCase):
    """Tests for UserSerializer."""
    
    def test_user_serialization(self):
        """Test serializing a user instance."""
        user = Users.objects.create(
            username='testuser', password='hashed123',
            email='test@example.com',
            firstname='Test', lastname='User', role='admin'
        )
        serializer = UserSerializer(instance=user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['role'], 'admin')
