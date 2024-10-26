from django.urls import path

from .api import auth, users, products


urlpatterns = [
    path("login", auth.login),
    path("users", users.getUsers),
    path("user/<str:pk>", users.getUser),
    path("create-user", users.createUser),
    path("update-user/<str:pk>", users.updateUser),
    path("delete-user/<str:pk>", users.deleteUser),
    path("products", products.getProducts),
    path("add-product", products.addProduct),
    path("product-categories", products.getProductCategories),
    path("product-names", products.getProductNames),
    path("productbycategory/<str:category>", products.getProductsByCategory),
    path("productbyname/<str:name>", products.getProductsByNames),
]
