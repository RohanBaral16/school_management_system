from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ResultViewSet

router = DefaultRouter()

router.register(r'results', ResultViewSet, basename='results')

urlpatterns = [
    path('', include(router.urls))
]
