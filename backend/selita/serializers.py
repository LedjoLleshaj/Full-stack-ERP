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
