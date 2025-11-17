from rest_framework import permissions

class IsAdminUserOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role == 1


   