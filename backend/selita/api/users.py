from rest_framework.response import Response
from rest_framework import permissions
from ..models import Users
from rest_framework.decorators import api_view, permission_classes
from ..serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.contrib.auth.hashers import make_password


# ======== USERS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getUsers(request):
    try:
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def getUser(request, pk):
    try:
        user = Users.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def createUser(request):
    try:
        data = request.data
        user = Users.objects.create(
            username=data["username"],
            password=make_password(
                data["password"]
            ),  # Hash the password here            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data["phone"],
            city=data["city"],
        )
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def updateUser(request, pk):
    try:
        user = Users.objects.get(id=pk)
        data = request.data
        user.username = data["username"]
        user.password = data["password"]
        user.email = data["email"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.phone = data["phone"]
        user.city = data["city"]
        user.save()
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def deleteUser(request, pk):
    try:
        user = Users.objects.get(id=pk)
        user.delete()
        return Response("User deleted successfully")
    except ObjectDoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
