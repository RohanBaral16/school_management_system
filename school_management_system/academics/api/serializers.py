from rest_framework import serializers
from accounts.api.serializers import StudentSerializer, TeacherSerializer

from accounts.models import Student, Teacher
from ..models import (
    AcademicYear,
    ClassTeacher,
    Standard,
    StudentEnrollment,
    Subject,
    TeacherSubject,
)


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'


class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    standard = StandardSerializer(read_only=True)
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=Standard.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Subject
        fields = '__all__'



class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=Student.objects.all(),
        write_only=True,
    )
    standard = StandardSerializer(read_only=True)
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=Standard.objects.all(),
        write_only=True,
    )
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYear.objects.all(),
        write_only=True,
    )

    class Meta:
        model = StudentEnrollment
        fields = '__all__'


class ClassTeacherSerializer(serializers.ModelSerializer):
    standard = StandardSerializer(read_only=True)
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=Standard.objects.all(),
        write_only=True,
    )
    teacher = TeacherSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        source='teacher',
        queryset=Teacher.objects.all(),
        write_only=True,
    )
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYear.objects.all(),
        write_only=True,
    )

    class Meta:
        model = ClassTeacher
        fields = '__all__'


class TeacherSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject',
        queryset=Subject.objects.all(),
        write_only=True,
    )
    teacher = TeacherSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        source='teacher',
        queryset=Teacher.objects.all(),
        write_only=True,
    )
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYear.objects.all(),
        write_only=True,
    )

    class Meta:
        model = TeacherSubject
        fields = '__all__'
        
