"""
ViewSets for Accounts app.
Implements CRUD operations with role-based permissions.
"""

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..models import Student, Teacher
from .serializers import (
    StudentSerializer,
    StudentWriteSerializer,
    TeacherSerializer,
    TeacherWriteSerializer,
)
from .permissions import IsTeacherOrAdmin, ReadOnlyIfNotTeacher
from .filters import StudentFilter


# ============================================================================
# STUDENT VIEWSETS
# ============================================================================

class StudentViewSet(ModelViewSet):
    """
    CRUD ViewSet for Student model.
    - List/Create: Admin and Teachers
    - Read: All authenticated users
    - Update/Delete: Admin only
    """
    
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated, ReadOnlyIfNotTeacher]
    filterset_class = StudentFilter
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on request method.
        - Read operations: StudentSerializer (with nested fields)
        - Write operations: StudentWriteSerializer (flat structure)
        """
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return StudentWriteSerializer
        return StudentSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = Student.objects.all()
        
        # Implement filtering logic if needed
        # Non-admin users might see specific students only
        
        return queryset


class StudentReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    Legacy read-only ViewSet for backward compatibility.
    """
    
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentFilter


# ============================================================================
# TEACHER VIEWSETS
# ============================================================================

class TeacherViewSet(ModelViewSet):
    """
    CRUD ViewSet for Teacher model.
    - List/Create: Admin and Teachers
    - Read: All authenticated users
    - Update: Teachers can update their own records, Admins can update all
    - Delete: Admin only
    """
    
    queryset = Teacher.objects.select_related('user')
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on request method.
        - Read operations: TeacherSerializer (with nested User info)
        - Write operations: TeacherWriteSerializer (flat structure)
        """
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return TeacherWriteSerializer
        return TeacherSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = Teacher.objects.select_related('user')
        
        # Implement filtering if needed
        # Non-admin teachers might see specific teachers only
        
        return queryset
    
    def perform_create(self, serializer):
        """Override create to add any custom logic."""
        serializer.save()
    
    def perform_update(self, serializer):
        """Override update to add any custom logic."""
        serializer.save()


class TeacherReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    Legacy read-only ViewSet for backward compatibility.
    """
    
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    