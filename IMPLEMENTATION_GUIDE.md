# Implementation Guide for New Features

## Table of Contents
1. [Quick Start](#quick-start)
2. [Step-by-Step Implementation](#step-by-step-implementation)
3. [Code Examples](#code-examples)
4. [Testing Guidelines](#testing-guidelines)
5. [Common Patterns](#common-patterns)

---

## Quick Start

### Adding a New Model - Example: Guardian Model

#### Step 1: Create the Model

Create a new file or add to `/school_management_system/accounts/models.py`:

```python
class Guardian(models.Model):
    """Parent/Guardian information"""
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('legal_guardian', 'Legal Guardian'),
        ('grandparent', 'Grandparent'),
        ('other', 'Other'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='guardians'
    )
    relationship = models.CharField(
        max_length=20, 
        choices=RELATIONSHIP_CHOICES
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Contact
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True
    )
    
    # Address
    address = models.TextField()
    occupation = models.CharField(max_length=100, blank=True)
    
    # Flags
    is_primary_contact = models.BooleanField(default=False)
    can_pick_student = models.BooleanField(default=True)
    is_emergency_contact = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary_contact', 'first_name']
        verbose_name = 'Guardian'
        verbose_name_plural = 'Guardians'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.relationship}) - {self.student}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary contact per student
        if self.is_primary_contact:
            Guardian.objects.filter(
                student=self.student, 
                is_primary_contact=True
            ).exclude(pk=self.pk).update(is_primary_contact=False)
        super().save(*args, **kwargs)
```

#### Step 2: Register in Admin

Add to `/school_management_system/accounts/admin.py`:

```python
from django.contrib import admin
from .models import Student, Teacher, Guardian

class GuardianInline(admin.TabularInline):
    model = Guardian
    extra = 1
    fields = [
        'relationship', 
        'first_name', 
        'last_name', 
        'phone', 
        'email',
        'is_primary_contact', 
        'is_emergency_contact'
    ]

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'admission_number', 
        'first_name', 
        'last_name', 
        'gender', 
        'date_of_birth'
    ]
    search_fields = ['first_name', 'last_name', 'admission_number']
    list_filter = ['gender', 'created_at']
    inlines = [GuardianInline]

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = [
        'first_name', 
        'last_name', 
        'student', 
        'relationship', 
        'phone',
        'is_primary_contact'
    ]
    search_fields = ['first_name', 'last_name', 'phone']
    list_filter = ['relationship', 'is_primary_contact']
```

#### Step 3: Create and Run Migrations

```bash
cd /home/runner/work/school_management_system/school_management_system/school_management_system
python manage.py makemigrations
python manage.py migrate
```

#### Step 4: Create API Serializer (Optional)

Create `/school_management_system/accounts/serializers.py`:

```python
from rest_framework import serializers
from .models import Guardian, Student

class GuardianSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.first_name', 
        read_only=True
    )
    
    class Meta:
        model = Guardian
        fields = [
            'id', 
            'student', 
            'student_name',
            'relationship',
            'first_name', 
            'last_name',
            'email', 
            'phone', 
            'alternate_phone',
            'address', 
            'occupation',
            'is_primary_contact',
            'can_pick_student',
            'is_emergency_contact',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """Ensure phone number is provided"""
        if not data.get('phone'):
            raise serializers.ValidationError(
                "Phone number is required"
            )
        return data
```

#### Step 5: Create API Views

Create or update `/school_management_system/accounts/views.py`:

```python
from rest_framework import viewsets, permissions
from .models import Guardian
from .serializers import GuardianSerializer

class GuardianViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Guardian CRUD operations
    """
    queryset = Guardian.objects.select_related('student').all()
    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter by student
        """
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        return queryset
```

#### Step 6: Register URLs

Create or update `/school_management_system/accounts/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuardianViewSet

router = DefaultRouter()
router.register(r'guardians', GuardianViewSet, basename='guardian')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

Then include in main URLs `/school_management_system/school_management_system/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # ... other paths
]
```

---

## Step-by-Step Implementation for Key Features

### Feature 1: Fee Management System

#### Models (Add to `academics/models.py`)

```python
class FeeStructure(models.Model):
    """Define fee types and amounts for each class"""
    FEE_TYPE_CHOICES = [
        ('admission', 'Admission Fee'),
        ('tuition', 'Tuition Fee'),
        ('exam', 'Exam Fee'),
        ('library', 'Library Fee'),
        ('lab', 'Lab Fee'),
        ('transport', 'Transport Fee'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_mandatory = models.BooleanField(default=True)
    due_date = NepaliDateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('name', 'standard', 'academic_year')
        ordering = ['standard', 'fee_type']
    
    def __str__(self):
        return f"{self.name} - {self.standard} ({self.academic_year})"


class FeePayment(models.Model):
    """Track individual fee payments"""
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
    ]
    
    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('cheque', 'Cheque'),
    ]
    
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS, 
        default='pending'
    )
    
    payment_date = NepaliDateField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD, 
        blank=True
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    
    receipt_number = models.CharField(max_length=50, unique=True)
    received_by = models.ForeignKey(
        'accounts.Teacher', 
        on_delete=models.SET_NULL, 
        null=True
    )
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.fee_structure.name} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-generate receipt number if not provided
        if not self.receipt_number:
            from django.utils import timezone
            year = timezone.now().year
            count = FeePayment.objects.filter(
                created_at__year=year
            ).count() + 1
            self.receipt_number = f"REC-{year}-{count:05d}"
        
        # Update status based on amount paid
        if self.amount_paid >= self.amount_due:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif self.fee_structure.due_date:
            from nepali_datetime import date
            if date.today() > self.fee_structure.due_date:
                self.status = 'overdue'
        
        super().save(*args, **kwargs)
    
    @property
    def balance(self):
        """Calculate remaining balance"""
        return self.amount_due - self.amount_paid
```

#### Admin Configuration

```python
# academics/admin.py
from django.contrib import admin
from .models import FeeStructure, FeePayment

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'fee_type', 
        'standard', 
        'academic_year', 
        'amount', 
        'is_mandatory'
    ]
    list_filter = ['fee_type', 'standard', 'academic_year', 'is_mandatory']
    search_fields = ['name']

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = [
        'receipt_number',
        'student', 
        'fee_structure', 
        'amount_due',
        'amount_paid',
        'balance',
        'status',
        'payment_date'
    ]
    list_filter = ['status', 'payment_method', 'academic_year']
    search_fields = [
        'receipt_number', 
        'student__first_name', 
        'student__last_name',
        'transaction_id'
    ]
    readonly_fields = ['receipt_number', 'balance']
    
    def balance(self, obj):
        return obj.balance
    balance.short_description = 'Balance'
```

---

### Feature 2: Homework & Assignment System

#### Models (Add to `academics/models.py`)

```python
class Homework(models.Model):
    """Homework assignments"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE)
    teacher = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_date = NepaliDateField(default=nepali_datetime.date.today)
    due_date = NepaliDateField()
    
    max_marks = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.0
    )
    
    attachment = models.FileField(
        upload_to='homework/', 
        blank=True, 
        null=True
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='assigned'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.title} - {self.subject} - {self.standard}"
    
    def is_overdue(self):
        """Check if homework is past due date"""
        return nepali_datetime.date.today() > self.due_date


class HomeworkSubmission(models.Model):
    """Student submissions for homework"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('late', 'Late Submission'),
        ('graded', 'Graded'),
    ]
    
    homework = models.ForeignKey(
        Homework, 
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    
    submission_date = NepaliDateField(default=nepali_datetime.date.today)
    submission_file = models.FileField(
        upload_to='homework/submissions/', 
        blank=True
    )
    submission_text = models.TextField(blank=True)
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    marks_obtained = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        'accounts.Teacher', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('homework', 'student')
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"{self.student} - {self.homework.title} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-mark as late if submitted after due date
        if self.submission_date and self.submission_date > self.homework.due_date:
            if self.status == 'pending':
                self.status = 'late'
        
        # Update graded timestamp
        if self.marks_obtained is not None and self.status != 'graded':
            self.status = 'graded'
            if not self.graded_at:
                from django.utils import timezone
                self.graded_at = timezone.now()
        
        super().save(*args, **kwargs)
```

---

## Common Patterns & Best Practices

### Pattern 1: Audit Trail with `created_at` and `updated_at`

Always include these fields for tracking:

```python
class MyModel(models.Model):
    # ... other fields ...
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Pattern 2: Using Choices for Status Fields

```python
class MyModel(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
```

### Pattern 3: Foreign Key Relationships

```python
# CASCADE: Delete related objects when parent is deleted
student = models.ForeignKey(
    Student, 
    on_delete=models.CASCADE
)

# PROTECT: Prevent deletion if related objects exist
academic_year = models.ForeignKey(
    AcademicYear, 
    on_delete=models.PROTECT
)

# SET_NULL: Set to NULL when parent is deleted
teacher = models.ForeignKey(
    Teacher, 
    on_delete=models.SET_NULL, 
    null=True
)
```

### Pattern 4: Custom Validation

```python
from django.core.exceptions import ValidationError

class MyModel(models.Model):
    # ... fields ...
    
    def clean(self):
        """Custom validation logic"""
        super().clean()
        
        if self.start_date > self.end_date:
            raise ValidationError({
                'end_date': 'End date must be after start date.'
            })
    
    def save(self, *args, **kwargs):
        # Force validation before save
        self.full_clean()
        super().save(*args, **kwargs)
```

### Pattern 5: Property Methods for Calculated Fields

```python
class FeePayment(models.Model):
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def balance(self):
        """Calculate remaining balance"""
        return self.amount_due - self.amount_paid
    
    @property
    def is_fully_paid(self):
        """Check if payment is complete"""
        return self.amount_paid >= self.amount_due
```

### Pattern 6: Select Related for Performance

```python
# In views or queries
students = Student.objects.select_related(
    'current_enrollment__standard',
    'current_enrollment__academic_year'
).all()

# For Many-to-Many
homework = Homework.objects.prefetch_related(
    'submissions__student'
).all()
```

---

## Testing Guidelines

### Unit Tests Example

Create `tests.py` in each app:

```python
# accounts/tests.py
from django.test import TestCase
from .models import Student, Guardian

class GuardianModelTest(TestCase):
    def setUp(self):
        """Create test student"""
        self.student = Student.objects.create(
            first_name="John",
            last_name="Doe",
            gender="male",
            date_of_birth="2010-01-01",
            admission_number="2024001"
        )
    
    def test_create_guardian(self):
        """Test guardian creation"""
        guardian = Guardian.objects.create(
            student=self.student,
            relationship="father",
            first_name="Robert",
            last_name="Doe",
            phone="9876543210",
            address="Kathmandu",
            is_primary_contact=True
        )
        
        self.assertEqual(guardian.student, self.student)
        self.assertTrue(guardian.is_primary_contact)
    
    def test_only_one_primary_contact(self):
        """Test that only one guardian can be primary contact"""
        guardian1 = Guardian.objects.create(
            student=self.student,
            relationship="father",
            first_name="Robert",
            last_name="Doe",
            phone="9876543210",
            address="Kathmandu",
            is_primary_contact=True
        )
        
        guardian2 = Guardian.objects.create(
            student=self.student,
            relationship="mother",
            first_name="Mary",
            last_name="Doe",
            phone="9876543211",
            address="Kathmandu",
            is_primary_contact=True
        )
        
        # Refresh guardian1 from database
        guardian1.refresh_from_db()
        
        # guardian1 should no longer be primary
        self.assertFalse(guardian1.is_primary_contact)
        self.assertTrue(guardian2.is_primary_contact)

# Run tests with:
# python manage.py test accounts
```

---

## Database Migration Tips

### Creating Migrations

```bash
# Create migration for specific app
python manage.py makemigrations accounts

# Create migration with name
python manage.py makemigrations accounts --name add_guardian_model

# Show SQL that will be executed
python manage.py sqlmigrate accounts 0001

# Apply migrations
python manage.py migrate

# Rollback migration
python manage.py migrate accounts 0001
```

### Data Migrations

When you need to populate or transform data:

```bash
python manage.py makemigrations --empty accounts --name populate_default_data
```

Then edit the migration file:

```python
# Generated migration file
from django.db import migrations

def populate_default_data(apps, schema_editor):
    AcademicYear = apps.get_model('academics', 'AcademicYear')
    
    # Create default academic year
    AcademicYear.objects.get_or_create(
        name='2081',
        defaults={
            'is_current': True,
            'status': 'active'
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('academics', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(populate_default_data),
    ]
```

---

## API Endpoints Design

### RESTful API Structure

```
GET    /api/students/              # List all students
POST   /api/students/              # Create new student
GET    /api/students/{id}/         # Get student detail
PUT    /api/students/{id}/         # Update student
PATCH  /api/students/{id}/         # Partial update
DELETE /api/students/{id}/         # Delete student

# Nested resources
GET    /api/students/{id}/guardians/      # Get student's guardians
POST   /api/students/{id}/guardians/      # Add guardian to student

# Filtering
GET    /api/students/?standard=10&academic_year=2081

# Custom actions
POST   /api/students/{id}/promote/        # Promote student to next class
GET    /api/students/{id}/report-card/    # Get student report card
```

---

## Security Considerations

### 1. Sensitive Data

```python
# Don't expose sensitive fields in API
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['internal_notes', 'medical_records']
```

### 2. Permission Classes

```python
from rest_framework import permissions

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Only teachers can edit, others read-only
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is a teacher
        return hasattr(request.user, 'teacher')
```

### 3. Data Validation

```python
def clean_phone_number(phone):
    """Validate Nepal phone number format"""
    import re
    pattern = r'^(98|97)\d{8}$'
    if not re.match(pattern, phone):
        raise ValidationError('Invalid Nepal phone number')
```

---

## Performance Optimization

### 1. Database Indexing

```python
class Student(models.Model):
    # ... fields ...
    
    class Meta:
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['email']),
        ]
```

### 2. Query Optimization

```python
# Bad: N+1 queries
students = Student.objects.all()
for student in students:
    print(student.current_enrollment.standard.name)  # Query each time

# Good: Use select_related
students = Student.objects.select_related(
    'current_enrollment__standard'
).all()
for student in students:
    print(student.current_enrollment.standard.name)  # No extra queries
```

### 3. Caching

```python
from django.core.cache import cache

def get_student_count():
    count = cache.get('student_count')
    if count is None:
        count = Student.objects.count()
        cache.set('student_count', count, 3600)  # Cache for 1 hour
    return count
```

---

## Deployment Checklist

### Before Production

- [ ] Set `DEBUG = False` in settings
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up environment variables for sensitive data
- [ ] Configure static files with `collectstatic`
- [ ] Set up proper database backups
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure email backend for notifications
- [ ] Set up logging and monitoring
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Test with production-like data
- [ ] Document deployment process

---

## Additional Resources

### Django Documentation
- Models: https://docs.djangoproject.com/en/4.2/topics/db/models/
- Admin: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/
- Testing: https://docs.djangoproject.com/en/4.2/topics/testing/

### DRF Documentation
- Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- ViewSets: https://www.django-rest-framework.org/api-guide/viewsets/
- Authentication: https://www.django-rest-framework.org/api-guide/authentication/

---

**Document Version**: 1.0  
**Last Updated**: February 10, 2026
