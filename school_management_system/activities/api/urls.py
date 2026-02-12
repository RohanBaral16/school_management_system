from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ResultReadOnlyViewSet, ExamSubjectReadOnlyViewSet
router = DefaultRouter()

router.register(r'results-readonly', ResultReadOnlyViewSet , basename='results-readonly')
router.register(r'examsubject-readonly', ExamSubjectReadOnlyViewSet, basename='examsubject-readonly')

urlpatterns = [
    path('', include(router.urls))
]
