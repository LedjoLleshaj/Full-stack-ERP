from rest_framework.response import Response
from ..models import Inventory, Product, Product_Names, Transaction, Restock, Supplier
from rest_framework.decorators import api_view, permission_classes
from ..serializers import InventorySerializer, ProductSerializer, RestockSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal


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
        # category = request.data.get("category")
        quantity = request.data.get("quantity")
        price = request.data.get("price")
        supplier_id = request.data.get("supplier_id")
        description = request.data.get("description", "")  # Default to empty string
        is_paid = request.data.get("is_paid", True)  # Default to True (paid)
        print("addProductToInventory", name, quantity, price, "supplier_id:", supplier_id, "description:", description, "is_paid:", is_paid)
        
        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if price < 0:
            return Response(
                {"error": "Price must be greater than or equal to zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not supplier_id:
            return Response(
                {"error": "Supplier is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Get the supplier
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Supplier not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Convert price to Decimal for accurate calculations
        price = Decimal(str(price))
        
        # Check if the product already exists
        try:
            product = Product.objects.get(name=name)
            print("Product already exists", product)
            # Update description if a new one is provided, or if current is empty, use name
            if description:
                product.description = description
                product.save()
            elif not product.description:
                product.description = name
                product.save()
        except ObjectDoesNotExist:
            # Create a new product if it doesn't exist
            # Get category from Product_Names table
            try:
                product_name_obj = Product_Names.objects.get(product_name=name)
                category = product_name_obj.category.category_name
            except ObjectDoesNotExist:
                category = "Uncategorized"
            
            # Note: For new products, we use the purchase price as initial selling price
            # If no description provided, use the product name as default
            product = Product.objects.create(
                name=name, 
                price=price, 
                category=category,
                description=description if description else name
            )
        
        # Determine transaction status based on is_paid
        transaction_status = "COMPLETED" if is_paid else "PENDING"
        
        # Create purchase transaction to track the expense
        total_amount = price * quantity
        transaction = Transaction.objects.create(
            transaction_type="PURCHASE",
            supplier=supplier,
            total_amount=total_amount,
            currency="EUR",
            status=transaction_status,
            notes=f"Restock: {quantity} x {product.name} @ {price}/unit"
        )
        
        # Create restock record to track purchase cost per unit
        restock = Restock.objects.create(
            transaction=transaction,
            prod=product,
            quantity=quantity,
            restock_price=price
        )
        
        # Update inventory quantity
        try:
            inventory = Inventory.objects.get(prod=product)
            inventory.quantity += quantity
            inventory.save()
        except ObjectDoesNotExist:
            # Create a new inventory item if it doesn't exist
            inventory = Inventory.objects.create(prod=product, quantity=quantity)
        
        # Serialize the response
        inventory_serializer = InventorySerializer(inventory)
        restock_serializer = RestockSerializer(restock)
        
        return Response({
            "inventory": inventory_serializer.data,
            "restock": restock_serializer.data,
            "transaction_id": transaction.id,
            "message": f"Added {quantity} units of {product.name} to inventory. Purchase cost recorded: {total_amount} EUR"
        })
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
