from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from ..models import SubjectResult, ExamSubject, StudentResultSummary, Attendance, Exam
from .serializers import (
    SubjectResultSerializer,
    ExamSubjectSerializer,
    StudentResultSummarySerializer,
    ExamSerializer,
    AttendanceSerializer,
    MarksheetDetailSerializer,
)
from .filters import SubjectResultFilter, ExamSubjectFilter, StudentResultSummaryFilter, MarksheetDetailFilter


class ExamReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    queryset = Exam.objects.select_related('academic_year')


class AttendanceReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Attendance.objects.select_related(
        'student',
        'standard',
        'subject__standard',
        'recorded_by',
        'academic_year',
    )


class MarksheetDetailReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for marksheet details - replaces StudentMarksheetReadOnlyViewSet.
    Uses SubjectResult as base model instead of the removed StudentMarksheet through table.
    
    Note: To optimize the summary field lookups in the serializer, the viewset could be enhanced
    to prefetch StudentResultSummary objects and pass them in the serializer context to avoid N+1 queries.
    """
    serializer_class = MarksheetDetailSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MarksheetDetailFilter
    
    def get_queryset(self):
        return SubjectResult.objects.select_related(
            'student',
            'student__student',
            'student__standard',
            'student__academic_year',
            'exam_subject',
            'exam_subject__exam',
            'exam_subject__subject',
        )


class SubjectResultReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = SubjectResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SubjectResultFilter

    def get_queryset(self):
        return SubjectResult.objects.select_related(
            'exam_subject__exam__academic_year',
            'exam_subject__subject__standard',
            'exam_subject__standard',
            'student__student',
            'student__standard',
            'student__academic_year',
        )


class ExamSubjectReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = ExamSubjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ExamSubjectFilter

    def get_queryset(self):
        return ExamSubject.objects.select_related(
            'exam',
            'exam__academic_year',
            'subject',
            'subject__standard',
            'standard',
        )


class StudentResultSummaryReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = StudentResultSummarySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentResultSummaryFilter

    def get_queryset(self):
        # No need to prefetch results anymore since we use SerializerMethodField
        # The serializer will handle fetching results dynamically with proper select_related
        return StudentResultSummary.objects.select_related(
            'student__student',
            'student__standard',
            'student__academic_year',
            'exam__academic_year',
            'academic_year',
        )