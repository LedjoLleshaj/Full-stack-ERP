from decimal import Decimal

from rest_framework import serializers

from .models import (
    Account,
    AccountTransaction,
    Client,
    Inventory,
    Payment,
    PaymentTerms,
    Product,
    Product_Categories,
    Product_Names,
    Quotation,
    QuotationItem,
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


class PaymentTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTerms
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(read_only=True)
    payment_terms_name = serializers.CharField(
        source="payment_terms.name", read_only=True, default=None
    )
    payment_terms_days = serializers.IntegerField(
        source="payment_terms.days", read_only=True, default=None
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = "__all__"

    def get_is_overdue(self, obj):
        if not obj.due_date:
            return False
        from django.utils import timezone
        return (
            obj.due_date < timezone.now().date()
            and obj.status in ("PENDING", "PARTIAL")
        )


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


class QuotationItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    tax_rate_name = serializers.CharField(source="tax_rate.name", read_only=True, default=None)

    class Meta:
        model = QuotationItem
        fields = [
            "id", "product", "product_name", "quantity", "unit_price",
            "tax_rate", "tax_rate_name", "tax_amount", "subtotal", "line_total",
        ]


class QuotationListSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = Quotation
        fields = [
            "id", "client", "client_name", "status", "currency",
            "valid_until", "notes", "created_date", "total_amount", "item_count",
        ]

    def get_client_name(self, obj):
        return f"{obj.client.firstname} {obj.client.lastname}" if obj.client else None


class QuotationDetailSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    client_name = serializers.SerializerMethodField()
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = [
            "id", "client", "client_name", "status", "currency",
            "valid_until", "notes", "created_date", "created_by", "created_by_name",
            "converted_transaction", "items", "total_amount",
        ]

    def get_client_name(self, obj):
        return f"{obj.client.firstname} {obj.client.lastname}" if obj.client else None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.firstname} {obj.created_by.lastname}"
        return None


class QuotationCreateSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True)

    class Meta:
        model = Quotation
        fields = ["client", "currency", "valid_until", "notes", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        quotation = Quotation.objects.create(**validated_data)
        for item_data in items_data:
            item_data.pop("product_name", None)
            item_data.pop("subtotal", None)
            item_data.pop("line_total", None)
            item_data.pop("tax_rate_name", None)
            QuotationItem.objects.create(quotation=quotation, **item_data)
        return quotation

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                item_data.pop("product_name", None)
                item_data.pop("subtotal", None)
                item_data.pop("line_total", None)
                item_data.pop("tax_rate_name", None)
                QuotationItem.objects.create(quotation=instance, **item_data)
        return instance


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
