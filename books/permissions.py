# books/permissions.py
from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)

class IsPublisher(BasePermission):
    """
    Allows access only to users with role 3 (Publisher)
    """
    def has_permission(self, request, view):
        user = request.user
        try:
            role = int(getattr(user, 'role', 0))  # cast to int
        except (ValueError, TypeError):
            role = 0

        is_publisher = bool(user.is_authenticated and role == 3)

        print(f"user.role: {user.role} ({type(user.role)})")
        print(f"is_publisher: {is_publisher}")

        return is_publisher


class IsAdmin(BasePermission):
    """
    Allows access only to users with role 3 (Publisher)
    """
    def has_permission(self, request, view):
        user = request.user
        try:
            role = int(getattr(user, 'role', 0))  # cast to int
        except (ValueError, TypeError):
            role = 0

        is_admin = bool(user.is_authenticated and role == 1)

        print(f"user.role: {user.role} ({type(user.role)})")
        print(f"is_admin: {is_admin}")

        return is_admin
