"""
Notification service for creating and managing notifications
"""

from django.utils import timezone
from .notification_models import Notification, NotificationPreference, NotificationType
from .email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    def get_or_create_preference(user):
        """Get or create notification preference for a user"""
        preference, created = NotificationPreference.objects.get_or_create(user=user)
        return preference
    
    @staticmethod
    def should_send_notification(user, notification_type):
        """Check if notification should be sent to user"""
        preference = NotificationService.get_or_create_preference(user)
        
        # Check if preference is enabled for this type
        if not preference.is_preference_enabled(notification_type):
            return False
        
        # Check if in quiet hours
        if preference.is_in_quiet_hours():
            return False
        
        return True
    
    @staticmethod
    def create_notification(user, notification_type, subject, message, context=None, send_email=True):
        """
        Create a notification and optionally send email
        
        Args:
            user: User instance
            notification_type: NotificationType choice
            subject: Email subject
            message: Notification message
            context: Additional context data (dict)
            send_email: Whether to send email notification
        
        Returns:
            Notification instance
        """
        if context is None:
            context = {}
        
        # Create notification record
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            subject=subject,
            message=message,
            context=context,
            is_sent=False
        )
        
        # Send email if enabled and appropriate
        if send_email and NotificationService.should_send_notification(user, notification_type):
            try:
                # Map notification types to email templates
                template_map = {
                    NotificationType.RESULT_PUBLISHED: 'result_published',
                    NotificationType.ATTENDANCE_MARKED: 'attendance_marked',
                    NotificationType.EXAM_SCHEDULED: 'exam_scheduled',
                    NotificationType.ENROLLMENT_CONFIRMED: 'enrollment_confirmed',
                    NotificationType.GRADE_UPDATED: 'grade_updated',
                    NotificationType.ANNOUNCEMENT: 'announcement',
                    NotificationType.SYSTEM_ALERT: 'system_alert',
                }
                
                template_name = template_map.get(notification_type, 'generic_notification')
                
                # Prepare email context
                email_context = {
                    'notification_message': message,
                    **context
                }
                
                # Send email
                if EmailService.send_notification_email(user, subject, template_name, email_context):
                    notification.is_sent = True
                    notification.sent_at = timezone.now()
                    notification.save(update_fields=['is_sent', 'sent_at'])
                    logger.info(f"Notification {notification.id} sent via email")
                else:
                    logger.warning(f"Failed to send email for notification {notification.id}")
                    
            except Exception as e:
                logger.error(f"Error sending notification {notification.id}: {str(e)}")
        
        return notification
    
    @staticmethod
    def notify_result_published(student_enrollment, exam):
        """
        Notify student when exam results are published
        """
        try:
            user = student_enrollment.student.user
            if not user:
                logger.warning(f"Student {student_enrollment.student.id} has no associated user")
                return None
            
            subject = f"Exam Results Published: {exam.name}"
            message = f"Your results for {exam.name} ({student_enrollment.standard.display_name()}) have been published."
            
            context = {
                'student_name': student_enrollment.student.full_name(),
                'exam_name': exam.display_name() if hasattr(exam, 'display_name') else str(exam),
                'standard': student_enrollment.standard.display_name(),
            }
            
            return NotificationService.create_notification(
                user=user,
                notification_type=NotificationType.RESULT_PUBLISHED,
                subject=subject,
                message=message,
                context=context,
                send_email=True
            )
        except Exception as e:
            logger.error(f"Error notifying result published: {str(e)}")
            return None
    
    @staticmethod
    def notify_attendance_marked(student, date, status, standard):
        """
        Notify student when attendance is marked
        """
        try:
            user = student.user
            if not user:
                logger.warning(f"Student {student.id} has no associated user")
                return None
            
            subject = f"Attendance Recorded: {date}"
            message = f"Your attendance on {date} has been marked as {status.replace('_', ' ').title()}."
            
            context = {
                'student_name': student.full_name(),
                'date': str(date),
                'status': status.replace('_', ' ').title(),
                'standard': standard.display_name(),
            }
            
            return NotificationService.create_notification(
                user=user,
                notification_type=NotificationType.ATTENDANCE_MARKED,
                subject=subject,
                message=message,
                context=context,
                send_email=True
            )
        except Exception as e:
            logger.error(f"Error notifying attendance marked: {str(e)}")
            return None
    
    @staticmethod
    def notify_exam_scheduled(standard, exam):
        """
        Notify all students in a standard when exam is scheduled
        """
        from academics.models import StudentEnrollment
        
        try:
            enrollments = StudentEnrollment.objects.filter(
                standard=standard,
                status='enrolled'
            ).select_related('student', 'student__user', 'academic_year')
            
            notifications = []
            for enrollment in enrollments:
                try:
                    user = enrollment.student.user
                    if not user:
                        continue
                    
                    subject = f"New Exam Scheduled: {exam.name}"
                    message = f"An exam has been scheduled for your class: {exam.name} from {exam.start_date} to {exam.end_date}"
                    
                    context = {
                        'student_name': enrollment.student.full_name(),
                        'exam_name': exam.display_name() if hasattr(exam, 'display_name') else str(exam),
                        'standard': standard.display_name(),
                        'start_date': str(exam.start_date),
                        'end_date': str(exam.end_date),
                    }
                    
                    notification = NotificationService.create_notification(
                        user=user,
                        notification_type=NotificationType.EXAM_SCHEDULED,
                        subject=subject,
                        message=message,
                        context=context,
                        send_email=True
                    )
                    
                    if notification:
                        notifications.append(notification)
                        
                except Exception as e:
                    logger.error(f"Error notifying student {enrollment.student.id}: {str(e)}")
                    continue
            
            return notifications
        except Exception as e:
            logger.error(f"Error notifying exam scheduled: {str(e)}")
            return []
    
    @staticmethod
    def notify_enrollment_confirmed(student, standard, academic_year):
        """
        Notify student when enrollment is confirmed
        """
        try:
            user = student.user
            if not user:
                logger.warning(f"Student {student.id} has no associated user")
                return None
            
            subject = f"Enrollment Confirmed: {academic_year.name}"
            message = f"Your enrollment in {standard.display_name()} for {academic_year.name} has been confirmed."
            
            context = {
                'student_name': student.full_name(),
                'standard': standard.display_name(),
                'academic_year': academic_year.name,
            }
            
            return NotificationService.create_notification(
                user=user,
                notification_type=NotificationType.ENROLLMENT_CONFIRMED,
                subject=subject,
                message=message,
                context=context,
                send_email=True
            )
        except Exception as e:
            logger.error(f"Error notifying enrollment confirmed: {str(e)}")
            return None
