from rest_framework.response import Response
from rest_framework import permissions
from ..models import Restock, Product, Payment, Inventory, Transaction, Supplier
from rest_framework.decorators import api_view, permission_classes
from ..serializers import (
    RestockSerializer,
    ProductSerializer,
    PaymentSerializer,
    TransactionSerializer,
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.utils import timezone
from decimal import Decimal


# ======== RESTOCKS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getRestocks(request):
    try:
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
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getRestock(request, pk):
    try:
        restock = Restock.objects.select_related('transaction', 'prod').get(id=pk)
        serializer = RestockSerializer(restock, many=False)

        response_data = serializer.data

        # Add full product info
        product_serializer = ProductSerializer(restock.prod)
        response_data["product_info"] = product_serializer.data

        # Add transaction info
        transaction_serializer = TransactionSerializer(restock.transaction)
        response_data["transaction_info"] = transaction_serializer.data

        # Add payments for this transaction
        payments = Payment.objects.filter(transaction=restock.transaction)
        payment_serializer = PaymentSerializer(payments, many=True)
        response_data["payments"] = payment_serializer.data

        return Response(response_data)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Restock not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def addRestock(request):
    """Create a new restock with transaction and optional payment"""
    try:
        # Extract data from request
        supplier_id = request.data.get("supplier_id")
        product_id = request.data.get("prod")
        quantity = request.data.get("quantity")
        restock_price = Decimal(str(request.data.get("restock_price")))
        currency = request.data.get("currency", "EUR")
        payment_data = request.data.get("payment")  # Optional payment info

        # Validate inputs
        if not all([supplier_id, product_id, quantity, restock_price]):
            return Response(
                {"error": "Missing required fields: supplier_id, prod, quantity, restock_price"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get product to update inventory
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Create Transaction record
        transaction = Transaction.objects.create(
            transaction_type='PURCHASE',
            supplier_id=supplier_id,
            total_amount=restock_price,
            currency=currency,
            status='PENDING',
            notes=f"Restock of {quantity} units of {product.name}"
        )

        # Create Restock record linked to transaction
        restock = Restock.objects.create(
            transaction=transaction,
            prod=product,
            quantity=quantity,
            restock_price=restock_price
        )

        # Update inventory using InventoryService
        from selita.services.inventory_service import InventoryService
        InventoryService.add_inventory(product, Decimal(str(quantity)))

        # If payment data provided, create payment
        if payment_data:
            payment_amount = Decimal(str(payment_data.get('amount', 0)))
            if payment_amount > 0:
                payment = Payment.objects.create(
                    transaction=transaction,
                    account_id=payment_data.get('account_id'),
                    amount=payment_amount,
                    currency=payment_data.get('currency', currency),
                    payment_method=payment_data.get('payment_method', 'CASH'),
                    notes=payment_data.get('notes', '')
                )

                # Update transaction status based on payment
                if payment_amount >= restock_price:
                    transaction.status = 'COMPLETED'
                    transaction.completed_date = timezone.now()
                elif payment_amount > 0:
                    transaction.status = 'PARTIAL'
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

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
def updateRestock(request, pk):
    try:
        restock = Restock.objects.get(id=pk)
        old_quantity = restock.quantity

        serializer = RestockSerializer(instance=restock, data=request.data)
        if serializer.is_valid():
            updated_restock = serializer.save()

            # Update inventory: remove old quantity and add new quantity
            quantity_difference = updated_restock.quantity - old_quantity
            if quantity_difference != 0:
                try:
                    inventory = Inventory.objects.get(prod=updated_restock.prod)
                    inventory.quantity += quantity_difference
                    inventory.save()
                except ObjectDoesNotExist:
                    pass

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Restock not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def deleteRestock(request, pk):
    try:
        restock = Restock.objects.get(id=pk)

        # Remove the restocked quantity from inventory
        try:
            inventory = Inventory.objects.get(prod=restock.prod)
            inventory.quantity -= restock.quantity
            inventory.save()
        except ObjectDoesNotExist:
            pass

        restock.delete()
        return Response("Restock deleted successfully")
    except ObjectDoesNotExist:
        return Response(
            {"error": "Restock not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getRestocksBySupplier(request, supplier_id):
    """Get restocks for a specific supplier. Add ?all=true to get all restocks."""
    try:
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
                "status": transaction.status if transaction else "PENDING",
                "transaction_id": transaction.id if transaction else None
            })
        
        return Response(restocks_list)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def payRestock(request, pk):
    """Add a payment to a restock's transaction"""
    from selita.services.payment_service import PaymentService, PaymentError
    
    try:
        restock = Restock.objects.select_related('transaction').get(id=pk)
        transaction = restock.transaction
        
        if not transaction:
            return Response(
                {"error": "No transaction found for this restock"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Extract payment data
        amount = Decimal(str(request.data.get('amount', 0)))
        payment_currency = request.data.get('currency', transaction.currency)
        payment_method = request.data.get('payment_method', 'CASH')
        notes = request.data.get('notes', f'Payment for restock #{pk}')
        pay_remaining = request.data.get('pay_remaining', False)
        
        # Use PaymentService for all payment logic
        result = PaymentService.create_payment(
            transaction=transaction,
            amount=amount,
            payment_currency=payment_currency,
            payment_method=payment_method,
            notes=notes,
            pay_remaining=pay_remaining,
        )
        
        return Response({
            "message": "Payment recorded successfully",
            "payment_id": result["payment_id"],
            "transaction_status": result["transaction_status"],
            "total_paid": result["total_paid"],
            "remaining": result["remaining"],
        }, status=status.HTTP_201_CREATED)
        
    except Restock.DoesNotExist:
        return Response(
            {"error": "Restock not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except PaymentError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
