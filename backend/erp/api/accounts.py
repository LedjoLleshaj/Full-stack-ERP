from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from erp.utils.responses import api_error_handler, not_found_response

from ..models import Account, AccountTransaction
from ..serializers import AccountSerializer, AccountTransactionSerializer

# ======== ACCOUNTS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getAccounts(request):
    accounts = Account.objects.all()
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getAccount(request, pk):
    try:
        account = Account.objects.get(id=pk)
        serializer = AccountSerializer(account, many=False)

        # Get recent transactions for this account
        transactions = AccountTransaction.objects.filter(account=account).order_by(
            "-transaction_date"
        )[:10]
        trans_serializer = AccountTransactionSerializer(transactions, many=True)

        response_data = serializer.data
        response_data["recent_transactions"] = trans_serializer.data

        return Response(response_data)
    except ObjectDoesNotExist:
        return not_found_response("Account")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def addAccount(request):
    serializer = AccountSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def updateAccount(request, pk):
    try:
        account = Account.objects.get(id=pk)
        serializer = AccountSerializer(instance=account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return not_found_response("Account")


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def deleteAccount(request, pk):
    try:
        account = Account.objects.get(id=pk)
        account.delete()
        return Response("Account deleted successfully")
    except ObjectDoesNotExist:
        return not_found_response("Account")
