from rest_framework.response import Response
from rest_framework import permissions
from ..models import Payment, Transaction, Account
from rest_framework.decorators import api_view, permission_classes
from ..serializers import PaymentSerializer, TransactionSerializer, AccountSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== PAYMENTS ========


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getPayments(request):
    try:
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        
        # Add transaction and account info
        for payment_data in serializer.data:
            try:
                transaction = Transaction.objects.get(id=payment_data['transaction'])
                transaction_serializer = TransactionSerializer(transaction)
                payment_data['transaction_info'] = {
                    'invoice_number': transaction_serializer.data.get('invoice_number'),
                    'transaction_type': transaction_serializer.data.get('transaction_type'),
                    'total_amount': transaction_serializer.data.get('total_amount'),
                }
            except ObjectDoesNotExist:
                payment_data['transaction_info'] = None
                
            try:
                account = Account.objects.get(id=payment_data['account'])
                account_serializer = AccountSerializer(account)
                payment_data['account_info'] = {
                    'account_name': account_serializer.data.get('account_name'),
                    'account_type': account_serializer.data.get('account_type'),
                }
            except ObjectDoesNotExist:
                payment_data['account_info'] = None
        
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getPayment(request, pk):
    try:
        payment = Payment.objects.get(id=pk)
        serializer = PaymentSerializer(payment, many=False)
        
        response_data = serializer.data
        
        # Add full transaction info
        transaction_serializer = TransactionSerializer(payment.transaction)
        response_data['transaction_info'] = transaction_serializer.data
        
        # Add full account info
        account_serializer = AccountSerializer(payment.account)
        response_data['account_info'] = account_serializer.data
        
        return Response(response_data)
    except ObjectDoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
def addPayment(request):
    try:
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
# @permission_classes([permissions.IsAuthenticated])
def updatePayment(request, pk):
    try:
        payment = Payment.objects.get(id=pk)
        serializer = PaymentSerializer(instance=payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
# @permission_classes([permissions.IsAuthenticated])
def deletePayment(request, pk):
    try:
        payment = Payment.objects.get(id=pk)
        payment.delete()
        return Response("Payment deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
