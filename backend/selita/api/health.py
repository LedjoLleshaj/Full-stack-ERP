"""
Health check endpoint for Docker and load balancer health checks.
"""
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint.
    Returns 200 OK if the service is running.
    Used by Docker healthcheck and load balancers.
    """
    return JsonResponse({"status": "ok"})
