from django.db import models
from nepali_datetime_field.models import NepaliDateField
import nepali_datetime

# --- ACADEMIC YEAR ---
class AcademicYear(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived')
    ]
    name = models.CharField(max_length=20, help_text="e.g. 2081")
    year_start_date = NepaliDateField(default=nepali_datetime.date.today)
    year_end_date = NepaliDateField(default=nepali_datetime.date.today)
    is_current = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-name']
        verbose_name = "Academic Year"

    # def __str__(self):
    #     return self.name
    
    def display_name(self):
        """Display method for academic year"""
        status_icon = "✓" if self.is_current else ""
        return f"{self.name} {status_icon}".strip()
    
# --- standard ---
class Standard(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("archived", "Archived")
    ]
    name = models.CharField(max_length=20)
    section = models.CharField(max_length=2, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'section']
        unique_together = ('name', 'section')
        verbose_name = 'Class / Standard'

    # def __str__(self):
    #     return f"{self.name} - {self.section}" if self.section else self.name
    
    def display_name(self):
        """Display method for standard"""
        return f"{self.name} - {self.section}" if self.section else self.name

# --- SUBJECT ---
class Subject(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    # Decimal 3,1 allows for values like 2.5 or 4.0
    standard = models.ForeignKey(Standard, on_delete=models.PROTECT)
    credit_hours = models.DecimalField(decimal_places=1, max_digits=3)
    curriculum_version = models.CharField(max_length=10, default="2077/2078")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     # Now it shows: "Mathematics (Class 10)"
    #     return f"{self.name} ({self.standard.name} {self.curriculum_version})"
    
    def display_name(self):
        """Display method for subject"""
        return f"{self.name} ({self.standard.display_name()})"
    



# --- ENROLLMENT ---
class StudentEnrollment(models.Model):
    ENROLLMENT_STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('dropped_out', 'Dropped Out'),
        ('transferred', 'Transferred'),
        ('promoted', 'Promoted'),
        ('failed', 'Failed'),
        ('graduated', 'Graduated'),
        ('withdrawn', 'Withdrawn'),
    ]
    student = models.ForeignKey('accounts.Student', on_delete=models.PROTECT)
    standard = models.ForeignKey(Standard, on_delete=models.PROTECT)
    roll_number = models.CharField(max_length=20)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default='enrolled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevent double enrollment in the same year
        unique_together = [('student', 'academic_year'),('standard', 'academic_year', 'roll_number'), ]   
        ordering = ['-academic_year', 'standard']
    
    # def __str__(self):
    #     return f"{self.student}-{self.standard}-{self.roll_number}"
    
    def display_name(self):
        """Display method for student enrollment"""
        return f"{self.student.full_name()} - {self.standard.display_name()} - Roll {self.roll_number}"

#Class teacher assignment
class ClassTeacher(models.Model):
    standard = models.ForeignKey(Standard, on_delete=models.PROTECT)
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.PROTECT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('teacher', 'standard', 'academic_year')
        ordering = ['-academic_year', 'standard']
    
    def display_name(self):
        """Display method for class teacher"""
        return f"{self.teacher.full_name()} - {self.standard.display_name()}"


#one subject may have two techers, so correctly modeled this too
class TeacherSubject(models.Model):
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Subject Teacher'
    
    # def __str__(self):
    #     return f"{self.subject} ->> {self.teacher}"
    
    def display_name(self):
        """Display method for teacher subject"""
        return f"{self.subject.display_name()} - {self.teacher.full_name()}"