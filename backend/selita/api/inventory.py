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
