from django.urls import path

from .api import auth, users, products, inventory, sales


urlpatterns = [
    path("login", auth.login),
    path("users", users.getUsers),
    path("user/<str:pk>", users.getUser),
    path("create-user", users.createUser),
    path("update-user/<str:pk>", users.updateUser),
    path("delete-user/<str:pk>", users.deleteUser),
    path("product/<str:pk>", products.getProduct),
    path("products", products.getProducts),
    path("add-product", products.addProduct),
    path("product-categories", products.getProductCategories),
    path("product-names", products.getProductNames),
    path("productbycategory/<str:category>", products.getProductsByCategory),
    path("productbyname/<str:name>", products.getProductsByNames),
    path("inventory", inventory.getInventory),
    path("productsfrominventory", inventory.getProductsFromInventory),
    path("sale/<str:pk>", sales.getSale),
    path("sales", sales.getSales),
    path("salesinfo", sales.getProductsFromSales),
    path("usersfromsales", sales.getUsersFromSales),
]
