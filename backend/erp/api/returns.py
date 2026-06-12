from decimal import Decimal

from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from erp.constants import TransactionType
from erp.permissions import IsStaffOrAbove
from erp.services.payment_service import PaymentError, PaymentService
from erp.utils.responses import api_error_handler, bad_request_response, not_found_response

from ..models import Payment, Sales, Transaction


@api_view(["POST"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def create_return(request, pk):
    try:
        sale = Sales.objects.select_related("transaction").get(id=pk)
    except Sales.DoesNotExist:
        return not_found_response("Sale")

    transaction = sale.transaction

    items = request.data.get("items", [])
    refund_method = request.data.get("refund_method", "CASH")
    refund_currency = request.data.get("refund_currency", transaction.currency)
    notes = request.data.get("notes", "")

    if not items:
        return bad_request_response("No return items provided")

    try:
        result = PaymentService.process_return(
            original_transaction=transaction,
            return_items=items,
            refund_method=refund_method,
            refund_currency=refund_currency,
            user=request.user,
        )
    except PaymentError as e:
        return bad_request_response(str(e))

    result["message"] = "Return processed successfully"
    if notes:
        return_tx = Transaction.objects.get(id=result["return_transaction_id"])
        return_tx.notes = notes
        return_tx.save()

    return Response(result, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def get_returns(request):
    returns = Transaction.objects.filter(
        transaction_type=TransactionType.RETURN
    ).select_related("client", "original_transaction").order_by("-created_date")

    results = []
    for ret in returns:
        items = Sales.objects.filter(transaction=ret).select_related("prod")
        results.append({
            "id": ret.id,
            "return_date": ret.created_date.isoformat(),
            "return_value": float(ret.total_amount),
            "original_transaction_id": ret.original_transaction_id,
            "client": (
                f"{ret.client.firstname} {ret.client.lastname}" if ret.client else None
            ),
            "currency": ret.currency,
            "notes": ret.notes,
            "items": [
                {
                    "product_name": s.prod.name,
                    "quantity": s.quantity,
                    "unit_price": float(s.prod_price),
                }
                for s in items
            ],
        })

    return Response(results)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def get_return(request, pk):
    try:
        ret = Transaction.objects.select_related(
            "client", "original_transaction"
        ).get(id=pk, transaction_type=TransactionType.RETURN)
    except Transaction.DoesNotExist:
        return not_found_response("Return")

    items = Sales.objects.filter(transaction=ret).select_related("prod", "tax_rate")

    payments = Payment.objects.filter(transaction=ret)
    refund_amount = float(
        payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")
    )

    return Response({
        "id": ret.id,
        "return_date": ret.created_date.isoformat(),
        "return_value": float(ret.total_amount),
        "refund_amount": refund_amount,
        "original_transaction_id": ret.original_transaction_id,
        "client": (
            f"{ret.client.firstname} {ret.client.lastname}" if ret.client else None
        ),
        "currency": ret.currency,
        "status": ret.status,
        "notes": ret.notes,
        "items": [
            {
                "product_name": s.prod.name,
                "quantity": s.quantity,
                "unit_price": float(s.prod_price),
                "tax_amount": float(s.tax_amount),
            }
            for s in items
        ],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def get_sale_returns(request, sale_id):
    try:
        sale = Sales.objects.select_related("transaction").get(id=sale_id)
    except Sales.DoesNotExist:
        return not_found_response("Sale")

    transaction = sale.transaction
    return_txs = Transaction.objects.filter(
        original_transaction=transaction,
        transaction_type=TransactionType.RETURN,
    ).order_by("-created_date")

    results = []
    for ret in return_txs:
        items = Sales.objects.filter(transaction=ret).select_related("prod")
        payments = Payment.objects.filter(transaction=ret)
        refund_amount = float(
            payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        )

        results.append({
            "id": ret.id,
            "return_date": ret.created_date.isoformat(),
            "return_value": float(ret.total_amount),
            "refund_amount": refund_amount,
            "notes": ret.notes,
            "items": [
                {
                    "product_name": s.prod.name,
                    "quantity": s.quantity,
                    "unit_price": float(s.prod_price),
                }
                for s in items
            ],
        })

    return Response(results)
