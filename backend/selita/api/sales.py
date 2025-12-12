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
    try:
        sale = Sales.objects.select_related("transaction").get(id=pk)
        transaction = sale.transaction

        if transaction.status == "COMPLETED":
            return Response(
                {"error": "Sale already fully paid"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get payment details from request
        account_id = request.data.get("account_id")
        amount = Decimal(str(request.data.get("amount", 0)))
        currency = request.data.get("currency", "EUR")
        payment_method = request.data.get("payment_method", "CASH")
        notes = request.data.get("notes", "")

        if amount <= 0:
            return Response(
                {"error": "Payment amount must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate total paid so far
        total_paid = Payment.objects.filter(transaction=transaction).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")

        # Check if payment amount exceeds remaining balance
        remaining = transaction.total_amount - total_paid
        if amount > remaining:
            return Response(
                {
                    "error": f"Payment amount ({amount}) exceeds remaining balance ({remaining})"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create payment record
        payment = Payment.objects.create(
            transaction=transaction,
            account_id=account_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            notes=notes,
        )

        # Update transaction status
        new_total_paid = total_paid + amount
        if new_total_paid >= transaction.total_amount:
            transaction.status = "COMPLETED"
            transaction.completed_date = timezone.now()
        elif new_total_paid > 0:
            transaction.status = "PARTIAL"

        transaction.save()

        return Response(
            {
                "message": "Payment added successfully",
                "payment_id": payment.id,
                "transaction_status": transaction.status,
                "total_paid": float(new_total_paid),
                "remaining": float(transaction.total_amount - new_total_paid),
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
                    payment_method=payment_method,
                    notes=payment_data.get("notes", ""),
                )

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
