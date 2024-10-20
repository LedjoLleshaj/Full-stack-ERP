from django.shortcuts import render

# Create your views here.


from rest_framework.response import Response
from .models import Users, Product
from rest_framework.decorators import api_view
from .serializers import UserSerializer, ProductSerializer


# Create your views here.
# ======== USERS ========


@api_view(["GET"])
def getUsers(request):
    users = Users.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getUser(request, pk):
    user = Users.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(["POST"])
def createUser(request):
    data = request.data
    user = Users.objects.create(
        username=data["username"],
        password=data["password"],
        email=data["email"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        city=data["city"],
    )
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(["POST"])
def updateUser(request, pk):
    user = Users.objects.get(id=pk)
    data = request.data
    user.username = data["username"]
    user.password = data["password"]
    user.email = data["email"]
    user.firstname = data["first_name"]
    user.lastname = data["last_name"]
    user.save()
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(["DELETE"])
def deleteUser(request, pk):
    user = Users.objects.get(id=pk)
    user.delete()
    return Response("User deleted successfully")


# ======== PRODUCTS ========


@api_view(["GET"])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
