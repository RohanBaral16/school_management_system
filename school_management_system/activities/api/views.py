from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Sum

from ..models import SubjectResult, ExamSubject, StudentResultSummary, Attendance, Exam
from .serializers import (
    SubjectResultSerializer,
    SubjectResultWriteSerializer,
    ExamSubjectSerializer,
    ExamSubjectWriteSerializer,
    StudentResultSummarySerializer,
    StudentResultSummaryWriteSerializer,
    ExamSerializer,
    ExamWriteSerializer,
    AttendanceSerializer,
    AttendanceWriteSerializer,
    MarksheetDetailSerializer,
)
from .filters import SubjectResultFilter, ExamSubjectFilter, StudentResultSummaryFilter, MarksheetDetailFilter
from .permissions import IsAdminOrTeacher


def _update_result_summary(student, exam):
    results = SubjectResult.objects.filter(
        student=student,
        exam_subject__exam=exam,
    )

    if not results.exists():
        StudentResultSummary.objects.filter(student=student, exam=exam).delete()
        return

    aggregates = results.aggregate(
        theory=Sum('marks_obtained_theory'),
        practical=Sum('marks_obtained_practical'),
        avg_gpa=Avg('subject_grade_point'),
    )
    total_marks = (aggregates['theory'] or 0) + (aggregates['practical'] or 0)
    avg_gpa = aggregates['avg_gpa'] or 0
    has_ng = results.filter(subject_grade='NG').exists()

    StudentResultSummary.objects.update_or_create(
        student=student,
        exam=exam,
        defaults={
            'academic_year': student.academic_year,
            'total_marks': total_marks,
            'gpa': 0 if has_ng else avg_gpa,
            'overall_grade': 'NG' if has_ng else 'PASS',
        },
    )


class ExamViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    queryset = Exam.objects.select_related('academic_year')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ExamWriteSerializer
        return ExamSerializer


class AttendanceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    queryset = Attendance.objects.select_related(
        'student',
        'standard',
        'subject__standard',
        'recorded_by',
        'academic_year',
    )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AttendanceWriteSerializer
        return AttendanceSerializer


class ExamSubjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = ExamSubjectFilter
    queryset = ExamSubject.objects.select_related(
        'exam',
        'exam__academic_year',
        'subject',
        'subject__standard',
        'standard',
    )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ExamSubjectWriteSerializer
        return ExamSubjectSerializer


class SubjectResultViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = SubjectResultFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubjectResultWriteSerializer
        return SubjectResultSerializer

    def get_queryset(self):
        return SubjectResult.objects.select_related(
            'exam_subject__exam__academic_year',
            'exam_subject__subject__standard',
            'exam_subject__standard',
            'student__student',
            'student__standard',
            'student__academic_year',
        )

    def perform_create(self, serializer):
        result = serializer.save()
        _update_result_summary(result.student, result.exam_subject.exam)

    def perform_update(self, serializer):
        result = serializer.save()
        _update_result_summary(result.student, result.exam_subject.exam)

    def perform_destroy(self, instance):
        student = instance.student
        exam = instance.exam_subject.exam
        instance.delete()
        _update_result_summary(student, exam)


class StudentResultSummaryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = StudentResultSummaryFilter
    queryset = StudentResultSummary.objects.select_related(
        'student__student',
        'student__standard',
        'student__academic_year',
        'exam__academic_year',
        'academic_year',
    )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudentResultSummaryWriteSerializer
        return StudentResultSummarySerializer

    def perform_create(self, serializer):
        summary = serializer.save(academic_year=serializer.validated_data['student'].academic_year)
        _update_result_summary(summary.student, summary.exam)

    def perform_update(self, serializer):
        student = serializer.validated_data.get('student', serializer.instance.student)
        summary = serializer.save(academic_year=student.academic_year)
        _update_result_summary(summary.student, summary.exam)


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