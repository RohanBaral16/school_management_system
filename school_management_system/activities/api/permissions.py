from rest_framework.permissions import BasePermission

from accounts.models import Teacher


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        return Teacher.objects.filter(user=user).exists()
