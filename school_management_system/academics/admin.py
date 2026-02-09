from django.contrib import admin
from .models import Subject, Standard, AcademicYear, StudentEnrollment

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')

@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'credit_hours')

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'standard', 'academic_year', 'status')
    list_filter = ('standard', 'academic_year')