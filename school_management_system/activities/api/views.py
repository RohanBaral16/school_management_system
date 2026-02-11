from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import Result, ExamSubject
from .serializers import ResultSerializer, ExamSubjectSerializer
# Create your views here.


class ResultViewSet(ModelViewSet):
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
        
class ExamSubjectViewSet(ModelViewSet):
    serializer_class = ExamSubjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs =  ExamSubject.objects.all().select_related(
            'exam',
            'subject',
            'standard'
        )
        exam = self.request.query_params.get('exam')
        standard = self.request.query_params.get('standard')
        subject = self.request.query_params.get('subject')
        if exam:
            qs = qs.filter(exam = exam)
        if standard:
            qs = qs.filter(standard = standard)
        if subject:
            qs = qs.filter(subject = subject)
        return qs