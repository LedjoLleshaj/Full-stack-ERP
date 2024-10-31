from django.shortcuts import render

# Create your views here.


from rest_framework.response import Response
from ..models import Product
from rest_framework.decorators import api_view
from ..serializers import ProductSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== PRODUCTS ========


@api_view(["GET"])
def getProducts(request):
    try:
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def addProduct(request):
    try:
        serializer = ProductSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {"message": "Product added successfully!", "product_id": product.id},
                status=status.HTTP_201_CREATED,
            )

        # If serializer is invalid, respond with validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle any unexpected exceptions
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
