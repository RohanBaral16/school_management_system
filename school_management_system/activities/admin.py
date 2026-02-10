from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.db.models import Sum, Avg

from .models import (
    Attendance,
    Exam,
    ExamSubject,
    Result,
    ResultSummary,
)

from academics.models import StudentEnrollment, Standard


# ============================================================
# EXAM SUBJECT INLINE (inside Exam)
# ============================================================

class ExamSubjectInline(admin.TabularInline):
    model = ExamSubject
    fields = (
        'subject',
        'exam_date',
        'full_marks_theory',
        'pass_marks_theory',
        'full_marks_practical',
        'pass_marks_practical',
    )
    autocomplete_fields = ['subject']
    extra = 0

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('subject')
        )


# ============================================================
# RESULT INLINE (inside ExamSubject)
# ============================================================

class ResultFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            return

        enrolled_qs = StudentEnrollment.objects.filter(
            standard=self.instance.standard,
            academic_year=self.instance.exam.academic_year,
            status='enrolled',
        )

        enrolled_ids = list(enrolled_qs.values_list('id', flat=True))
        existing_ids = set(self.queryset.values_list('student_id', flat=True))

        missing_ids = [sid for sid in enrolled_ids if sid not in existing_ids]

        self.initial = [{'student': sid} for sid in missing_ids]
        self.extra = len(self.initial)

        self.form.base_fields['student'].queryset = enrolled_qs


class ResultInline(admin.TabularInline):
    model = Result
    formset = ResultFormSet
    fields = (
        'get_roll_no',
        'student',
        'marks_obtained_theory',
        'marks_obtained_practical',
        'subject_grade',
        
        
    )
    readonly_fields = ('subject_grade', 'get_roll_no', )
    autocomplete_fields = [('student')]
    extra = 0

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                'student',
                'student__student',
                'student__standard',
                'exam_subject',
                'exam_subject__subject',
            )
        )
        
    @admin.display(description="Roll No")
    def get_roll_no(self, obj):
        # obj is a Result instance
        return obj.student.roll_number  # or obj.student.roll_no depending on your field name


# ============================================================
# RESULT SUMMARY INLINE (through table)
# ============================================================

class ResultSummaryResultInline(admin.TabularInline):
    model = ResultSummary.results.through
    extra = 0
    can_delete = False
    verbose_name = 'Subject Result'
    verbose_name_plural = 'Subject Results'

    fields = (
        'subject_name',
        'marks_obtained_theory',
        'marks_obtained_practical',
        'subject_grade',
        'subject_grade_point',
    )

    readonly_fields = fields

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                'result__exam_subject__subject'
            )
        )

    @admin.display(description='Subject')
    def subject_name(self, obj):
        return obj.result.exam_subject.subject.name

    @admin.display(description='Theory')
    def marks_obtained_theory(self, obj):
        return obj.result.marks_obtained_theory

    @admin.display(description='Practical')
    def marks_obtained_practical(self, obj):
        return obj.result.marks_obtained_practical

    @admin.display(description='Grade')
    def subject_grade(self, obj):
        return obj.result.subject_grade

    @admin.display(description='GP')
    def subject_grade_point(self, obj):
        return obj.result.subject_grade_point


# ============================================================
# ADMIN ACTIONS
# ============================================================

