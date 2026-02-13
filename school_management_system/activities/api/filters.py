import django_filters
from django.db.models import Q

from ..models import SubjectResult, ExamSubject, StudentResultSummary, StudentMarksheet


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

class StudentMarksheetFilter(django_filters.FilterSet):
    resultsummary_id = django_filters.NumberFilter(field_name='resultsummary_id')
    result_id = django_filters.NumberFilter(field_name='result_id')
    student_id = django_filters.NumberFilter(field_name='resultsummary__student_id')
    exam_id = django_filters.NumberFilter(field_name='resultsummary__exam_id')
    student_full_name = django_filters.CharFilter(method='filter_student_full_name')

    def filter_student_full_name(self, queryset, name, value):
        parts = value.strip().split()
        q = Q()
        for part in parts:
            q &= (
                Q(resultsummary__student__student__first_name__icontains=part)
                | Q(resultsummary__student__student__middle_name__icontains=part)
                | Q(resultsummary__student__student__last_name__icontains=part)
            )
        return queryset.filter(q)

    class Meta:
        model = StudentMarksheet
        fields = ['id', 'resultsummary_id', 'result_id', 'student_id', 'exam_id']