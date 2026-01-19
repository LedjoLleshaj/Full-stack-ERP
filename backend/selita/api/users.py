from rest_framework.response import Response
from rest_framework import permissions
from ..models import Users
from rest_framework.decorators import api_view, permission_classes
from ..serializers import UserSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from selita.utils.responses import api_error_handler, not_found_response


# ======== USERS ========


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getUsers(request):
    users = Users.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getUser(request, pk):
    try:
        user = Users.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("User")


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@api_error_handler
def createUser(request):
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


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
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
        return not_found_response("User")


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def deleteUser(request, pk):
    try:
        user = Users.objects.get(id=pk)
        user.delete()
        return Response("User deleted successfully")
    except ObjectDoesNotExist:
        return not_found_response("User")
