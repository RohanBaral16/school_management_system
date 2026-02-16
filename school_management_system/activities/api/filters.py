import django_filters
from django.db.models import Q

from ..models import SubjectResult, ExamSubject, StudentResultSummary


class SubjectResultFilter(django_filters.FilterSet):
    student_full_name = django_filters.CharFilter(method='filter_student_full_name')
    student_id = django_filters.NumberFilter(field_name='student_id')
    exam_id = django_filters.NumberFilter(field_name='exam_subject__exam_id')
    subject_id = django_filters.NumberFilter(field_name='exam_subject__subject_id')
    standard_id = django_filters.NumberFilter(field_name='student__standard_id')
    subject_grade = django_filters.CharFilter(field_name='subject_grade', lookup_expr='exact')

    def filter_student_full_name(self, queryset, name, value):
        parts = value.strip().split()
        q = Q()
        for part in parts:
            q &= (
                Q(student__student__first_name__icontains=part)
                | Q(student__student__middle_name__icontains=part)
                | Q(student__student__last_name__icontains=part)
            )
        return queryset.filter(q)

    class Meta:
        model = SubjectResult
        fields = ['id', 'student_id', 'exam_id', 'subject_id', 'standard_id', 'subject_grade']


class ExamSubjectFilter(django_filters.FilterSet):
    exam_id = django_filters.NumberFilter(field_name='exam_id')
    standard_id = django_filters.NumberFilter(field_name='standard_id')
    subject_id = django_filters.NumberFilter(field_name='subject_id')

    class Meta:
        model = ExamSubject
        fields = ['id', 'exam_id', 'standard_id', 'subject_id']


class StudentResultSummaryFilter(django_filters.FilterSet):
    student_full_name = django_filters.CharFilter(method='filter_student_full_name')
    student_id = django_filters.NumberFilter(field_name='student_id')
    exam_id = django_filters.NumberFilter(field_name='exam_id')
    academic_year_id = django_filters.NumberFilter(field_name='academic_year_id')
    standard_id = django_filters.NumberFilter(field_name='student__standard_id')
    overall_grade = django_filters.CharFilter(field_name='overall_grade', lookup_expr='exact')

    def filter_student_full_name(self, queryset, name, value):
        parts = value.strip().split()
        q = Q()
        for part in parts:
            q &= (
                Q(student__student__first_name__icontains=part)
                | Q(student__student__middle_name__icontains=part)
                | Q(student__student__last_name__icontains=part)
            )
        return queryset.filter(q)

    class Meta:
        model = StudentResultSummary
        fields = ['id', 'student_id', 'exam_id', 'academic_year_id', 'standard_id', 'overall_grade']

class MarksheetDetailFilter(django_filters.FilterSet):
    """
    Filter for marksheet details - replaces StudentMarksheetFilter.
    Filters SubjectResult directly instead of the removed StudentMarksheet through table.
    """
    resultsummary_id = django_filters.NumberFilter(method='filter_resultsummary_id')
    result_id = django_filters.NumberFilter(field_name='id')
    student_id = django_filters.NumberFilter(field_name='student_id')
    exam_id = django_filters.NumberFilter(field_name='exam_subject__exam_id')
    student_full_name = django_filters.CharFilter(method='filter_student_full_name')

    def filter_resultsummary_id(self, queryset, name, value):
        """Filter by result summary ID by finding matching student and exam."""
        try:
            summary = StudentResultSummary.objects.get(id=value)
            return queryset.filter(
                student=summary.student,
                exam_subject__exam=summary.exam
            )
        except StudentResultSummary.DoesNotExist:
            return queryset.none()

    def filter_student_full_name(self, queryset, name, value):
        parts = value.strip().split()
        q = Q()
        for part in parts:
            q &= (
                Q(student__student__first_name__icontains=part)
                | Q(student__student__middle_name__icontains=part)
                | Q(student__student__last_name__icontains=part)
            )
        return queryset.filter(q)

    class Meta:
        model = SubjectResult
        fields = ['id', 'resultsummary_id', 'result_id', 'student_id', 'exam_id']