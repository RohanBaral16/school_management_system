from django.contrib import admin
from .models import Attendance, Exam, ExamSubject, Result, ResultSummary
from django.forms.models import BaseInlineFormSet
from academics.models import StudentEnrollment

class ExamSubjectInline(admin.TabularInline):
    model = ExamSubject
    fields = ['subject', 'exam_date', 'full_marks_theory', 'pass_marks_theory', 'full_marks_practical', 'pass_marks_practical']
    extra = 1
    

class ResultFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Check if we are editing an existing ExamSubject
            # 1. Get all enrolled student IDs for this standard
            enrolled_qs = StudentEnrollment.objects.filter(
                standard=self.instance.standard,
                academic_year=self.instance.exam.academic_year,
                status='enrolled'
            )
            enrolled_ids = enrolled_qs.values_list('id', flat=True)

            # 2. See who already has a result record
            existing_ids = self.queryset.values_list('student_id', flat=True)

            # 3. Create a list of students who need a row
            missing_ids = [s_id for s_id in enrolled_ids if s_id not in existing_ids]

            # 4. Force Django to provide "Initial" data for the extra rows
            self.initial = [{'student': s_id} for s_id in missing_ids]
            self.extra = len(self.initial)

            # Limit the student dropdown to enrolled students only
            self.form.base_fields['student'].queryset = enrolled_qs

class ResultInline(admin.TabularInline):
    model = Result
    formset = ResultFormSet # Use the custom logic above
    fields = ['student', 'marks_obtained_theory', 'marks_obtained_practical', 'subject_grade']
    readonly_fields = ['subject_grade']
    extra = 0

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'academic_year', 'is_published')
    inlines = [ExamSubjectInline]

@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'exam_date')
    inlines = [ResultInline]

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'exam_subject',
        'total_marks_obtained',
        'subject_grade',
        'subject_grade_point',
        'is_pass',
    )
    readonly_fields = (
        'total_marks_obtained',
        'subject_grade',
        'subject_grade_point',
        'is_pass',
    )
    list_filter = ('exam_subject__exam',)
    search_fields = ('student__first_name', 'student__last_name')

    @admin.display(description='Total Marks Obtained')
    def total_marks_obtained(self, obj):
        return obj.marks_obtained_theory + obj.marks_obtained_practical

    @admin.display(description='Pass', boolean=True)
    def is_pass(self, obj):
        return obj.subject_grade != 'NG'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'status', 'standard')
    date_hierarchy = 'date'