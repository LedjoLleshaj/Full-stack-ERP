from rest_framework.response import Response
from ..models import Inventory, Product, Product_Names
from rest_framework.decorators import api_view
from ..serializers import InventorySerializer, ProductSerializer

# ======== USERS ========


@api_view(["GET"])
def getInventory(request):
    inventory = Inventory.objects.all()
    serializer = InventorySerializer(inventory, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getProductsFromInventory(request):
    inventory = Inventory.objects.all()
    serializer = InventorySerializer(inventory, many=True)

    for i in range(len(serializer.data)):
        prod_id = serializer.data[i]["prod"]

        product = Product.objects.get(id=prod_id)
        p_serializer = ProductSerializer(product, many=False)
        serializer.data[i]["product"] = p_serializer.data

    return Response(serializer.data)
