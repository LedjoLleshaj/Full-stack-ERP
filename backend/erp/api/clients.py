from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from erp.constants import TransactionStatus
from erp.permissions import IsManagerOrAbove, IsStaffOrAbove
from erp.utils.currency import convert_to_eur_with_rates, get_all_rates_dict
from erp.utils.responses import api_error_handler, not_found_response

from ..models import Client, Sales
from ..serializers import ClientSerializer

# ======== CLIENTS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getClients(request):
    from collections import defaultdict
    from decimal import Decimal

    from ..models import Transaction
    
    # Cache exchange rates upfront (1 query)
    rates = get_all_rates_dict()
    
    # Pre-calculate unpaid balances per client in memory
    # Step 1: Get all unpaid transactions with their payments (2 queries)
    unpaid_transactions = Transaction.objects.filter(
        client__isnull=False,
        status__in=TransactionStatus.UNPAID_STATUSES
    ).select_related('client').prefetch_related('payments')
    
    # Step 2: Calculate remaining balance per client
    client_balances = defaultdict(lambda: Decimal("0"))
    
    for transaction in unpaid_transactions:
        total_paid = sum(p.amount for p in transaction.payments.all())
        remaining = transaction.total_amount - total_paid
        remaining_eur = convert_to_eur_with_rates(remaining, transaction.currency, rates)
        client_balances[transaction.client_id] += remaining_eur
    
    # Step 3: Get all active clients (1 query)
    clients = Client.objects.filter(is_active=True)
    
    # Build response
    results = []
    for client in clients:
        results.append({
            "id": client.id,
            "firstname": client.firstname,
            "lastname": client.lastname,
            "phone": client.phone,
            "email": client.email,
            "address": client.address,
            "city": client.city,
            "unpaidBalance": round(float(client_balances.get(client.id, Decimal("0"))), 2),
        })
    
    return Response(results)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getClient(request, pk):
    from decimal import Decimal
    
    try:
        client = Client.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Client")
    
    serializer = ClientSerializer(client, many=False)
    client_data = serializer.data
    
    # Cache exchange rates upfront (1 query)
    rates = get_all_rates_dict()
    
    # Get sales with prefetched transactions and payments (2 queries)
    sales = Sales.objects.filter(
        transaction__client_id=client_data["id"]
    ).select_related('transaction').prefetch_related('transaction__payments')
    
    unpaidBalance = Decimal("0")
    totalBought = Decimal("0")
    
    for sale in sales:
        sale_total = Decimal(str(sale.prod_price)) * sale.quantity
        currency = sale.transaction.currency if sale.transaction else "EUR"
        totalBought += convert_to_eur_with_rates(sale_total, currency, rates)
        
        # Calculate remaining from prefetched payments (no additional query)
        total_paid = sum(p.amount for p in sale.transaction.payments.all())
        remaining = Decimal(str(sale.transaction.total_amount)) - Decimal(str(total_paid))
        if remaining > 0:
            unpaidBalance += convert_to_eur_with_rates(remaining, currency, rates)
    
    client_data["unpaidBalance"] = round(float(unpaidBalance), 2)
    client_data["totalBought"] = round(float(totalBought), 2)
    return Response(client_data)


@api_view(["POST"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def addClient(request):
    data = request.data
    client = Client.objects.create(
        firstname=data["firstname"],
        lastname=data["lastname"],
        email=data["email"] if "email" in data else None,
        phone=data["phone"],
        address=data["address"],
        city=data["city"],
    )
    client.save()
    serializer = ClientSerializer(client, many=False)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsStaffOrAbove])
@api_error_handler
def updateClient(request, pk):
    try:
        client = Client.objects.get(id=pk)
        data = request.data
        client.firstname = data["firstname"]
        client.lastname = data["lastname"]
        client.email = data["email"]
        client.phone = data["phone"]
        client.address = data["address"]
        client.city = data["city"]
        client.save()
        serializer = ClientSerializer(client, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("Client")


@api_view(["DELETE"])
@permission_classes([IsManagerOrAbove])
@api_error_handler
def deleteClient(request, pk):
    from ..models import Transaction
    
    try:
        client = Client.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Client")
    
    # Check for unpaid transactions
    if Transaction.objects.filter(
        client=client,
        status__in=TransactionStatus.UNPAID_STATUSES
    ).exists():
        return Response(
            {"error": "Cannot delete client with unpaid transactions"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Soft delete
    client.is_active = False
    client.save()
    
    return Response({"message": "Client deactivated successfully"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getClientSales(request, pk):
    try:
        client = Client.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Client")
    
    # Get sales with prefetched transaction and product (2 queries total)
    sales = Sales.objects.filter(
        transaction__client=client
    ).select_related('transaction', 'prod').order_by('-sale_date')
    
    # Build response directly from prefetched data (no additional queries)
    results = []
    for sale in sales:
        sale_data = {
            "id": sale.id,
            "prod": sale.prod_id,
            "quantity": float(sale.quantity),
            "prod_price": float(sale.prod_price),
            "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
            "transaction": sale.transaction_id,
            "user": sale.user_id,
        }
        
        # Product info (already loaded via select_related)
        if sale.prod:
            sale_data["product"] = {
                "id": sale.prod.id,
                "name": sale.prod.name,
                "category": sale.prod.category,
                "price": float(sale.prod.price) if sale.prod.price else None,
                "description": sale.prod.description,
            }
        else:
            sale_data["product"] = {"error": "Product not found"}
        
        # Transaction info (already loaded via select_related)
        if sale.transaction:
            sale_data["payment_status"] = sale.transaction.status
            sale_data["currency"] = sale.transaction.currency
        else:
            sale_data["payment_status"] = TransactionStatus.PENDING
            sale_data["currency"] = "EUR"
        
        results.append(sale_data)
    
    return Response(results)
