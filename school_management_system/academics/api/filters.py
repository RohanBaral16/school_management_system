import django_filters
from django.db.models import Q

from ..models import (
	AcademicYear,
	ClassTeacher,
	Standard,
	StudentEnrollment,
	Subject,
	TeacherSubject,
)


class AcademicYearFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
	status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
	is_current = django_filters.BooleanFilter(field_name='is_current')

	class Meta:
		model = AcademicYear
		fields = ['id', 'name', 'status', 'is_current']


class StandardFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
	section = django_filters.CharFilter(field_name='section', lookup_expr='icontains')
	status = django_filters.CharFilter(field_name='status', lookup_expr='exact')

	class Meta:
		model = Standard
		fields = ['id', 'name', 'section', 'status']


class SubjectFilter(django_filters.FilterSet):
	name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
	code = django_filters.CharFilter(field_name='code', lookup_expr='icontains')
	standard_id = django_filters.NumberFilter(field_name='standard_id')

	class Meta:
		model = Subject
		fields = ['id', 'name', 'code', 'standard_id']


class StudentEnrollmentFilter(django_filters.FilterSet):
	student_full_name = django_filters.CharFilter(method='filter_student_full_name')
	roll_number = django_filters.CharFilter(field_name='roll_number', lookup_expr='icontains')
	status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
	standard_id = django_filters.NumberFilter(field_name='standard_id')
	academic_year_id = django_filters.NumberFilter(field_name='academic_year_id')

	def filter_student_full_name(self, queryset, name, value):
		parts = value.strip().split()
		q = Q()
		for part in parts:
			q &= (
				Q(student__first_name__icontains=part)
				| Q(student__middle_name__icontains=part)
				| Q(student__last_name__icontains=part)
			)
		return queryset.filter(q)

	class Meta:
		model = StudentEnrollment
		fields = ['id', 'roll_number', 'status', 'standard_id', 'academic_year_id']


class ClassTeacherFilter(django_filters.FilterSet):
	teacher_full_name = django_filters.CharFilter(method='filter_teacher_full_name')
	standard_id = django_filters.NumberFilter(field_name='standard_id')
	academic_year_id = django_filters.NumberFilter(field_name='academic_year_id')

	def filter_teacher_full_name(self, queryset, name, value):
		parts = value.strip().split()
		q = Q()
		for part in parts:
			q &= (
				Q(teacher__first_name__icontains=part)
				| Q(teacher__middle_name__icontains=part)
				| Q(teacher__last_name__icontains=part)
			)
		return queryset.filter(q)

	class Meta:
		model = ClassTeacher
		fields = ['id', 'standard_id', 'academic_year_id']


class TeacherSubjectFilter(django_filters.FilterSet):
	teacher_full_name = django_filters.CharFilter(method='filter_teacher_full_name')
	subject_id = django_filters.NumberFilter(field_name='subject_id')
	academic_year_id = django_filters.NumberFilter(field_name='academic_year_id')

	def filter_teacher_full_name(self, queryset, name, value):
		parts = value.strip().split()
		q = Q()
		for part in parts:
			q &= (
				Q(teacher__first_name__icontains=part)
				| Q(teacher__middle_name__icontains=part)
				| Q(teacher__last_name__icontains=part)
			)
		return queryset.filter(q)

	class Meta:
		model = TeacherSubject
		fields = ['id', 'subject_id', 'academic_year_id']
