from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsAdminRole(BasePermission):
    message = "Chỉ Admin mới được sử dụng API này."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN)
