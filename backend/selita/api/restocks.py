from rest_framework.response import Response
from rest_framework import permissions
from ..models import Restock, Product, Payment, Inventory
from rest_framework.decorators import api_view, permission_classes
from ..serializers import RestockSerializer, ProductSerializer, PaymentSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== RESTOCKS ========


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getRestocks(request):
    try:
        restocks = Restock.objects.all().order_by('-restock_date')
        serializer = RestockSerializer(restocks, many=True)
        
        # Add product and payment info
        for restock_data in serializer.data:
            try:
                product = Product.objects.get(id=restock_data['prod'])
                product_serializer = ProductSerializer(product)
                restock_data['product_info'] = {
                    'name': product_serializer.data.get('name'),
                    'category': product_serializer.data.get('category'),
                    'price': product_serializer.data.get('price'),
                }
            except ObjectDoesNotExist:
                restock_data['product_info'] = None
                
            try:
                payment = Payment.objects.get(id=restock_data['payment'])
                payment_serializer = PaymentSerializer(payment)
                restock_data['payment_info'] = {
                    'amount': payment_serializer.data.get('amount'),
                    'currency': payment_serializer.data.get('currency'),
                    'payment_method': payment_serializer.data.get('payment_method'),
                }
            except ObjectDoesNotExist:
                restock_data['payment_info'] = None
        
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getRestock(request, pk):
    try:
        restock = Restock.objects.get(id=pk)
        serializer = RestockSerializer(restock, many=False)
        
        response_data = serializer.data
        
        # Add full product info
        product_serializer = ProductSerializer(restock.prod)
        response_data['product_info'] = product_serializer.data
        
        # Add full payment info
        payment_serializer = PaymentSerializer(restock.payment)
        response_data['payment_info'] = payment_serializer.data
        
        return Response(response_data)
    except ObjectDoesNotExist:
        return Response({"error": "Restock not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
def addRestock(request):
    try:
        serializer = RestockSerializer(data=request.data)
        if serializer.is_valid():
            restock = serializer.save()
            
            # Update inventory - add the restocked quantity
            product_id = request.data.get('prod')
            quantity = request.data.get('quantity')
            
            try:
                product = Product.objects.get(id=product_id)
                inventory = Inventory.objects.get(prod=product)
                inventory.quantity += quantity
                inventory.save()
            except ObjectDoesNotExist:
                # If no inventory record exists, create one
                product = Product.objects.get(id=product_id)
                Inventory.objects.create(prod=product, quantity=quantity)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
# @permission_classes([permissions.IsAuthenticated])
def updateRestock(request, pk):
    try:
        restock = Restock.objects.get(id=pk)
        old_quantity = restock.quantity
        
        serializer = RestockSerializer(instance=restock, data=request.data)
        if serializer.is_valid():
            updated_restock = serializer.save()
            
            # Update inventory: remove old quantity and add new quantity
            quantity_difference = updated_restock.quantity - old_quantity
            if quantity_difference != 0:
                try:
                    inventory = Inventory.objects.get(prod=updated_restock.prod)
                    inventory.quantity += quantity_difference
                    inventory.save()
                except ObjectDoesNotExist:
                    pass
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({"error": "Restock not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
# @permission_classes([permissions.IsAuthenticated])
def deleteRestock(request, pk):
    try:
        restock = Restock.objects.get(id=pk)
        
        # Remove the restocked quantity from inventory
        try:
            inventory = Inventory.objects.get(prod=restock.prod)
            inventory.quantity -= restock.quantity
            inventory.save()
        except ObjectDoesNotExist:
            pass
        
        restock.delete()
        return Response("Restock deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "Restock not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
