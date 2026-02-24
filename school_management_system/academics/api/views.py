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


# ACADEMIC YEAR VIEWSETS

class AcademicYearViewSet(ModelViewSet):
    """
    CRUD ViewSet for AcademicYear model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = AcademicYear.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = AcademicYearFilter
    ordering_fields = ['id', 'title', 'start_date', 'end_date']
    ordering = ['-start_date']
    
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
    ordering_fields = ['id', 'title', 'start_date', 'end_date']
    ordering = ['-start_date']



# STANDARD VIEWSETS


class StandardViewSet(ModelViewSet):
    """
    CRUD ViewSet for Standard model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = Standard.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = StandardFilter
    ordering_fields = ['id', 'title', 'created_at']
    ordering = ['title']
    
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
    ordering_fields = ['id', 'title', 'created_at']
    ordering = ['title']



# SUBJECT VIEWSETS


class SubjectViewSet(ModelViewSet):
    """
    CRUD ViewSet for Subject model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = Subject.objects.select_related('standard')
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = SubjectFilter
    ordering_fields = ['id', 'title', 'code', 'standard']
    ordering = ['standard', 'title']
    
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
    ordering_fields = ['id', 'title', 'code', 'standard']
    ordering = ['standard', 'title']


# STUDENT ENROLLMENT VIEWSETS


class StudentEnrollmentViewSet(ModelViewSet):
    """
    CRUD ViewSet for StudentEnrollment model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = StudentEnrollment.objects.select_related('student', 'standard', 'academic_year')
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = StudentEnrollmentFilter
    ordering_fields = ['id', 'student', 'standard', 'academic_year', 'enrollment_date']
    ordering = ['-enrollment_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return StudentEnrollmentWriteSerializer
        return StudentEnrollmentSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        from accounts.models import Student, Teacher
        user = self.request.user
        
        # Admin/Superuser can see all enrollments
        if user.is_staff or user.is_superuser:
            return StudentEnrollment.objects.select_related('student', 'standard', 'academic_year')
        
        # Teachers can see enrollments for their assigned classes
        try:
            teacher = Teacher.objects.get(user=user)
            class_standards = ClassTeacher.objects.filter(teacher=teacher).values_list('standard', flat=True)
            subject_standards = TeacherSubject.objects.filter(teacher=teacher).values_list('subject__standard', flat=True)
            all_standards = set(list(class_standards) + list(subject_standards))
            return StudentEnrollment.objects.filter(standard__in=all_standards).select_related('student', 'standard', 'academic_year')
        except Teacher.DoesNotExist:
            pass
        
        # Students can see only their own enrollments
        try:
            student = Student.objects.get(user=user)
            return StudentEnrollment.objects.filter(student=student).select_related('student', 'standard', 'academic_year')
        except Student.DoesNotExist:
            pass
        
        return StudentEnrollment.objects.none()


class StudentEnrollmentReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = StudentEnrollment.objects.select_related('student', 'standard', 'academic_year')
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentEnrollmentFilter
    ordering_fields = ['id', 'student', 'standard', 'academic_year', 'enrollment_date']
    ordering = ['-enrollment_date']



# CLASS TEACHER VIEWSETS


class ClassTeacherViewSet(ModelViewSet):
    """
    CRUD ViewSet for ClassTeacher model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = ClassTeacher.objects.select_related('standard', 'teacher', 'academic_year')
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = ClassTeacherFilter
    ordering_fields = ['id', 'standard', 'teacher', 'academic_year']
    ordering = ['academic_year', 'standard']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ClassTeacherWriteSerializer
        return ClassTeacherSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        from accounts.models import Student, Teacher
        user = self.request.user
        
        # Admin/Superuser can see all class teacher assignments
        if user.is_staff or user.is_superuser:
            return ClassTeacher.objects.select_related('standard', 'teacher', 'academic_year')
        
        # Teachers can see class teacher assignments for their classes
        try:
            teacher = Teacher.objects.get(user=user)
            return ClassTeacher.objects.filter(teacher=teacher).select_related('standard', 'teacher', 'academic_year')
        except Teacher.DoesNotExist:
            pass
        
        # Students can see class teachers for their enrolled standards
        try:
            student = Student.objects.get(user=user)
            enrolled_standards = StudentEnrollment.objects.filter(student=student).values_list('standard', flat=True)
            return ClassTeacher.objects.filter(standard__in=enrolled_standards).select_related('standard', 'teacher', 'academic_year')
        except Student.DoesNotExist:
            pass
        
        return ClassTeacher.objects.none()


class ClassTeacherReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = ClassTeacher.objects.select_related('standard', 'teacher', 'academic_year')
    serializer_class = ClassTeacherSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ClassTeacherFilter
    ordering_fields = ['id', 'standard', 'teacher', 'academic_year']
    ordering = ['academic_year', 'standard']



# TEACHER SUBJECT VIEWSETS

class TeacherSubjectViewSet(ModelViewSet):
    """
    CRUD ViewSet for TeacherSubject model.
    - Admins and Teachers can create, update, delete
    - All authenticated users can read
    """
    
    queryset = TeacherSubject.objects.select_related('subject', 'teacher', 'academic_year')
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = TeacherSubjectFilter
    ordering_fields = ['id', 'teacher', 'subject', 'academic_year']
    ordering = ['academic_year', 'teacher']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return TeacherSubjectWriteSerializer
        return TeacherSubjectSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        from accounts.models import Student, Teacher
        user = self.request.user
        
        # Admin/Superuser can see all teacher-subject assignments
        if user.is_staff or user.is_superuser:
            return TeacherSubject.objects.select_related('subject', 'teacher', 'academic_year')
        
        # Teachers can see their own subject assignments
        try:
            teacher = Teacher.objects.get(user=user)
            return TeacherSubject.objects.filter(teacher=teacher).select_related('subject', 'teacher', 'academic_year')
        except Teacher.DoesNotExist:
            pass
        
        # Students can see teacher-subject assignments for their enrolled standards
        try:
            student = Student.objects.get(user=user)
            enrolled_standards = StudentEnrollment.objects.filter(student=student).values_list('standard', flat=True)
            return TeacherSubject.objects.filter(subject__standard__in=enrolled_standards).select_related('subject', 'teacher', 'academic_year')
        except Student.DoesNotExist:
            pass
        
        return TeacherSubject.objects.none()


class TeacherSubjectReadOnlyViewSet(ReadOnlyModelViewSet):
    """Legacy read-only ViewSet for backward compatibility."""
    
    queryset = TeacherSubject.objects.select_related('subject', 'teacher', 'academic_year')
    serializer_class = TeacherSubjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TeacherSubjectFilter
    ordering_fields = ['id', 'teacher', 'subject', 'academic_year']
    ordering = ['academic_year', 'teacher']
