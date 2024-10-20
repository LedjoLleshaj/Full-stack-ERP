from rest_framework import serializers
from .models import Users, Product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
