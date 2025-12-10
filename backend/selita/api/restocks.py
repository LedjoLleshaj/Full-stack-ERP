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
        restocks = Restock.objects.select_related('transaction', 'prod').all().order_by("-restock_date")
        serializer = RestockSerializer(restocks, many=True)

        # Add product and transaction/payment info
        for restock_data in serializer.data:
            try:
                product = Product.objects.get(id=restock_data["prod"])
                product_serializer = ProductSerializer(product)
                restock_data["product_info"] = {
                    "name": product_serializer.data.get("name"),
                    "category": product_serializer.data.get("category"),
                    "price": product_serializer.data.get("price"),
                }
            except ObjectDoesNotExist:
                restock_data["product_info"] = None

            # Get payment info through transaction
            try:
                transaction = Transaction.objects.get(id=restock_data["transaction"])
                restock_data["transaction_info"] = {
                    "id": transaction.id,
                    "status": transaction.status,
                    "total_amount": float(transaction.total_amount),
                    "currency": transaction.currency,
                }
                
                # Get payments for this transaction
                payments = Payment.objects.filter(transaction=transaction)
                if payments.exists():
                    payment_serializer = PaymentSerializer(payments, many=True)
                    restock_data["payments"] = payment_serializer.data
                else:
                    restock_data["payments"] = []
            except ObjectDoesNotExist:
                restock_data["transaction_info"] = None
                restock_data["payments"] = []

        return Response(serializer.data)
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

        # Update inventory - add the restocked quantity
        try:
            inventory = Inventory.objects.get(prod=product)
            inventory.quantity += quantity
            inventory.save()
        except ObjectDoesNotExist:
            # If no inventory record exists, create one
            Inventory.objects.create(prod=product, quantity=quantity)

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
