"""
Standardized response utilities for the ERP backend.

This module centralizes all response patterns, replacing the duplicated
error handling code that was spread across 50+ locations in API files.
"""

from rest_framework.response import Response
from rest_framework import status
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def success_response(data=None, message: str = None, status_code: int = status.HTTP_200_OK) -> Response:
    """
    Create a standardized success response.
    
    Args:
        data: Response data (dict, list, or any serializable object)
        message: Optional success message
        status_code: HTTP status code (default 200)
    
    Returns:
        DRF Response object
    """
    response_data = data if data is not None else {}
    if message and isinstance(response_data, dict):
        response_data["message"] = message
    return Response(response_data, status=status_code)


def created_response(data=None, message: str = "Created successfully") -> Response:
    """Create a 201 Created response."""
    response_data = data if data is not None else {}
    if isinstance(response_data, dict):
        response_data["message"] = message
    return Response(response_data, status=status.HTTP_201_CREATED)


def error_response(
    message: str, 
    details: str = None, 
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> Response:
    """
    Create a standardized error response.
    
    Args:
        message: User-friendly error message
        details: Technical details (shown in development)
        status_code: HTTP status code (default 500)
    
    Returns:
        DRF Response object
    """
    data = {"error": message}
    if details:
        data["details"] = details
    return Response(data, status=status_code)


def not_found_response(entity: str = "Resource") -> Response:
    """Create a 404 Not Found response."""
    return error_response(f"{entity} not found", status_code=status.HTTP_404_NOT_FOUND)


def bad_request_response(message: str, details: str = None) -> Response:
    """Create a 400 Bad Request response."""
    return error_response(message, details, status_code=status.HTTP_400_BAD_REQUEST)


def validation_error_response(errors: dict) -> Response:
    """Create a 400 response for validation errors from serializers."""
    return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)


def unauthorized_response(message: str = "Authentication required") -> Response:
    """Create a 401 Unauthorized response."""
    return error_response(message, status_code=status.HTTP_401_UNAUTHORIZED)


def api_error_handler(func):
    """
    Decorator for consistent API error handling.
    
    Wraps a view function to catch exceptions and return standardized
    error responses instead of crashing.
    
    Usage:
        @api_view(["GET"])
        @api_error_handler
        def my_view(request):
            # If this raises an exception, it will be caught
            # and returned as a proper error response
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            return error_response("An unexpected error occurred", str(e))
    return wrapper
