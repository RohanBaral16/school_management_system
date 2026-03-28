"""
Notification models for the school management system
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class NotificationType(models.TextChoices):
    """Types of notifications that can be sent"""
    RESULT_PUBLISHED = 'result_published', 'Result Published'
    ATTENDANCE_MARKED = 'attendance_marked', 'Attendance Marked'
    EXAM_SCHEDULED = 'exam_scheduled', 'Exam Scheduled'
    ENROLLMENT_CONFIRMED = 'enrollment_confirmed', 'Enrollment Confirmed'
    GRADE_UPDATED = 'grade_updated', 'Grade Updated'
    DOCUMENT_UPLOADED = 'document_uploaded', 'Document Uploaded'
    ANNOUNCEMENT = 'announcement', 'Announcement'
    SYSTEM_ALERT = 'system_alert', 'System Alert'


class Notification(models.Model):
    """
    Stores sent notifications for audit and user reference
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NotificationType.choices)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    # Context data for the notification (stored as JSON)
    context = models.JSONField(default=dict, blank=True)
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.get_full_name()}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])


class NotificationPreference(models.Model):
    """
    Stores user preferences for notifications
    Allows granular control over which notifications to receive
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')
    
    # Global enable/disable
    notifications_enabled = models.BooleanField(default=True)
    
    # Email preferences per notification type
    result_published = models.BooleanField(default=True, help_text="Notify when exam results are published")
    attendance_marked = models.BooleanField(default=True, help_text="Notify when attendance is recorded")
    exam_scheduled = models.BooleanField(default=True, help_text="Notify when exams are scheduled")
    enrollment_confirmed = models.BooleanField(default=True, help_text="Notify on enrollment confirmation")
    grade_updated = models.BooleanField(default=True, help_text="Notify when grades are updated")
    document_uploaded = models.BooleanField(default=False, help_text="Notify when documents are uploaded")
    announcement = models.BooleanField(default=True, help_text="Notify of school announcements")
    system_alert = models.BooleanField(default=True, help_text="Notify of important system alerts")
    
    # Time preferences
    quiet_hours_enabled = models.BooleanField(default=False, help_text="Enable quiet hours (no notifications)")
    quiet_hours_start = models.TimeField(null=True, blank=True, help_text="Quiet hours start time (HH:MM)")
    quiet_hours_end = models.TimeField(null=True, blank=True, help_text="Quiet hours end time (HH:MM)")
    
    # Digest preferences
    digest_enabled = models.BooleanField(default=False, help_text="Receive daily digest instead of instant notifications")
    digest_time = models.TimeField(default='09:00', help_text="Time to send daily digest")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Notification Preferences"
    
    def __str__(self):
        return f"Notification Preferences - {self.user.get_full_name()}"
    
    def is_preference_enabled(self, notification_type):
        """Check if a specific notification type is enabled for this user"""
        if not self.notifications_enabled:
            return False
        
        preference_map = {
            NotificationType.RESULT_PUBLISHED: self.result_published,
            NotificationType.ATTENDANCE_MARKED: self.attendance_marked,
            NotificationType.EXAM_SCHEDULED: self.exam_scheduled,
            NotificationType.ENROLLMENT_CONFIRMED: self.enrollment_confirmed,
            NotificationType.GRADE_UPDATED: self.grade_updated,
            NotificationType.DOCUMENT_UPLOADED: self.document_uploaded,
            NotificationType.ANNOUNCEMENT: self.announcement,
            NotificationType.SYSTEM_ALERT: self.system_alert,
        }
        
        return preference_map.get(notification_type, False)
    
    def should_send_immediately(self):
        """Check if notifications should be sent immediately or as a digest"""
        return not self.digest_enabled
    
    def is_in_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_enabled:
            return False
        
        from datetime import datetime
        current_time = datetime.now().time()
        
        # Handle case where quiet hours span midnight
        if self.quiet_hours_start < self.quiet_hours_end:
            return self.quiet_hours_start <= current_time < self.quiet_hours_end
        else:
            # Quiet hours span midnight
            return current_time >= self.quiet_hours_start or current_time < self.quiet_hours_end
