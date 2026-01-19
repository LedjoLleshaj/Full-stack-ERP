from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "email", "firstname", "lastname"]
        # Explicitly exclude password - never expose password hashes in API responses


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


class SalesReportSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    sale_date = serializers.DateTimeField()
    client_name = serializers.CharField()
    client_address = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_paid = serializers.CharField()
