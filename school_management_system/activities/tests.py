from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from activities.models import SubjectResult, StudentResultSummary, Exam, ExamSubject
from academics.models import (
    StudentEnrollment, Standard, Subject, AcademicYear
)
from accounts.models import Student

User = get_user_model()


class StudentResultSummaryTestCase(TestCase):
    """Test cases for StudentResultSummary model after M2M refactoring."""
    
    def setUp(self):
        """Set up test data."""
        # Create academic year
        self.academic_year = AcademicYear.objects.create(
            year='2081',
            is_current=True
        )
        
        # Create standard
        self.standard = Standard.objects.create(
            name='Class 10',
            section='A',
            academic_year=self.academic_year
        )
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Mathematics',
            standard=self.standard
        )
        
        # Create student
        self.student_user = Student.objects.create(
            username='student1',
            email='student1@test.com',
            first_name='Test',
            last_name='Student'
        )
        
        # Create enrollment
        self.enrollment = StudentEnrollment.objects.create(
            student=self.student_user,
            standard=self.standard,
            academic_year=self.academic_year,
            roll_number='001',
            status='enrolled'
        )
        
        # Create exam
        self.exam = Exam.objects.create(
            name='First Terminal Exam 2081',
            term='first_term',
            academic_year=self.academic_year,
            start_date='2081-01-01',
            end_date='2081-01-15',
            is_published=False
        )
        
        # Create exam subject
        self.exam_subject = ExamSubject.objects.create(
            exam=self.exam,
            subject=self.subject,
            exam_date='2081-01-05',
            full_marks_theory=Decimal('75.00'),
            pass_marks_theory=Decimal('27.00'),
            full_marks_practical=Decimal('25.00'),
            pass_marks_practical=Decimal('9.00')
        )
        
        # Create subject result
        self.subject_result = SubjectResult.objects.create(
            student=self.enrollment,
            exam_subject=self.exam_subject,
            marks_obtained_theory=Decimal('60.00'),
            marks_obtained_practical=Decimal('20.00')
        )
        
        # Create result summary
        self.summary = StudentResultSummary.objects.create(
            student=self.enrollment,
            exam=self.exam,
            academic_year=self.academic_year,
            total_marks=Decimal('80.00'),
            percentage=Decimal('80.00'),
            gpa=Decimal('3.60'),
            overall_grade='A',
            rank=1
        )
    
    def test_get_subject_results_method(self):
        """Test the new get_subject_results() method."""
        results = self.summary.get_subject_results()
        
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first(), self.subject_result)
    
    def test_subject_results_filtering(self):
        """Test that subject results can be fetched by filtering."""
        results = SubjectResult.objects.filter(
            student=self.summary.student,
            exam_subject__exam=self.summary.exam
        )
        
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().marks_obtained_theory, Decimal('60.00'))
        self.assertEqual(results.first().marks_obtained_practical, Decimal('20.00'))
    
    def test_multiple_subject_results(self):
        """Test filtering with multiple subject results."""
        # Create another subject and exam subject
        subject2 = Subject.objects.create(
            name='Science',
            standard=self.standard
        )
        
        exam_subject2 = ExamSubject.objects.create(
            exam=self.exam,
            subject=subject2,
            exam_date='2081-01-06',
            full_marks_theory=Decimal('75.00'),
            pass_marks_theory=Decimal('27.00'),
            full_marks_practical=Decimal('25.00'),
            pass_marks_practical=Decimal('9.00')
        )
        
        # Create another subject result
        SubjectResult.objects.create(
            student=self.enrollment,
            exam_subject=exam_subject2,
            marks_obtained_theory=Decimal('65.00'),
            marks_obtained_practical=Decimal('22.00')
        )
        
        # Test filtering
        results = self.summary.get_subject_results()
        self.assertEqual(results.count(), 2)
    
    def test_no_m2m_field_exists(self):
        """Test that the M2M field no longer exists."""
        self.assertFalse(hasattr(self.summary, 'results'))
        # But the method should exist
        self.assertTrue(hasattr(self.summary, 'get_subject_results'))


class SubjectResultTestCase(TestCase):
    """Test cases for SubjectResult model."""
    
    def setUp(self):
        """Set up test data."""
        self.academic_year = AcademicYear.objects.create(
            year='2081',
            is_current=True
        )
        
        self.standard = Standard.objects.create(
            name='Class 10',
            section='A',
            academic_year=self.academic_year
        )
        
        self.subject = Subject.objects.create(
            name='Mathematics',
            standard=self.standard
        )
        
        self.student_user = Student.objects.create(
            username='student2',
            email='student2@test.com',
            first_name='Test',
            last_name='Student2'
        )
        
        self.enrollment = StudentEnrollment.objects.create(
            student=self.student_user,
            standard=self.standard,
            academic_year=self.academic_year,
            roll_number='002',
            status='enrolled'
        )
        
        self.exam = Exam.objects.create(
            name='First Terminal Exam 2081',
            term='first_term',
            academic_year=self.academic_year,
            start_date='2081-01-01',
            end_date='2081-01-15',
            is_published=False
        )
        
        self.exam_subject = ExamSubject.objects.create(
            exam=self.exam,
            subject=self.subject,
            exam_date='2081-01-05',
            full_marks_theory=Decimal('75.00'),
            pass_marks_theory=Decimal('27.00'),
            full_marks_practical=Decimal('25.00'),
            pass_marks_practical=Decimal('9.00')
        )
    
    def test_grading_calculation(self):
        """Test that grading is calculated correctly."""
        result = SubjectResult.objects.create(
            student=self.enrollment,
            exam_subject=self.exam_subject,
            marks_obtained_theory=Decimal('70.00'),
            marks_obtained_practical=Decimal('20.00')
        )
        
        # 90/100 = 90% should be A+
        self.assertEqual(result.subject_grade, 'A+')
        self.assertEqual(result.subject_grade_point, Decimal('4.00'))
    
    def test_unique_constraint(self):
        """Test that unique constraint on student and exam_subject works."""
        SubjectResult.objects.create(
            student=self.enrollment,
            exam_subject=self.exam_subject,
            marks_obtained_theory=Decimal('60.00'),
            marks_obtained_practical=Decimal('20.00')
        )
        
        # Trying to create duplicate should raise error
        with self.assertRaises(Exception):
            SubjectResult.objects.create(
                student=self.enrollment,
                exam_subject=self.exam_subject,
                marks_obtained_theory=Decimal('65.00'),
                marks_obtained_practical=Decimal('22.00')
            )
