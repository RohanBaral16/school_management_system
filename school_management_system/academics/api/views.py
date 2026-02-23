"""
ViewSets for Academics app.
Implements CRUD operations with role-based permissions.
"""

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from ..models import (
    AcademicYear,
    ClassTeacher,
    Standard,
    StudentEnrollment,
    Subject,
    TeacherSubject,
)
from .serializers import (
    AcademicYearSerializer,
    AcademicYearWriteSerializer,
    ClassTeacherSerializer,
    ClassTeacherWriteSerializer,
    StandardSerializer,
    StandardWriteSerializer,
    StudentEnrollmentSerializer,
    StudentEnrollmentWriteSerializer,
    SubjectSerializer,
    SubjectWriteSerializer,
    TeacherSubjectSerializer,
    TeacherSubjectWriteSerializer,
)
from .filters import (
    AcademicYearFilter,
    ClassTeacherFilter,
    StandardFilter,
    StudentEnrollmentFilter,
    SubjectFilter,
    TeacherSubjectFilter,
)
from .permissions import IsAdminOrTeacher


# ============================================================================
# ACADEMIC YEAR VIEWSETS
# ============================================================================

class AcademicYearViewSet(ModelViewSet):
    """
    CRUD ViewSet for AcademicYear model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = AcademicYear.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = AcademicYearFilter
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return AcademicYearWriteSerializer
        return AcademicYearSerializer


class AcademicYearReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AcademicYearFilter


# ============================================================================
# STANDARD VIEWSETS
# ============================================================================

class StandardViewSet(ModelViewSet):
    """
    CRUD ViewSet for Standard model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = Standard.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = StandardFilter
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return StandardWriteSerializer
        return StandardSerializer


class StandardReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StandardFilter


# ============================================================================
# SUBJECT VIEWSETS
# ============================================================================

class SubjectViewSet(ModelViewSet):
    """
    CRUD ViewSet for Subject model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = Subject.objects.select_related('standard')
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = SubjectFilter
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return SubjectWriteSerializer
        return SubjectSerializer


class SubjectReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = Subject.objects.select_related('standard')
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SubjectFilter


# ============================================================================
# STUDENT ENROLLMENT VIEWSETS
# ============================================================================

class StudentEnrollmentViewSet(ModelViewSet):
    """
    CRUD ViewSet for StudentEnrollment model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = StudentEnrollment.objects.select_related('student', 'standard', 'academic_year')
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = StudentEnrollmentFilter
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return StudentEnrollmentWriteSerializer
        return StudentEnrollmentSerializer


class StudentEnrollmentReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = StudentEnrollment.objects.select_related('student', 'standard', 'academic_year')
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentEnrollmentFilter


# ============================================================================
# CLASS TEACHER VIEWSETS
# ============================================================================

class ClassTeacherViewSet(ModelViewSet):
    """
    CRUD ViewSet for ClassTeacher model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = ClassTeacher.objects.select_related('standard', 'teacher', 'academic_year')
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = ClassTeacherFilter
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ClassTeacherWriteSerializer
        return ClassTeacherSerializer


class ClassTeacherReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = ClassTeacher.objects.select_related('standard', 'teacher', 'academic_year')
    serializer_class = ClassTeacherSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ClassTeacherFilter


# ============================================================================
# TEACHER SUBJECT VIEWSETS
# ============================================================================

class TeacherSubjectViewSet(ModelViewSet):
    """
    CRUD ViewSet for TeacherSubject model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = TeacherSubject.objects.select_related('subject', 'teacher', 'academic_year')
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = TeacherSubjectFilter
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return TeacherSubjectWriteSerializer
        return TeacherSubjectSerializer


class TeacherSubjectReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = TeacherSubject.objects.select_related('subject', 'teacher', 'academic_year')
    serializer_class = TeacherSubjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TeacherSubjectFilter
