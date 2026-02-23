"""
Serializers for Accounts app.
Implements separate read and write serializers for better separation of concerns.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Student, Teacher


# ============================================================================
# STUDENT SERIALIZERS
# ============================================================================

class StudentSerializer(serializers.ModelSerializer):
    """Read-only serializer for Student with nested fields."""
    
    full_name = serializers.SerializerMethodField(read_only=True)
    
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
            'admission_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Get full name from model method."""
        return obj.full_name()


class StudentWriteSerializer(serializers.ModelSerializer):
    """Write serializer for Student with flat field structure."""
    
    class Meta:
        model = Student
        fields = [
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'email',
            'phone',
            'date_of_birth',
            'date_of_birth_bs',
            'admission_number',
        ]
        read_only_fields = ['id']
    
    def validate_email(self, value):
        """Validate email uniqueness (optional, depends on requirements)."""
        if not value:
            return value
        
        if Student.objects.filter(email=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        
        return value
    
    def validate_admission_number(self, value):
        """Validate admission number uniqueness."""
        if Student.objects.filter(admission_number=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("A student with this admission number already exists.")
        
        return value


# ============================================================================
# TEACHER SERIALIZERS
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser']
        read_only_fields = ['id']


class TeacherSerializer(serializers.ModelSerializer):
    """Read-only serializer for Teacher with nested fields."""
    
    full_name = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Teacher
        fields = [
            'id',
            'user',
            'full_name',
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'designation',
            'email',
            'status',
            'phone',
            'date_of_birth',
            'date_of_birth_bs',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        """Get full name from model method."""
        return obj.full_name()


class TeacherWriteSerializer(serializers.ModelSerializer):
    """Write serializer for Teacher with flat field structure."""
    
    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    
    class Meta:
        model = Teacher
        fields = [
            'id',
            'user_id',
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'designation',
            'email',
            'status',
            'phone',
            'date_of_birth',
            'date_of_birth_bs',
        ]
        read_only_fields = ['id']
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if Teacher.objects.filter(email=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("A teacher with this email already exists.")
        
        return value