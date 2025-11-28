from rest_framework.response import Response
from rest_framework import permissions
from ..models import Supplier
from rest_framework.decorators import api_view, permission_classes
from ..serializers import SupplierSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status


# ======== SUPPLIERS ========


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getSuppliers(request):
    try:
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
def getSupplier(request, pk):
    try:
        supplier = Supplier.objects.get(id=pk)
        serializer = SupplierSerializer(supplier, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
# @permission_classes([permissions.AllowAny])
def addSupplier(request):
    try:
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
# @permission_classes([permissions.IsAuthenticated])
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
        return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
# @permission_classes([permissions.IsAuthenticated])
def deleteSupplier(request, pk):
    try:
        supplier = Supplier.objects.get(id=pk)
        supplier.delete()
        return Response("Supplier deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
