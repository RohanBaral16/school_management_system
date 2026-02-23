"""
Test suite for Academics API.
Tests CRUD operations for academic resources.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
import nepali_datetime

from accounts.models import Student, Teacher
from academics.models import AcademicYear, Standard, Subject, StudentEnrollment, ClassTeacher, TeacherSubject


class AcademicYearAPITestCase(APITestCase):
    """Test cases for AcademicYear ViewSet."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher@test.com',
            password='teacher123'
        )
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John',
            last_name='Doe',
            email='john@test.com',
            phone='9841234567'
        )
        
        self.academic_year = AcademicYear.objects.create(
            name='2081',
            is_current=True
        )
        
        self.api_url = '/api/academic-years/'
    
    def test_academic_year_list(self):
        """Test listing academic years."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_academic_year_create_by_teacher(self):
        """Test that teachers can create academic years."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': '2082',
            'is_current': False,
            'status': 'active'
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AcademicYear.objects.count(), 2)
    
    def test_academic_year_create_invalid_name(self):
        """Test that invalid academic year names are rejected."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': 'invalid',  # Not a number
            'is_current': False,
            'status': 'active'
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_academic_year_update(self):
        """Test updating an academic year."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': '2081',
            'is_current': False,
            'status': 'archived'
        }
        response = self.client.put(f'{self.api_url}{self.academic_year.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_academic_year_delete(self):
        """Test deleting an academic year."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.delete(f'{self.api_url}{self.academic_year.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class StandardAPITestCase(APITestCase):
    """Test cases for Standard ViewSet."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher@test.com',
            password='teacher123'
        )
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John',
            last_name='Doe',
            email='john@test.com',
            phone='9841234567'
        )
        
        self.standard = Standard.objects.create(
            name='9',
            section='A',
            status='active'
        )
        
        self.api_url = '/api/standards/'
    
    def test_standard_list(self):
        """Test listing standards."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_standard_create_by_teacher(self):
        """Test that teachers can create standards."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': '10',
            'section': 'B',
            'status': 'active'
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Standard.objects.count(), 2)
    
    def test_standard_duplicate_name_section(self):
        """Test that duplicate standards are rejected."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': '9',
            'section': 'A',  # Duplicate
            'status': 'active'
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_standard_retrieve(self):
        """Test retrieving a specific standard."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.standard.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '9')


class SubjectAPITestCase(APITestCase):
    """Test cases for Subject ViewSet."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher@test.com',
            password='teacher123'
        )
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John',
            last_name='Doe',
            email='john@test.com',
            phone='9841234567'
        )
        
        self.standard = Standard.objects.create(
            name='9',
            section='A',
            status='active'
        )
        
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH',
            standard=self.standard,
            credit_hours=3.0
        )
        
        self.api_url = '/api/subjects/'
    
    def test_subject_list(self):
        """Test listing subjects."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_subject_create_by_teacher(self):
        """Test that teachers can create subjects."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': 'English',
            'code': 'ENG',
            'standard_id': self.standard.id,
            'credit_hours': 2.5
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subject.objects.count(), 2)
    
    def test_subject_create_duplicate_code(self):
        """Test that duplicate subject codes are rejected."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': 'Applied Math',
            'code': 'MATH',  # Duplicate
            'standard_id': self.standard.id,
            'credit_hours': 2.0
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_subject_invalid_credit_hours(self):
        """Test that invalid credit hours are rejected."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': 'Science',
            'code': 'SCI',
            'standard_id': self.standard.id,
            'credit_hours': -1  # Invalid
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StudentEnrollmentAPITestCase(APITestCase):
    """Test cases for StudentEnrollment ViewSet."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher@test.com',
            password='teacher123'
        )
        
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John',
            last_name='Doe',
            email='john@test.com',
            phone='9841234567'
        )
        
        self.student = Student.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@test.com',
            admission_number='ADM001'
        )
        
        self.standard = Standard.objects.create(
            name='9',
            section='A',
            status='active'
        )
        
        self.academic_year = AcademicYear.objects.create(
            name='2081',
            is_current=True
        )
        
        self.enrollment = StudentEnrollment.objects.create(
            student=self.student,
            standard=self.standard,
            roll_number='1',
            academic_year=self.academic_year,
            status='enrolled'
        )
        
        self.api_url = '/api/student-enrollments/'
    
    def test_enrollment_list(self):
        """Test listing enrollments."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_enrollment_create_by_teacher(self):
        """Test that teachers can create enrollments."""
        student2 = Student.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.s@test.com',
            admission_number='ADM002'
        )
        
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_id': student2.id,
            'standard_id': self.standard.id,
            'roll_number': '2',
            'academic_year_id': self.academic_year.id,
            'status': 'enrolled'
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_enrollment_duplicate_student_year(self):
        """Test that duplicate enrollments in same year are rejected."""
        student2 = Student.objects.create(
            first_name='Bob',
            last_name='Johnson',
            email='bob@test.com',
            admission_number='ADM003'
        )
        
        self.client.force_authenticate(user=self.teacher_user)
        
        # Try to enroll the SAME student in the SAME year in a different standard
        data = {
            'student_id': self.student.id,
            'standard_id': self.standard.id,
            'roll_number': '2',
            'academic_year_id': self.academic_year.id,
            'status': 'enrolled'
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_enrollment_retrieve(self):
        """Test retrieving a specific enrollment."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.enrollment.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['roll_number'], '1')
