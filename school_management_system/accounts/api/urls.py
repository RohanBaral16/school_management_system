from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import StudentReadOnlyViewSet, TeacherReadOnlyViewSet
router = DefaultRouter()

router.register(r'students-readonly', StudentReadOnlyViewSet , basename='students-readonly')
router.register(r'teachers-readonly', TeacherReadOnlyViewSet, basename='teachers-readonly')

urlpatterns = [
    path('', include(router.urls))
]