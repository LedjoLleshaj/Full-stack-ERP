from decimal import Decimal

from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from erp.constants import DiscountType, TransactionStatus, TransactionType
from erp.permissions import IsManagerOrAbove, IsStaffOrAbove
from erp.utils.responses import api_error_handler, bad_request_response, not_found_response

from ..models import Client, Payment, PaymentTerms, Product, Sales, TaxRate, Transaction
from ..serializers import (
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
    """Return sales grouped by transaction (one row per transaction)"""
    transactions = Transaction.objects.filter(
        transaction_type=TransactionType.SALE
    ).select_related("client").prefetch_related("sales__prod").order_by("-created_date")

    results = []
    for tx in transactions:
        sale_lines = list(tx.sales.all())
        if not sale_lines:
            continue

        product_names = ", ".join(s.prod.name for s in sale_lines if s.prod)
        if len(product_names) > 60:
            product_names = product_names[:57] + "..."

        results.append({
            "transaction_id": tx.id,
            "products": product_names,
            "item_count": len(sale_lines),
            "total_amount": float(tx.total_amount),
            "currency": tx.currency,
            "sale_date": tx.created_date.isoformat(),
            "payment_status": tx.status,
            "client": {
                "id": tx.client.id,
                "name": f"{tx.client.firstname} {tx.client.lastname}",
                "phone": tx.client.phone,
                "address": tx.client.address,
            } if tx.client else {"name": "N/A", "phone": "", "address": ""},
        })

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
    """Create a new sale with multiple line items and optional payment"""
    from django.db import transaction as db_transaction

    from erp.services.inventory_service import InventoryError, InventoryService
    from erp.services.payment_service import PaymentError, PaymentService

    client_id = request.data.get("client_id")
    items = request.data.get("items", [])
    currency = request.data.get("currency", "EUR")
    payment_data = request.data.get("payment")
    user_id = request.user.id

    if not client_id:
        return bad_request_response("Missing required field: client_id")
    try:
        Client.objects.get(id=client_id, is_active=True)
    except Client.DoesNotExist:
        return bad_request_response("Client not found or inactive")
    if not items:
        return bad_request_response("At least one item is required")

    payment_terms_id = request.data.get("payment_terms_id")
    payment_terms = None
    if payment_terms_id:
        try:
            payment_terms = PaymentTerms.objects.get(id=payment_terms_id, is_active=True)
        except PaymentTerms.DoesNotExist:
            return bad_request_response("Payment terms not found or inactive")

    # Validate all items upfront before creating anything
    validated_items = []
    for idx, item in enumerate(items):
        product_id = item.get("prod")
        prod_price = item.get("prod_price")
        quantity = item.get("quantity")

        if product_id is None or prod_price is None or quantity is None:
            return bad_request_response(f"Item {idx + 1}: missing required fields (prod, prod_price, quantity)")

        prod_price = Decimal(str(prod_price))
        quantity = Decimal(str(quantity))
        if quantity <= 0:
            return bad_request_response(f"Item {idx + 1}: quantity must be greater than zero")

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return bad_request_response(f"Item {idx + 1}: product not found or inactive")

        if not InventoryService.check_availability(product, quantity):
            return bad_request_response(
                f"Item {idx + 1}: insufficient inventory for {product.name}. "
                f"Available: {InventoryService.available_stock(product)}, Requested: {quantity}"
            )

        subtotal = prod_price * quantity

        discount_type = item.get("discount_type")
        discount_value = Decimal(str(item.get("discount_value", 0)))
        discount_amount = Decimal("0")
        if discount_type and discount_value > 0:
            if discount_type not in (DiscountType.PERCENT, DiscountType.FIXED):
                return bad_request_response(f"Item {idx + 1}: invalid discount type")
            if discount_type == DiscountType.PERCENT:
                if discount_value > 100:
                    return bad_request_response(f"Item {idx + 1}: percentage discount cannot exceed 100%")
                discount_amount = (subtotal * discount_value / Decimal("100")).quantize(Decimal("0.01"))
            else:
                if discount_value > subtotal:
                    return bad_request_response(f"Item {idx + 1}: fixed discount cannot exceed subtotal")
                discount_amount = discount_value
        else:
            discount_type = None
            discount_value = Decimal("0")

        discounted_subtotal = subtotal - discount_amount

        tax_rate_id = item.get("tax_rate_id")
        tax_rate_obj = None
        tax_amount = Decimal("0")
        if tax_rate_id:
            try:
                tax_rate_obj = TaxRate.objects.get(id=tax_rate_id, is_active=True)
                tax_amount = (discounted_subtotal * tax_rate_obj.rate / Decimal("100")).quantize(Decimal("0.01"))
            except TaxRate.DoesNotExist:
                return bad_request_response(f"Item {idx + 1}: tax rate not found or inactive")

        line_total = discounted_subtotal + tax_amount

        validated_items.append({
            "product": product,
            "prod_price": prod_price,
            "quantity": quantity,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "discount_amount": discount_amount,
            "tax_rate_obj": tax_rate_obj,
            "tax_amount": tax_amount,
            "line_total": line_total,
        })

    grand_total = sum(v["line_total"] for v in validated_items)

    payment_warning = None
    try:
        with db_transaction.atomic():
            product_names = ", ".join(v["product"].name for v in validated_items)
            transaction = Transaction.objects.create(
                transaction_type=TransactionType.SALE,
                client_id=client_id,
                total_amount=grand_total,
                currency=currency,
                status=TransactionStatus.PENDING,
                payment_terms=payment_terms,
                notes=f"Sale: {product_names}",
            )

            sale_ids = []
            items_response = []
            for v in validated_items:
                sale = Sales.objects.create(
                    transaction=transaction,
                    prod=v["product"],
                    prod_price=v["prod_price"],
                    user_id=user_id,
                    quantity=v["quantity"],
                    tax_rate=v["tax_rate_obj"],
                    tax_amount=v["tax_amount"],
                    discount_type=v["discount_type"],
                    discount_value=v["discount_value"],
                    discount_amount=v["discount_amount"],
                )
                InventoryService.reduce_inventory(v["product"], v["quantity"], allow_negative=False)
                sale_ids.append(sale.id)
                items_response.append({
                    "sale_id": sale.id,
                    "product_id": v["product"].id,
                    "product_name": v["product"].name,
                    "quantity": float(v["quantity"]),
                    "prod_price": float(v["prod_price"]),
                    "tax_amount": float(v["tax_amount"]),
                    "discount_amount": float(v["discount_amount"]),
                    "line_total": float(v["line_total"]),
                })

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
                        transaction.notes += f" (Payment failed: {str(e)})"
                        transaction.save()
                        payment_warning = str(e)

    except InventoryError as e:
        return bad_request_response(str(e))

    transaction.refresh_from_db()
    return Response(
        {
            "message": "Sale created successfully!",
            "transaction_id": transaction.id,
            "transaction_status": transaction.status,
            "total_amount": float(grand_total),
            "items": items_response,
            "payment_warning": payment_warning,
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
@permission_classes([IsStaffOrAbove])
@api_error_handler
def getSaleDetails(request, pk):
    """Get detailed sale information by transaction ID, including all line items"""
    try:
        transaction = Transaction.objects.select_related(
            "client", "payment_terms"
        ).get(id=pk, transaction_type=TransactionType.SALE)
    except Transaction.DoesNotExist:
        return not_found_response("Sale transaction")

    sale_lines = Sales.objects.filter(
        transaction=transaction
    ).select_related("prod", "tax_rate", "user").order_by("id")

    items_data = []
    for sale in sale_lines:
        subtotal = float(sale.prod_price) * float(sale.quantity)
        discount_amt = float(sale.discount_amount)
        tax_amt = float(sale.tax_amount)
        line_total = subtotal - discount_amt + tax_amt

        items_data.append({
            "id": sale.id,
            "product": ProductSerializer(sale.prod).data if sale.prod else None,
            "quantity": sale.quantity,
            "prod_price": float(sale.prod_price),
            "tax_rate_name": sale.tax_rate.name if sale.tax_rate else None,
            "tax_rate_percent": float(sale.tax_rate.rate) if sale.tax_rate else None,
            "tax_amount": float(sale.tax_amount),
            "discount_type": sale.discount_type,
            "discount_value": float(sale.discount_value),
            "discount_amount": float(sale.discount_amount),
            "line_total": round(line_total, 2),
        })

    response_data = {
        "transaction": TransactionSerializer(transaction).data,
        "items": items_data,
    }

    if transaction.client:
        client = transaction.client
        response_data["client"] = {
            "id": client.id,
            "name": f"{client.firstname} {client.lastname}",
            "firstname": client.firstname,
            "lastname": client.lastname,
            "phone": client.phone,
            "address": client.address,
            "city": getattr(client, "city", ""),
        }

    payments = list(Payment.objects.filter(transaction=transaction).order_by("payment_date"))
    response_data["payments"] = PaymentSerializer(payments, many=True).data

    total_paid = sum(float(p.amount) for p in payments)
    response_data["payment_summary"] = {
        "total_amount": float(transaction.total_amount),
        "total_paid": total_paid,
        "remaining": float(transaction.total_amount) - total_paid,
        "payment_count": len(payments),
    }

    return_txs = Transaction.objects.filter(
        original_transaction=transaction,
        transaction_type=TransactionType.RETURN,
    ).prefetch_related("sales__prod", "payments").order_by("-created_date")

    returns_data = []
    for ret in return_txs:
        ret_items = ret.sales.select_related("prod").all()
        ret_payments = ret.payments.all()
        refund = sum(float(p.amount) for p in ret_payments)
        returns_data.append({
            "id": ret.id,
            "return_date": ret.created_date.isoformat(),
            "return_value": float(ret.total_amount),
            "refund_amount": refund,
            "notes": ret.notes,
            "items": [
                {
                    "product_name": s.prod.name if s.prod else "Unknown",
                    "quantity": s.quantity,
                    "unit_price": float(s.prod_price),
                }
                for s in ret_items
            ],
        })
    response_data["returns"] = returns_data

    returned_rows = Sales.objects.filter(
        transaction__original_transaction=transaction,
        transaction__transaction_type=TransactionType.RETURN,
    ).values("prod_id").annotate(total=Sum("quantity"))
    already_returned = {str(row["prod_id"]): row["total"] for row in returned_rows}
    response_data["already_returned"] = already_returned

    return Response(response_data)


@api_view(["PUT"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def updateSale(request, pk):
    """Update a sale transaction with multiple line items (replace strategy)"""
    from django.db import transaction as db_transaction

    from erp.services.inventory_service import InventoryError, InventoryService
    from erp.services.payment_service import PaymentError, PaymentService

    try:
        transaction = Transaction.objects.get(id=pk, transaction_type=TransactionType.SALE)
    except Transaction.DoesNotExist:
        return not_found_response("Sale transaction")

    items = request.data.get("items", [])
    if not items:
        return bad_request_response("At least one item is required")

    currency = request.data.get("currency", transaction.currency)
    old_sales = {s.id: s for s in Sales.objects.filter(transaction=transaction).select_related("prod")}

    # Validate item IDs belong to this transaction
    for item in items:
        item_id = item.get("id")
        if item_id and item_id not in old_sales:
            return bad_request_response(f"Item ID {item_id} does not belong to this transaction")

    # Validate all new/updated items
    validated_items = []
    for idx, item in enumerate(items):
        product_id = item.get("prod")
        prod_price_raw = item.get("prod_price")
        quantity_raw = item.get("quantity")

        if product_id is None or prod_price_raw is None or quantity_raw is None:
            return bad_request_response(f"Item {idx + 1}: missing required fields")

        prod_price = Decimal(str(prod_price_raw))
        quantity = Decimal(str(quantity_raw))
        if quantity <= 0:
            return bad_request_response(f"Item {idx + 1}: quantity must be greater than zero")

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return bad_request_response(f"Item {idx + 1}: product not found or inactive")

        subtotal = prod_price * quantity

        discount_type = item.get("discount_type")
        discount_value = Decimal(str(item.get("discount_value", 0)))
        discount_amount = Decimal("0")
        if discount_type and discount_value > 0:
            if discount_type not in (DiscountType.PERCENT, DiscountType.FIXED):
                return bad_request_response(f"Item {idx + 1}: invalid discount type")
            if discount_type == DiscountType.PERCENT:
                if discount_value > 100:
                    return bad_request_response(f"Item {idx + 1}: percentage discount cannot exceed 100%")
                discount_amount = (subtotal * discount_value / Decimal("100")).quantize(Decimal("0.01"))
            else:
                if discount_value > subtotal:
                    return bad_request_response(f"Item {idx + 1}: fixed discount cannot exceed subtotal")
                discount_amount = discount_value
        else:
            discount_type = None
            discount_value = Decimal("0")

        discounted_subtotal = subtotal - discount_amount

        tax_rate_id = item.get("tax_rate_id")
        tax_rate_obj = None
        tax_amount = Decimal("0")
        if tax_rate_id:
            try:
                tax_rate_obj = TaxRate.objects.get(id=tax_rate_id, is_active=True)
                tax_amount = (discounted_subtotal * tax_rate_obj.rate / Decimal("100")).quantize(Decimal("0.01"))
            except TaxRate.DoesNotExist:
                return bad_request_response(f"Item {idx + 1}: tax rate not found or inactive")

        line_total = discounted_subtotal + tax_amount

        validated_items.append({
            "id": item.get("id"),
            "product": product,
            "prod_price": prod_price,
            "quantity": quantity,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "discount_amount": discount_amount,
            "tax_rate_obj": tax_rate_obj,
            "tax_amount": tax_amount,
            "line_total": line_total,
        })

    new_total = sum(v["line_total"] for v in validated_items)
    new_item_ids = {v["id"] for v in validated_items if v["id"]}
    removed_ids = set(old_sales.keys()) - new_item_ids

    # Check inventory for new/changed items before committing
    for v in validated_items:
        old_sale = old_sales.get(v["id"])
        if old_sale:
            if old_sale.prod_id == v["product"].id:
                extra_needed = v["quantity"] - old_sale.quantity
                if extra_needed > 0 and not InventoryService.check_availability(v["product"], extra_needed):
                    return bad_request_response(f"Insufficient inventory for {v['product'].name}")
            else:
                if not InventoryService.check_availability(v["product"], v["quantity"]):
                    return bad_request_response(f"Insufficient inventory for {v['product'].name}")
        else:
            if not InventoryService.check_availability(v["product"], v["quantity"]):
                return bad_request_response(f"Insufficient inventory for {v['product'].name}")

    # Validate client_id before entering the atomic block
    client_id = request.data.get("client_id")
    if client_id:
        try:
            Client.objects.get(id=client_id, is_active=True)
        except Client.DoesNotExist:
            return bad_request_response("Client not found or inactive")

    # Validate payment_terms_id before entering the atomic block so a failure
    # doesn't leave preceding inventory/sales writes committed without saving the total.
    payment_terms_id = request.data.get("payment_terms_id")
    payment_terms = None
    if payment_terms_id:
        try:
            payment_terms = PaymentTerms.objects.get(id=payment_terms_id, is_active=True)
        except PaymentTerms.DoesNotExist:
            return bad_request_response("Payment terms not found or inactive")

    try:
        with db_transaction.atomic():
            # Remove deleted items — restore inventory
            for rid in removed_ids:
                old = old_sales[rid]
                InventoryService.add_inventory(old.prod, old.quantity)
                old.delete()

            # Update/create items
            user_id = request.user.id
            for v in validated_items:
                old_sale = old_sales.get(v["id"])
                if old_sale:
                    # Reverse old inventory, then re-apply new
                    InventoryService.add_inventory(old_sale.prod, old_sale.quantity)
                    old_sale.prod = v["product"]
                    old_sale.prod_price = v["prod_price"]
                    old_sale.quantity = v["quantity"]
                    old_sale.tax_rate = v["tax_rate_obj"]
                    old_sale.tax_amount = v["tax_amount"]
                    old_sale.discount_type = v["discount_type"]
                    old_sale.discount_value = v["discount_value"]
                    old_sale.discount_amount = v["discount_amount"]
                    old_sale.save()
                    # Fix 3: enforce inventory constraints (allow_negative=False)
                    InventoryService.reduce_inventory(v["product"], v["quantity"], allow_negative=False)
                else:
                    Sales.objects.create(
                        transaction=transaction,
                        prod=v["product"],
                        prod_price=v["prod_price"],
                        user_id=user_id,
                        quantity=v["quantity"],
                        tax_rate=v["tax_rate_obj"],
                        tax_amount=v["tax_amount"],
                        discount_type=v["discount_type"],
                        discount_value=v["discount_value"],
                        discount_amount=v["discount_amount"],
                    )
                    # Fix 3: enforce inventory constraints (allow_negative=False)
                    InventoryService.reduce_inventory(v["product"], v["quantity"], allow_negative=False)

            # Update client if provided (already validated above)
            if client_id:
                transaction.client_id = client_id

            # Update payment terms if provided (already validated above)
            if payment_terms is not None:
                transaction.payment_terms = payment_terms

            transaction.total_amount = new_total
            transaction.save()
    except InventoryError as e:
        return bad_request_response(str(e))

    # Fix 1: Move PaymentService calls OUTSIDE the atomic block so a PaymentError
    # does not leave the prior DB writes committed while returning an error response.
    try:
        PaymentService.update_transaction_status(
            transaction=transaction,
            new_total_amount=new_total,
            transaction_currency=currency,
        )
        total_paid = PaymentService.calculate_total_paid(transaction)
    except PaymentError as e:
        return bad_request_response(str(e))

    transaction.refresh_from_db()

    return Response({
        "message": "Sale updated successfully",
        "transaction_id": transaction.id,
        "transaction_status": transaction.status,
        "total_amount": float(new_total),
        "total_paid": float(total_paid),
        "remaining": float(new_total - total_paid),
    })


@api_view(["DELETE"])
@permission_classes([IsManagerOrAbove])
@api_error_handler
def deleteSale(request, pk):
    """Delete a sale transaction and reverse all effects (payments, inventory)"""
    from django.db import transaction as db_transaction

    from erp.services.inventory_service import InventoryService
    from erp.services.payment_service import PaymentService

    try:
        transaction = Transaction.objects.get(id=pk, transaction_type=TransactionType.SALE)
    except Transaction.DoesNotExist:
        return not_found_response("Sale transaction")

    # Fix 4: evaluate eagerly so the queryset isn't re-run after transaction.delete()
    sale_lines = list(Sales.objects.filter(transaction=transaction).select_related("prod"))
    inventory_restored = []

    with db_transaction.atomic():
        reversal_result = PaymentService.reverse_all_payments(transaction)

        for sale in sale_lines:
            InventoryService.add_inventory(sale.prod, sale.quantity)
            inventory_restored.append({
                "product_name": sale.prod.name,
                "quantity": float(sale.quantity),
            })

        transaction_id = transaction.id
        transaction.delete()

    return Response({
        "message": "Sale deleted successfully",
        "transaction_id": transaction_id,
        "inventory_restored": inventory_restored,
        "payments_reversed": reversal_result["payment_count"],
        "total_reversed": reversal_result["total_reversed"],
        "accounts_affected": reversal_result["accounts_affected"],
    })
