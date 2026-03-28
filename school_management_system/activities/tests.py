from django.test import TestCase
from decimal import Decimal
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from activities.models import SubjectResult, StudentResultSummary, Exam, ExamSubject
from academics.models import (
    StudentEnrollment, Standard, Subject, AcademicYear
)
from accounts.models import Student

NEPALI_DATE_STR = "2081-01-01"


class StudentResultSummaryTestCase(TestCase):
    """Test cases for StudentResultSummary model after M2M refactoring."""
    
    def setUp(self):
        """Set up test data."""
        # Create academic year
        self.academic_year = AcademicYear.objects.create(
            name='2081',
            is_current=True
        )
        
        # Create standard
        self.standard = Standard.objects.create(
            name='10',
            section='A'
        )
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH',
            standard=self.standard,
            credit_hours=Decimal('3.0'),
            curriculum_version='2077/2078'
        )
        
        # Create student
        self.student_user = Student.objects.create(
            first_name='Test',
            last_name='Student',
            email='student1@test.com',
            admission_number='ADM001',
            gender='male'
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
            start_date=NEPALI_DATE_STR,
            end_date=NEPALI_DATE_STR,
            is_published=False
        )
        
        # Create exam subject
        self.exam_subject = ExamSubject.objects.create(
            exam=self.exam,
            subject=self.subject,
            exam_date=NEPALI_DATE_STR,
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
        
        # Create or update result summary (signals may already create one)
        self.summary, _ = StudentResultSummary.objects.update_or_create(
            student=self.enrollment,
            exam=self.exam,
            defaults={
                'academic_year': self.academic_year,
                'total_marks': Decimal('80.00'),
                'percentage': Decimal('80.00'),
                'gpa': Decimal('3.60'),
                'overall_grade': 'A',
                'rank': 1,
            },
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
            code='SCI',
            standard=self.standard,
            credit_hours=Decimal('3.0'),
            curriculum_version='2077/2078'
        )
        
        exam_subject2 = ExamSubject.objects.create(
            exam=self.exam,
            subject=subject2,
            exam_date=NEPALI_DATE_STR,
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
        # Check that the attribute doesn't exist on the instance
        self.assertFalse(hasattr(self.summary, 'results'))
        
        # Check at the model meta level that the field has been removed
        field_names = [f.name for f in StudentResultSummary._meta.get_fields()]
        self.assertNotIn('results', field_names)
        
        # But the method should exist
        self.assertTrue(hasattr(self.summary, 'get_subject_results'))


class SubjectResultTestCase(TestCase):
    """Test cases for SubjectResult model."""
    
    def setUp(self):
        """Set up test data."""
        self.academic_year = AcademicYear.objects.create(
            name='2081',
            is_current=True
        )
        
        self.standard = Standard.objects.create(
            name='10',
            section='A'
        )
        
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH',
            standard=self.standard,
            credit_hours=Decimal('3.0'),
            curriculum_version='2077/2078'
        )
        
        self.student_user = Student.objects.create(
            first_name='Test',
            last_name='Student2',
            email='student2@test.com',
            admission_number='ADM002',
            gender='male'
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
            start_date=NEPALI_DATE_STR,
            end_date=NEPALI_DATE_STR,
            is_published=False
        )
        
        self.exam_subject = ExamSubject.objects.create(
            exam=self.exam,
            subject=self.subject,
            exam_date=NEPALI_DATE_STR,
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
        with self.assertRaises(ValidationError):
            SubjectResult.objects.create(
                student=self.enrollment,
                exam_subject=self.exam_subject,
                marks_obtained_theory=Decimal('65.00'),
                marks_obtained_practical=Decimal('22.00')
            )
