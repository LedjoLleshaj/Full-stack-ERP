from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from erp.constants import DiscountType, TransactionStatus, TransactionType
from erp.permissions import IsManagerOrAbove, IsStaffOrAbove
from erp.utils.responses import api_error_handler, bad_request_response, not_found_response

from ..models import Payment, PaymentTerms, Product, Sales, TaxRate, Transaction, User
from ..serializers import (
    ClientSerializer,
    PaymentSerializer,
    ProductSerializer,
    SalesSerializer,
    TransactionSerializer,
)

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
@permission_classes([IsAuthenticated])
@api_error_handler
def getProductsFromSales(request):
    # Optimized query: load all related data in ONE query
    # Exclude RETURN transactions — only show original sales
    sales = Sales.objects.filter(
        transaction__transaction_type=TransactionType.SALE
    ).select_related(
        "prod",
        "transaction",
        "transaction__client",
        "user",
        "tax_rate",
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

        sale_data["tax_amount"] = float(sale.tax_amount)
        sale_data["tax_rate_name"] = sale.tax_rate.name if sale.tax_rate else None
        sale_data["discount_type"] = sale.discount_type
        sale_data["discount_value"] = float(sale.discount_value)
        sale_data["discount_amount"] = float(sale.discount_amount)

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
@permission_classes([IsStaffOrAbove])
@api_error_handler
def paySale(request, pk):
    """Add a payment to a sale's transaction"""
    from erp.services.payment_service import PaymentError, PaymentService

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
@permission_classes([IsStaffOrAbove])
@api_error_handler
def createSale(request):
    """Create a new sale with transaction and optional payment"""
    from erp.services.inventory_service import InventoryError, InventoryService
    from erp.services.payment_service import PaymentError, PaymentService
    
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
    subtotal = prod_price * quantity

    # Discount calculation
    discount_type = request.data.get("discount_type")
    discount_value = Decimal(str(request.data.get("discount_value", 0)))
    discount_amount = Decimal("0")
    if discount_type and discount_value > 0:
        if discount_type not in (DiscountType.PERCENT, DiscountType.FIXED):
            return bad_request_response("Invalid discount type. Use PERCENT or FIXED.")
        if discount_type == DiscountType.PERCENT:
            if discount_value > 100:
                return bad_request_response("Percentage discount cannot exceed 100%")
            discount_amount = (subtotal * discount_value / Decimal("100")).quantize(Decimal("0.01"))
        else:
            if discount_value > subtotal:
                return bad_request_response("Fixed discount cannot exceed subtotal")
            discount_amount = discount_value
    else:
        discount_type = None
        discount_value = Decimal("0")

    discounted_subtotal = subtotal - discount_amount

    # Tax calculation (on discounted subtotal)
    tax_rate_id = request.data.get("tax_rate_id")
    tax_rate_obj = None
    tax_amount = Decimal("0")
    if tax_rate_id:
        try:
            tax_rate_obj = TaxRate.objects.get(id=tax_rate_id, is_active=True)
            tax_amount = (discounted_subtotal * tax_rate_obj.rate / Decimal("100")).quantize(Decimal("0.01"))
        except TaxRate.DoesNotExist:
            return bad_request_response("Tax rate not found or inactive")

    total_amount = discounted_subtotal + tax_amount

    # Resolve payment terms
    payment_terms_id = request.data.get("payment_terms_id")
    payment_terms = None
    if payment_terms_id:
        try:
            payment_terms = PaymentTerms.objects.get(id=payment_terms_id, is_active=True)
        except PaymentTerms.DoesNotExist:
            return bad_request_response("Payment terms not found or inactive")

    # Create Transaction record
    transaction = Transaction.objects.create(
        transaction_type=TransactionType.SALE,
        client_id=client_id,
        total_amount=total_amount,
        currency=currency,
        status=TransactionStatus.PENDING,
        payment_terms=payment_terms,
        notes=f"Sale of {quantity} units of {product.name}",
    )

    # Create Sale record linked to transaction
    sale = Sales.objects.create(
        transaction=transaction,
        prod=product,
        prod_price=prod_price,
        user_id=user_id,
        quantity=quantity,
        tax_rate=tax_rate_obj,
        tax_amount=tax_amount,
        discount_type=discount_type,
        discount_value=discount_value,
        discount_amount=discount_amount,
    )

    # Use InventoryService to reduce inventory (disallow overselling)
    try:
        InventoryService.reduce_inventory(product, quantity, allow_negative=False)
    except InventoryError:
        # Rollback: delete the sale and transaction we just created
        sale.delete()
        transaction.delete()
        return bad_request_response(
            f"Insufficient inventory for {product.name}. "
            f"Available: {InventoryService.available_stock(product)}, Requested: {quantity}"
        )

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
            "tax_amount": float(tax_amount),
            "discount_amount": float(discount_amount),
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
            "transaction", "transaction__client", "prod", "tax_rate"
        ).get(id=pk)
    except Sales.DoesNotExist:
        return not_found_response("Sale")
    
    # Build response data
    response_data = {
        "id": sale.id,
        "quantity": sale.quantity,
        "sale_date": sale.sale_date,
        "prod_price": float(sale.prod_price),
        "tax_amount": float(sale.tax_amount),
        "tax_rate_name": sale.tax_rate.name if sale.tax_rate else None,
        "tax_rate_percent": float(sale.tax_rate.rate) if sale.tax_rate else None,
        "discount_type": sale.discount_type,
        "discount_value": float(sale.discount_value),
        "discount_amount": float(sale.discount_amount),
    }
    
    # Add product info
    if sale.prod:
        product_serializer = ProductSerializer(sale.prod)
        response_data["product"] = product_serializer.data
    
    # Add user info
    try:
        user = User.objects.get(id=sale.user_id)
        response_data["user"] = {
            "id": user.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
        }
    except User.DoesNotExist:
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

        # Get linked returns
        return_txs = Transaction.objects.filter(
            original_transaction=transaction,
            transaction_type=TransactionType.RETURN,
        ).order_by("-created_date")

        returns_data = []
        for ret in return_txs:
            ret_items = Sales.objects.filter(transaction=ret).select_related("prod")
            ret_payments = Payment.objects.filter(transaction=ret)
            refund = sum(float(p.amount) for p in ret_payments)
            returns_data.append({
                "id": ret.id,
                "return_date": ret.created_date.isoformat(),
                "return_value": float(ret.total_amount),
                "refund_amount": refund,
                "notes": ret.notes,
                "items": [
                    {
                        "product_name": s.prod.name,
                        "quantity": s.quantity,
                        "unit_price": float(s.prod_price),
                    }
                    for s in ret_items
                ],
            })
        response_data["returns"] = returns_data

        # Already-returned quantities per product
        already_returned = {}
        sale_lines = Sales.objects.filter(transaction=transaction)
        for sl in sale_lines:
            returned_qty = Sales.objects.filter(
                transaction__original_transaction=transaction,
                transaction__transaction_type=TransactionType.RETURN,
                prod=sl.prod,
            ).aggregate(total=Sum("quantity"))["total"] or 0
            already_returned[str(sl.prod_id)] = returned_qty
        response_data["already_returned"] = already_returned

    return Response(response_data)


