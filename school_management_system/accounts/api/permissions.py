"""
Permission classes for Accounts API endpoints.
Implements role-based access control for Students and Teachers.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated
from accounts.models import Teacher, Student


class IsAdmin(BasePermission):
    """Only superusers can access."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsTeacherOrAdmin(BasePermission):
    """Teachers and admins can access."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins have full access
        if request.user.is_superuser:
            return True
        
        # Check if user is a teacher
        return Teacher.objects.filter(user=request.user).exists()


class IsTeacher(BasePermission):
    """Only teachers can access."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return Teacher.objects.filter(user=request.user).exists()
    
    def has_object_permission(self, request, view, obj):
        """Teachers can only modify their own records."""
        if request.user.is_superuser:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsStudentOrTeacherOrAdmin(BasePermission):
    """Authenticated users with role-based filtering."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class ReadOnlyIfNotTeacher(BasePermission):
    """Non-teachers can only read. Teachers and admins have full access."""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Allow read access to all authenticated users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write access only for teachers/admins
        if not request.user.is_superuser:
            teacher_exists = Teacher.objects.filter(user=request.user).exists()
            if not teacher_exists:
                return False
        
        return True
