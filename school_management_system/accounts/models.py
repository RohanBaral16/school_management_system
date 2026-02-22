from django.db import models
from django.contrib.auth.models import User
from nepali_datetime_field.models import NepaliDateField
import nepali_datetime
from datetime import date

class Student(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    
    # Contact Info
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Dates (Stored both for system logic and local reporting)
    date_of_birth = models.DateField(help_text="Date of birth in AD", default=date.today)
    date_of_birth_bs = NepaliDateField(default=nepali_datetime.date.today)
    
    # Identifiers
    
    admission_number = models.CharField(max_length=20, unique=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.full_name
    
    # def __str__(self):
    #     return f"{self.first_name} {self.last_name}"
    
    def full_name(self):
        """Display method for student name"""
        if self.middle_name and self.middle_name.strip():
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class Teacher(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("on_leave", "On Leave"),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    # Linking to Django's built-in User for Authentication
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    designation = models.CharField(max_length=100, help_text="e.g. Secondary Level Teacher")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    date_of_birth = models.DateField(help_text="Date of birth in AD", default=date.today)
    date_of_birth_bs = NepaliDateField(default=nepali_datetime.date.today)
    # Contact Info
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name}"
    
    def full_name(self):
        """Display method for teacher name"""
        if self.middle_name and self.middle_name.strip():
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
