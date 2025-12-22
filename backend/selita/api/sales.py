from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..models import Sales, Product, Users, Client, Inventory, Transaction, Payment
from ..serializers import (
    SalesSerializer,
    ProductSerializer,
    UserSerializer,
    ClientSerializer,
    InventorySerializer,
    TransactionSerializer,
    PaymentSerializer,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal


# ======== USERS ========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSales(request):
    try:
        sales = Sales.objects.all()
        serializer = SalesSerializer(sales, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSale(request, pk):
    try:
        # Retrieve sale record by primary key
        sale = Sales.objects.get(id=pk)
        sale_serializer = SalesSerializer(sale)

        # Extract product and user IDs from sale data
        prod_id = sale_serializer.data["prod"]
        user_id = sale_serializer.data["user"]

        # Retrieve and serialize product data
        try:
            product = Product.objects.get(id=prod_id)
            product_serializer = ProductSerializer(product)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Retrieve and serialize user data
        try:
            user = Users.objects.get(id=user_id)
            user_serializer = UserSerializer(user)
        except ObjectDoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Construct the response data
        response_data = sale_serializer.data
        response_data["product"] = product_serializer.data
        response_data["user"] = {
            "firstname": user_serializer.data["firstname"],
            "lastname": user_serializer.data["lastname"],
        }

        return Response(response_data)

    except Sales.DoesNotExist:
        return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def getProductsFromSales(request):
    try:
        sales = Sales.objects.select_related(
            "transaction", "transaction__client", "prod"
        ).all()
        sales_serializer = SalesSerializer(sales, many=True)

        # For each sale, retrieve and add the product and client data from transaction
        for sale_data in sales_serializer.data:
            prod_id = sale_data["prod"]
            transaction_id = sale_data["transaction"]

            try:
                product = Product.objects.get(id=prod_id)
                product_serializer = ProductSerializer(product)
                sale_data["product"] = product_serializer.data
            except Product.DoesNotExist:
                sale_data["product"] = {"error": "Product not found"}

            # Get client info from transaction
            try:
                transaction = Transaction.objects.get(id=transaction_id)
                if transaction.client:
                    client_serializer = ClientSerializer(transaction.client)
                    sale_data["client"] = {
                        "id": transaction.client.id,
                        "name": client_serializer.data["firstname"]
                        + " "
                        + client_serializer.data["lastname"],
                        "phone": client_serializer.data["phone"],
                        "address": client_serializer.data["address"],
                    }
                    # Add payment status
                    sale_data["payment_status"] = transaction.status
                else:
                    sale_data["client"] = {
                        "error": "No client associated with transaction"
                    }

            except Transaction.DoesNotExist:
                sale_data["client"] = {"error": "Transaction not found"}

        return Response(sales_serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getUsersFromSales(request):
    try:
        sales = Sales.objects.all()
        sales_serializer = SalesSerializer(sales, many=True)

        # For each sale, retrieve and add the user data
        for sale_data in sales_serializer.data:
            user_id = sale_data["user"]

            try:
                user = Users.objects.get(id=user_id)
                user_serializer = UserSerializer(user)
                sale_data["user"] = {
                    "firstname": user_serializer.data["firstname"],
                    "lastname": user_serializer.data["lastname"],
                }
            except Users.DoesNotExist:
                sale_data["user"] = {"error": "User not found"}

        return Response(sales_serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def paySale(request, pk):
    """Add a payment to a sale's transaction"""
    from ..models import ExchangeRate, Account

    try:
        sale = Sales.objects.select_related("transaction").get(id=pk)
        transaction = sale.transaction

        if transaction.status == "COMPLETED":
            return Response(
                {"error": "Sale already fully paid"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get payment details from request
        amount = Decimal(str(request.data.get("amount", 0)))
        payment_currency = request.data.get("currency", "EUR")
        payment_method = request.data.get("payment_method", "CASH")
        notes = request.data.get("notes", "")
        transaction_currency = transaction.currency
        pay_remaining = request.data.get("pay_remaining", False)  # User clicked MAX button

        if amount <= 0:
            return Response(
                {"error": "Payment amount must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate total paid so far (in transaction currency)
        total_paid = Payment.objects.filter(transaction=transaction).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")

        remaining = transaction.total_amount - total_paid

        # Convert payment amount to transaction currency if different
        amount_in_transaction_currency = amount
        exchange_rate = Decimal("1.0")
        
        if payment_currency != transaction_currency:
            try:
                # Get exchange rate: payment_currency -> transaction_currency
                # E.g., if paying in LEK for EUR transaction, get LEK -> EUR rate
                rate_obj = ExchangeRate.objects.get(
                    from_currency=payment_currency,
                    to_currency=transaction_currency
                )
                exchange_rate = rate_obj.rate
                amount_in_transaction_currency = amount * exchange_rate
            except ExchangeRate.DoesNotExist:
                return Response(
                    {"error": f"Exchange rate not found for {payment_currency} to {transaction_currency}. Please sync exchange rates."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # If pay_remaining is True, use exact remaining balance (avoids rounding issues)
        if pay_remaining:
            # Check that the converted amount is reasonably close to remaining (within 5%)
            tolerance = remaining * Decimal("0.05")  # 5% tolerance
            if abs(amount_in_transaction_currency - remaining) <= tolerance:
                amount_in_transaction_currency = remaining
            # If not close enough, fall through to normal validation

        # Check if payment amount exceeds remaining balance (compare in transaction currency)
        
        # Allow small tolerance for rounding errors (0.01)
        if amount_in_transaction_currency > remaining + Decimal("0.01"):
            return Response(
                {
                    "error": f"Payment amount ({amount_in_transaction_currency:.2f} {transaction_currency}) exceeds remaining balance ({remaining:.2f} {transaction_currency})"
                },
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

        # Generate default note if not provided
        if not notes or notes.strip() == "":
            method_label = "Cash" if payment_method == "CASH" else "Kartë"
            if payment_currency != transaction_currency:
                notes = f"Pagesë me {method_label}: {amount} {payment_currency} → {amount_in_transaction_currency:.2f} {transaction_currency}"
            else:
                notes = f"Pagesë me {method_label}: {amount} {payment_currency}"

        # Create payment record with original and converted amounts
        payment = Payment.objects.create(
            transaction=transaction,
            account=account,
            amount=amount_in_transaction_currency,  # Converted amount in transaction currency
            currency=transaction_currency,  # Transaction currency
            original_amount=amount,  # Original amount in payment currency
            original_currency=payment_currency,  # Payment currency used by customer
            exchange_rate=exchange_rate if payment_currency != transaction_currency else None,
            payment_method=payment_method,
            notes=notes,
        )

        # Update account balance (SALE = money coming in, so increase balance)
        # Note: Payment amount is stored in payment currency for the account
        account.current_balance += amount
        account.save()

        # Update transaction status
        new_total_paid = total_paid + amount_in_transaction_currency
        
        # Check completion with tolerance for rounding errors (0.01 tolerance)
        # This handles cases where currency conversion causes tiny discrepancies
        remaining_after_payment = transaction.total_amount - new_total_paid
        if remaining_after_payment <= Decimal("0.01"):
            # Transaction is effectively complete
            transaction.status = "COMPLETED"
            transaction.completed_date = timezone.now()
            # Ensure remaining shows as 0, not a tiny negative/positive value
            remaining_after_payment = Decimal("0.00")
        elif new_total_paid > 0:
            transaction.status = "PARTIAL"

        transaction.save()

        return Response(
            {
                "message": "Payment added successfully",
                "payment_id": payment.id,
                "transaction_status": transaction.status,
                "total_paid": float(new_total_paid),
                "remaining": float(remaining_after_payment),
                "payment_amount": float(amount),
                "payment_currency": payment_currency,
                "converted_amount": float(amount_in_transaction_currency),
                "transaction_currency": transaction_currency,
            }
        )

    except Sales.DoesNotExist:
        return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createSale(request):
    """Create a new sale with transaction and optional payment"""
    try:
        # Extract data from request
        client_id = request.data.get("client_id")
        product_id = request.data.get("prod")
        prod_price = Decimal(str(request.data.get("prod_price")))
        quantity = request.data.get("quantity")
        user_id = request.data.get("user")
        currency = request.data.get("currency", "EUR")
        payment_data = request.data.get("payment")  # Optional payment info

        # Validate inputs
        if not all([client_id, product_id, prod_price, quantity, user_id]):
            return Response(
                {
                    "error": "Missing required fields: client_id, prod, prod_price, quantity, user"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {"error": "Quantity must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if product exists and enough quantity is available
        try:
            product = Product.objects.get(id=product_id)
            inventory = Inventory.objects.get(prod=product)
            if inventory.quantity < quantity:
                return Response(
                    {"error": "Not enough product in inventory"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ObjectDoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Calculate total amount
        total_amount = prod_price * quantity

        # Create Transaction record
        transaction = Transaction.objects.create(
            transaction_type="SALE",
            client_id=client_id,
            total_amount=total_amount,
            currency=currency,
            status="PENDING",
            notes=f"Sale of {quantity} units of {product.name}",
        )

        # Create Sale record linked to transaction
        sale = Sales.objects.create(
            transaction=transaction,
            prod=product,
            prod_price=prod_price,
            user_id=user_id,
            quantity=quantity,
        )

        # Reduce inventory
        inventory.quantity -= quantity
        inventory.save()

        # If payment data provided, create payment
        if payment_data:
            payment_amount = Decimal(str(payment_data.get("amount", 0)))
            if payment_amount > 0:
                payment_method = payment_data.get("payment_method", "CASH")
                payment_currency = payment_data.get("currency", currency)
                
                # Determine account type based on payment method
                # CASH payment → CASH account, CARD payment → BANK account
                account_type = "CASH" if payment_method == "CASH" else "BANK"
                
                # Find the appropriate account based on type and currency
                from ..models import Account
                try:
                    account = Account.objects.get(
                        account_type=account_type,
                        currency=payment_currency
                    )
                except Account.DoesNotExist:
                    return Response(
                        {"error": f"No {account_type} account found for currency {payment_currency}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                
                payment = Payment.objects.create(
                    transaction=transaction,
                    account=account,
                    amount=payment_amount,
                    currency=payment_currency,
                    original_amount=payment_amount,  # Same currency, so original = converted
                    original_currency=payment_currency,
                    payment_method=payment_method,
                    notes=payment_data.get("notes", ""),
                )

                # Update account balance (SALE = money coming in, so increase balance)
                account.current_balance += payment_amount
                account.save()

                # Update transaction status based on payment
                if payment_amount >= total_amount:
                    transaction.status = "COMPLETED"
                    transaction.completed_date = timezone.now()
                elif payment_amount > 0:
                    transaction.status = "PARTIAL"
                transaction.save()

        return Response(
            {
                "message": "Sale created successfully!",
                "sale_id": sale.id,
                "transaction_id": transaction.id,
                "transaction_status": transaction.status,
                "total_amount": float(total_amount),
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getLastSoldPrice(request):
    client_id = request.query_params.get("client_id")
    product_id = request.query_params.get("product_id")

    if not client_id or not product_id:
        return Response(
            {"error": "client_id and product_id are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Get the latest sale for this client and product through transaction
        last_sale = (
            Sales.objects.filter(transaction__client_id=client_id, prod_id=product_id)
            .order_by("-sale_date")
            .first()
        )

        if last_sale:
            return Response({"price": last_sale.prod_price})
        else:
            return Response({"price": None})  # No previous sale found

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSaleDetails(request, pk):
    """Get detailed sale information including transaction and payment history"""
    try:
        # Retrieve sale with related transaction
        sale = Sales.objects.select_related(
            "transaction", "transaction__client", "prod"
        ).get(id=pk)
        
        # Build response data
        response_data = {
            "id": sale.id,
            "quantity": sale.quantity,
            "sale_date": sale.sale_date,
            "prod_price": float(sale.prod_price),
        }
        
        # Add product info
        if sale.prod:
            product_serializer = ProductSerializer(sale.prod)
            response_data["product"] = product_serializer.data
        
        # Add user info
        try:
            user = Users.objects.get(id=sale.user_id)
            response_data["user"] = {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
            }
        except Users.DoesNotExist:
            response_data["user"] = None
        
        # Add transaction and client info
        transaction = sale.transaction
        if transaction:
            transaction_serializer = TransactionSerializer(transaction)
            response_data["transaction"] = transaction_serializer.data
            
            # Add client info from transaction
            if transaction.client:
                client_serializer = ClientSerializer(transaction.client)
                response_data["client"] = {
                    "id": transaction.client.id,
                    "name": f"{client_serializer.data['firstname']} {client_serializer.data['lastname']}",
                    "firstname": client_serializer.data["firstname"],
                    "lastname": client_serializer.data["lastname"],
                    "phone": client_serializer.data["phone"],
                    "address": client_serializer.data["address"],
                    "city": client_serializer.data.get("city", ""),
                }
            
            # Get all payments for this transaction
            payments = Payment.objects.filter(transaction=transaction).order_by("payment_date")
            payment_serializer = PaymentSerializer(payments, many=True)
            response_data["payments"] = payment_serializer.data
            
            # Calculate payment summary
            total_paid = sum(float(p.amount) for p in payments)
            response_data["payment_summary"] = {
                "total_amount": float(transaction.total_amount),
                "total_paid": total_paid,
                "remaining": float(transaction.total_amount) - total_paid,
                "payment_count": len(payments),
            }
        
        return Response(response_data)
    
    except Sales.DoesNotExist:
        return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
