from django.shortcuts import render

# Create your views here.


from rest_framework.response import Response
from ..models import Product
from rest_framework.decorators import api_view
from ..serializers import ProductSerializer


# ======== PRODUCTS ========


@api_view(["GET"])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def addProduct(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(
            {"message": "Product added successfully!", "product_id": product.id},
            status=201,
        )
    return Response(serializer.errors, status=400)
