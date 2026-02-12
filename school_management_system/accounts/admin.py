from django.contrib import admin
from django.db.models import F, Value
from django.db.models.functions import Concat
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
    list_display = ('student_full_name', 'admission_number')
    search_fields = ('first_name', 'last_name', 'admission_number')
    inlines = [StudentEnrollmentInline]
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Annotate full name to avoid computing it per-row in Python
        return queryset.only('id', 'first_name', 'last_name', 'admission_number').annotate(
            full_name_display=Concat(
                F('first_name'),
                Value(' '),
                F('last_name'),
            )
        )
    
    @admin.display(description='Name')
    def student_full_name(self, obj):
        # Use annotated value when present, fall back to full_name property
        return getattr(obj, 'full_name_display', obj.full_name)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_full_name', 'designation', 'status')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('status',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        qs = queryset.select_related('user')  # Get User data in single query
        # Annotate full name to avoid computing it per-row in Python
        return qs.only('id', 'first_name', 'last_name', 'designation', 'status', 'email').annotate(
            full_name_display=Concat(
                F('first_name'),
                Value(' '),
                F('last_name'),
            )
        )
    
    @admin.display(description='Name')
    def teacher_full_name(self, obj):
        # Use annotated value when present, fall back to full_name property
        return getattr(obj, 'full_name_display', obj.full_name)