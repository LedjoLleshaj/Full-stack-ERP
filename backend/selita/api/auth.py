from rest_framework.response import Response
from ..models import Users
from rest_framework.decorators import api_view
import jwt
import time
import os
import dotenv
from datetime import timedelta, datetime, timezone

dotenv.load_dotenv()

secret = os.getenv("secret")
algorithm = os.getenv("algorithm")


# ======== LOGIN ========
@api_view(["POST"])
def login(request):
    data = request.data
    user = Users.objects.get(username=data["username"])
    if user.password == data["password"]:

        token = jwt.encode(
            {
                "username": user.username,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=30),
            },
            secret,
            algorithm=algorithm,
        )
        # response has token, user's first name and last name
        return Response(
            {
                "token": token,
                "first_name": user.firstname,
                "last_name": user.lastname,
            }
        )

    else:
        return Response(
            {"error": "Invalid username or password"},
            status=401,
        )
