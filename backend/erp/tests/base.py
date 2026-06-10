from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from erp.constants import AccountType, Currency, TransactionStatus, TransactionType
from erp.models import (
    Account,
    Client,
    Inventory,
    Product,
    Product_Categories,
    Sales,
    Supplier,
    Transaction,
)

User = get_user_model()


class ErpTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            firstname="Test",
            lastname="User",
            role="ADMIN",
        )

        cls.account = Account.objects.create(
            account_name="Test Cash",
            account_type=AccountType.CASH,
            currency=Currency.EUR,
            current_balance=Decimal("1000.00"),
        )

        cls.category = Product_Categories.objects.create(
            category_name="Test Category",
        )

        cls.supplier = Supplier.objects.create(
            firstname="Test",
            lastname="Supplier",
            address="123 Test St",
        )

        cls.product = Product.objects.create(
            name="Test Product",
            category="Test Category",
            category_fk=cls.category,
            price=Decimal("15.00"),
            description="A test product",
        )

        cls.client_obj = Client.objects.create(
            firstname="Test",
            lastname="Client",
            phone="1234567890",
            address="456 Client Ave",
            city="Tirana",
        )

    def create_inventory(self, product=None, quantity=100):
        if product is None:
            product = self.product
        return Inventory.objects.create(prod=product, quantity=quantity)

    def create_sale(self, client=None, product=None, quantity=10):
        if client is None:
            client = self.client_obj
        if product is None:
            product = self.product

        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=client,
            total_amount=product.price * quantity,
            currency=Currency.EUR,
            status=TransactionStatus.PENDING,
        )
        sale = Sales.objects.create(
            transaction=transaction,
            prod=product,
            prod_price=product.price,
            user=self.user,
            quantity=quantity,
        )
        return sale
