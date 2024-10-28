from rest_framework.response import Response
from ..models import Users
from rest_framework.decorators import api_view
import jwt
import time
import os
import dotenv
from datetime import timedelta, datetime, timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

dotenv.load_dotenv()

secret = os.getenv("secret")
algorithm = os.getenv("algorithm")


# ======== LOGIN ========


@api_view(["POST"])
def login(request):
    try:
        data = request.data

        # Check if both 'username' and 'password' are provided
        if "username" not in data or "password" not in data:
            return Response(
                {"error": "Both username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Attempt to retrieve user by username
        try:
            user = Users.objects.get(username=data["username"])
        except ObjectDoesNotExist:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Check password (consider using hashing for real applications)
        if (
            user.password == data["password"]
        ):  # Replace with hashed password check if applicable

            # Generate JWT token with a 30-second expiration
            token = jwt.encode(
                {
                    "username": user.username,
                    "exp": datetime.now(timezone.utc) + timedelta(seconds=30),
                },
                secret,
                algorithm=algorithm,
            )

            # Return response with token and user details
            return Response(
                {
                    "token": token,
                    "first_name": user.firstname,
                    "last_name": user.lastname,
                },
                status=status.HTTP_200_OK,
            )

        else:
            # Password does not match
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    except jwt.PyJWTError as e:
        # Catch JWT encoding/decoding errors
        return Response(
            {"error": "Token generation error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except Exception as e:
        # Catch any other unexpected errors
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