@api_view(["PUT"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def updateSale(request, pk):
    """Update an existing sale with validation to prevent overpayment"""
    from erp.services.inventory_service import InventoryService
    from erp.services.payment_service import PaymentError, PaymentService
    
    try:
        sale = Sales.objects.select_related('transaction', 'prod', 'user').get(id=pk)
    except Sales.DoesNotExist:
        return not_found_response("Sale")
    
    transaction = sale.transaction
    
    # Store old values for inventory reversal
    old_quantity = sale.quantity
    old_prod_id = sale.prod_id
    old_product = sale.prod
    
    # Get new values from request
    new_prod_id = request.data.get("prod", old_prod_id)
    new_quantity = Decimal(str(request.data.get("quantity", old_quantity)))
    new_prod_price = Decimal(str(request.data.get("prod_price", sale.prod_price)))
    new_user_id = request.data.get("user", sale.user_id)
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
    
    # Calculate new total
    new_subtotal = new_prod_price * new_quantity

    # Discount calculation
    discount_type = request.data.get("discount_type", sale.discount_type)
    discount_value = Decimal(str(request.data.get("discount_value", sale.discount_value)))
    discount_amount = Decimal("0")
    if discount_type and discount_value > 0:
        if discount_type not in (DiscountType.PERCENT, DiscountType.FIXED):
            return bad_request_response("Invalid discount type. Use PERCENT or FIXED.")
        if discount_type == DiscountType.PERCENT:
            if discount_value > 100:
                return bad_request_response("Percentage discount cannot exceed 100%")
            discount_amount = (new_subtotal * discount_value / Decimal("100")).quantize(Decimal("0.01"))
        else:
            if discount_value > new_subtotal:
                return bad_request_response("Fixed discount cannot exceed subtotal")
            discount_amount = discount_value
    else:
        discount_type = None
        discount_value = Decimal("0")

    discounted_subtotal = new_subtotal - discount_amount

    # Tax calculation (on discounted subtotal)
    tax_rate_id = request.data.get("tax_rate_id")
    tax_rate_obj = None
    tax_amount = Decimal("0")
    if tax_rate_id:
        try:
            tax_rate_obj = TaxRate.objects.get(id=tax_rate_id, is_active=True)
            tax_amount = (discounted_subtotal * tax_rate_obj.rate / Decimal("100")).quantize(Decimal("0.01"))
        except TaxRate.DoesNotExist:
            return bad_request_response("Tax rate not found or inactive")

    new_total_with_tax = discounted_subtotal + tax_amount

    # Handle inventory changes
    if new_prod_id != old_prod_id:
        # Product changed: reverse old, add new
        InventoryService.add_inventory(old_product, old_quantity)
        if not InventoryService.check_availability(new_product, new_quantity):
            return bad_request_response(f"Not enough {new_product.name} in inventory")
        InventoryService.reduce_inventory(new_product, new_quantity, allow_negative=True)
    else:
        # Same product, quantity changed
        quantity_diff = new_quantity - old_quantity
        if quantity_diff > 0:
            # Need more inventory
            if not InventoryService.check_availability(new_product, quantity_diff):
                return bad_request_response(f"Not enough {new_product.name} in inventory")
            InventoryService.reduce_inventory(new_product, quantity_diff, allow_negative=True)
        elif quantity_diff < 0:
            # Returning inventory
            InventoryService.add_inventory(new_product, abs(quantity_diff))
    
    # Update sale record
    sale.prod = new_product
    sale.quantity = new_quantity
    sale.prod_price = new_prod_price
    sale.user_id = new_user_id
    sale.tax_rate = tax_rate_obj
    sale.tax_amount = tax_amount
    sale.discount_type = discount_type
    sale.discount_value = discount_value
    sale.discount_amount = discount_amount
    sale.save()
    
    # Update transaction details and status via PaymentService
    try:
        PaymentService.update_transaction_status(
            transaction=transaction,
            new_total_amount=new_total_with_tax,
            transaction_currency=currency
        )
        # Recalculate total_paid for response after update
        total_paid = PaymentService.calculate_total_paid(transaction)
    except PaymentError as e:
        return bad_request_response(str(e))
    
    return Response({
        "message": "Sale updated successfully",
        "sale_id": sale.id,
        "transaction_id": transaction.id,
        "transaction_status": transaction.status,
        "total_amount": float(new_total_with_tax),
        "total_paid": float(total_paid),
        "remaining": float(new_total_with_tax - total_paid),
    })


@api_view(["DELETE"])
@permission_classes([IsManagerOrAbove])
@api_error_handler
def deleteSale(request, pk):
    """Delete a sale and reverse all its effects (payments, inventory)"""
    from django.db import transaction as db_transaction

    from erp.services.inventory_service import InventoryService
    from erp.services.payment_service import PaymentService
    
    try:
        sale = Sales.objects.select_related('transaction', 'prod').get(id=pk)
    except Sales.DoesNotExist:
        return not_found_response("Sale")
    
    transaction = sale.transaction
    product = sale.prod
    quantity = sale.quantity
    
    # Wrap entire delete operation in atomic transaction for consistency
    with db_transaction.atomic():
        # CRITICAL: Reverse all payments FIRST (before deleting)
        reversal_result = PaymentService.reverse_all_payments(transaction)
        
        # Reverse inventory (add back the sold quantity)
        InventoryService.add_inventory(product, quantity)
        
        # Store info for response
        sale_id = sale.id
        transaction_id = transaction.id
        
        # Delete the transaction (CASCADE will delete Sale and Payments)
        transaction.delete()
    
    return Response({
        "message": "Sale deleted successfully",
        "sale_id": sale_id,
        "transaction_id": transaction_id,
        "inventory_restored": float(quantity),
        "product_name": product.name,
        "payments_reversed": reversal_result["payment_count"],
        "total_reversed": reversal_result["total_reversed"],
        "accounts_affected": reversal_result["accounts_affected"],
    })
