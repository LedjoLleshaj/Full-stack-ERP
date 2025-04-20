from rest_framework.response import Response
from rest_framework import permissions
from ..models import Clients, Sales, Product
from rest_framework.decorators import api_view, permission_classes
from ..serializers import ClientSerializer, ProductSerializer, SalesSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== CLIENTS ========


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getClients(request):
    try:
        clients = Clients.objects.all()
        # for each client get the balance by summing the amount they have to pay in unpaid sales
        serializer = ClientSerializer(clients, many=True)
        for client in serializer.data:
            sales = Sales.objects.filter(client=client["id"], is_paid=False)
            total_amount = 0
            for sale in sales:
                total_amount += sale.prod_price * sale.quantity
            client["unpaidBalance"] = total_amount
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getClient(request, pk):
    try:
        client = Clients.objects.get(id=pk)
        serializer = ClientSerializer(client, many=False)
        client = serializer.data
        sales = Sales.objects.filter(client=client["id"])
        unpaidBalance = 0
        totalBought = 0
        for sale in sales:
            if sale.is_paid == False:
                unpaidBalance += sale.prod_price * sale.quantity

            totalBought += sale.prod_price * sale.quantity
        client["unpaidBalance"] = unpaidBalance
        client["totalBought"] = totalBought
        return Response(client)
    except ObjectDoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
# @permission_classes([permissions.AllowAny])
def createClient(request):
    try:
        data = request.data
        client = Clients.objects.create(
            firstname=data["firstname"],
            lastname=data["lastname"],
            email=data["email"],
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
# @permission_classes([permissions.IsAuthenticated])
def updateClient(request, pk):
    try:
        client = Clients.objects.get(id=pk)
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
# @permission_classes([permissions.IsAuthenticated])
def deleteClient(request, pk):
    try:
        Client = Clients.objects.get(id=pk)
        Client.delete()
        return Response("Client deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getClientSales(request, pk):
    try:
        client = Clients.objects.get(id=pk)
        sales = Sales.objects.filter(client=client)
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
