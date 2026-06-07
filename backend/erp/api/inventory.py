import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from erp.utils.responses import api_error_handler, not_found_response

from ..models import (
    Inventory,
    Product,
    Product_Names,
    Restock,
    Supplier,
    Transaction,
)
from ..serializers import (
    AddInventorySerializer,
    InventorySerializer,
    RestockSerializer,
)

logger = logging.getLogger(__name__)


# ======== INVENTORY ========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getInventory(request):
    inventory = Inventory.objects.all()
    serializer = InventorySerializer(inventory, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProductsFromInventory(request):
    # Optimized: Use select_related to load products in ONE query
    # Only return inventory for ACTIVE products
    inventory = Inventory.objects.select_related('prod').filter(prod__is_active=True).all()
    
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


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@api_error_handler
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
        return not_found_response("Inventory item")


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@api_error_handler
def addProductToInventory(request):
    from erp.services.inventory_service import InventoryService
    from erp.services.payment_service import PaymentError, PaymentService
    
    # Validate and parse input using serializer
    serializer = AddInventorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    name = data['name']
    quantity = data['quantity']  # int from serializer
    price = data['price']  # Decimal from serializer
    supplier_id = data['supplier_id']
    description = data['description']
    is_paid = data['is_paid']  # Properly parsed boolean
    
    logger.debug("addProductToInventory: %s, qty=%s, price=%s, supplier=%s, is_paid=%s (type=%s)", 
                 name, quantity, price, supplier_id, is_paid, type(is_paid).__name__)
    
    # Get the supplier
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except ObjectDoesNotExist:
        return not_found_response("Supplier")
    
    # Check if the product already exists
    try:
        product = Product.objects.get(name=name)
        logger.debug("Produkti ekziston: %s (id=%s)", product.name, product.id)
        
        # REACTIVATE product if it was soft-deleted
        if not product.is_active:
            product.is_active = True
        
        # Update description if a new one is provided, or if current is empty, use name
        if description:
            product.description = description
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
    
    # Create purchase transaction (start as PENDING, PaymentService will update to COMPLETED)
    total_amount = price * quantity
    transaction = Transaction.objects.create(
        transaction_type="PURCHASE",
        supplier=supplier,
        total_amount=total_amount,
        currency="EUR",
        status="PENDING",  # Start as PENDING, payment will update to COMPLETED
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
                notes=f"Pagesa per furnizimin #{restock.id}",
            )
        except PaymentError as e:
            # If payment fails, update transaction status and log
            transaction.status = "PENDING"
            transaction.notes += f" (Payment failed: {str(e)})"
            transaction.save()
            logger.warning("Pagesa nuk u krye per furnizimin #%s: %s", restock.id, str(e))
    
    # Use InventoryService to update inventory
    InventoryService.add_inventory(product, quantity)
    
    # Get inventory record for response
    inventory = Inventory.objects.get(prod=product)
    
    # Serialize the response
    inventory_serializer = InventorySerializer(inventory)
    restock_serializer = RestockSerializer(restock)
    
    return Response({
        "inventory": inventory_serializer.data,
        "restock": restock_serializer.data,
        "transaction_id": transaction.id,
        "message": f"U shtuan {quantity} njesi te produktit {product.name} ne magazine. Kosto e blerjes u regjistrua: {total_amount} EUR"
    })
