"""
Serializers for Academics app.
Implements separate read and write serializers for better separation of concerns.
"""

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


# ============================================================================
# ACADEMIC YEAR SERIALIZERS
# ============================================================================

class AcademicYearSerializer(serializers.ModelSerializer):
    """Read-only serializer for AcademicYear."""
    
    display_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AcademicYear
        fields = [
            'id',
            'name',
            'display_name',
            'year_start_date',
            'year_end_date',
            'is_current',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display_name(self, obj):
        """Get display name from model method."""
        return obj.display_name()


class AcademicYearWriteSerializer(serializers.ModelSerializer):
    """Write serializer for AcademicYear."""
    
    class Meta:
        model = AcademicYear
        fields = [
            'id',
            'name',
            'year_start_date',
            'year_end_date',
            'is_current',
            'status',
        ]
        read_only_fields = ['id']
    
    def validate_name(self, value):
        """Validate academic year name format."""
        if not value or not value.isdigit():
            raise serializers.ValidationError("Academic year name must be a numeric value (e.g., 2081).")
        return value


# ============================================================================
# STANDARD SERIALIZERS
# ============================================================================

class StandardSerializer(serializers.ModelSerializer):
    """Read-only serializer for Standard."""
    
    display_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Standard
        fields = [
            'id',
            'name',
            'section',
            'display_name',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display_name(self, obj):
        """Get display name from model method."""
        return obj.display_name()


class StandardWriteSerializer(serializers.ModelSerializer):
    """Write serializer for Standard."""
    
    class Meta:
        model = Standard
        fields = [
            'id',
            'name',
            'section',
            'status',
        ]
        read_only_fields = ['id']
    
    def validate_unique_together(self, data):
        """Validate unique_together constraint for name + section."""
        name = data.get('name')
        section = data.get('section')
        
        queryset = Standard.objects.filter(name=name, section=section)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError("A standard with this name and section already exists.")
        
        return data


# ============================================================================
# SUBJECT SERIALIZERS
# ============================================================================

class SubjectSerializer(serializers.ModelSerializer):
    """Read-only serializer for Subject with nested fields."""
    
    standard = StandardSerializer(read_only=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'code',
            'standard',
            'display_name',
            'credit_hours',
            'curriculum_version',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display_name(self, obj):
        """Get display name from model method."""
        return obj.display_name()


class SubjectWriteSerializer(serializers.ModelSerializer):
    """Write serializer for Subject with flat field structure."""
    
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=Standard.objects.all(),
        write_only=False,  # Allow direct field in write
    )
    
    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'code',
            'standard_id',
            'credit_hours',
            'curriculum_version',
        ]
        read_only_fields = ['id']
    
    def validate_code(self, value):
        """Validate subject code uniqueness."""
        queryset = Subject.objects.filter(code=value)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError("A subject with this code already exists.")
        
        return value
    
    def validate_credit_hours(self, value):
        """Validate credit hours is positive."""
        if value <= 0:
            raise serializers.ValidationError("Credit hours must be a positive number.")
        
        return value


# ============================================================================
# STUDENT ENROLLMENT SERIALIZERS
# ============================================================================

class StudentEnrollmentSerializer(serializers.ModelSerializer):
    """Read-only serializer for StudentEnrollment with nested fields."""
    
    student = StudentSerializer(read_only=True)
    standard = StandardSerializer(read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = StudentEnrollment
        fields = [
            'id',
            'student',
            'standard',
            'roll_number',
            'academic_year',
            'status',
            'display_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display_name(self, obj):
        """Get display name from model method."""
        return obj.display_name()


class StudentEnrollmentWriteSerializer(serializers.ModelSerializer):
    """Write serializer for StudentEnrollment with flat field structure."""
    
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=Student.objects.all(),
    )
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=Standard.objects.all(),
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYear.objects.all(),
    )
    
    class Meta:
        model = StudentEnrollment
        fields = [
            'id',
            'student_id',
            'standard_id',
            'roll_number',
            'academic_year_id',
            'status',
        ]
        read_only_fields = ['id']
    
    def validate_unique_together(self, data):
        """Validate unique_together constraints."""
        student = data.get('student')
        academic_year = data.get('academic_year')
        standard = data.get('standard')
        roll_number = data.get('roll_number')
        
        # Check student + academic_year uniqueness
        queryset = StudentEnrollment.objects.filter(
            student=student,
            academic_year=academic_year
        )
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "Student is already enrolled in this academic year."
            )
        
        # Check standard + academic_year + roll_number uniqueness
        queryset = StudentEnrollment.objects.filter(
            standard=standard,
            academic_year=academic_year,
            roll_number=roll_number
        )
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "This roll number is already assigned in this standard for this academic year."
            )
        
        return data


# ============================================================================
# CLASS TEACHER SERIALIZERS
# ============================================================================

class ClassTeacherSerializer(serializers.ModelSerializer):
    """Read-only serializer for ClassTeacher with nested fields."""
    
    standard = StandardSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ClassTeacher
        fields = [
            'id',
            'standard',
            'teacher',
            'academic_year',
            'display_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display_name(self, obj):
        """Get display name from model method."""
        return obj.display_name()


class ClassTeacherWriteSerializer(serializers.ModelSerializer):
    """Write serializer for ClassTeacher with flat field structure."""
    
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=Standard.objects.all(),
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        source='teacher',
        queryset=Teacher.objects.all(),
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYear.objects.all(),
    )
    
    class Meta:
        model = ClassTeacher
        fields = [
            'id',
            'standard_id',
            'teacher_id',
            'academic_year_id',
        ]
        read_only_fields = ['id']
    
    def validate_unique_together(self, data):
        """Validate unique_together constraint."""
        teacher = data.get('teacher')
        standard = data.get('standard')
        academic_year = data.get('academic_year')
        
        queryset = ClassTeacher.objects.filter(
            teacher=teacher,
            standard=standard,
            academic_year=academic_year
        )
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "This teacher is already assigned as class teacher for this standard in this academic year."
            )
        
        return data


# ============================================================================
# TEACHER SUBJECT SERIALIZERS
# ============================================================================

class TeacherSubjectSerializer(serializers.ModelSerializer):
    """Read-only serializer for TeacherSubject with nested fields."""
    
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)
    display_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = TeacherSubject
        fields = [
            'id',
            'subject',
            'teacher',
            'academic_year',
            'display_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display_name(self, obj):
        """Get display name from model method."""
        return obj.display_name()


class TeacherSubjectWriteSerializer(serializers.ModelSerializer):
    """Write serializer for TeacherSubject with flat field structure."""
    
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject',
        queryset=Subject.objects.all(),
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        source='teacher',
        queryset=Teacher.objects.all(),
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYear.objects.all(),
    )
    
    class Meta:
        model = TeacherSubject
        fields = [
            'id',
            'subject_id',
            'teacher_id',
            'academic_year_id',
        ]
        read_only_fields = ['id']
        
