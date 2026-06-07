from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from erp.models import User
from erp.serializers import UserSerializer
from erp.utils.responses import api_error_handler, not_found_response, bad_request_response


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def getUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("User")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def createUser(request):
    d = request.data
    required = ("username", "password", "firstname", "lastname")
    if any(k not in d or not d[k] for k in required):
        return bad_request_response(f"Required: {', '.join(required)}")
    try:
        user = User.objects.create_user(
            username=d["username"],
            password=d["password"],
            email=d.get("email", ""),
            firstname=d["firstname"],
            lastname=d["lastname"],
            role=d.get("role", "STAFF"),
        )
    except IntegrityError:
        return bad_request_response("Username already exists")
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def updateUser(request, pk):
    try:
        user = User.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("User")
    d = request.data
    user.username = d.get("username", user.username)
    user.email = d.get("email", user.email)
    user.firstname = d.get("firstname", user.firstname)
    user.lastname = d.get("lastname", user.lastname)
    user.role = d.get("role", user.role)
    if d.get("password"):
        user.set_password(d["password"])
    user.save()
    return Response(UserSerializer(user).data)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
@api_error_handler
def deleteUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        user.delete()
        return Response("User deleted successfully")
    except ObjectDoesNotExist:
        return not_found_response("User")
