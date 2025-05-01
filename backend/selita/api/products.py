from rest_framework.response import Response
from ..models import Product, Product_Categories, Product_Names, Inventory
from rest_framework.decorators import api_view, permission_classes
from ..serializers import (
    ProductSerializer,
    ProductCategoriesSerializer,
    ProductNamesSerializer,
    InventorySerializer,
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


# ======== PRODUCTS ========


@api_view(["GET"])
def getProducts(request):
    try:
        products = Product.objects.all()
        # for each product get disponibility from inventory by porduct id
        product_serializer = ProductSerializer(products, many=True)

        for product in product_serializer.data:
            try:
                inventory = Inventory.objects.get(prod=product["id"])
                product["disponibility"] = inventory.quantity
            except ObjectDoesNotExist:
                product["disponibility"] = 0
        return Response(product_serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addProduct(request):
    try:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {"message": "Product added successfully!", "product_id": product.id},
                status=201,
            )
        return Response(serializer.errors, status=400)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updatePrice(request, pk):
    print(request.data)
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(instance=product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Product price updated successfully!"}, status=200
            )
        return Response(serializer.errors, status=400)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def getProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def getProductByName(request, name):
    try:
        product = Product.objects.get(name=name)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def getProductCategories(request):
    try:
        categories = Product_Categories.objects.all()
        serializer = ProductCategoriesSerializer(categories, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def getProductNames(request):
    try:
        names = Product_Names.objects.all()
        serializer = ProductNamesSerializer(names, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def getProductsByCategory(request, category):
    try:
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def filterByCategories(request):
    # Get the 'categories' parameter from the query string
    categories = request.GET.get("categories", "")

    # If the 'categories' parameter is empty, return an empty list
    if not categories:
        products = Product.objects.all()
    else:
        # Split the comma-separated string into a list
        categories_list = categories.split(",")

        # Filter products whose category is in the list of categories
        products = Product.objects.filter(category__in=categories_list)

    product_serializer = ProductSerializer(products, many=True)

    for product in product_serializer.data:
        try:
            inventory = Inventory.objects.get(prod=product["id"])
            product["disponibility"] = inventory.quantity
        except ObjectDoesNotExist:
            product["disponibility"] = 0
    return Response(product_serializer.data)


@api_view(["GET"])
def getProductByNames(request, name):
    name = Product.objects.filter(name=name)
    serializer = ProductSerializer(name, many=False)
    return Response(serializer.data)


@api_view(["GET"])
def checkDisponibility(request, pk):
    try:
        product = Product.objects.get(id=pk)
        inventory = Inventory.objects.get(prod=product)
        serializer = InventorySerializer(inventory, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
