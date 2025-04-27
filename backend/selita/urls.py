from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api import auth, users, clients, products, inventory, sales


urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login", auth.login),
    path("users", users.getUsers),
    path("user/<str:pk>", users.getUser),
    path("client/<str:pk>", clients.getClient),
    path("clients", clients.getClients),
    path("client-sales/<str:pk>", clients.getClientSales),
    path("add-client", clients.addClient),
    path("create-user", users.createUser),
    path("update-user/<str:pk>", users.updateUser),
    path("delete-user/<str:pk>", users.deleteUser),
    path("product/<str:pk>", products.getProduct),
    path("products", products.getProducts),
    path("add-product", products.addProduct),
    path("product-categories", products.getProductCategories),
    path("product-names", products.getProductNames),
    path("productbycategory/<str:category>", products.getProductsByCategory),
    path(
        "productbyname/<str:name>",
        products.getProductByName,
    ),
    path("filterbycategories", products.filterByCategories),
    path("productbyname/<str:name>", products.getProductByNames),
    path("inventory", inventory.getInventory),
    path("productsfrominventory", inventory.getProductsFromInventory),
    path("sale/<str:pk>", sales.getSale),
    path("sales", sales.getSales),
    path("salesinfo", sales.getProductsFromSales),
    path("usersfromsales", sales.getUsersFromSales),
    path("pay-sale/<str:pk>", sales.paySale),
    path("checkdisponibility/<str:pk>", products.checkDisponibility),
    path("create-sale", sales.createSale),
    path("update-inventory", inventory.addProductToInventory),
]
