from rest_framework.response import Response
from rest_framework import permissions
from ..models import Account, AccountTransaction
from rest_framework.decorators import api_view, permission_classes
from ..serializers import AccountSerializer, AccountTransactionSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== ACCOUNTS ========


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getAccounts(request):
    try:
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getAccount(request, pk):
    try:
        account = Account.objects.get(id=pk)
        serializer = AccountSerializer(account, many=False)
        
        # Get recent transactions for this account
        transactions = AccountTransaction.objects.filter(account=account).order_by('-transaction_date')[:10]
        trans_serializer = AccountTransactionSerializer(transactions, many=True)
        
        response_data = serializer.data
        response_data['recent_transactions'] = trans_serializer.data
        
        return Response(response_data)
    except ObjectDoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
def addAccount(request):
    try:
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
# @permission_classes([permissions.IsAuthenticated])
def updateAccount(request, pk):
    try:
        account = Account.objects.get(id=pk)
        serializer = AccountSerializer(instance=account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
# @permission_classes([permissions.IsAuthenticated])
def deleteAccount(request, pk):
    try:
        account = Account.objects.get(id=pk)
        account.delete()
        return Response("Account deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
