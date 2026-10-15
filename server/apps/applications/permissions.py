from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsCandidate(BasePermission):
    message = "Chỉ Candidate mới được quản lý application của mình."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.CANDIDATE)


class IsEmployer(BasePermission):
    message = "Chỉ Employer mới được quản lý application của Company mình."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.EMPLOYER)
