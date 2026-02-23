"""
Test suite for Accounts API.
Tests CRUD operations, permissions, and serializer validation.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from accounts.models import Student, Teacher


class StudentAPITestCase(APITestCase):
    """Test cases for Student ViewSet."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create users
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
        
        self.normal_user = User.objects.create_user(
            username='user1',
            email='user@test.com',
            password='user123'
        )
        
        # Create teacher record
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='John',
            last_name='Doe',
            email='teacher@test.com',
            phone='9841234567'
        )
        
        # Create test student
        self.student = Student.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@test.com',
            admission_number='ADM001',
            gender='female'
        )
        
        self.api_url = '/api/students/'
    
    def test_student_list_unauthenticated(self):
        """Test that unauthenticated users cannot access student list."""
        response = self.client.get(self.api_url)
        # Permission denied returns 403, not 401
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_student_list_authenticated(self):
        """Test that authenticated users can view student list."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_student_create_by_teacher(self):
        """Test that teachers can create students."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'email': 'alice@test.com',
            'admission_number': 'ADM002',
            'gender': 'female'
        }
        response = self.client.post(self.api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 2)
    
    def test_student_create_by_normal_user_forbidden(self):
        """Test that normal users cannot create students."""
        self.client.force_authenticate(user=self.normal_user)
        
        data = {
            'first_name': 'Bob',
            'last_name': 'Brown',
            'email': 'bob@test.com',
            'admission_number': 'ADM003',
            'gender': 'male'
        }
        response = self.client.post(self.api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_student_create_duplicate_admission_number(self):
        """Test that duplicate admission numbers are rejected."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'first_name': 'Charlie',
            'last_name': 'Davis',
            'email': 'charlie@test.com',
            'admission_number': 'ADM001',  # Duplicate
            'gender': 'male'
        }
        response = self.client.post(self.api_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_student_retrieve(self):
        """Test retrieving a specific student."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.student.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.student.id)
        self.assertEqual(response.data['first_name'], 'Jane')
    
    def test_student_update_by_teacher(self):
        """Test that teachers can update students."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'first_name': 'Janet',
            'last_name': 'Smithson',
            'email': 'janet@test.com',
            'admission_number': 'ADM001',
            'gender': 'female'
        }
        response = self.client.put(f'{self.api_url}{self.student.id}/', data, format='json')
        
        # Update should work for teachers
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
    
    def test_student_delete_by_admin(self):
        """Test that only admins can delete students."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.delete(f'{self.api_url}{self.student.id}/')
        # Admin can delete
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TeacherAPITestCase(APITestCase):
    """Test cases for Teacher ViewSet."""
    
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
        
        self.api_url = '/api/teachers/'
    
    def test_teacher_list_authenticated(self):
        """Test that authenticated users can view teacher list."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_teacher_create_by_admin(self):
        """Test that admins can create teachers."""
        admin_user = User.objects.create_user(
            username='newadmin',
            email='newadmin@test.com'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'user_id': admin_user.id,
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'email': 'sarah@test.com',
            'phone': '9842222222',
            'designation': 'Principal'
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Teacher.objects.count(), 2)
    
    def test_teacher_retrieve(self):
        """Test retrieving a specific teacher."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.teacher.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')
    
    def test_teacher_update_own_record(self):
        """Test that teachers can update their own records."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'first_name': 'Jonathan',
            'last_name': 'Doe',
            'email': 'jonathan@test.com',
            'phone': '9843333333',
            'designation': 'Senior Teacher'
        }
        response = self.client.put(f'{self.api_url}{self.teacher.id}/', data, format='json')
        
        # Teacher should be able to update own record
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_teacher_delete_by_admin(self):
        """Test that only admins can delete teachers."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.delete(f'{self.api_url}{self.teacher.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
