from django.contrib import admin
from django.db.models import F, Value
from django.db.models.functions import Concat
from .models import Subject, Standard, AcademicYear, StudentEnrollment, ClassTeacher, TeacherSubject




@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')
    
@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'standard', 'credit_hours')
    search_fields = ['name']
    list_filter = ('standard__name',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('standard')

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'standard', 'roll_number',  'academic_year', 'status')
    list_filter = ('standard', 'academic_year', 'status')
    
    list_select_related = ('student', 'standard', 'academic_year')
    search_fields = ('student__first_name', 'student__last_name', 'standard__name')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        qs = queryset.select_related('student', 'standard', 'academic_year')
        # Annotate student full name to avoid calling __str__ for each row
        return qs.annotate(
            student_full_name=Concat(
                F('student__first_name'),
                Value(' '),
                F('student__last_name'),
            )
        )
    
    @admin.display(description='Student')
    def student_name(self, obj):
        # Use annotated value when present, fall back to object property
        return getattr(obj, 'student_full_name', obj.student.full_name)

@admin.register(ClassTeacher)
class ClassTeacherAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'standard', 'teacher_name')
    list_select_related = ('academic_year', 'standard', 'teacher')
    list_filter = ('academic_year', 'standard')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        qs = queryset.select_related('academic_year', 'standard', 'teacher')
        # Annotate teacher full name to avoid calling __str__ for each row
        return qs.annotate(
            teacher_full_name=Concat(
                F('teacher__first_name'),
                Value(' '),
                F('teacher__last_name'),
            )
        )
    
    @admin.display(description='Teacher')
    def teacher_name(self, obj):
        # Use annotated value when present, fall back to object property
        return getattr(obj, 'teacher_full_name', obj.teacher.full_name)

@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher_name', 'academic_year')
    list_select_related = ('subject', 'teacher', 'academic_year')
    list_filter = ('academic_year', 'subject__standard')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        qs = queryset.select_related('subject', 'subject__standard', 'teacher', 'academic_year')
        # Annotate teacher full name to avoid calling __str__ for each row
        return qs.annotate(
            teacher_full_name=Concat(
                F('teacher__first_name'),
                Value(' '),
                F('teacher__last_name'),
            )
        )
    
    @admin.display(description='Teacher')
    def teacher_name(self, obj):
        # Use annotated value when present, fall back to object property
        return getattr(obj, 'teacher_full_name', obj.teacher.full_name)
    