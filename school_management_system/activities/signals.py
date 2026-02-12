from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, Avg
from .models import SubjectResult, StudentResultSummary

@receiver(post_save, sender=SubjectResult)
def update_result_summary(sender, instance, **kwargs):
    print('!!! Signal triggered')
    # 'instance.student' is now a StudentEnrollment object
    enrollment = instance.student 
    actual_student = enrollment.student # The underlying Student model
    exam = instance.exam_subject.exam
    academic_year = enrollment.academic_year

    # 1. Fetch all subject results for this student for THIS specific exam
    results = SubjectResult.objects.filter(
        student__student=actual_student, 
        exam_subject__exam=exam
    )
    
    # 2. Calculate totals
    # We aggregate both theory and practical from all subjects
    aggregates = results.aggregate(
        total_theory=Sum('marks_obtained_theory'),
        total_practical=Sum('marks_obtained_practical'),
        avg_gpa=Avg('subject_grade_point')
    )
    
    total_marks = (aggregates['total_theory'] or 0) + (aggregates['total_practical'] or 0)
    avg_gpa = aggregates['avg_gpa'] or 0

    # 3. Determine Overall Grade (CDC Logic)
    # If ANY subject has an 'NG', the overall grade is 'NG'
    if results.filter(subject_grade='NG').exists():
        overall = 'NG'
        avg_gpa = 0.00 # Usually, GPA is not awarded if a student fails a subject
    else:
        # Simple mapping based on total average percentage or GPA
        if avg_gpa >= 3.6: overall = 'A+'
        elif avg_gpa >= 3.2: overall = 'A'
        elif avg_gpa >= 2.8: overall = 'B+'
        elif avg_gpa >= 2.4: overall = 'B'
        elif avg_gpa >= 2.0: overall = 'C+'
        elif avg_gpa >= 1.6: overall = 'C'
        else: overall = 'D'

    # 4. Update or Create the Summary
    # We use actual_student so the summary links to the person, not just the enrollment record
    StudentResultSummary.objects.update_or_create(
        student=actual_student,
        exam=exam,
        defaults={
            'academic_year': academic_year,
            'total_marks': total_marks,
            'gpa': avg_gpa,
            'overall_grade': overall,
            # 'percentage' calculation if needed:
            # 'percentage': (total_marks / total_full_marks) * 100 
        }
    )