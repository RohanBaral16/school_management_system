from django.contrib import admin
from .models import Subject, Standard, AcademicYear, StudentEnrollment, ClassTeacher

@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')
    
@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'standard', 'credit_hours')

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'standard', 'academic_year', 'status')
    list_filter = ('standard', 'academic_year')
    
    list_select_related = ('student', 'standard', 'academic_year')
    search_fields = ('student__first_name', 'student__last_name', 'standard__name')
    
    
@admin.register(ClassTeacher)
class ClassTeacherAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'standard', 'teacher')
    list_select_related = ('academic_year', 'standard', 'teacher')
    