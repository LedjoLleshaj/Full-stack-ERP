from rest_framework.response import Response
from ..models import Inventory, Product, Product_Names
from rest_framework.decorators import api_view, permission_classes
from ..serializers import InventorySerializer, ProductSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


# ======== USERS ========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getInventory(request):
    try:
        inventory = Inventory.objects.all()
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getProductsFromInventory(request):
    try:
        inventory = Inventory.objects.all()
        serializer = InventorySerializer(inventory, many=True)

        for i in range(len(serializer.data)):
            prod_id = serializer.data[i]["prod"]

            product = Product.objects.get(id=prod_id)
            p_serializer = ProductSerializer(product, many=False)
            serializer.data[i]["product"] = p_serializer.data

        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateInventory(request, pk):
    try:
        inventory = Inventory.objects.get(id=pk)
        serializer = InventorySerializer(instance=inventory, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Inventory item not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def addProductToInventory(request):
    try:
        name = request.data.get("name")
        category = request.data.get("category")
        description = request.data.get("description")
        quantity = request.data.get("quantity")
        price = request.data.get("price")
        print("addProductToInventory", name, category, description, quantity, price)
        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if price <= 0:
            return Response(
                {"error": "Price must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Check if the product already exists
        try:
            product = Product.objects.get(name=name)
            print("Product already exists", product)
        except ObjectDoesNotExist:
            # Create a new product if it doesn't exist
            product = Product.objects.create(
                name=name, category=category, description=description, price=price
            )
        # Check if the inventory item already exists
        try:
            inventory = Inventory.objects.get(prod=product)
            # Update the existing inventory item's quantity
            inventory.quantity += quantity

            inventory.save()
        except ObjectDoesNotExist:
            # Create a new inventory item if it doesn't exist
            inventory = Inventory.objects.create(prod=product, quantity=quantity)
        # Serialize the updated inventory item
        serializer = InventorySerializer(inventory)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
