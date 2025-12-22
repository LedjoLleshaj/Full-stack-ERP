from rest_framework.response import Response
from rest_framework import permissions
from ..models import Client, Sales, Product
from rest_framework.decorators import api_view, permission_classes
from ..serializers import ClientSerializer, ProductSerializer, SalesSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== CLIENTS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getClients(request):
    try:
        clients = Client.objects.all()
        # for each client get the balance by summing the amount they have to pay in unpaid sales
        serializer = ClientSerializer(clients, many=True)
        for client in serializer.data:
            # Get sales through transaction relationship
            sales = Sales.objects.filter(
                transaction__client_id=client["id"],
                transaction__status__in=["PENDING", "PARTIAL"]  # Not fully paid
            ).select_related('transaction')
            
            total_amount = 0
            for sale in sales:
                # Calculate remaining balance for this sale's transaction
                from ..models import Payment
                from django.db.models import Sum
                total_paid = Payment.objects.filter(
                    transaction=sale.transaction
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                remaining = sale.transaction.total_amount - total_paid
                total_amount += remaining
                
            client["unpaidBalance"] = float(total_amount)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getClient(request, pk):
    try:
        client = Client.objects.get(id=pk)
        serializer = ClientSerializer(client, many=False)
        client_data = serializer.data
        
        # Get sales through transaction relationship
        sales = Sales.objects.filter(
            transaction__client_id=client_data["id"]
        ).select_related('transaction')
        
        from ..models import Payment, ExchangeRate
        from django.db.models import Sum
        from decimal import Decimal
        
        def convert_to_eur(amount, currency):
            """Convert amount from any currency to EUR"""
            if currency == "EUR":
                return Decimal(str(amount))
            try:
                rate = ExchangeRate.objects.get(from_currency=currency, to_currency="EUR")
                return Decimal(str(amount)) * rate.rate
            except ExchangeRate.DoesNotExist:
                # Fallback: return as-is if no rate found
                return Decimal(str(amount))
        
        unpaidBalance = Decimal("0")
        totalBought = Decimal("0")
        
        for sale in sales:
            sale_total = Decimal(str(sale.prod_price)) * sale.quantity
            # Convert sale total to EUR using the transaction's currency
            currency = sale.transaction.currency if sale.transaction else "EUR"
            totalBought += convert_to_eur(sale_total, currency)
            
            # Calculate how much is still owed for this transaction
            total_paid = Payment.objects.filter(
                transaction=sale.transaction
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            remaining = Decimal(str(sale.transaction.total_amount)) - Decimal(str(total_paid))
            if remaining > 0:
                # Convert remaining balance to EUR
                unpaidBalance += convert_to_eur(remaining, currency)
        
        client_data["unpaidBalance"] = float(unpaidBalance)
        client_data["totalBought"] = float(totalBought)
        return Response(client_data)
    except ObjectDoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
# @permission_classes([permissions.AllowAny])
def addClient(request):
    try:
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
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
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
        return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def deleteClient(request, pk):
    try:
        client = Client.objects.get(id=pk)
        client.delete()
        return Response("Client deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getClientSales(request, pk):
    try:
        client = Client.objects.get(id=pk)
        # Get sales through transaction relationship
        sales = Sales.objects.filter(
            transaction__client=client
        ).select_related('transaction', 'prod')
        
        serializer = SalesSerializer(sales, many=True)
        # For each sale, retrieve and add the product data
        for sale_data in serializer.data:
            prod_id = sale_data["prod"]

            try:
                product = Product.objects.get(id=prod_id)
                product_serializer = ProductSerializer(product)
                sale_data["product"] = product_serializer.data
            except Product.DoesNotExist:
                sale_data["product"] = {"error": "Product not found"}
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
