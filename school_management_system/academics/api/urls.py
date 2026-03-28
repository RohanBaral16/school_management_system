"""
URL configuration for Academics API.
Exports viewsets for main router in urls.py
"""

from .views import (
    AcademicYearViewSet,
    AcademicYearReadOnlyViewSet,
    StandardViewSet,
    StandardReadOnlyViewSet,
    SubjectViewSet,
    SubjectReadOnlyViewSet,
    StudentEnrollmentViewSet,
    StudentEnrollmentReadOnlyViewSet,
    ClassTeacherViewSet,
    ClassTeacherReadOnlyViewSet,
    TeacherSubjectViewSet,
    TeacherSubjectReadOnlyViewSet,
)

# Export viewsets for main router
api_viewsets = [
    ('academic-years', AcademicYearViewSet, 'academic-years'),
    ('standards', StandardViewSet, 'standards'),
    ('subjects', SubjectViewSet, 'subjects'),
    ('student-enrollments', StudentEnrollmentViewSet, 'student-enrollments'),
    ('class-teachers', ClassTeacherViewSet, 'class-teachers'),
    ('teacher-subjects', TeacherSubjectViewSet, 'teacher-subjects'),
    ('academic-years-readonly', AcademicYearReadOnlyViewSet, 'academic-years-readonly'),
    ('standards-readonly', StandardReadOnlyViewSet, 'standards-readonly'),
    ('subjects-readonly', SubjectReadOnlyViewSet, 'subjects-readonly'),
    ('student-enrollments-readonly', StudentEnrollmentReadOnlyViewSet, 'student-enrollments-readonly'),
    ('class-teachers-readonly', ClassTeacherReadOnlyViewSet, 'class-teachers-readonly'),
    ('teacher-subjects-readonly', TeacherSubjectReadOnlyViewSet, 'teacher-subjects-readonly'),
]

urlpatterns = []
