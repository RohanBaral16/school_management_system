from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import Student, Teacher
from .serializers import StudentSerializer, TeacherSerializer
from django.db.models import Q
from .filters import StudentFilter


class StudentReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentFilter

class TeacherReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    