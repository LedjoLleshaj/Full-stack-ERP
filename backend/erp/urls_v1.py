from rest_framework.routers import DefaultRouter

from erp.viewsets import (
    AccountTransactionViewSet,
    AccountViewSet,
    CategoryViewSet,
    ClientViewSet,
    ExchangeRateViewSet,
    InventoryViewSet,
    PaymentViewSet,
    ProductViewSet,
    RestockViewSet,
    SalesViewSet,
    SupplierViewSet,
    TransactionViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("suppliers", SupplierViewSet)
router.register("clients", ClientViewSet)
router.register("accounts", AccountViewSet)
router.register("transactions", TransactionViewSet)
router.register("payments", PaymentViewSet)
router.register("account-transactions", AccountTransactionViewSet)
router.register("products", ProductViewSet)
router.register("categories", CategoryViewSet)
router.register("inventory", InventoryViewSet)
router.register("sales", SalesViewSet)
router.register("restocks", RestockViewSet)
router.register("exchange-rates", ExchangeRateViewSet)

urlpatterns = router.urls
