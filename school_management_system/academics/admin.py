from django.contrib import admin
from .models import (
    Subject, Standard, AcademicYear, StudentEnrollment, ClassTeacher, TeacherSubject,
    Room, TimeSlot, ClassTimetable, TeacherAvailability, HolidayCalendar
)




@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ('get_display_name', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'section')
    
    @admin.display(description='Standard', ordering='name')
    def get_display_name(self, obj):
        return obj.display_name()
    
@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('get_display_name', 'status', 'year_start_date', 'year_end_date', 'is_current')
    list_filter = ('status', 'is_current')
    search_fields = ('name',)
    
    @admin.display(description='Academic Year', ordering='name')
    def get_display_name(self, obj):
        return obj.display_name()


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'get_standard', 'credit_hours', 'curriculum_version')
    list_filter = ('standard', 'curriculum_version')
    search_fields = ('name', 'code')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('standard')
    
    @admin.display(description='Standard', ordering='standard__name')
    def get_standard(self, obj):
        return obj.standard.display_name()

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_standard', 'roll_number', 'get_academic_year', 'status')
    list_filter = ('standard', 'academic_year', 'status')
    search_fields = ('student__first_name', 'student__last_name', 'roll_number')
    
    list_select_related = ('student', 'standard', 'academic_year')
    
    @admin.display(description='Student', ordering='student__first_name')
    def get_student_name(self, obj):
        return obj.student.full_name()
    
    @admin.display(description='Standard', ordering='standard__name')
    def get_standard(self, obj):
        return obj.standard.display_name()
    
    @admin.display(description='Academic Year', ordering='academic_year__name')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()

@admin.register(ClassTeacher)
class ClassTeacherAdmin(admin.ModelAdmin):
    list_display = ('get_academic_year', 'get_standard', 'get_teacher')
    list_filter = ('academic_year', 'standard')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'standard__name')
    
    list_select_related = ('academic_year', 'standard', 'teacher')
    @admin.display(description='Academic Year', ordering='academic_year__name')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()
    
    @admin.display(description='Standard', ordering='standard__name')
    def get_standard(self, obj):
        return obj.standard.display_name()
    
    @admin.display(description='Teacher', ordering='teacher__first_name')
    def get_teacher(self, obj):
        return obj.teacher.full_name()

@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('get_subject', 'get_teacher', 'get_academic_year')
    list_filter = ('academic_year', 'subject__standard')
    search_fields = ('subject__name', 'teacher__first_name', 'teacher__last_name')
    
    list_select_related = ('subject', 'subject__standard', 'teacher', 'academic_year')
    
    @admin.display(description='Subject', ordering='subject__name')
    def get_subject(self, obj):
        return obj.subject.display_name()
    
    @admin.display(description='Teacher', ordering='teacher__first_name')
    def get_teacher(self, obj):
        return obj.teacher.full_name()
    
    @admin.display(description='Academic Year', ordering='academic_year__name')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()


# --- TIMETABLE AND SCHEDULE ADMIN ---

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('get_display_name', 'room_type', 'capacity', 'status')
    list_filter = ('room_type', 'status')
    search_fields = ('room_number', 'room_name', 'location')
    
    @admin.display(description='Room', ordering='room_number')
    def get_display_name(self, obj):
        return obj.display_name()


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('get_display_name', 'get_academic_year', 'start_time', 'end_time', 'is_break')
    list_filter = ('academic_year', 'is_break', 'is_active')
    search_fields = ('period_name',)
    ordering = ('academic_year', 'period_number')
    
    list_select_related = ('academic_year',)
    
    @admin.display(description='Time Slot', ordering='period_number')
    def get_display_name(self, obj):
        return obj.display_name()
    
    @admin.display(description='Academic Year', ordering='academic_year__name')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()


@admin.register(ClassTimetable)
class ClassTimetableAdmin(admin.ModelAdmin):
    list_display = ('get_standard', 'get_day', 'get_time_slot', 'get_subject', 'get_teacher', 'get_room')
    list_filter = ('academic_year', 'standard', 'day', 'subject__standard')
    search_fields = ('standard__name', 'subject__name', 'teacher__first_name', 'teacher__last_name')
    ordering = ('standard', 'day', 'time_slot__period_number')
    
    list_select_related = ('standard', 'time_slot', 'subject', 'teacher', 'room', 'academic_year')
    
    @admin.display(description='Standard', ordering='standard__name')
    def get_standard(self, obj):
        return obj.standard.display_name()
    
    @admin.display(description='Day', ordering='day')
    def get_day(self, obj):
        return obj.get_day_display()
    
    @admin.display(description='Time Slot', ordering='time_slot__period_number')
    def get_time_slot(self, obj):
        return obj.time_slot.display_name()
    
    @admin.display(description='Subject', ordering='subject__name')
    def get_subject(self, obj):
        return obj.subject.name if obj.subject else "---"
    
    @admin.display(description='Teacher', ordering='teacher__first_name')
    def get_teacher(self, obj):
        return obj.teacher.full_name() if obj.teacher else "---"
    
    @admin.display(description='Room', ordering='room__room_number')
    def get_room(self, obj):
        return obj.room.display_name() if obj.room else "---"


@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('get_teacher', 'get_academic_year', 'get_day', 'get_time_slot', 'is_available', 'reason')
    list_filter = ('academic_year', 'day', 'is_available')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'reason')
    ordering = ('academic_year', 'teacher', 'day', 'time_slot__period_number')
    
    list_select_related = ('teacher', 'academic_year', 'time_slot')
    
    @admin.display(description='Teacher', ordering='teacher__first_name')
    def get_teacher(self, obj):
        return obj.teacher.full_name()
    
    @admin.display(description='Academic Year', ordering='academic_year__name')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()
    
    @admin.display(description='Day', ordering='day')
    def get_day(self, obj):
        return obj.get_day_display()
    
    @admin.display(description='Time Slot', ordering='time_slot__period_number')
    def get_time_slot(self, obj):
        return obj.time_slot.display_name()


@admin.register(HolidayCalendar)
class HolidayCalendarAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_academic_year', 'holiday_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('academic_year', 'holiday_type', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('academic_year', 'start_date')
    
    list_select_related = ('academic_year',)
    
    @admin.display(description='Academic Year', ordering='academic_year__name')
    def get_academic_year(self, obj):
        return obj.academic_year.display_name()