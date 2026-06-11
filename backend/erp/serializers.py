from decimal import Decimal

from rest_framework import serializers

from .models import (
    Account,
    AccountTransaction,
    Client,
    Inventory,
    Payment,
    Product,
    Product_Categories,
    Product_Names,
    Restock,
    Sales,
    Supplier,
    TaxRate,
    Transaction,
    Users,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "email", "firstname", "lastname", "role", "is_active"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Account
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    payment_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


class AccountTransactionSerializer(serializers.ModelSerializer):
    transaction_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = AccountTransaction
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Categories
        fields = "__all__"


class ProductNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Names
        fields = "__all__"


class InventorySerializer(serializers.ModelSerializer):
    restock_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Inventory
        fields = "__all__"


class SalesSerializer(serializers.ModelSerializer):
    sale_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Sales
        fields = "__all__"


class RestockSerializer(serializers.ModelSerializer):
    restock_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Restock
        fields = "__all__"


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = "__all__"


class SalesReportSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    sale_date = serializers.DateTimeField()
    client_name = serializers.CharField()
    client_address = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_paid = serializers.CharField()


class AddInventorySerializer(serializers.Serializer):
    """Serializer for adding products to inventory (restocks)."""
    name = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)  # INT in schema
    price = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0'))  # DECIMAL(8,2)
    supplier_id = serializers.IntegerField(min_value=1)  # Must be a valid positive ID
    description = serializers.CharField(required=False, allow_blank=True, default="")
    is_paid = serializers.BooleanField(default=True)  # Handles bool/string conversion
