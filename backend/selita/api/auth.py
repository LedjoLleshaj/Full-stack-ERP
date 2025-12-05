# login_view.py
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.conf import settings
from selita.models import Users
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist

@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
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

            # Return response with user details and set cookies
            response = Response(
                {
                    "first_name": user.firstname,
                    "last_name": user.lastname,
                    "username": user.username,
                },
                status=status.HTTP_200_OK,
            )
            
            # Clear any existing cookies first to prevent stale cookie issues
            response.delete_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/')
            )
            response.delete_cookie(
                key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/')
            )
            
            # Set Access Token Cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            
            # Set Refresh Token Cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                value=refresh_token,
                max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            
            return response
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


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    try:
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        
        if refresh_token is None:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        refresh = RefreshToken(refresh_token)
        
        data = {"access": str(refresh.access_token)}

        if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
            if settings.SIMPLE_JWT['BLACKLIST_AFTER_ROTATION']:
                try:
                    # Attempt to blacklist the old refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app is not installed, ignore
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data['refresh'] = str(refresh)
            
        response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=data['access'],
            max_age=int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
        
        if 'refresh' in data:
            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                value=data['refresh'],
                max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            
        return response
        
    except Exception as e:
        # Clear cookies on error to prevent stale cookie issues
        response = Response(
            {"error": "Invalid refresh token", "details": str(e)},
            status=status.HTTP_401_UNAUTHORIZED
        )
        response.delete_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/')
        )
        response.delete_cookie(
            key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
            path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/')
        )
        return response


@api_view(["POST"])
def logout_view(request):
    response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
    response.delete_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/')
    )
    response.delete_cookie(
        key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
        path=settings.SIMPLE_JWT.get('AUTH_COOKIE_PATH', '/')
    )
    return response
