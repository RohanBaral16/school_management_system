from django.contrib import admin
from .models import Student, Teacher
from academics.models import StudentEnrollment # Import this to use as an Inline

class StudentEnrollmentInline(admin.TabularInline):
    model = StudentEnrollment
    extra = 0

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ( 'first_name', 'last_name', 'admission_number')
    search_fields = ('first_name', 'last_name', 'admission_number')
    inlines = [StudentEnrollmentInline]

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'designation', 'status')