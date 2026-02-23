"""
Test suite for Activities API.
Tests CRUD operations for exams, results, and attendance.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from datetime import date

from accounts.models import Student, Teacher
from academics.models import (
    AcademicYear, Standard, Subject, StudentEnrollment, 
    ClassTeacher, TeacherSubject
)
from activities.models import Exam, ExamSubject, SubjectResult, StudentResultSummary, Attendance


class ExamAPITestCase(APITestCase):
    """Test cases for Exam ViewSet."""
    
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
        
        self.exam = Exam.objects.create(
            name='Mid Term',
            term='first',
            academic_year=self.academic_year,
            start_date=date.today(),
            end_date=date.today(),
        )
        
        self.api_url = '/api/exams/'
    
    def test_exam_list(self):
        """Test listing exams."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_exam_create_by_teacher(self):
        """Test that teachers can create exams."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': 'Final Exam',
            'term': 'second',
            'academic_year_id': self.academic_year.id,
            'start_date': '2026-03-01',
            'end_date': '2026-03-15',
            'is_published': False
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exam.objects.count(), 2)
    
    def test_exam_retrieve(self):
        """Test retrieving a specific exam."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.exam.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mid Term')
    
    def test_exam_update_by_teacher(self):
        """Test that teachers can update exams."""
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'name': 'Midterm Exam',
            'term': 'first',
            'academic_year_id': self.academic_year.id,
            'start_date': '2026-02-01',
            'end_date': '2026-02-10',
            'is_published': True
        }
        response = self.client.put(f'{self.api_url}{self.exam.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_exam_delete_by_admin(self):
        """Test that admins can delete exams."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.delete(f'{self.api_url}{self.exam.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ExamSubjectAPITestCase(APITestCase):
    """Test cases for ExamSubject ViewSet."""
    
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
            section='A'
        )
        
        self.academic_year = AcademicYear.objects.create(
            name='2081',
            is_current=True
        )
        
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH',
            standard=self.standard,
            credit_hours=3.0
        )
        
        self.exam = Exam.objects.create(
            name='Mid Term',
            term='first',
            academic_year=self.academic_year
        )
        
        self.exam_subject = ExamSubject.objects.create(
            exam=self.exam,
            subject=self.subject,
            total_marks=100,
            pass_marks=40,
            marks_distribution_theory=60,
            marks_distribution_practical=40
        )
        
        self.api_url = '/api/exam-subjects/'
    
    def test_exam_subject_list(self):
        """Test listing exam subjects."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_exam_subject_create_by_teacher(self):
        """Test that teachers can create exam subjects."""
        subject2 = Subject.objects.create(
            name='English',
            code='ENG',
            standard=self.standard,
            credit_hours=2.0
        )
        
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'exam_id': self.exam.id,
            'subject_id': subject2.id,
            'total_marks': 100,
            'pass_marks': 35,
            'marks_distribution_theory': 75,
            'marks_distribution_practical': 25
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_exam_subject_retrieve(self):
        """Test retrieving a specific exam subject."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.exam_subject.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_marks'], 100)


class SubjectResultAPITestCase(APITestCase):
    """Test cases for SubjectResult ViewSet."""
    
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
            section='A'
        )
        
        self.academic_year = AcademicYear.objects.create(
            name='2081',
            is_current=True
        )
        
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH',
            standard=self.standard,
            credit_hours=3.0
        )
        
        self.exam = Exam.objects.create(
            name='Mid Term',
            term='first',
            academic_year=self.academic_year
        )
        
        self.exam_subject = ExamSubject.objects.create(
            exam=self.exam,
            subject=self.subject,
            total_marks=100
        )
        
        self.result = SubjectResult.objects.create(
            student=self.student,
            exam_subject=self.exam_subject,
            marks_obtained_theory=50,
            marks_obtained_practical=30
        )
        
        self.api_url = '/api/subject-results/'
    
    def test_subject_result_list(self):
        """Test listing subject results."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_subject_result_create_by_teacher(self):
        """Test that teachers can create subject results."""
        student2 = Student.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.s@test.com',
            admission_number='ADM002'
        )
        
        self.client.force_authenticate(user=self.teacher_user)
        
        data = {
            'student_id': student2.id,
            'exam_subject_id': self.exam_subject.id,
            'marks_obtained_theory': 45,
            'marks_obtained_practical': 35
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_subject_result_retrieve(self):
        """Test retrieving a specific result."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.result.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marks_obtained_theory'], 50)


class StudentResultSummaryAPITestCase(APITestCase):
    """Test cases for StudentResultSummary ViewSet."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        self.student = Student.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@test.com',
            admission_number='ADM001'
        )
        
        self.academic_year = AcademicYear.objects.create(
            name='2081',
            is_current=True
        )
        
        self.exam = Exam.objects.create(
            name='Mid Term',
            term='first',
            academic_year=self.academic_year
        )
        
        self.summary = StudentResultSummary.objects.create(
            student=self.student,
            exam=self.exam,
            academic_year=self.academic_year,
            total_marks=160,
            gpa=3.8,
            overall_grade='A+'
        )
        
        self.api_url = '/api/result-summaries/'
    
    def test_summary_list(self):
        """Test listing result summaries."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_summary_retrieve(self):
        """Test retrieving a specific summary."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.summary.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_marks'], 160)
        self.assertEqual(response.data['gpa'], 3.8)


class AttendanceAPITestCase(APITestCase):
    """Test cases for Attendance ViewSet."""
    
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
            section='A'
        )
        
        self.academic_year = AcademicYear.objects.create(
            name='2081',
            is_current=True
        )
        
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH',
            standard=self.standard,
            credit_hours=3.0
        )
        
        self.attendance = Attendance.objects.create(
            student=self.student,
            standard=self.standard,
            academic_year=self.academic_year,
            subject=self.subject,
            recorded_by=self.teacher,
            status='present',
            date=date.today()
        )
        
        self.api_url = '/api/attendance/'
    
    def test_attendance_list(self):
        """Test listing attendance records."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.api_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_attendance_create_by_teacher(self):
        """Test that teachers can create attendance records."""
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
            'academic_year_id': self.academic_year.id,
            'subject_id': self.subject.id,
            'recorded_by_id': self.teacher.id,
            'status': 'absent',
            'date': '2026-02-23'
        }
        response = self.client.post(self.api_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_attendance_retrieve(self):
        """Test retrieving a specific attendance record."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.api_url}{self.attendance.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'present')
