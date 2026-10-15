from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsEmployer(BasePermission):
    message = "Chỉ Employer mới được quản lý Company."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.EMPLOYER)
