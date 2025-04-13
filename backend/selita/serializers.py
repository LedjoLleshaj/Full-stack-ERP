from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
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
    class Meta:
        model = Sales
        fields = "__all__"


class RestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restock
        fields = "__all__"
