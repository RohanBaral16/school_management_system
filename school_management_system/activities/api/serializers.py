from rest_framework import serializers
from ..models import Result, ExamSubject

class ResultSerializer(serializers.ModelSerializer):
    student_full_name = serializers.CharField(
        source = "student.student.full_name",
        read_only = True
    )
    subject_name = serializers.CharField(
        source = "exam_subject.subject.name",
        read_only = True
    )
    student_roll_number = serializers.CharField(
        source = "student.roll_number",
        read_only = True
    )
    
    class Meta:
        model = Result
        fields = [
            "id",
            "student",
            "student_full_name",
            "exam_subject",
            "subject_name",
            "marks_obtained_theory",
            "marks_obtained_practical",
            "student_roll_number"
        ]
        read_only_fields = [
            "subject_grade",
            "subject_grade_point"
        ]
        
class ExamSubjectSerializer(serializers.ModelSerializer):
    # Custom fields for nested info
    subject_name = serializers.CharField(
        source='subject.name',
        read_only=True
    )
    standard_name = serializers.CharField(
        source='standard.name',
        read_only=True
    )

    class Meta:
        model = ExamSubject
        # Include all model fields + custom fields
        fields = list([f.name for f in model._meta.fields]) + ['subject_name', 'standard_name']