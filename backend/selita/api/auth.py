# login_view.py
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.conf import settings
from selita.models import Users
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    try:
        data = request.data

        # Validate that both username and password are provided
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

        # Verify password
        if check_password(data["password"], user.password):
            # Generate access and refresh tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Return response with tokens and user details
            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "first_name": user.firstname,
                    "last_name": user.lastname,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
