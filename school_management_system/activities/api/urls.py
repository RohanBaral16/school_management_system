from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ResultViewSet, ExamSubjectViewSet

router = DefaultRouter()

router.register(r'results', ResultViewSet, basename='results')
router.register(r'examsubject', ExamSubjectViewSet, basename='examsubject')

urlpatterns = [
    path('', include(router.urls))
]
