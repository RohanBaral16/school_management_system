from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    SubjectResultReadOnlyViewSet,
    ExamSubjectReadOnlyViewSet,
    StudentResultSummaryReadOnlyViewSet,
    ExamReadOnlyViewSet,
    AttendanceReadOnlyViewSet,
    MarksheetDetailReadOnlyViewSet,
)

router = DefaultRouter()

router.register(r'subjectresults-readonly', SubjectResultReadOnlyViewSet, basename='subjectresults-readonly')
router.register(r'examsubject-readonly', ExamSubjectReadOnlyViewSet, basename='examsubject-readonly')
router.register(r'resultsummary-readonly', StudentResultSummaryReadOnlyViewSet, basename='resultsummary-readonly')
router.register(r'exam-readonly', ExamReadOnlyViewSet, basename='exam-readonly')
router.register(r'attendance-readonly', AttendanceReadOnlyViewSet, basename='attendance-readonly')
router.register(r'marksheet-readonly', MarksheetDetailReadOnlyViewSet, basename='marksheet-readonly')

urlpatterns = [
    path('', include(router.urls))
]
