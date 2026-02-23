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
        user = self.request.user
        
        # Admin/Superuser can see all students
        if user.is_staff or user.is_superuser:
            return Student.objects.all()
        
        # Check if user is a teacher
        try:
            teacher = Teacher.objects.get(user=user)
            # Teacher can see students in their assigned classes
            from academics.models import ClassTeacher, TeacherSubject, StudentEnrollment
            
            # Get standards where teacher is class teacher
            class_standards = ClassTeacher.objects.filter(teacher=teacher).values_list('standard', flat=True)
            
            # Get standards from subjects teacher teaches
            subject_standards = TeacherSubject.objects.filter(teacher=teacher).values_list('subject__standard', flat=True)
            
            # Combine both querysets
            all_standards = set(list(class_standards) + list(subject_standards))
            
            # Get students enrolled in these standards
            student_ids = StudentEnrollment.objects.filter(
                standard__in=all_standards
            ).values_list('student', flat=True).distinct()
            
            return Student.objects.filter(id__in=student_ids)
        except Teacher.DoesNotExist:
            pass
        
        # Check if user is a student
        try:
            student = Student.objects.get(user=user)
            # Students can only see their own record
            return Student.objects.filter(id=student.id)
        except Student.DoesNotExist:
            pass
        
        # If user is neither teacher nor student, return empty queryset
        return Student.objects.none()


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
        user = self.request.user
        
        # Admin/Superuser can see all teachers
        if user.is_staff or user.is_superuser:
            return Teacher.objects.select_related('user')
        
        # Teachers can see all other teachers
        try:
            teacher = Teacher.objects.get(user=user)
            return Teacher.objects.select_related('user')
        except Teacher.DoesNotExist:
            pass
        
        # Students can see all teachers
        try:
            student = Student.objects.get(user=user)
            return Teacher.objects.select_related('user')
        except Student.DoesNotExist:
            pass
        
        # If user is neither, return empty queryset
        return Teacher.objects.none()
    
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
    