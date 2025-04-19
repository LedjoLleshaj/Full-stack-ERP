from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ..models import Sales, Product, Users, Clients
from ..serializers import (
    SalesSerializer,
    ProductSerializer,
    UserSerializer,
    ClientSerializer,
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


# ======== USERS ========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSales(request):
    try:
        sales = Sales.objects.all()
        serializer = SalesSerializer(sales, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSale(request, pk):
    try:
        # Retrieve sale record by primary key
        sale = Sales.objects.get(id=pk)
        sale_serializer = SalesSerializer(sale)

        # Extract product and user IDs from sale data
        prod_id = sale_serializer.data["prod"]
        user_id = sale_serializer.data["user"]

        # Retrieve and serialize product data
        try:
            product = Product.objects.get(id=prod_id)
            product_serializer = ProductSerializer(product)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Retrieve and serialize user data
        try:
            user = Users.objects.get(id=user_id)
            user_serializer = UserSerializer(user)
        except ObjectDoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Construct the response data
        response_data = sale_serializer.data
        response_data["product"] = product_serializer.data
        response_data["user"] = {
            "firstname": user_serializer.data["firstname"],
            "lastname": user_serializer.data["lastname"],
        }

        return Response(response_data)

    except Sales.DoesNotExist:
        return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def getProductsFromSales(request):
    try:
        sales = Sales.objects.all()
        sales_serializer = SalesSerializer(sales, many=True)

        # For each sale, retrieve and add the product data
        for sale_data in sales_serializer.data:
            prod_id = sale_data["prod"]
            client_id = sale_data["client"]

            try:
                product = Product.objects.get(id=prod_id)
                product_serializer = ProductSerializer(product)
                sale_data["product"] = product_serializer.data
            except Product.DoesNotExist:
                sale_data["product"] = {"error": "Product not found"}
            try:
                client = Clients.objects.get(id=client_id)
                client_serializer = ClientSerializer(client)
                sale_data["client"] = {
                    "name": client_serializer.data["firstname"]
                    + " "
                    + client_serializer.data["lastname"],
                    "phone": client_serializer.data["phone"],
                    "address": client_serializer.data["address"],
                }

            except Users.DoesNotExist:
                sale_data["client"] = {"error": "Client not found"}
        # Return the sales data with product and client information
        # return Response(sales_serializer.data)

        return Response(sales_serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getUsersFromSales(request):
    try:
        sales = Sales.objects.all()
        sales_serializer = SalesSerializer(sales, many=True)

        # For each sale, retrieve and add the user data
        for sale_data in sales_serializer.data:
            user_id = sale_data["user"]

            try:
                user = Users.objects.get(id=user_id)
                user_serializer = UserSerializer(user)
                sale_data["user"] = {
                    "firstname": user_serializer.data["firstname"],
                    "lastname": user_serializer.data["lastname"],
                }
            except Users.DoesNotExist:
                sale_data["user"] = {"error": "User not found"}

        return Response(sales_serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def paySale(request, pk):
    try:
        # Retrieve the sale record by primary key
        sale = Sales.objects.get(id=pk)
        if sale.is_paid:
            return Response(
                {"error": "Sale already paid"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Update the sale status to "paid"
        sale.is_paid = True
        sale.save()

        # Serialize the updated sale record
        serializer = SalesSerializer(sale)

        return Response(serializer.data)
    except Sales.DoesNotExist:
        return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
