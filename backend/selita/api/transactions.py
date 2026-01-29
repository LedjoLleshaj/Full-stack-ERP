from rest_framework.response import Response
from rest_framework import permissions, status
from ..models import Transaction, Supplier, Client, Payment
from rest_framework.decorators import api_view, permission_classes
from ..serializers import (
    TransactionSerializer,
    PaymentSerializer,
    SupplierSerializer,
    ClientSerializer,
)
from django.core.exceptions import ObjectDoesNotExist
from selita.utils.responses import api_error_handler, not_found_response


# ======== TRANSACTIONS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getTransactions(request):
    # Allow filtering by transaction type
    transaction_type = request.GET.get("type")

    if transaction_type and transaction_type in ["PURCHASE", "SALE"]:
        transactions = Transaction.objects.filter(transaction_type=transaction_type)
    else:
        transactions = Transaction.objects.all()

    # Optimized: Use select_related to fetch supplier and client in ONE query
    transactions = transactions.select_related('supplier', 'client')
    
    results = []
    for trans in transactions:
        trans_data = {
            "id": trans.id,
            "invoice_number": trans.invoice_number,
            "transaction_type": trans.transaction_type,
            "total_amount": float(trans.total_amount),
            "currency": trans.currency,
            "status": trans.status,
            "notes": trans.notes,
            "created_date": trans.created_date.isoformat() if trans.created_date else None,
            "completed_date": trans.completed_date.isoformat() if trans.completed_date else None,
            "supplier": trans.supplier_id,
            "client": trans.client_id,
        }
        
        # Add supplier info (already loaded via select_related)
        if trans.supplier:
            trans_data["supplier_info"] = {
                "id": trans.supplier.id,
                "firstname": trans.supplier.firstname,
                "lastname": trans.supplier.lastname,
            }
        else:
            trans_data["supplier_info"] = None
        
        # Add client info (already loaded via select_related)
        if trans.client:
            trans_data["client_info"] = {
                "id": trans.client.id,
                "firstname": trans.client.firstname,
                "lastname": trans.client.lastname,
            }
        else:
            trans_data["client_info"] = None
        
        results.append(trans_data)

    return Response(results)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getTransaction(request, pk):
    try:
        # Optimized: Use select_related and prefetch_related
        transaction = Transaction.objects.select_related('supplier', 'client').prefetch_related('payments').get(id=pk)
        serializer = TransactionSerializer(transaction, many=False)

        response_data = serializer.data

        # Add supplier or client info (already loaded via select_related)
        if transaction.supplier:
            supplier_serializer = SupplierSerializer(transaction.supplier)
            response_data["supplier_info"] = supplier_serializer.data

        if transaction.client:
            client_serializer = ClientSerializer(transaction.client)
            response_data["client_info"] = client_serializer.data

        # Add payments for this transaction (already loaded via prefetch_related)
        payment_serializer = PaymentSerializer(transaction.payments.all(), many=True)
        response_data["payments"] = payment_serializer.data

        return Response(response_data)
    except ObjectDoesNotExist:
        return not_found_response("Transaction")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def addTransaction(request):
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        transaction = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def updateTransaction(request, pk):
    try:
        transaction = Transaction.objects.get(id=pk)
        serializer = TransactionSerializer(instance=transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return not_found_response("Transaction")


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def deleteTransaction(request, pk):
    try:
        transaction = Transaction.objects.get(id=pk)
        transaction.delete()
        return Response("Transaction deleted successfully")
    except ObjectDoesNotExist:
        return not_found_response("Transaction")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getTransactionPayments(request, pk):
    try:
        transaction = Transaction.objects.get(id=pk)
        payments = Payment.objects.filter(transaction=transaction)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("Transaction")
