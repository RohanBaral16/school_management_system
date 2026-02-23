"""
URL configuration for Accounts API.
Exports viewsets for main router in urls.py
"""

from .views import (
    StudentViewSet,
    StudentReadOnlyViewSet,
    TeacherViewSet,
    TeacherReadOnlyViewSet,
)

# Export viewsets for main router
api_viewsets = [
    ('students', StudentViewSet, 'students'),
    ('teachers', TeacherViewSet, 'teachers'),
    ('students-readonly', StudentReadOnlyViewSet, 'students-readonly'),
    ('teachers-readonly', TeacherReadOnlyViewSet, 'teachers-readonly'),
]

urlpatterns = []