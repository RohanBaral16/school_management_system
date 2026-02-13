from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch

from ..models import SubjectResult, ExamSubject, StudentResultSummary, Attendance, Exam, StudentMarksheet
from .serializers import (
    SubjectResultSerializer,
    ExamSubjectSerializer,
    StudentResultSummarySerializer,
    ExamSerializer,
    AttendanceSerializer,
    StudentMarksheetSerializer,
)
from .filters import SubjectResultFilter, ExamSubjectFilter, StudentResultSummaryFilter, StudentMarksheetFilter


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


class StudentMarksheetReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = StudentMarksheetSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentMarksheetFilter
    queryset = StudentMarksheet.objects.select_related(
        'resultsummary',
        'resultsummary__student',
        'resultsummary__student__student',
        'resultsummary__student__standard',
        'resultsummary__exam',
        'result',
        'result__exam_subject',
        'result__exam_subject__subject',
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
        # Prefetch SubjectResults with all their nested relationships
        results_prefetch = Prefetch(
            'results',
            SubjectResult.objects.select_related(
                'exam_subject__exam__academic_year',
                'exam_subject__subject__standard',
                'exam_subject__standard',
                'student__student',
                'student__standard',
                'student__academic_year',
            ),
        )

        return StudentResultSummary.objects.select_related(
            'student__student',
            'student__standard',
            'student__academic_year',
            'exam__academic_year',
            'academic_year',
        ).prefetch_related(results_prefetch)