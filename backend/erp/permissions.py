from rest_framework.permissions import BasePermission

from erp.constants import UserRole


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN)


class IsManagerOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in UserRole.MANAGER_AND_ABOVE)


class IsStaffOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in UserRole.STAFF_AND_ABOVE)


class IsViewer(BasePermission):
    """Read-only for all authenticated users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
