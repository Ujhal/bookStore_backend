from rest_framework import permissions

class IsAdminUserOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role == '1'


class IsPublisher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == '3'

class IsPublisherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        is_admin = request.user.is_superuser or request.user.role == '1'
        is_publisher = request.user.is_authenticated and request.user.role == '3'
        return is_admin or is_publisher