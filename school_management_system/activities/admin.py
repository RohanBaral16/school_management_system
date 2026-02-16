from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.db.models import Sum, Avg
from django.utils.safestring import mark_safe

from .models import (
    Attendance,
    Exam,
    ExamSubject,
    SubjectResult,
    StudentResultSummary,
    StudentMarksheet,
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
# SUBJECT RESULT INLINE (inside ExamSubject)
# ============================================================

class SubjectResultFormSet(BaseInlineFormSet):
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


class SubjectResultInline(admin.TabularInline):
    model = SubjectResult
    formset = SubjectResultFormSet
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
        # obj is a SubjectResult instance
        return obj.student.roll_number  # or obj.student.roll_no depending on your field name


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
                results = SubjectResult.objects.filter(
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

                # Update or create summary - no longer need to set M2M relationship
                StudentResultSummary.objects.update_or_create(
                    student=enrollment,
                    exam=exam,
                    defaults={
                        'academic_year': enrollment.academic_year,
                        'total_marks': total_marks,
                        'gpa': 0 if has_ng else avg_gpa,
                        'overall_grade': 'NG' if has_ng else 'PASS',
                    },
                )
                total_processed += 1

            summaries = (
                StudentResultSummary.objects
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
            StudentResultSummary.objects
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
    list_display = ('name', 'term', 'get_academic_year', 'is_published', 'start_date', 'end_date')
    list_filter = ('term', 'academic_year', 'is_published')
    search_fields = ('name',)
    list_select_related = ('academic_year',)
    inlines = [ExamSubjectInline]
    actions = [process_exam_full_results]

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions
    
    @admin.display(description='Academic Year', ordering='academic_year__name')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()


@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ('get_exam', 'get_subject', 'get_standard', 'exam_date', 'full_marks_theory', 'full_marks_practical')
    list_filter = ('exam', 'standard', 'subject')
    search_fields = ('exam__name', 'subject__name')
    list_select_related = ('exam', 'exam__academic_year', 'subject', 'subject__standard', 'standard')
    inlines = [SubjectResultInline]
    
    @admin.display(description='Exam', ordering='exam__name')
    def get_exam(self, obj):
        return obj.exam.display_name()
    
    @admin.display(description='Subject', ordering='subject__name')
    def get_subject(self, obj):
        if obj.subject:
            return obj.subject.display_name()
        return "-"
    
    @admin.display(description='Standard', ordering='standard__name')
    def get_standard(self, obj):
        if obj.standard:
            return obj.standard.display_name()
        return "-"


@admin.register(SubjectResult)
class SubjectResultAdmin(admin.ModelAdmin):
    list_display = (
        'get_student_info',
        'get_subject_name',
        'get_exam',
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

    list_filter = ('exam_subject__exam', 'exam_subject__standard',  'exam_subject__subject', 'subject_grade')
    search_fields = (
        'student__student__first_name',
        'student__student__last_name',
        'student__roll_number',
    )

    list_select_related = (
        'student',
        'student__student',
        'student__standard',
        'student__academic_year',
        'exam_subject',
        'exam_subject__exam',
        'exam_subject__exam__academic_year',
        'exam_subject__subject',
        'exam_subject__subject__standard',
        'exam_subject__standard',
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
    
    @admin.display(description='Student (Roll No)', ordering='student__student__first_name')
    def get_student_info(self, obj):
        return f"{obj.student.student.full_name()} ({obj.student.roll_number})"
    
    @admin.display(description='Subject')
    def get_subject_name(self, obj):
        if obj.exam_subject and obj.exam_subject.subject:
            return obj.exam_subject.subject.name
        return "-"
    
    @admin.display(description='Exam', ordering='exam_subject__exam__name')
    def get_exam(self, obj):
        return obj.exam_subject.exam.name


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'get_student_name', 'status', 'get_standard', 'get_subject', 'get_recorded_by')
    list_filter = ('status', 'standard', 'academic_year', 'date')
    search_fields = ('student__first_name', 'student__last_name')
    date_hierarchy = 'date'
    
    list_select_related = (
        'student',
        'standard',
        'subject',
        'subject__standard',
        'recorded_by',
        'academic_year',
    )
    
    @admin.display(description='Student', ordering='student__first_name')
    def get_student_name(self, obj):
        return obj.student.full_name()
    
    @admin.display(description='Standard', ordering='standard__name')
    def get_standard(self, obj):
        return obj.standard.display_name()
    
    @admin.display(description='Subject')
    def get_subject(self, obj):
        if obj.subject:
            return obj.subject.name
        return "General"
    
    @admin.display(description='Recorded By')
    def get_recorded_by(self, obj):
        if obj.recorded_by:
            return obj.recorded_by.full_name()
        return "-"


@admin.register(StudentResultSummary)
class StudentResultSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_student_name',
        'get_roll_number',
        'get_exam',
        'get_student_standard',
        'get_academic_year',
        'total_marks',
        'gpa',
        'overall_grade',
        'rank',
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
        'exam__academic_year',
        'academic_year',
    )

    readonly_fields = (
        'id',
        'get_student_name',
        'get_roll_number',
        'get_exam',
        'get_academic_year',
        'total_marks',
        'percentage',
        'gpa',
        'overall_grade',
        'rank',
        'subject_results_display',
    )
    
    fields = (
        'id',
        'student',
        'get_student_name',
        'get_roll_number',
        'exam',
        'get_exam',
        'academic_year',
        'get_academic_year',
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
                'exam__academic_year',
                'academic_year',
            )
        )

    @admin.display(description='Student', ordering='student__student__first_name')
    def get_student_name(self, obj):
        return obj.student.student.full_name()
    
    @admin.display(description='Roll No', ordering='student__roll_number')
    def get_roll_number(self, obj):
        return obj.student.roll_number
    
    @admin.display(description='Exam', ordering='exam__name')
    def get_exam(self, obj):
        return obj.exam.name
    
    @admin.display(description='Class', ordering='student__standard__name')
    def get_student_standard(self, obj):
        return obj.student.standard.display_name()
    
    @admin.display(description='Academic Year', ordering='academic_year__name')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()

    @admin.display(description='Subject Results')
    def subject_results_display(self, obj):
        # Fetch results dynamically instead of using M2M
        results = SubjectResult.objects.filter(
            student=obj.student,
            exam_subject__exam=obj.exam
        ).select_related('exam_subject__subject')
        
        if not results:
            return "-"
        return ", ".join(
            f"{r.exam_subject.subject.name}: {r.subject_grade}"
            for r in results
        )


# ============================================================
# STUDENT MARKSHEET VIEW (Individual Marksheet Panel)
# ============================================================

from django.utils.html import format_html

@admin.register(StudentMarksheet)
class StudentMarksheetAdmin(admin.ModelAdmin):
    """
    Admin panel to view individual student marksheets.
    This provides a detailed view of each student's performance across different exams.
    """
    list_display = (
        'get_student_name',
        'roll_number',
        'get_standard',
        'get_academic_year',
        'status',
    )
    
    list_filter = (
        'academic_year',
        'standard',
        'status',
    )
    
    search_fields = (
        'student__first_name',
        'student__last_name',
        'roll_number',
        'student__admission_number',
    )
    
    list_select_related = (
        'student',
        'standard',
        'academic_year',
    )
    
    fieldsets = (
        ('Student Information', {
            'fields': (
                'get_student_name',
                'get_admission_number',
                'get_gender',
                'get_email',
            )
        }),
        ('Enrollment Details', {
            'fields': (
                'get_standard',
                'roll_number',
                'get_academic_year',
                'status',
            )
        }),
        ('Performance Summary', {
            'fields': (
                'get_exam_summaries',
            ),
            'classes': ('wide',),
        }),
        ('Subject-wise Results', {
            'fields': (
                'get_all_subject_results',
            ),
            'classes': ('wide',),
        }),
    )
    
    readonly_fields = (
        'get_student_name',
        'get_admission_number',
        'get_gender',
        'get_email',
        'get_standard',
        'get_academic_year',
        'get_exam_summaries',
        'get_all_subject_results',
        'roll_number',
        'status',
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    @admin.display(description='Student Name')
    def get_student_name(self, obj):
        return obj.student.full_name()
    
    @admin.display(description='Admission Number')
    def get_admission_number(self, obj):
        return obj.student.admission_number
    
    @admin.display(description='Gender')
    def get_gender(self, obj):
        return obj.student.get_gender_display()
    
    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.student.email or "N/A"
    
    @admin.display(description='Standard')
    def get_standard(self, obj):
        return obj.standard.display_name()
    
    @admin.display(description='Academic Year')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()
    
    @admin.display(description='Exam Performance Summary')
    def get_exam_summaries(self, obj):
        """Display summary of all exams for this student"""
        summaries = StudentResultSummary.objects.filter(
            student=obj
        ).select_related('exam').order_by('-exam__start_date')
        
        if not summaries:
            return mark_safe("<p>No exam results available</p>")
        
        html = "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr style='background-color: #f2f2f2;'>"
        html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Exam</th>"
        html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Total Marks</th>"
        html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>GPA</th>"
        html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Grade</th>"
        html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Rank</th>"
        html += "</tr>"
        
        for summary in summaries:
            html += "<tr>"
            html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{summary.exam.name}</td>"
            html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{summary.total_marks}</td>"
            html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{summary.gpa}</td>"
            html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{summary.overall_grade}</td>"
            html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{summary.rank or 'N/A'}</td>"
            html += "</tr>"
        
        html += "</table>"
        return mark_safe(html)
    
    @admin.display(description='Detailed Subject-wise Results')
    def get_all_subject_results(self, obj):
        """Display detailed subject-wise results for all exams"""
        # Get all exams for this academic year
        exams = Exam.objects.filter(
            academic_year=obj.academic_year
        ).select_related('academic_year').order_by('-start_date')
        
        if not exams:
            return mark_safe("<p>No exams found for this academic year</p>")
        
        html = ""
        for exam in exams:
            # Get subject results for this student and exam
            results = SubjectResult.objects.filter(
                student=obj,
                exam_subject__exam=exam
            ).select_related(
                'exam_subject',
                'exam_subject__subject',
                'exam_subject__exam'
            ).order_by('exam_subject__subject__name')
            
            if not results.exists():
                continue
            
            html += f"<h3 style='margin-top: 20px;'>{exam.name}</h3>"
            html += "<table style='width:100%; border-collapse: collapse;'>"
            html += "<tr style='background-color: #f2f2f2;'>"
            html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Subject</th>"
            html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: center;'>Theory (Obtained/Full)</th>"
            html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: center;'>Practical (Obtained/Full)</th>"
            html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: center;'>Total</th>"
            html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: center;'>Grade</th>"
            html += "<th style='border: 1px solid #ddd; padding: 8px; text-align: center;'>GPA</th>"
            html += "</tr>"
            
            for result in results:
                subject_name = result.exam_subject.subject.name if result.exam_subject.subject else "N/A"
                theory_marks = f"{result.marks_obtained_theory}/{result.exam_subject.full_marks_theory}"
                practical_marks = f"{result.marks_obtained_practical}/{result.exam_subject.full_marks_practical}"
                total_obtained = result.marks_obtained_theory + result.marks_obtained_practical
                total_full = result.exam_subject.full_marks_theory + result.exam_subject.full_marks_practical
                total_marks = f"{total_obtained}/{total_full}"
                
                # Color code based on grade
                grade_color = "#4CAF50" if result.subject_grade != "NG" else "#f44336"
                
                html += "<tr>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{subject_name}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{theory_marks}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{practical_marks}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'><strong>{total_marks}</strong></td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center; color: {grade_color}; font-weight: bold;'>{result.subject_grade}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{result.subject_grade_point}</td>"
                html += "</tr>"
            
            html += "</table>"
        
        if not html:
            return mark_safe("<p>No subject results available</p>")
        
        return mark_safe(html)
