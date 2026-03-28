"""
Email service for sending notifications
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def send_notification_email(user, subject, template_name, context):
        """
        Send email notification to a user
        
        Args:
            user: User instance
            subject: Email subject
            template_name: Name of template file (without extension)
            context: Context data for template rendering
        """
        if not user.email:
            logger.warning(f"User {user.id} has no email address")
            return False
        
        try:
            # Add user to context
            context['user'] = user
            context['site_name'] = 'School Management System'
            
            # Render HTML and text versions
            html_message = render_to_string(f'emails/{template_name}.html', context)
            text_message = render_to_string(f'emails/{template_name}.txt', context)
            
            # Create email with both versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            
            # Send email
            result = email.send(fail_silently=False)
            
            if result:
                logger.info(f"Email sent successfully to {user.email}: {subject}")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_result_published_notification(student_enrollment, exam):
        """Send email when results are published"""
        context = {
            'student_name': student_enrollment.student.full_name(),
            'exam_name': exam.display_name() if hasattr(exam, 'display_name') else str(exam),
            'standard': student_enrollment.standard.display_name(),
            'results_url': f'{settings.FRONTEND_URL}/results/{exam.id}' if hasattr(settings, 'FRONTEND_URL') else '',
        }
        
        return EmailService.send_notification_email(
            user=student_enrollment.student.user,
            subject=f"Exam Results Published: {exam.name}",
            template_name='result_published',
            context=context
        )
    
    @staticmethod
    def send_attendance_marked_notification(student, date, status, standard):
        """Send email when attendance is marked"""
        context = {
            'student_name': student.full_name(),
            'date': date,
            'status': status.replace('_', ' ').title(),
            'standard': standard.display_name(),
        }
        
        return EmailService.send_notification_email(
            user=student.user,
            subject=f"Attendance Recorded: {date}",
            template_name='attendance_marked',
            context=context
        )
    
    @staticmethod
    def send_exam_scheduled_notification(standard, exam):
        """Send email when exam is scheduled"""
        # Get all students enrolled in this standard
        from academics.models import StudentEnrollment
        
        enrollments = StudentEnrollment.objects.filter(
            standard=standard,
            status='enrolled'
        ).select_related('student', 'student__user')
        
        for enrollment in enrollments:
            context = {
                'student_name': enrollment.student.full_name(),
                'exam_name': exam.display_name() if hasattr(exam, 'display_name') else str(exam),
                'standard': standard.display_name(),
                'start_date': exam.start_date,
                'end_date': exam.end_date,
            }
            
            EmailService.send_notification_email(
                user=enrollment.student.user,
                subject=f"New Exam Scheduled: {exam.name}",
                template_name='exam_scheduled',
                context=context
            )
    
    @staticmethod
    def send_enrollment_confirmed_notification(student, standard, academic_year):
        """Send email when enrollment is confirmed"""
        context = {
            'student_name': student.full_name(),
            'standard': standard.display_name(),
            'academic_year': academic_year.name,
        }
        
        return EmailService.send_notification_email(
            user=student.user,
            subject=f"Enrollment Confirmed: {academic_year.name}",
            template_name='enrollment_confirmed',
            context=context
        )
    
    @staticmethod
    def send_grade_updated_notification(student_enrollment, subject, grade):
        """Send email when grade is updated"""
        context = {
            'student_name': student_enrollment.student.full_name(),
            'subject': subject.name if hasattr(subject, 'name') else str(subject),
            'grade': grade,
            'standard': student_enrollment.standard.display_name(),
        }
        
        return EmailService.send_notification_email(
            user=student_enrollment.student.user,
            subject=f"Grade Updated: {subject}",
            template_name='grade_updated',
            context=context
        )