@admin.action(description='Process All Results & Ranks for this Exam')
def process_exam_full_results(modeladmin, request, queryset):
    for exam in queryset:
        standards = (
            ExamSubject.objects
            .filter(exam=exam)
            .values_list('subject__standard', flat=True)
            .distinct()
        )

        total_processed = 0

        for standard_id in standards:
            standard = Standard.objects.only('id').get(id=standard_id)

            enrollments = StudentEnrollment.objects.filter(
                standard=standard,
                academic_year=exam.academic_year,
                status='enrolled',
            )

            for enrollment in enrollments:
                results = Result.objects.filter(
                    student=enrollment,
                    exam_subject__exam=exam,
                )

                if not results.exists():
                    continue

                aggregates = results.aggregate(
                    theory=Sum('marks_obtained_theory'),
                    practical=Sum('marks_obtained_practical'),
                    avg_gpa=Avg('subject_grade_point'),
                )

                total_marks = (aggregates['theory'] or 0) + (aggregates['practical'] or 0)
                avg_gpa = aggregates['avg_gpa'] or 0
                has_ng = results.filter(subject_grade='NG').exists()

                summary, _ = ResultSummary.objects.update_or_create(
                    student=enrollment,
                    exam=exam,
                    defaults={
                        'academic_year': enrollment.academic_year,
                        'total_marks': total_marks,
                        'gpa': 0 if has_ng else avg_gpa,
                        'overall_grade': 'NG' if has_ng else 'PASS',
                    },
                )

                summary.results.set(results)
                total_processed += 1

            summaries = (
                ResultSummary.objects
                .filter(
                    exam=exam,
                    student__standard=standard,
                    student__academic_year=exam.academic_year,
                )
                .order_by('-gpa', '-total_marks')
            )

            for idx, summary in enumerate(summaries, start=1):
                summary.rank = idx
                summary.save(update_fields=['rank'])

        modeladmin.message_user(
            request,
            f"Successfully processed {total_processed} result summaries for {exam.name}."
        )


@admin.action(description='Generate Ranks by Class and Exam')
def calculate_exam_ranks(modeladmin, request, queryset):
    groups = queryset.values_list('exam', 'student__standard').distinct()

    updated = 0
    for exam, standard in groups:
        summaries = (
            ResultSummary.objects
            .filter(exam=exam, student__standard=standard)
            .order_by('-gpa', '-total_marks')
        )

        for idx, summary in enumerate(summaries, start=1):
            summary.rank = idx
            summary.save(update_fields=['rank'])
            updated += 1

    modeladmin.message_user(
        request,
        f"Successfully recalculated ranks for {updated} records."
    )


# ============================================================
# ADMIN REGISTRATIONS
# ============================================================

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'academic_year', 'is_published')
    list_select_related = ('academic_year',)
    inlines = [ExamSubjectInline]
    actions = [process_exam_full_results]

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions


@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'exam_date')
    list_select_related = ('exam', 'subject', 'standard')
    list_filter = ['exam', 'subject', 'standard']
    inlines = [ResultInline]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'get_subject_name',
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

    list_filter = ('exam_subject__exam', 'exam_subject__standard',  'exam_subject__subject', )
    search_fields = (
        'student__student__first_name',
        'student__student__last_name',
    )

    list_select_related = (
        'student',
        'student__student',
        'student__standard',
        'exam_subject',
        'exam_subject__subject',
    )

    @admin.display(description='Total Marks Obtained')
    def total_marks_obtained(self, obj):
        return obj.marks_obtained_theory + obj.marks_obtained_practical

    @admin.display(description='Pass', boolean=True)
    def is_pass(self, obj):
        return obj.subject_grade != 'NG'

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions
    @admin.display(description="Subject")
    def get_subject_name(self, obj):
        # obj is a Result instance
        return obj.exam_subject.subject.name  # or obj.student.roll_no depending on your field name


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'status', 'standard')
    date_hierarchy = 'date'


@admin.register(ResultSummary)
class ResultSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'exam',
        'student_standard',
        'academic_year',
        'total_marks',
        'gpa',
        'overall_grade',
        'rank',
        'subject_results_display',
    )

    list_filter = (
        'academic_year',
        'exam',
        'student__standard',
        'overall_grade',
    )

    search_fields = (
        'student__student__first_name',
        'student__student__last_name',
        'student__roll_number',
    )

    list_select_related = (
        'student',
        'student__student',
        'student__standard',
        'exam',
        'academic_year',
    )

    inlines = [ResultSummaryResultInline]
    actions = [calculate_exam_ranks]

    readonly_fields = (
        'total_marks',
        'percentage',
        'gpa',
        'overall_grade',
        'rank',
        'subject_results_display',
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                'student',
                'student__student',
                'student__standard',
                'exam',
                'academic_year',
            )
            .prefetch_related(
                'results__exam_subject__subject'
            )
        )

    @admin.display(description='Class')
    def student_standard(self, obj):
        return obj.student.standard

    @admin.display(description='Subject Results')
    def subject_results_display(self, obj):
        results = obj.results.all()
        if not results:
            return "-"
        return ", ".join(
            f"{r.exam_subject.subject.name}: {r.subject_grade}"
            for r in results
        )
