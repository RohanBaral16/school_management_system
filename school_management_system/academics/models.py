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

    def __str__(self):
        return self.display_name()

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

    def __str__(self):
        return self.display_name()

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
    
    def __str__(self):
        return self.display_name()

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
    
    def __str__(self):
        return self.display_name()

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
    
    def __str__(self):
        return self.display_name()

    def display_name(self):
        """Display method for teacher subject"""
        return f"{self.subject.display_name()} - {self.teacher.full_name()}"


# --- TIMETABLE AND SCHEDULE MANAGEMENT ---

class Room(models.Model):
    """Represents classrooms or rooms in the school"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    room_number = models.CharField(max_length=20, unique=True, help_text="e.g. 101, A1, Lab-1")
    room_name = models.CharField(max_length=100, help_text="e.g. Class IX-A, Biology Lab")
    room_type = models.CharField(
        max_length=20,
        choices=[
            ('classroom', 'Classroom'),
            ('lab', 'Laboratory'),
            ('library', 'Library'),
            ('office', 'Office'),
            ('other', 'Other'),
        ],
        default='classroom'
    )
    capacity = models.PositiveIntegerField(help_text="Maximum students the room can accommodate")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=100, blank=True, help_text="e.g. Building A, First Floor")
    remarks = models.TextField(blank=True, help_text="Special features or notes about the room")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['room_number']
        verbose_name = 'Room / Classroom'

    def __str__(self):
        return self.display_name()

    def display_name(self):
        """Display method for room"""
        return f"{self.room_number} - {self.room_name}"


class TimeSlot(models.Model):
    """Represents daily time periods/periods in school"""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    period_number = models.PositiveIntegerField(help_text="e.g., 1, 2, 3...")
    period_name = models.CharField(max_length=50, blank=True, help_text="e.g., Period 1, Assembly, Recess")
    start_time = models.TimeField(help_text="e.g., 09:00")
    end_time = models.TimeField(help_text="e.g., 09:45")
    duration_minutes = models.PositiveIntegerField(help_text="Duration in minutes")
    is_break = models.BooleanField(default=False, help_text="Mark if this is a break/recess period")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['academic_year', 'period_number']
        unique_together = ('academic_year', 'period_number')
        verbose_name = 'Time Slot / Period'

    def __str__(self):
        return self.display_name()

    def display_name(self):
        """Display method for time slot"""
        return f"{self.period_name or f'Period {self.period_number}'} ({self.start_time} - {self.end_time})"


class ClassTimetable(models.Model):
    """Represents the complete weekly timetable for a class"""
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='class_timetables')
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='timetables')
    day = models.CharField(max_length=10, choices=DAY_CHOICES, help_text="Day of the week")
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, null=True, blank=True)
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional info
    is_optional = models.BooleanField(default=False, help_text="Mark if attendance is optional")
    remarks = models.TextField(blank=True, help_text="e.g., Project work, Guest lecture")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['standard', 'day', 'time_slot']
        unique_together = ('academic_year', 'standard', 'day', 'time_slot')
        verbose_name = 'Class Timetable'
        verbose_name_plural = 'Class Timetables'

    def __str__(self):
        return self.display_name()

    def display_name(self):
        """Display method for class timetable"""
        subject_name = self.subject.name if self.subject else "Break/Assembly"
        teacher_name = self.teacher.full_name() if self.teacher else "N/A"
        return f"{self.standard.display_name()} - {self.get_day_display()} - {self.time_slot.display_name()} - {subject_name}"


class TeacherAvailability(models.Model):
    """Tracks teacher availability and free periods"""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='teacher_availability')
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE)
    day = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ]
    )
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    is_available = models.BooleanField(default=True, help_text="True if teacher is available, False if busy/leave")
    reason = models.CharField(max_length=100, blank=True, help_text="e.g., Staff Meeting, Training, Leave")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['teacher', 'day', 'time_slot']
        unique_together = ('academic_year', 'teacher', 'day', 'time_slot')
        verbose_name = 'Teacher Availability'
        verbose_name_plural = 'Teacher Availability'

    def __str__(self):
        availability_status = "Available" if self.is_available else "Busy/On Leave"
        return f"{self.teacher.full_name()} - {self.get_day_display()} - {availability_status}"


class HolidayCalendar(models.Model):
    """School holidays and vacation periods"""
    HOLIDAY_TYPE_CHOICES = [
        ('national_holiday', 'National Holiday'),
        ('school_holiday', 'School Holiday'),
        ('vacation', 'Vacation / Break'),
        ('exam_week', 'Exam Week'),
        ('other', 'Other'),
    ]
    
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='holidays')
    title = models.CharField(max_length=100, help_text="e.g., Dashain, Christmas, Mid-Term Break")
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPE_CHOICES, default='school_holiday')
    start_date = NepaliDateField()
    end_date = NepaliDateField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['academic_year', 'start_date']
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holiday Calendar'

    def __str__(self):
        return self.display_name()

    def display_name(self):
        """Display method for holiday"""
        return f"{self.title} ({self.start_date} - {self.end_date})"

    def is_holiday_today(self):
        """Check if today is a holiday"""
        from django.utils import timezone
        today = nepali_datetime.date.today()
        return self.start_date <= today <= self.end_date and self.is_active
