from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
	AcademicYearReadOnlyViewSet,
	StandardReadOnlyViewSet,
	SubjectReadOnlyViewSet,
	StudentEnrollmentReadOnlyViewSet,
	ClassTeacherReadOnlyViewSet,
	TeacherSubjectReadOnlyViewSet,
)

router = DefaultRouter()

router.register(r'academic-years-readonly', AcademicYearReadOnlyViewSet, basename='academic-years-readonly')
router.register(r'standards-readonly', StandardReadOnlyViewSet, basename='standards-readonly')
router.register(r'subjects-readonly', SubjectReadOnlyViewSet, basename='subjects-readonly')
router.register(r'student-enrollments-readonly', StudentEnrollmentReadOnlyViewSet, basename='student-enrollments-readonly')
router.register(r'class-teachers-readonly', ClassTeacherReadOnlyViewSet, basename='class-teachers-readonly')
router.register(r'teacher-subjects-readonly', TeacherSubjectReadOnlyViewSet, basename='teacher-subjects-readonly')

urlpatterns = [
	path('', include(router.urls)),
]
