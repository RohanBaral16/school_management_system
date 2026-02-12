from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SubjectResultReadOnlyViewSet, ExamSubjectReadOnlyViewSet
router = DefaultRouter()

router.register(r'results-readonly', SubjectResultReadOnlyViewSet , basename='results-readonly')
router.register(r'examsubject-readonly', ExamSubjectReadOnlyViewSet, basename='examsubject-readonly')

urlpatterns = [
    path('', include(router.urls))
]
