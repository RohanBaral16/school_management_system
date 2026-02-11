from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import Result
from .serializers import ResultSerializer
# Create your views here.


class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Result.objects.all().select_related(
        'student',                # FK → StudentEnrollment
        'student__student',       # FK → Student
        'student__standard',      # FK → Standard
        'exam_subject',           # FK → ExamSubject
        'exam_subject__subject',  # FK → Subject
        'exam_subject__subject__standard',  # FK → Standard via Subject
        'exam_subject__exam',     # FK → Exam
    )