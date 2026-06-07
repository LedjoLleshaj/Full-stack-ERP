from rest_framework.response import Response
from rest_framework import permissions, status
from ..models import AccountTransaction, Account, Payment
from rest_framework.decorators import api_view, permission_classes
from ..serializers import (
    AccountTransactionSerializer,
    AccountSerializer,
    PaymentSerializer,
)
from django.core.exceptions import ObjectDoesNotExist
from erp.utils.responses import api_error_handler, not_found_response


# ======== ACCOUNT TRANSACTIONS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getAccountTransactions(request):
    # Optimized: Use select_related to fetch account in ONE query
    account_transactions = AccountTransaction.objects.select_related('account').order_by(
        "-transaction_date"
    )
    
    results = []
    for trans in account_transactions:
        trans_data = {
            "id": trans.id,
            "account": trans.account_id,
            "transaction_type": trans.transaction_type,
            "amount": float(trans.amount),
            "balance_before": float(trans.balance_before) if trans.balance_before else None,
            "balance_after": float(trans.balance_after) if trans.balance_after else None,
            "transaction_date": trans.transaction_date.isoformat() if trans.transaction_date else None,
            "description": trans.description,
            "payment": trans.payment_id,
        }
        
        # Add account info (already loaded via select_related)
        if trans.account:
            trans_data["account_info"] = {
                "account_name": trans.account.account_name,
                "account_type": trans.account.account_type,
                "currency": trans.account.currency,
            }
        else:
            trans_data["account_info"] = None
        
        results.append(trans_data)
    
    return Response(results)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getAccountTransaction(request, pk):
    try:
        account_transaction = AccountTransaction.objects.select_related('account', 'payment').get(id=pk)
        serializer = AccountTransactionSerializer(account_transaction, many=False)

        response_data = serializer.data

        # Add full account info (already loaded via select_related)
        account_serializer = AccountSerializer(account_transaction.account)
        response_data["account_info"] = account_serializer.data

        # Add payment info if exists (already loaded via select_related)
        if account_transaction.payment:
            payment_serializer = PaymentSerializer(account_transaction.payment)
            response_data["payment_info"] = payment_serializer.data

        return Response(response_data)
    except ObjectDoesNotExist:
        return not_found_response("Account transaction")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getTransactionsByAccount(request, account_id):
    try:
        account = Account.objects.get(id=account_id)
        account_transactions = AccountTransaction.objects.filter(
            account=account
        ).order_by("-transaction_date")
        serializer = AccountTransactionSerializer(account_transactions, many=True)

        return Response(
            {
                "account": AccountSerializer(account).data,
                "transactions": serializer.data,
            }
        )
    except ObjectDoesNotExist:
        return not_found_response("Account")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def addAccountTransaction(request):
    serializer = AccountTransactionSerializer(data=request.data)
    if serializer.is_valid():
        account_transaction = serializer.save()

        # Update account balance
        account = account_transaction.account
        account.current_balance = account_transaction.balance_after
        account.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def deleteAccountTransaction(request, pk):
    try:
        account_transaction = AccountTransaction.objects.get(id=pk)
        account_transaction.delete()
        return Response("Account transaction deleted successfully")
    except ObjectDoesNotExist:
        return not_found_response("Account transaction")
