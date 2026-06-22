from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action

from erp.models import (
    Account,
    AccountTransaction,
    Client,
    ExchangeRate,
    Inventory,
    Payment,
    PaymentTerms,
    Product,
    Product_Categories,
    Restock,
    Sales,
    Supplier,
    TaxRate,
    Transaction,
    User,
)
from erp.pagination import StandardPagination
from erp.permissions import IsManagerOrAbove, IsStaffOrAbove
from erp.serializers import (
    AccountSerializer,
    AccountTransactionSerializer,
    ClientSerializer,
    InventorySerializer,
    PaymentSerializer,
    PaymentTermsSerializer,
    ProductCategoriesSerializer,
    ProductSerializer,
    RestockSerializer,
    SalesSerializer,
    SupplierSerializer,
    TaxRateSerializer,
    TransactionSerializer,
    UserSerializer,
)
from erp.services.inventory_service import InventoryService
from erp.utils.responses import success_response


class ExchangeRateSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = "__all__"


class BaseViewSet(viewsets.ModelViewSet):
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action == "destroy":
            return [IsManagerOrAbove()]
        if self.action in ("create", "update", "partial_update"):
            return [IsStaffOrAbove()]
        return [permissions.IsAuthenticated()]


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SupplierViewSet(BaseViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ClientViewSet(BaseViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class AccountViewSet(BaseViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class PaymentTermsViewSet(BaseViewSet):
    queryset = PaymentTerms.objects.filter(is_active=True)
    serializer_class = PaymentTermsSerializer


class TransactionViewSet(BaseViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=False, methods=["get"], url_path="overdue")
    def overdue(self, request):
        today = timezone.now().date()
        qs = Transaction.objects.filter(
            due_date__lt=today,
            status__in=["PENDING", "PARTIAL"],
        ).select_related("client", "supplier", "payment_terms")
        serializer = self.get_serializer(qs, many=True)
        return success_response(serializer.data)

    @action(detail=False, methods=["get"], url_path="aging-report")
    def aging_report(self, request):
        today = timezone.now().date()
        unpaid = Transaction.objects.filter(
            due_date__isnull=False,
            status__in=["PENDING", "PARTIAL"],
        ).select_related("client", "supplier", "payment_terms")

        buckets = {
            "current": [],
            "1_30": [],
            "31_60": [],
            "61_90": [],
            "over_90": [],
        }
        summary = {k: {"count": 0, "total": 0} for k in buckets}

        for txn in unpaid:
            days_overdue = (today - txn.due_date).days
            if days_overdue <= 0:
                bucket = "current"
            elif days_overdue <= 30:
                bucket = "1_30"
            elif days_overdue <= 60:
                bucket = "31_60"
            elif days_overdue <= 90:
                bucket = "61_90"
            else:
                bucket = "over_90"

            entry = {
                "id": txn.id,
                "invoice_number": txn.invoice_number,
                "transaction_type": txn.transaction_type,
                "client": (
                    f"{txn.client.firstname} {txn.client.lastname}"
                    if txn.client else None
                ),
                "supplier": (
                    f"{txn.supplier.firstname} {txn.supplier.lastname}"
                    if txn.supplier else None
                ),
                "total_amount": str(txn.total_amount),
                "currency": txn.currency,
                "due_date": str(txn.due_date),
                "days_overdue": max(days_overdue, 0),
                "status": txn.status,
            }
            buckets[bucket].append(entry)
            summary[bucket]["count"] += 1
            summary[bucket]["total"] += float(txn.total_amount)

        return success_response({
            "buckets": buckets,
            "summary": summary,
        })


class PaymentViewSet(BaseViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class AccountTransactionViewSet(BaseViewSet):
    queryset = AccountTransaction.objects.all()
    serializer_class = AccountTransactionSerializer


class ProductViewSet(BaseViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class CategoryViewSet(BaseViewSet):
    queryset = Product_Categories.objects.all()
    serializer_class = ProductCategoriesSerializer


class InventoryViewSet(BaseViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        products = InventoryService.get_low_stock_products()
        data = [
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": float(product.price),
                "quantity": product.stock,
                "reorder_level": product.reorder_level,
                "reorder_quantity": product.reorder_quantity,
            }
            for product in products
        ]
        return success_response(data)


class SalesViewSet(BaseViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer


class RestockViewSet(BaseViewSet):
    queryset = Restock.objects.all()
    serializer_class = RestockSerializer


class TaxRateViewSet(BaseViewSet):
    queryset = TaxRate.objects.filter(is_active=True)
    serializer_class = TaxRateSerializer


class ExchangeRateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
