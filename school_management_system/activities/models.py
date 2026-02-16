from django.db import models
from django.core.exceptions import ValidationError
from nepali_datetime_field.models import NepaliDateField
import nepali_datetime


# Import StudentEnrollment for proxy model
from academics.models import StudentEnrollment


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

    # def __str__(self):
    #     return f"{self.student} - {self.date} ({self.status})"
    
    def display_name(self):
        """Display method for attendance"""
        return f"{self.student.full_name()} - {self.date} ({self.status})"

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

    # def __str__(self):
    #     return f"{self.name} ({self.academic_year})"
    # def __str__(self):
    #     return self.name
    
    def display_name(self):
        """Display method for exam"""
        return f"{self.name} ({self.academic_year.display_name()})"


class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_subjects')
    subject = models.ForeignKey('academics.Subject', on_delete=models.SET_NULL, blank=True, null=True)
    
    exam_date = NepaliDateField()
    
    # Theory Marks
    full_marks_theory = models.DecimalField(max_digits=5, decimal_places=2, default=75.0)
    pass_marks_theory = models.DecimalField(max_digits=5, decimal_places=2, default=27.0)
    
    # Practical Marks
    full_marks_practical = models.DecimalField(max_digits=5, decimal_places=2, default=25.0)
    pass_marks_practical = models.DecimalField(max_digits=5, decimal_places=2, default=9.0)
    
    standard = models.ForeignKey('academics.Standard', on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-assign the standard from the subject before saving
        if self.subject:
            self.standard = self.subject.standard
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('exam', 'subject')
        verbose_name_plural = 'Exam Subjects -> Fill Result Per Subject'

    # def __str__(self):
    #     return f"{self.exam.name} - {self.exam.academic_year} - {self.subject.standard} - {self.subject.name}"
    # def __str__(self):
    #     return f"ExamSubject #{self.pk}"
    
    def display_name(self):
        """Display method for exam subject"""
        if self.subject:
            return f"{self.exam.display_name()} - {self.subject.display_name()}"
        return f"{self.exam.display_name()} - ExamSubject #{self.pk}"
    

# --- RESULTS ---


class SubjectResult(models.Model):
    student = models.ForeignKey('academics.StudentEnrollment', on_delete=models.CASCADE)
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    marks_obtained_theory = models.DecimalField(max_digits=5, decimal_places=2)
    marks_obtained_practical = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Auto-calculated fields
    subject_grade_point = models.DecimalField(max_digits=3, decimal_places=2, editable=False)
    subject_grade = models.CharField(max_length=5, editable=False)

    class Meta:
        unique_together = ('student', 'exam_subject')
        verbose_name_plural = 'Student -> Subject Marks'

    def clean(self):
        """Ensure obtained marks do not exceed full marks."""
        super().clean()
        if self.student and self.student.status != 'enrolled':
            raise ValidationError({
                'student': "Result can only be recorded for enrolled students."
            })
        if self.exam_subject:
            if self.marks_obtained_theory > self.exam_subject.full_marks_theory:
                raise ValidationError({
                    'marks_obtained_theory': f"Theory marks cannot exceed {self.exam_subject.full_marks_theory}."
                })
            if self.marks_obtained_practical > self.exam_subject.full_marks_practical:
                raise ValidationError({
                    'marks_obtained_practical': f"Practical marks cannot exceed {self.exam_subject.full_marks_practical}."
                })

    def calculate_grading(self):
        """Logic to calculate Grade and GPA based on Nepal CDC standard."""
        theory_fm = self.exam_subject.full_marks_theory
        practical_fm = self.exam_subject.full_marks_practical
        total_fm = theory_fm + practical_fm
        
        obtained_total = self.marks_obtained_theory + self.marks_obtained_practical
        
        # Avoid division by zero
        if total_fm <= 0:
            return 'NG', 0.0

        # Calculate percentages
        total_percentage = (obtained_total / total_fm) * 100
        
        # Individual component check (NG if Theory < 35% or Practical < 35%)
        # Note: Nepal CDC typically requires min 35% in theory AND practical separately to pass.
        theory_pass_perc = (self.marks_obtained_theory / theory_fm * 100) if theory_fm > 0 else 100
        practical_pass_perc = (self.marks_obtained_practical / practical_fm * 100) if practical_fm > 0 else 100

        if theory_pass_perc < 35 or practical_pass_perc < 35:
            return 'NG', 0.00
        
        # Grading Scale based on total percentage
        if total_percentage >= 90: return 'A+', 4.0
        if total_percentage >= 80: return 'A', 3.6
        if total_percentage >= 70: return 'B+', 3.2
        if total_percentage >= 60: return 'B', 2.8
        if total_percentage >= 50: return 'C+', 2.4
        if total_percentage >= 40: return 'C', 2.0
        if total_percentage >= 35: return 'D', 1.6
        return 'NG', 0.0

    def save(self, *args, **kwargs):
        # Force validation before saving
        self.full_clean()
        
        # Perform grading calculation
        self.subject_grade, self.subject_grade_point = self.calculate_grading()
        
        super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.student} - {self.exam_subject.subject.name}: {self.subject_grade}"
    # def __str__(self):
    #     return f"SubjectResult #{self.pk}"
    
    def display_name(self):
        """Display method for subject result"""
        return f"{self.student.display_name()} - {self.exam_subject.display_name()}: {self.subject_grade}"
    


class StudentResultSummary(models.Model):
    student = models.ForeignKey('academics.StudentEnrollment', on_delete=models.CASCADE)
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

    # def __str__(self):
    #     return f"{self.student} - {self.exam.name}"
    
    def display_name(self):
        """Display method for student result summary"""
        return f"{self.student.display_name()} - {self.exam.display_name()}"
    
    def get_subject_results(self):
        """
        Dynamically fetch subject results for this student and exam.
        This replaces the old M2M relationship.
        """
        return SubjectResult.objects.filter(
            student=self.student,
            exam_subject__exam=self.exam
        )


# ============================================================
# PROXY MODEL FOR STUDENT MARKSHEET VIEW
# ============================================================

class StudentMarksheet(StudentEnrollment):
    """
    Proxy model for viewing individual student marksheets in admin.
    This allows us to have a separate admin interface focused on marksheet viewing
    without duplicating the StudentEnrollment model.
    """
    class Meta:
        proxy = True
        verbose_name = "Student Marksheet"
        verbose_name_plural = "Student Marksheets"