from django.contrib import admin
from .models import Student, Teacher
from academics.models import StudentEnrollment # Import this to use as an Inline



class StudentEnrollmentInline(admin.TabularInline):
    model = StudentEnrollment
    extra = 0
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optimize inline queryset with select_related
        return qs.select_related('standard', 'academic_year')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'admission_number', 'gender', 'email')
    search_fields = ('first_name', 'last_name', 'admission_number', 'email')
    list_filter = ('gender',)
    inlines = [StudentEnrollmentInline]
    
    @admin.display(description='Full Name', ordering='first_name')
    def get_full_name(self, obj):
        return obj.full_name()

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'designation', 'status', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('status', 'designation')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    @admin.display(description='Full Name', ordering='first_name')
    def get_full_name(self, obj):
        return obj.full_name()
