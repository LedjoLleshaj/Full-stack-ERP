from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from selita.models import Users

def enforce_csrf(request):
    check = CSRFCheck(request)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        
        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        # enforce_csrf(request) # Optional: Enforce CSRF if needed, but HttpOnly + SameSite=Lax is usually enough for GET
        return self.get_user(validated_token), validated_token
    
    def get_user(self, validated_token):
        """
        Override to use custom Users model instead of Django's default User model
        """
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                raise InvalidToken('Token contained no recognizable user identification')
            
            # Use custom Users model
            user = Users.objects.get(id=user_id)
            return user
        except Users.DoesNotExist:
            raise InvalidToken('User not found')
