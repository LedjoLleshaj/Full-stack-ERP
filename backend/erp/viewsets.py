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


class TransactionViewSet(BaseViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


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
