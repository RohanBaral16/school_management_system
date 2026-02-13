from rest_framework import serializers
from ..models import Student, Teacher

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        read_only = True
    )
    class Meta:
        model = Student
        fields = [
            'id',
            'full_name',
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'email',
            'phone',
            'date_of_birth',
            'date_of_birth_bs',
            'admission_number'
        ]
        
class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        read_only = True
    )
    class Meta:
        model = Teacher
        fields = [
            'id',
            'user',
            'full_name',
            'first_name',
            'last_name',
            'gender',
            'designation',
            'email',
            'status',
            'phone',
            'date_of_birth'
        ]