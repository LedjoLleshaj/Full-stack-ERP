from django.urls import path
from . import views

urlpatterns = [
    path("users", views.getUsers, name="users"),
    path("user/<str:pk>", views.getUser, name="user"),
    path("create-user", views.createUser, name="create-user"),
    path("update-user/<str:pk>", views.updateUser, name="update-user"),
    path("delete-user/<str:pk>", views.deleteUser, name="delete-user"),
]