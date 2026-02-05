from rest_framework.response import Response
from rest_framework import permissions
from ..models import Supplier
from rest_framework.decorators import api_view, permission_classes
from ..serializers import SupplierSerializer
from django.core.exceptions import ObjectDoesNotExist
from selita.utils.responses import api_error_handler, not_found_response


# ======== SUPPLIERS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getSuppliers(request):
    suppliers = Supplier.objects.filter(is_active=True)
    serializer = SupplierSerializer(suppliers, many=True)
    return Response(serializer.data)


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getSupplier(request, pk):
    try:
        supplier = Supplier.objects.get(id=pk)
        serializer = SupplierSerializer(supplier, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("Supplier")


@api_view(["POST"])
# @permission_classes([permissions.AllowAny])
@api_error_handler
def addSupplier(request):
    data = request.data
    supplier = Supplier.objects.create(
        firstname=data["firstname"],
        lastname=data["lastname"],
        phone=data.get("phone"),
        email=data.get("email"),
        address=data["address"],
    )
    supplier.save()
    serializer = SupplierSerializer(supplier, many=False)
    return Response(serializer.data, status=201)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def updateSupplier(request, pk):
    try:
        supplier = Supplier.objects.get(id=pk)
        data = request.data
        supplier.firstname = data["firstname"]
        supplier.lastname = data["lastname"]
        supplier.phone = data.get("phone")
        supplier.email = data.get("email")
        supplier.address = data["address"]
        supplier.save()
        serializer = SupplierSerializer(supplier, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("Supplier")


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def deleteSupplier(request, pk):
    from ..models import Transaction, Restock
    
    try:
        supplier = Supplier.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Supplier")
    
    # Soft delete
    supplier.is_active = False
    supplier.save()
    
    return Response({"message": "Supplier deactivated successfully"})
