from django.db import models
from django.core.exceptions import ValidationError
from nepali_datetime_field.models import NepaliDateField
import nepali_datetime

# --- ATTENDANCE ---
class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('leave', 'On Leave'),
    ]
    
    date = NepaliDateField(default=nepali_datetime.date.today)
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    standard = models.ForeignKey('academics.Standard', on_delete=models.CASCADE)
    # subject is optional for schools doing once-a-day attendance
    subject = models.ForeignKey('academics.Subject', on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='present')
    recorded_by = models.ForeignKey('accounts.Teacher', on_delete=models.SET_NULL, null=True)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.PROTECT)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('date', 'student', 'subject', 'standard')
        verbose_name_plural = "Attendance"

    def __str__(self):
        return f"{self.student} - {self.date} ({self.status})"

# --- EXAMS ---
class Exam(models.Model):
    TERM_CHOICES = [
        ('first_term', 'First Term'),
        ('second_term', 'Second Term'),
        ('third_term', 'Third Term'),
        ('final_term', 'Final Term'),
        ('unit_test', 'Unit Test'),
    ]
    
    name = models.CharField(max_length=100, help_text="e.g. First Terminal Examination 2081")
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.PROTECT)
    start_date = NepaliDateField()
    end_date = NepaliDateField()
    is_published = models.BooleanField(default=False, help_text="Set to true to show results to students/parents")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_subjects')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE)
    standard = models.ForeignKey('academics.Standard', on_delete=models.CASCADE)
    
    exam_date = NepaliDateField()
    
    # Theory Marks
    full_marks_theory = models.DecimalField(max_digits=5, decimal_places=2, default=75.0)
    pass_marks_theory = models.DecimalField(max_digits=5, decimal_places=2, default=27.0)
    
    # Practical Marks
    full_marks_practical = models.DecimalField(max_digits=5, decimal_places=2, default=25.0)
    pass_marks_practical = models.DecimalField(max_digits=5, decimal_places=2, default=9.0)

    class Meta:
        unique_together = ('exam', 'subject', 'standard')

    def __str__(self):
        return f"{self.exam.name} - {self.subject.name} ({self.standard})"

# --- RESULTS ---
class Result(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    marks_obtained_theory = models.DecimalField(max_digits=5, decimal_places=2)
    marks_obtained_practical = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Auto-calculated fields
    subject_grade_point = models.DecimalField(max_digits=3, decimal_places=2, editable=False)
    subject_grade = models.CharField(max_length=5, editable=False)

    def save(self, *args, **kwargs):
        # 1. Calculate Total Percentage for this subject
        theory_fm = self.exam_subject.full_marks_theory
        practical_fm = self.exam_subject.full_marks_practical
        total_fm = theory_fm + practical_fm
        obtained = self.marks_obtained_theory + self.marks_obtained_practical
        
        percentage = (obtained / total_fm) * 100

        # 2. Nepal CDC Grading Logic
        theory_perc = (self.marks_obtained_theory / theory_fm) * 100
        
        if theory_perc < 35:
            self.subject_grade = 'NG' 
            self.subject_grade_point = 0.00
        elif percentage >= 90:
            self.subject_grade, self.subject_grade_point = 'A+', 4.0
        elif percentage >= 80:
            self.subject_grade, self.subject_grade_point = 'A', 3.6
        elif percentage >= 70:
            self.subject_grade, self.subject_grade_point = 'B+', 3.2
        elif percentage >= 60:
            self.subject_grade, self.subject_grade_point = 'B', 2.8
        elif percentage >= 50:
            self.subject_grade, self.subject_grade_point = 'C+', 2.4
        elif percentage >= 40:
            self.subject_grade, self.subject_grade_point = 'C', 2.0
        elif percentage >= 35:
            self.subject_grade, self.subject_grade_point = 'D', 1.6
        else:
            self.subject_grade, self.subject_grade_point = 'NG', 0.0
            
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('student', 'exam_subject')

# --- MISSING MODEL (This solves your ImportError) ---
class ResultSummary(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.PROTECT)
    
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    overall_grade = models.CharField(max_length=5, blank=True)
    rank = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'exam')
        verbose_name_plural = "Result Summaries"

    def __str__(self):
        return f"{self.student} - {self.exam.name}"