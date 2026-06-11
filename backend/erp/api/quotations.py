from decimal import Decimal

from django.db import transaction as db_transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from erp.constants import QuotationStatus, TransactionStatus, TransactionType
from erp.models import Quotation, Sales, Transaction
from erp.permissions import IsManagerOrAbove, IsStaffOrAbove
from erp.serializers import (
    QuotationCreateSerializer,
    QuotationDetailSerializer,
    QuotationListSerializer,
)
from erp.utils.responses import (
    api_error_handler,
    bad_request_response,
    not_found_response,
    success_response,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def list_quotations(request):
    qs = Quotation.objects.select_related("client").prefetch_related("items").all()

    status_filter = request.query_params.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    client_filter = request.query_params.get("client")
    if client_filter:
        qs = qs.filter(client_id=client_filter)

    serializer = QuotationListSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def get_quotation(request, pk):
    try:
        quotation = (
            Quotation.objects
            .select_related("client", "created_by")
            .prefetch_related("items__product", "items__tax_rate")
            .get(id=pk)
        )
    except Quotation.DoesNotExist:
        return not_found_response("Quotation")

    serializer = QuotationDetailSerializer(quotation)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def create_quotation(request):
    serializer = QuotationCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return bad_request_response("Validation failed", str(serializer.errors))

    quotation = serializer.save(created_by=request.user)
    _recalculate_tax(quotation)

    detail = QuotationDetailSerializer(quotation)
    return Response(detail.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def update_quotation(request, pk):
    try:
        quotation = Quotation.objects.get(id=pk)
    except Quotation.DoesNotExist:
        return not_found_response("Quotation")

    if quotation.status == QuotationStatus.CONVERTED:
        return bad_request_response("Cannot edit a converted quotation")

    serializer = QuotationCreateSerializer(quotation, data=request.data, partial=True)
    if not serializer.is_valid():
        return bad_request_response("Validation failed", str(serializer.errors))

    quotation = serializer.save()
    _recalculate_tax(quotation)

    detail = QuotationDetailSerializer(quotation)
    return Response(detail.data)


@api_view(["DELETE"])
@permission_classes([IsManagerOrAbove])
@api_error_handler
def delete_quotation(request, pk):
    try:
        quotation = Quotation.objects.get(id=pk)
    except Quotation.DoesNotExist:
        return not_found_response("Quotation")

    if quotation.status == QuotationStatus.CONVERTED:
        return bad_request_response("Cannot delete a converted quotation")

    quotation_id = quotation.id
    quotation.delete()
    return success_response({"quotation_id": quotation_id}, "Quotation deleted")


@api_view(["POST"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def update_status(request, pk):
    try:
        quotation = Quotation.objects.get(id=pk)
    except Quotation.DoesNotExist:
        return not_found_response("Quotation")

    new_status = request.data.get("status")
    if new_status not in dict(QuotationStatus.CHOICES):
        return bad_request_response(f"Invalid status: {new_status}")

    if quotation.status == QuotationStatus.CONVERTED:
        return bad_request_response("Cannot change status of a converted quotation")

    quotation.status = new_status
    quotation.save(update_fields=["status"])
    return success_response({"id": quotation.id, "status": quotation.status}, "Status updated")


@api_view(["POST"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def convert_to_sale(request, pk):
    from erp.services.inventory_service import InventoryError, InventoryService

    try:
        quotation = (
            Quotation.objects
            .select_related("client")
            .prefetch_related("items__product", "items__tax_rate")
            .get(id=pk)
        )
    except Quotation.DoesNotExist:
        return not_found_response("Quotation")

    if quotation.status not in QuotationStatus.CONVERTIBLE:
        return bad_request_response(
            f"Only accepted quotations can be converted. Current status: {quotation.status}"
        )

    if quotation.converted_transaction:
        return bad_request_response("Quotation already converted")

    items = list(quotation.items.select_related("product", "tax_rate").all())
    if not items:
        return bad_request_response("Quotation has no items")

    for item in items:
        if not InventoryService.check_availability(item.product, item.quantity):
            return bad_request_response(
                f"Insufficient inventory for {item.product.name}. "
                f"Available: {InventoryService.available_stock(item.product)}, Needed: {item.quantity}"
            )

    user_id = request.user.id

    with db_transaction.atomic():
        total_amount = sum(item.line_total for item in items)

        transaction = Transaction.objects.create(
            transaction_type=TransactionType.SALE,
            client=quotation.client,
            total_amount=total_amount,
            currency=quotation.currency,
            status=TransactionStatus.PENDING,
            notes=f"Converted from Quotation QUO-{quotation.id:06d}",
        )

        for item in items:
            Sales.objects.create(
                transaction=transaction,
                prod=item.product,
                prod_price=item.unit_price,
                user_id=user_id,
                quantity=item.quantity,
                tax_rate=item.tax_rate,
                tax_amount=item.tax_amount,
            )
            try:
                InventoryService.reduce_inventory(item.product, item.quantity, allow_negative=False)
            except InventoryError:
                raise

        quotation.status = QuotationStatus.CONVERTED
        quotation.converted_transaction = transaction
        quotation.save(update_fields=["status", "converted_transaction"])

    return Response({
        "message": "Quotation converted to sale",
        "quotation_id": quotation.id,
        "transaction_id": transaction.id,
        "total_amount": float(total_amount),
    }, status=status.HTTP_201_CREATED)


def _recalculate_tax(quotation):
    for item in quotation.items.select_related("tax_rate").all():
        if item.tax_rate:
            new_tax = (item.unit_price * item.quantity * item.tax_rate.rate / Decimal("100")).quantize(Decimal("0.01"))
            if new_tax != item.tax_amount:
                item.tax_amount = new_tax
                item.save(update_fields=["tax_amount"])
