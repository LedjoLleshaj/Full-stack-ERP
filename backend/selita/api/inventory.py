from rest_framework.response import Response
from ..models import Inventory, Product, Product_Names, Transaction, Restock, Supplier, Payment, Account
from rest_framework.decorators import api_view, permission_classes
from ..serializers import InventorySerializer, ProductSerializer, RestockSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
import logging

logger = logging.getLogger(__name__)
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
        # Optimized: Use select_related to load products in ONE query
        inventory = Inventory.objects.select_related('prod').all()
        
        # Build response with product info already loaded
        results = []
        for inv in inventory:
            results.append({
                "id": inv.id,
                "prod": inv.prod_id,
                "quantity": float(inv.quantity) if inv.quantity else 0,
                "product": {
                    "id": inv.prod.id,
                    "name": inv.prod.name,
                    "category": inv.prod.category,
                    "price": float(inv.prod.price) if inv.prod.price else None,
                    "description": inv.prod.description,
                } if inv.prod else None
            })
        
        return Response(results)
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
    from selita.services.inventory_service import InventoryService
    from selita.services.payment_service import PaymentService, PaymentError
    
    try:
        name = request.data.get("name")
        quantity = request.data.get("quantity")
        price = request.data.get("price")
        supplier_id = request.data.get("supplier_id")
        description = request.data.get("description", "")  # Default to empty string
        is_paid = request.data.get("is_paid", True)  # Default to True (paid)
        logger.debug("addProductToInventory: %s, qty=%s, price=%s, supplier=%s", name, quantity, price, supplier_id)
        
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
        quantity = Decimal(str(quantity))
        
        # Check if the product already exists
        try:
            product = Product.objects.get(name=name)
            logger.debug("Product already exists: %s (id=%s)", product.name, product.id)
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
        
        # If marked as paid, use PaymentService
        if is_paid:
            try:
                PaymentService.create_payment(
                    transaction=transaction,
                    amount=total_amount,
                    payment_currency="EUR",
                    payment_method="CASH",
                    notes=f"Initial payment for restock #{restock.id}",
                )
            except PaymentError as e:
                # If payment fails, update transaction status and log
                transaction.status = "PENDING"
                transaction.notes += f" (Payment failed: {str(e)})"
                transaction.save()
                logger.warning("Payment failed for restock #%s: %s", restock.id, str(e))
        
        # Use InventoryService to update inventory
        new_quantity = InventoryService.add_inventory(product, quantity)
        
        # Get inventory record for response
        inventory = Inventory.objects.get(prod=product)
        
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
