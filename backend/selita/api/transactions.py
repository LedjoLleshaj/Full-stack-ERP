from rest_framework.response import Response
from rest_framework import permissions
from ..models import Transaction, Supplier, Client, Payment
from rest_framework.decorators import api_view, permission_classes
from ..serializers import TransactionSerializer, PaymentSerializer, SupplierSerializer, ClientSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== TRANSACTIONS ========


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getTransactions(request):
    try:
        # Allow filtering by transaction type
        transaction_type = request.GET.get('type')
        
        if transaction_type and transaction_type in ['PURCHASE', 'SALE']:
            transactions = Transaction.objects.filter(transaction_type=transaction_type)
        else:
            transactions = Transaction.objects.all()
        
        serializer = TransactionSerializer(transactions, many=True)
        
        # Add related supplier/client info
        for trans_data in serializer.data:
            if trans_data.get('supplier'):
                try:
                    supplier = Supplier.objects.get(id=trans_data['supplier'])
                    supplier_serializer = SupplierSerializer(supplier)
                    trans_data['supplier_info'] = supplier_serializer.data
                except ObjectDoesNotExist:
                    trans_data['supplier_info'] = None
            
            if trans_data.get('client'):
                try:
                    client = Client.objects.get(id=trans_data['client'])
                    client_serializer = ClientSerializer(client)
                    trans_data['client_info'] = client_serializer.data
                except ObjectDoesNotExist:
                    trans_data['client_info'] = None
        
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getTransaction(request, pk):
    try:
        transaction = Transaction.objects.get(id=pk)
        serializer = TransactionSerializer(transaction, many=False)
        
        response_data = serializer.data
        
        # Add supplier or client info
        if transaction.supplier:
            supplier_serializer = SupplierSerializer(transaction.supplier)
            response_data['supplier_info'] = supplier_serializer.data
        
        if transaction.client:
            client_serializer = ClientSerializer(transaction.client)
            response_data['client_info'] = client_serializer.data
        
        # Add payments for this transaction
        payments = Payment.objects.filter(transaction=transaction)
        payment_serializer = PaymentSerializer(payments, many=True)
        response_data['payments'] = payment_serializer.data
        
        return Response(response_data)
    except ObjectDoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
def addTransaction(request):
    try:
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
# @permission_classes([permissions.IsAuthenticated])
def updateTransaction(request, pk):
    try:
        transaction = Transaction.objects.get(id=pk)
        serializer = TransactionSerializer(instance=transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
# @permission_classes([permissions.IsAuthenticated])
def deleteTransaction(request, pk):
    try:
        transaction = Transaction.objects.get(id=pk)
        transaction.delete()
        return Response("Transaction deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getTransactionPayments(request, pk):
    try:
        transaction = Transaction.objects.get(id=pk)
        payments = Payment.objects.filter(transaction=transaction)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
