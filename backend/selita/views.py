from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User
from .serializers import UserSerializer


# Create your views here.

@api_view(["GET"])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

def getUser(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

def createUser(request):
    data = request.data
    user = User.objects.create(
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

def updateUser(request, pk):
    user = User.objects.get(id=pk)
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

def deleteUser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response("User deleted successfully")

