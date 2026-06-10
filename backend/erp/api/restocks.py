from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from erp.constants import TransactionStatus, TransactionType
from erp.permissions import IsManagerOrAbove, IsStaffOrAbove
from erp.utils.responses import api_error_handler, bad_request_response, not_found_response

from ..models import Payment, Product, Restock, Transaction
from ..serializers import (
    PaymentSerializer,
    ProductSerializer,
    RestockSerializer,
    TransactionSerializer,
)

# ======== RESTOCKS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getRestocks(request):
    # Optimized query: prefetch all related data in ONE query
    restocks = Restock.objects.select_related(
        'prod',
        'transaction',
        'transaction__supplier'
    ).prefetch_related(
        'transaction__payments'
    ).order_by("-restock_date")
    
    # Build response data directly from prefetched objects
    results = []
    for restock in restocks:
        restock_data = {
            "id": restock.id,
            "prod": restock.prod_id,
            "quantity": float(restock.quantity),
            "restock_price": float(restock.restock_price),
            "restock_date": restock.restock_date.isoformat() if restock.restock_date else None,
            "transaction": restock.transaction_id,
        }
        
        # Product info (already loaded via select_related)
        if restock.prod:
            restock_data["product_info"] = {
                "name": restock.prod.name,
                "category": restock.prod.category,
                "price": float(restock.prod.price) if restock.prod.price else None,
            }
        else:
            restock_data["product_info"] = None
        
        # Transaction info (already loaded via select_related)
        if restock.transaction:
            restock_data["transaction_info"] = {
                "id": restock.transaction.id,
                "status": restock.transaction.status,
                "total_amount": float(restock.transaction.total_amount),
                "currency": restock.transaction.currency,
            }
            
            # Payments (already loaded via prefetch_related)
            payments = restock.transaction.payments.all()
            restock_data["payments"] = [
                {
                    "id": p.id,
                    "amount": float(p.amount),
                    "currency": p.currency,
                    "payment_method": p.payment_method,
                    "payment_date": p.payment_date.isoformat() if p.payment_date else None,
                }
                for p in payments
            ]
        else:
            restock_data["transaction_info"] = None
            restock_data["payments"] = []
        
        results.append(restock_data)
    
    return Response(results)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getRestock(request, pk):
    try:
        restock = Restock.objects.select_related('transaction', 'prod').prefetch_related('transaction__payments').get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Restock")
    
    serializer = RestockSerializer(restock, many=False)
    response_data = serializer.data

    # Add full product info (already loaded via select_related)
    product_serializer = ProductSerializer(restock.prod)
    response_data["product_info"] = product_serializer.data

    # Add transaction info (already loaded via select_related)
    transaction_serializer = TransactionSerializer(restock.transaction)
    response_data["transaction_info"] = transaction_serializer.data

    # Add payments for this transaction (already loaded via prefetch_related)
    payment_serializer = PaymentSerializer(restock.transaction.payments.all(), many=True)
    response_data["payments"] = payment_serializer.data

    return Response(response_data)


