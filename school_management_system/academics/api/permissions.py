"""
Permission classes for Academics API endpoints.
Implements role-based access control for academic resources.
"""

from rest_framework.permissions import BasePermission
from accounts.models import Teacher


class IsAdminOrTeacher(BasePermission):
    """
    Only admin users and teachers can create, update, or delete.
    All authenticated users can read.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow read access to all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write access only for admins and teachers
        if request.user.is_superuser:
            return True
        
        return Teacher.objects.filter(user=request.user).exists()


class IsAdmin(BasePermission):
    """Only superusers can access."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsTeacher(BasePermission):
    """Only teachers can access."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return Teacher.objects.filter(user=request.user).exists()


class IsTeacherOrReadOnly(BasePermission):
    """Teachers can edit, others can only read."""
    
    def has_permission(self, request, view):
        # Allow read to all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return bool(request.user and request.user.is_authenticated)
        
        # Write access for authenticated users
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Read permission for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions for teachers and admins only
        if request.user.is_superuser:
            return True
        
        return Teacher.objects.filter(user=request.user).exists()
