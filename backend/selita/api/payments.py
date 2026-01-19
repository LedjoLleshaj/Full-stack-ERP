from rest_framework.response import Response
from rest_framework import permissions, status
from ..models import Payment, Transaction, Account
from rest_framework.decorators import api_view, permission_classes
from ..serializers import PaymentSerializer, TransactionSerializer, AccountSerializer
from django.core.exceptions import ObjectDoesNotExist
from selita.utils.responses import api_error_handler, not_found_response


# ======== PAYMENTS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getPayments(request):
    # Optimized: Use select_related to fetch transaction and account in ONE query
    payments = Payment.objects.select_related('transaction', 'account').all()
    
    results = []
    for payment in payments:
        payment_data = {
            "id": payment.id,
            "transaction": payment.transaction_id,
            "account": payment.account_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "original_amount": float(payment.original_amount) if payment.original_amount else None,
            "original_currency": payment.original_currency,
            "payment_method": payment.payment_method,
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "notes": payment.notes,
        }
        
        # Add transaction info (already loaded via select_related)
        if payment.transaction:
            payment_data["transaction_info"] = {
                "invoice_number": payment.transaction.invoice_number,
                "transaction_type": payment.transaction.transaction_type,
                "total_amount": float(payment.transaction.total_amount),
            }
        else:
            payment_data["transaction_info"] = None
        
        # Add account info (already loaded via select_related)
        if payment.account:
            payment_data["account_info"] = {
                "account_name": payment.account.account_name,
                "account_type": payment.account.account_type,
            }
        else:
            payment_data["account_info"] = None
        
        results.append(payment_data)
    
    return Response(results)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getPayment(request, pk):
    try:
        payment = Payment.objects.select_related('transaction', 'account').get(id=pk)
        serializer = PaymentSerializer(payment, many=False)

        response_data = serializer.data

        # Add full transaction info (already loaded via select_related)
        transaction_serializer = TransactionSerializer(payment.transaction)
        response_data["transaction_info"] = transaction_serializer.data

        # Add full account info (already loaded via select_related)
        account_serializer = AccountSerializer(payment.account)
        response_data["account_info"] = account_serializer.data

        return Response(response_data)
    except ObjectDoesNotExist:
        return not_found_response("Payment")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def addPayment(request):
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def updatePayment(request, pk):
    try:
        payment = Payment.objects.get(id=pk)
        serializer = PaymentSerializer(instance=payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return not_found_response("Payment")


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def deletePayment(request, pk):
    try:
        payment = Payment.objects.get(id=pk)
        payment.delete()
        return Response("Payment deleted successfully")
    except ObjectDoesNotExist:
        return not_found_response("Payment")