@api_view(["POST"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def addRestock(request):
    """Create a new restock with transaction and optional payment"""
    from erp.services.inventory_service import InventoryService
    
    # Extract data from request
    supplier_id = request.data.get("supplier_id")
    product_id = request.data.get("prod")
    quantity = request.data.get("quantity")
    restock_price = Decimal(str(request.data.get("restock_price")))
    currency = request.data.get("currency", "EUR")
    payment_data = request.data.get("payment")  # Optional payment info

    # Validate inputs
    if not all([supplier_id, product_id, quantity, restock_price]):
        return bad_request_response("Missing required fields: supplier_id, prod, quantity, restock_price")

    # Get product to update inventory
    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        return not_found_response("Product")

    # Create Transaction record
    transaction = Transaction.objects.create(
        transaction_type=TransactionType.PURCHASE,
        supplier_id=supplier_id,
        total_amount=restock_price,
        currency=currency,
        status=TransactionStatus.PENDING,
        notes=f"Restock of {quantity} units of {product.name}"
    )

    # Create Restock record linked to transaction
    # Store unit price in Restock model, while Transaction has total_amount
    unit_price = restock_price / Decimal(str(quantity))
    
    restock = Restock.objects.create(
        transaction=transaction,
        prod=product,
        quantity=quantity,
        restock_price=unit_price
    )

    # Update inventory using InventoryService
    InventoryService.add_inventory(product, Decimal(str(quantity)))

    # If payment data provided, create payment
    if payment_data:
        payment_amount = Decimal(str(payment_data.get('amount', 0)))
        if payment_amount > 0:
            Payment.objects.create(
                transaction=transaction,
                account_id=payment_data.get('account_id'),
                amount=payment_amount,
                currency=payment_data.get('currency', currency),
                payment_method=payment_data.get('payment_method', 'CASH'),
                notes=payment_data.get('notes', '')
            )

            # Update transaction status based on payment
            if payment_amount >= restock_price:
                transaction.status = TransactionStatus.COMPLETED
                transaction.completed_date = timezone.now()
            elif payment_amount > 0:
                transaction.status = TransactionStatus.PARTIAL
            transaction.save()

    serializer = RestockSerializer(restock)
    return Response(
        {
            "message": "Restock created successfully!",
            "restock_id": restock.id,
            "transaction_id": transaction.id,
            "transaction_status": transaction.status,
            **serializer.data
        },
        status=status.HTTP_201_CREATED
    )


@api_view(["PUT"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def updateRestock(request, pk):
    """Update an existing restock with validation to prevent overpayment"""
    from erp.services.inventory_service import InventoryService
    from erp.services.payment_service import PaymentError, PaymentService
    
    try:
        restock = Restock.objects.select_related('transaction', 'prod').get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Restock")
    
    transaction = restock.transaction
    
    # Store old values
    old_quantity = restock.quantity
    old_prod_id = restock.prod_id
    old_product = restock.prod
    old_total_amount = transaction.total_amount
    
    # Get new values from request
    # Use transaction.total_amount as default for price since input represents Total Price
    new_prod_id = request.data.get("prod", old_prod_id)
    new_quantity = Decimal(str(request.data.get("quantity", old_quantity)))
    new_restock_price = Decimal(str(request.data.get("restock_price", old_total_amount)))
    currency = request.data.get("currency", transaction.currency)
    
    # Validate inputs
    if new_quantity <= 0:
        return bad_request_response("Quantity must be greater than zero")
    
    # Get new product if changed
    if new_prod_id != old_prod_id:
        try:
            new_product = Product.objects.get(id=new_prod_id)
        except ObjectDoesNotExist:
            return not_found_response("Product")
    else:
        new_product = old_product
    
    # Handle inventory changes
    if new_prod_id != old_prod_id:
        # Product changed: reverse old inventory, add new
        InventoryService.reduce_inventory(old_product, old_quantity, allow_negative=True)
        InventoryService.add_inventory(new_product, new_quantity)
    else:
        # Same product, quantity changed
        quantity_diff = new_quantity - old_quantity
        if quantity_diff > 0:
            InventoryService.add_inventory(new_product, quantity_diff)
        elif quantity_diff < 0:
            InventoryService.reduce_inventory(new_product, abs(quantity_diff), allow_negative=True)
    
    # Calculate unit price for storage
    unit_price = new_restock_price / new_quantity
    
    # Update restock record
    restock.prod = new_product
    restock.quantity = new_quantity
    restock.restock_price = unit_price # Store unit price
    restock.save()
    
    # Update transaction details and status via PaymentService
    try:
        PaymentService.update_transaction_status(
            transaction=transaction,
            new_total_amount=new_restock_price,
            transaction_currency=currency
        )
        # Recalculate total_paid for response after update
        total_paid = PaymentService.calculate_total_paid(transaction)
    except PaymentError as e:
        return bad_request_response(str(e))
    
    return Response({
        "message": "Restock updated successfully",
        "restock_id": restock.id,
        "transaction_id": transaction.id,
        "transaction_status": transaction.status,
        "total_amount": float(new_restock_price),
        "total_paid": float(total_paid),
        "remaining": float(new_restock_price - total_paid),
    })


@api_view(["DELETE"])
@permission_classes([IsManagerOrAbove])
@api_error_handler
def deleteRestock(request, pk):
    from django.db import transaction as db_transaction

    from erp.services.inventory_service import InventoryError, InventoryService
    from erp.services.payment_service import PaymentService
    
    try:
        restock = Restock.objects.select_related('transaction', 'prod').get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Restock")
    
    transaction = restock.transaction
    product = restock.prod
    quantity = restock.quantity
    
    # Wrap entire delete operation in atomic transaction
    # If inventory reduction fails, payment reversal is also rolled back
    try:
        with db_transaction.atomic():
            # CRITICAL: Reverse all payments FIRST (before deleting)
            reversal_result = PaymentService.reverse_all_payments(transaction)
            
            # Reverse inventory (remove the restocked quantity)
            # allow_negative=False prevents deleting if items have been sold
            InventoryService.reduce_inventory(product, quantity, allow_negative=False)
            
            restock_id = restock.id
            transaction_id = transaction.id
            
            # Delete the transaction (CASCADE will delete Restock and Payments)
            transaction.delete()
    except InventoryError:
        # Atomic block ensures payment reversal is rolled back
        return bad_request_response(
            f"Furnizimi nuk mund të fshihet: {quantity} njësi u shtuan, por vetëm "
            f"{InventoryService.get_inventory_quantity(product)} janë në gjendje. "
            "Disa njësi mund të jenë shitur tashmë."
        )
    
    return Response({
        "message": "Restock deleted successfully",
        "restock_id": restock_id,
        "transaction_id": transaction_id,
        "inventory_removed": float(quantity),
        "product_name": product.name,
        "payments_reversed": reversal_result["payment_count"],
        "total_reversed": reversal_result["total_reversed"],
        "accounts_affected": reversal_result["accounts_affected"],
    })


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getRestocksBySupplier(request, supplier_id):
    """Get restocks for a specific supplier. Add ?all=true to get all restocks."""
    # Check if we should return all restocks
    fetch_all = request.query_params.get('all', 'false').lower() == 'true'
    
    # Get restocks for this supplier through transaction
    restocks = Restock.objects.filter(
        transaction__supplier_id=supplier_id
    ).select_related('transaction', 'prod').order_by('-restock_date')
    
    # Limit to 10 unless 'all' parameter is provided
    if not fetch_all:
        restocks = restocks[:10]
    
    restocks_list = []
    for restock in restocks:
        product = restock.prod
        transaction = restock.transaction
        
        restocks_list.append({
            "id": restock.id,
            "date": restock.restock_date.date().isoformat(),
            "product_name": product.name if product else "N/A",
            "product_category": product.category if product else "N/A",
            "quantity": restock.quantity,
            "price": float(restock.restock_price),
            "currency": transaction.currency if transaction else "EUR",
            "status": transaction.status if transaction else TransactionStatus.PENDING,
            "transaction_id": transaction.id if transaction else None
        })
    
    return Response(restocks_list)


@api_view(["POST"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def payRestock(request, pk):
    """Add a payment to a restock's transaction"""
    from erp.services.payment_service import PaymentError, PaymentService
    
    try:
        restock = Restock.objects.select_related('transaction').get(id=pk)
    except Restock.DoesNotExist:
        return not_found_response("Restock")
    
    transaction = restock.transaction
    
    if not transaction:
        return bad_request_response("No transaction found for this restock")
    
    # Extract payment data
    amount = Decimal(str(request.data.get('amount', 0)))
    payment_currency = request.data.get('currency', transaction.currency)
    payment_method = request.data.get('payment_method', 'CASH')
    notes = request.data.get('notes', f'Pagesa per furnizimin #{pk}')
    pay_remaining = request.data.get('pay_remaining', False)
    
    try:
        # Use PaymentService for all payment logic
        result = PaymentService.create_payment(
            transaction=transaction,
            amount=amount,
            payment_currency=payment_currency,
            payment_method=payment_method,
            notes=notes,
            pay_remaining=pay_remaining,
        )
    except PaymentError as e:
        return bad_request_response(str(e))
    
    return Response({
        "message": "Payment recorded successfully",
        "payment_id": result["payment_id"],
        "transaction_status": result["transaction_status"],
        "total_paid": result["total_paid"],
        "remaining": result["remaining"],
    }, status=status.HTTP_201_CREATED)
