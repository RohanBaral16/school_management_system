"""
Bulk Operations Module
Handles CSV imports and Excel exports for the school management system.
"""

import io
import csv
from datetime import datetime
from decimal import Decimal

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.contrib.auth.models import User
from django.db import transaction

from accounts.models import Student
from academics.models import AcademicYear, Standard, StudentEnrollment
from activities.models import Attendance, SubjectResult


class BulkImportError(Exception):
    """Custom exception for bulk import errors"""
    pass


class CSVImporter:
    """Handles CSV imports for students and enrollments"""
    
    @staticmethod
    def import_students_csv(csv_file):
        """
        Import students from CSV file.
        Expected columns: first_name, middle_name, last_name, gender, email, phone, 
                         date_of_birth, admission_number
        """
        errors = []
        created_count = 0
        updated_count = 0
        
        try:
            df = pd.read_csv(csv_file, dtype={'phone': str, 'email': str})
        except Exception as e:
            raise BulkImportError(f"Failed to read CSV file: {str(e)}")
        
        required_columns = {
            'first_name', 'last_name', 'gender', 'date_of_birth', 'admission_number'
        }
        
        if not required_columns.issubset(set(df.columns)):
            missing = required_columns - set(df.columns)
            raise BulkImportError(f"Missing required columns: {', '.join(missing)}")
        
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    row_num = idx + 2  # +2 for header and 1-based indexing
                    
                    admission_number = str(row['admission_number']).strip()
                    if not admission_number:
                        errors.append(f"Row {row_num}: admission_number is required")
                        continue
                    
                    # Parse date
                    try:
                        dob = pd.to_datetime(row['date_of_birth']).date()
                    except:
                        errors.append(f"Row {row_num}: Invalid date format for date_of_birth")
                        continue
                    
                    # Prepare data
                    data = {
                        'first_name': str(row['first_name']).strip(),
                        'last_name': str(row['last_name']).strip(),
                        'middle_name': str(row.get('middle_name', '')).strip() or '',
                        'gender': str(row['gender']).strip().lower(),
                        'email': str(row.get('email', '')).strip() or None,
                        'phone': str(row.get('phone', '')).strip() or None,
                        'date_of_birth': dob,
                        'admission_number': admission_number,
                    }
                    
                    # Validate gender
                    valid_genders = ['male', 'female', 'other']
                    if data['gender'] not in valid_genders:
                        errors.append(f"Row {row_num}: Invalid gender '{data['gender']}'")
                        continue
                    
                    # Get or create student
                    student, created = Student.objects.update_or_create(
                        admission_number=admission_number,
                        defaults=data
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            'created': created_count,
            'updated': updated_count,
            'errors': errors,
        }
    
    @staticmethod
    def import_enrollments_csv(csv_file):
        """
        Import student enrollments from CSV file.
        Expected columns: admission_number, standard_name, academic_year_name, roll_number, status
        """
        errors = []
        created_count = 0
        updated_count = 0
        
        try:
            df = pd.read_csv(csv_file, dtype={'roll_number': str})
        except Exception as e:
            raise BulkImportError(f"Failed to read CSV file: {str(e)}")
        
        required_columns = {
            'admission_number', 'standard_name', 'academic_year_name', 'roll_number'
        }
        
        if not required_columns.issubset(set(df.columns)):
            missing = required_columns - set(df.columns)
            raise BulkImportError(f"Missing required columns: {', '.join(missing)}")
        
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    row_num = idx + 2  # +2 for header and 1-based indexing
                    
                    admission_number = str(row['admission_number']).strip()
                    standard_name = str(row['standard_name']).strip()
                    academic_year_name = str(row['academic_year_name']).strip()
                    roll_number = str(row['roll_number']).strip()
                    status = str(row.get('status', 'enrolled')).strip().lower()
                    
                    # Get student
                    try:
                        student = Student.objects.get(admission_number=admission_number)
                    except Student.DoesNotExist:
                        errors.append(f"Row {row_num}: Student with admission_number '{admission_number}' not found")
                        continue
                    
                    # Get standard
                    try:
                        standard = Standard.objects.get(name=standard_name)
                    except Standard.DoesNotExist:
                        errors.append(f"Row {row_num}: Standard '{standard_name}' not found")
                        continue
                    
                    # Get academic year
                    try:
                        academic_year = AcademicYear.objects.get(name=academic_year_name)
                    except AcademicYear.DoesNotExist:
                        errors.append(f"Row {row_num}: Academic year '{academic_year_name}' not found")
                        continue
                    
                    # Validate status
                    valid_statuses = ['enrolled', 'dropped_out', 'transferred', 'promoted', 'failed', 'graduated', 'withdrawn']
                    if status not in valid_statuses:
                        status = 'enrolled'
                    
                    # Create or update enrollment
                    enrollment, created = StudentEnrollment.objects.update_or_create(
                        student=student,
                        academic_year=academic_year,
                        standard=standard,
                        defaults={
                            'roll_number': roll_number,
                            'status': status,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            'created': created_count,
            'updated': updated_count,
            'errors': errors,
        }


class ExcelExporter:
    """Handles Excel exports for results and attendance"""
    
    # Excel styling
    HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
    BORDER = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    @staticmethod
    def _style_header(worksheet, num_columns):
        """Apply header styling"""
        for col in range(1, num_columns + 1):
            cell = worksheet.cell(row=1, column=col)
            cell.fill = ExcelExporter.HEADER_FILL
            cell.font = ExcelExporter.HEADER_FONT
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = ExcelExporter.BORDER
    
    @staticmethod
    def _style_data_row(worksheet, row_num, num_columns):
        """Apply data row styling"""
        for col in range(1, num_columns + 1):
            cell = worksheet.cell(row=row_num, column=col)
            cell.border = ExcelExporter.BORDER
            cell.alignment = Alignment(horizontal='left', vertical='center')
    
    @staticmethod
    def export_results_to_excel(standard=None, exam=None, academic_year=None):
        """
        Export subject results to Excel.
        Can filter by standard, exam, or academic year.
        """
        from activities.models import SubjectResult
        
        # Build query
        queryset = SubjectResult.objects.select_related(
            'student', 'student__student', 'student__standard', 
            'exam_subject', 'exam_subject__exam', 'exam_subject__subject'
        )
        
        if standard:
            queryset = queryset.filter(student__standard=standard)
        if exam:
            queryset = queryset.filter(exam_subject__exam=exam)
        if academic_year:
            queryset = queryset.filter(student__academic_year=academic_year)
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Results"
        
        # Headers
        headers = [
            'Student Name',
            'Admission Number',
            'Standard',
            'Academic Year',
            'Exam',
            'Subject',
            'Theory Marks',
            'Practical Marks',
            'Total Marks',
            'Grade',
            'GPA'
        ]
        
        ws.append(headers)
        ExcelExporter._style_header(ws, len(headers))
        
        # Add data
        for row_num, result in enumerate(queryset, start=2):
            theory = float(result.marks_obtained_theory or 0)
            practical = float(result.marks_obtained_practical or 0)
            total = theory + practical
            
            row_data = [
                result.student.student.full_name(),
                result.student.student.admission_number,
                result.student.standard.name,
                result.student.academic_year.name,
                result.exam_subject.exam.name,
                result.exam_subject.subject.name if result.exam_subject.subject else 'N/A',
                theory,
                practical,
                total,
                result.subject_grade,
                float(result.subject_grade_point),
            ]
            
            ws.append(row_data)
            ExcelExporter._style_data_row(ws, row_num, len(headers))
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 20
        ws.column_dimensions['F'].width = 18
        
        # Convert to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
    
    @staticmethod
    def export_attendance_to_excel(standard=None, academic_year=None, start_date=None, end_date=None):
        """
        Export attendance records to Excel.
        Can filter by standard, academic year, and date range.
        """
        # Build query
        queryset = Attendance.objects.select_related(
            'student', 'standard', 'subject', 'academic_year'
        )
        
        if standard:
            queryset = queryset.filter(standard=standard)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Attendance"
        
        # Headers
        headers = [
            'Date',
            'Student Name',
            'Admission Number',
            'Standard',
            'Subject',
            'Status',
            'Recorded By',
            'Academic Year',
            'Remarks'
        ]
        
        ws.append(headers)
        ExcelExporter._style_header(ws, len(headers))
        
        # Add data
        for row_num, record in enumerate(queryset, start=2):
            row_data = [
                str(record.date),
                record.student.full_name(),
                record.student.admission_number,
                record.standard.name,
                record.subject.name if record.subject else 'All',
                record.status.replace('_', ' ').title(),
                record.recorded_by.full_name() if record.recorded_by else 'N/A',
                record.academic_year.name,
                record.remarks or '',
            ]
            
            ws.append(row_data)
            ExcelExporter._style_data_row(ws, row_num, len(headers))
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 18
        ws.column_dimensions['F'].width = 12
        
        # Convert to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
