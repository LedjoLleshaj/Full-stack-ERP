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


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getRestocksBySupplier(request, supplier_id):
    """Get recent restocks for a specific supplier"""
    try:
        # Get restocks for this supplier through transaction
        restocks = Restock.objects.filter(
            transaction__supplier_id=supplier_id
        ).select_related('transaction', 'prod').order_by('-restock_date')[:10]
        
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
    from ..models import Account, ExchangeRate
    
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
        transaction_currency = transaction.currency
        
        if amount <= 0:
            return Response(
                {"error": "Payment amount must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Calculate total paid so far
        existing_payments = Payment.objects.filter(transaction=transaction)
        total_paid = sum(Decimal(str(p.amount)) for p in existing_payments)
        remaining = transaction.total_amount - total_paid
        
        # Convert payment amount to transaction currency if different
        amount_in_transaction_currency = amount
        exchange_rate = Decimal("1.0")
        
        if payment_currency != transaction_currency:
            try:
                rate_obj = ExchangeRate.objects.get(
                    from_currency=payment_currency,
                    to_currency=transaction_currency
                )
                exchange_rate = rate_obj.rate
                amount_in_transaction_currency = amount * exchange_rate
            except ExchangeRate.DoesNotExist:
                return Response(
                    {"error": f"Exchange rate not found for {payment_currency} to {transaction_currency}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # If paying exact remaining, use remaining amount to avoid rounding issues
        if pay_remaining:
            tolerance = remaining * Decimal("0.05")
            if abs(amount_in_transaction_currency - remaining) <= tolerance:
                amount_in_transaction_currency = remaining
        
        if amount_in_transaction_currency > remaining + Decimal('0.01'):
            return Response(
                {"error": f"Payment amount ({amount_in_transaction_currency}) exceeds remaining balance ({remaining})"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Auto-select account based on payment method and currency
        try:
            account_type = "CASH" if payment_method == "CASH" else "BANK"
            account = Account.objects.get(
                account_type=account_type,
                currency=payment_currency
            )
        except Account.DoesNotExist:
            return Response(
                {"error": f"No {account_type} account found for currency {payment_currency}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Create payment
        payment = Payment.objects.create(
            transaction=transaction,
            account=account,
            amount=amount_in_transaction_currency,
            currency=transaction_currency,
            original_amount=amount,
            original_currency=payment_currency,
            exchange_rate=exchange_rate if payment_currency != transaction_currency else None,
            payment_method=payment_method,
            notes=notes
        )
        
        # Decrease account balance (PURCHASE = money going out)
        account.current_balance -= amount
        account.save()
        
        # Update transaction status
        new_total_paid = total_paid + amount_in_transaction_currency
        if new_total_paid >= transaction.total_amount - Decimal('0.01'):
            transaction.status = 'COMPLETED'
            transaction.completed_date = timezone.now()
        elif new_total_paid > 0:
            transaction.status = 'PARTIAL'
        transaction.save()
        
        return Response({
            "message": "Payment recorded successfully",
            "payment_id": payment.id,
            "transaction_status": transaction.status,
            "total_paid": float(new_total_paid),
            "remaining": float(transaction.total_amount - new_total_paid)
        }, status=status.HTTP_201_CREATED)
        
    except ObjectDoesNotExist:
        return Response(
            {"error": "Restock not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


