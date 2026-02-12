from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from ..models import SubjectResult, ExamSubject
from .serializers import SubjectResultSerializer, ExamSubjectSerializer
from django.db.models import Q
# Create your views here.


class SubjectResultReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = SubjectResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = SubjectResult.objects.select_related(
            'exam_subject__exam',
            'student',
            'student__student',
            'student__standard',
            'exam_subject',
            'exam_subject__subject',
            'exam_subject__exam',
        )

        # ID-based filters
        student_id = self.request.query_params.get("student")
        exam_id = self.request.query_params.get("exam")
        subject_id = self.request.query_params.get("subject")
        standard_id = self.request.query_params.get("standard")

        # Name-based filters
        student_name = self.request.query_params.get("student_name")
        subject_name = self.request.query_params.get("subject_name")

        if student_id:
            qs = qs.filter(student_id=student_id)

        if exam_id:
            qs = qs.filter(exam_subject__exam_id=exam_id)

        if subject_id:
            qs = qs.filter(exam_subject__subject_id=subject_id)

        if standard_id:
            qs = qs.filter(student__standard_id=standard_id)

        # Partial name search (case insensitive)
        if student_name:
            qs = qs.filter(
                Q(student__student__first_name__icontains=student_name) | Q(student__student__last_name__icontains=student_name)
    )

        if subject_name:
            qs = qs.filter(
                exam_subject__subject__name__icontains=subject_name
            )

        return qs
        
        
class ExamSubjectReadOnlyViewSet(ReadOnlyModelViewSet):
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