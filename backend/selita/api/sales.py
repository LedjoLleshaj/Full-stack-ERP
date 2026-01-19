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
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal
from selita.utils.responses import api_error_handler, not_found_response, bad_request_response


# ======== SALES ========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getSales(request):
    sales = Sales.objects.all()
    serializer = SalesSerializer(sales, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getSale(request, pk):
    try:
        # Retrieve sale record with related data in ONE query
        sale = Sales.objects.select_related('prod', 'user').get(id=pk)
    except Sales.DoesNotExist:
        return not_found_response("Sale")
    
    sale_serializer = SalesSerializer(sale)
    response_data = sale_serializer.data
    
    # Product info (already loaded via select_related)
    if sale.prod:
        product_serializer = ProductSerializer(sale.prod)
        response_data["product"] = product_serializer.data
    else:
        return not_found_response("Product")
    
    # User info (already loaded via select_related)
    if sale.user:
        response_data["user"] = {
            "firstname": sale.user.firstname,
            "lastname": sale.user.lastname,
        }
    else:
        return not_found_response("User")
    
    return Response(response_data)


@api_view(["GET"])
#@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getProductsFromSales(request):
    # Optimized query: load all related data in ONE query
    sales = Sales.objects.select_related(
        "prod",
        "transaction",
        "transaction__client",
        "user"
    ).order_by("-sale_date")
    
    # Build response data directly from prefetched objects (no additional queries)
    results = []
    for sale in sales:
        sale_data = {
            "id": sale.id,
            "prod": sale.prod_id,
            "quantity": float(sale.quantity),
            "prod_price": float(sale.prod_price),
            "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
            "transaction": sale.transaction_id,
            "user": sale.user_id,
        }
        
        # Product info (already loaded via select_related)
        if sale.prod:
            sale_data["product"] = {
                "id": sale.prod.id,
                "name": sale.prod.name,
                "category": sale.prod.category,
                "price": float(sale.prod.price) if sale.prod.price else None,
                "description": sale.prod.description,
            }
        else:
            sale_data["product"] = {"error": "Product not found"}
        
        # Client info (already loaded via select_related on transaction__client)
        if sale.transaction and sale.transaction.client:
            client = sale.transaction.client
            sale_data["client"] = {
                "id": client.id,
                "name": f"{client.firstname} {client.lastname}",
                "phone": client.phone,
                "address": client.address,
            }
            sale_data["payment_status"] = sale.transaction.status
            sale_data["currency"] = sale.transaction.currency
        else:
            sale_data["client"] = {"error": "No client associated with transaction"}
            sale_data["payment_status"] = None
            sale_data["currency"] = None
        
        results.append(sale_data)
    
    return Response(results)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getUsersFromSales(request):
    # Optimized: Use select_related to load user data in ONE query
    sales = Sales.objects.select_related('user').all()
    
    # Build response directly from prefetched data (no additional queries)
    results = []
    for sale in sales:
        sale_data = {
            "id": sale.id,
            "prod": sale.prod_id,
            "quantity": float(sale.quantity),
            "prod_price": float(sale.prod_price),
            "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
            "transaction": sale.transaction_id,
        }
        
        # User info (already loaded via select_related)
        if sale.user:
            sale_data["user"] = {
                "firstname": sale.user.firstname,
                "lastname": sale.user.lastname,
            }
        else:
            sale_data["user"] = {"error": "User not found"}
        
        results.append(sale_data)
    
    return Response(results)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@api_error_handler
def paySale(request, pk):
    """Add a payment to a sale's transaction"""
    from selita.services.payment_service import PaymentService, PaymentError

    try:
        sale = Sales.objects.select_related("transaction").get(id=pk)
    except Sales.DoesNotExist:
        return not_found_response("Sale")
    
    transaction = sale.transaction

    # Get payment details from request
    amount = Decimal(str(request.data.get("amount", 0)))
    payment_currency = request.data.get("currency", "EUR")
    payment_method = request.data.get("payment_method", "CASH")
    notes = request.data.get("notes", "")
    pay_remaining = request.data.get("pay_remaining", False)

    # Generate default note if not provided
    if not notes or notes.strip() == "":
        method_label = "Cash" if payment_method == "CASH" else "Kartë"
        notes = f"Pagesë me {method_label}: {amount} {payment_currency}"

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
        "message": "Payment added successfully",
        "payment_id": result["payment_id"],
        "transaction_status": result["transaction_status"],
        "total_paid": result["total_paid"],
        "remaining": result["remaining"],
        "payment_amount": float(amount),
        "payment_currency": payment_currency,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@api_error_handler
def createSale(request):
    """Create a new sale with transaction and optional payment"""
    from selita.services.inventory_service import InventoryService, InventoryError
    from selita.services.payment_service import PaymentService, PaymentError
    
    # Extract data from request
    client_id = request.data.get("client_id")
    product_id = request.data.get("prod")
    prod_price = Decimal(str(request.data.get("prod_price")))
    quantity = Decimal(str(request.data.get("quantity")))
    user_id = request.data.get("user")
    currency = request.data.get("currency", "EUR")
    payment_data = request.data.get("payment")  # Optional payment info

    # Validate inputs
    if not all([client_id, product_id, prod_price, quantity, user_id]):
        return bad_request_response("Missing required fields: client_id, prod, prod_price, quantity, user")

    if quantity <= 0:
        return bad_request_response("Quantity must be greater than zero")

    # Check if product exists
    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        return not_found_response("Product")
    
    # Use InventoryService to check availability
    if not InventoryService.check_availability(product, quantity):
        return bad_request_response("Not enough product in inventory")

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

    # Use InventoryService to reduce inventory
    InventoryService.reduce_inventory(product, quantity, allow_negative=True)

    # If payment data provided, use PaymentService
    if payment_data:
        payment_amount = Decimal(str(payment_data.get("amount", 0)))
        if payment_amount > 0:
            try:
                PaymentService.create_payment(
                    transaction=transaction,
                    amount=payment_amount,
                    payment_currency=payment_data.get("currency", currency),
                    payment_method=payment_data.get("payment_method", "CASH"),
                    notes=payment_data.get("notes", ""),
                )
            except PaymentError as e:
                # Payment failed but sale was created - log and continue
                transaction.notes += f" (Payment failed: {str(e)})"
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getLastSoldPrice(request):
    client_id = request.query_params.get("client_id")
    product_id = request.query_params.get("product_id")

    if not client_id or not product_id:
        return bad_request_response("client_id and product_id are required")

    # Get the latest sale for this client and product through transaction
    last_sale = (
        Sales.objects.filter(transaction__client_id=client_id, prod_id=product_id)
        .select_related('transaction')
        .order_by("-sale_date")
        .first()
    )

    if last_sale:
        return Response({
            "price": last_sale.prod_price,
            "currency": last_sale.transaction.currency
        })
    else:
        return Response({"price": None, "currency": None})  # No previous sale found


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getSaleDetails(request, pk):
    """Get detailed sale information including transaction and payment history"""
    try:
        # Retrieve sale with related transaction
        sale = Sales.objects.select_related(
            "transaction", "transaction__client", "prod"
        ).get(id=pk)
    except Sales.DoesNotExist:
        return not_found_response("Sale")
    
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
