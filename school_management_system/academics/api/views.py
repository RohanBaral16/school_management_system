from rest_framework.viewsets import ReadOnlyModelViewSet
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
	ClassTeacherSerializer,
	StandardSerializer,
	StudentEnrollmentSerializer,
	SubjectSerializer,
	TeacherSubjectSerializer,
)
from .filters import (
	AcademicYearFilter,
	ClassTeacherFilter,
	StandardFilter,
	StudentEnrollmentFilter,
	SubjectFilter,
	TeacherSubjectFilter,
)


class AcademicYearReadOnlyViewSet(ReadOnlyModelViewSet):
	queryset = AcademicYear.objects.all()
	serializer_class = AcademicYearSerializer
	permission_classes = [IsAuthenticated]
	filterset_class = AcademicYearFilter


class StandardReadOnlyViewSet(ReadOnlyModelViewSet):
	queryset = Standard.objects.all()
	serializer_class = StandardSerializer
	permission_classes = [IsAuthenticated]
	filterset_class = StandardFilter


class SubjectReadOnlyViewSet(ReadOnlyModelViewSet):
	queryset = Subject.objects.select_related('standard')
	serializer_class = SubjectSerializer
	permission_classes = [IsAuthenticated]
	filterset_class = SubjectFilter


class StudentEnrollmentReadOnlyViewSet(ReadOnlyModelViewSet):
	queryset = StudentEnrollment.objects.select_related('student', 'standard', 'academic_year')
	serializer_class = StudentEnrollmentSerializer
	permission_classes = [IsAuthenticated]
	filterset_class = StudentEnrollmentFilter


class ClassTeacherReadOnlyViewSet(ReadOnlyModelViewSet):
	queryset = ClassTeacher.objects.select_related('standard', 'teacher', 'academic_year')
	serializer_class = ClassTeacherSerializer
	permission_classes = [IsAuthenticated]
	filterset_class = ClassTeacherFilter


class TeacherSubjectReadOnlyViewSet(ReadOnlyModelViewSet):
	queryset = TeacherSubject.objects.select_related('subject', 'teacher', 'academic_year')
	serializer_class = TeacherSubjectSerializer
	permission_classes = [IsAuthenticated]
	filterset_class = TeacherSubjectFilter
