from rest_framework.response import Response
from ..models import Product, Product_Categories, Product_Names
from rest_framework.decorators import api_view
from ..serializers import (
    ProductSerializer,
    ProductCategoriesSerializer,
    ProductNamesSerializer,
)


# ======== PRODUCTS ========


@api_view(["GET"])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getProduct(request, pk):
    product = Product.objects.get(id=pk)
    serializer = ProductSerializer(product, many=False)
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


@api_view(["GET"])
def getProduct(request, pk):
    product = Product.objects.get(id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)


@api_view(["GET"])
def getProductCategories(request):
    categories = Product_Categories.objects.all()
    serializer = ProductCategoriesSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getProductNames(request):
    names = Product_Names.objects.all()
    serializer = ProductNamesSerializer(names, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getProductsByCategory(request, category):
    products = Product.objects.filter(category=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getProductsByNames(request, name):
    name = Product.objects.filter(name=name)
    serializer = ProductSerializer(name, many=True)
    return Response(serializer.data)
