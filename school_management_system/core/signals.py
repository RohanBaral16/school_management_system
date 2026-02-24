"""
Django signals for sending notifications on key events
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction

from activities.models import Exam, Attendance
from accounts.models import Student
from academics.models import StudentEnrollment
from core.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Exam)
def notify_exam_scheduled(sender, instance, created, **kwargs):
    """
    Signal handler to notify students when a new exam is scheduled
    """
    if created:
        # Only notify when a new exam is created
        try:
            # Get all standards that have exam subjects for this exam
            from activities.models import ExamSubject
            exam_subjects = instance.exam_subjects.all()
            
            # Get unique standards
            standards = set()
            for exam_subject in exam_subjects:
                if exam_subject.standard:
                    standards.add(exam_subject.standard)
            
            # Notify students in each standard
            for standard in standards:
                NotificationService.notify_exam_scheduled(standard, instance)
                
        except Exception as e:
            logger.error(f"Error in notify_exam_scheduled signal: {str(e)}")


@receiver(post_save, sender=Attendance)
def notify_attendance_recorded(sender, instance, created, **kwargs):
    """
    Signal handler to notify student when attendance is recorded
    """
    if created:
        # Notify student of attendance
        try:
            NotificationService.notify_attendance_marked(
                student=instance.student,
                date=instance.date,
                status=instance.status,
                standard=instance.standard
            )
        except Exception as e:
            logger.error(f"Error in notify_attendance_recorded signal: {str(e)}")


def notify_result_published(enrollment, exam):
    """
    Utility function to notify about result publication
    Called from admin or API when results are published
    """
    try:
        NotificationService.notify_result_published(enrollment, exam)
    except Exception as e:
        logger.error(f"Error notifying result published: {str(e)}")


def notify_enrollment_confirmed(student, standard, academic_year):
    """
    Utility function to notify about enrollment confirmation
    Called from API when enrollment is created
    """
    try:
        NotificationService.notify_enrollment_confirmed(student, standard, academic_year)
    except Exception as e:
        logger.error(f"Error notifying enrollment confirmed: {str(e)}")


# Register receivers in apps.py ready() method
