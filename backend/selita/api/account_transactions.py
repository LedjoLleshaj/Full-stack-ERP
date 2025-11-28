from rest_framework.response import Response
from rest_framework import permissions
from ..models import AccountTransaction, Account, Payment
from rest_framework.decorators import api_view, permission_classes
from ..serializers import AccountTransactionSerializer, AccountSerializer, PaymentSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== ACCOUNT TRANSACTIONS ========


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getAccountTransactions(request):
    try:
        account_transactions = AccountTransaction.objects.all().order_by('-transaction_date')
        serializer = AccountTransactionSerializer(account_transactions, many=True)
        
        # Add account info
        for trans_data in serializer.data:
            try:
                account = Account.objects.get(id=trans_data['account'])
                account_serializer = AccountSerializer(account)
                trans_data['account_info'] = {
                    'account_name': account_serializer.data.get('account_name'),
                    'account_type': account_serializer.data.get('account_type'),
                    'currency': account_serializer.data.get('currency'),
                }
            except ObjectDoesNotExist:
                trans_data['account_info'] = None
        
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getAccountTransaction(request, pk):
    try:
        account_transaction = AccountTransaction.objects.get(id=pk)
        serializer = AccountTransactionSerializer(account_transaction, many=False)
        
        response_data = serializer.data
        
        # Add full account info
        account_serializer = AccountSerializer(account_transaction.account)
        response_data['account_info'] = account_serializer.data
        
        # Add payment info if exists
        if account_transaction.payment:
            payment_serializer = PaymentSerializer(account_transaction.payment)
            response_data['payment_info'] = payment_serializer.data
        
        return Response(response_data)
    except ObjectDoesNotExist:
        return Response({"error": "Account transaction not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getTransactionsByAccount(request, account_id):
    try:
        account = Account.objects.get(id=account_id)
        account_transactions = AccountTransaction.objects.filter(account=account).order_by('-transaction_date')
        serializer = AccountTransactionSerializer(account_transactions, many=True)
        
        return Response({
            'account': AccountSerializer(account).data,
            'transactions': serializer.data
        })
    except ObjectDoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
def addAccountTransaction(request):
    try:
        serializer = AccountTransactionSerializer(data=request.data)
        if serializer.is_valid():
            account_transaction = serializer.save()
            
            # Update account balance
            account = account_transaction.account
            account.current_balance = account_transaction.balance_after
            account.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
# @permission_classes([permissions.IsAuthenticated])
def deleteAccountTransaction(request, pk):
    try:
        account_transaction = AccountTransaction.objects.get(id=pk)
        account_transaction.delete()
        return Response("Account transaction deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "Account transaction not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
