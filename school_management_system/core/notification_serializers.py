"""
Serializers for notification endpoints
"""

from rest_framework import serializers
from core.notification_models import Notification, NotificationPreference, NotificationType


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display', 'subject',
            'message', 'context', 'is_read', 'is_sent', 'sent_at',
            'user_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_sent', 'sent_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'notifications_enabled', 'result_published', 'attendance_marked',
            'exam_scheduled', 'enrollment_confirmed', 'grade_updated',
            'document_uploaded', 'announcement', 'system_alert',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end',
            'digest_enabled', 'digest_time', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationBulkActionSerializer(serializers.Serializer):
    """Serializer for bulk notification actions"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of notification IDs to perform action on"
    )
    action = serializers.ChoiceField(
        choices=['mark_read', 'mark_unread', 'delete'],
        help_text="Action to perform on notifications"
    )


class NotificationSettingsSerializer(serializers.Serializer):
    """Serializer for getting notification settings"""
    unread_count = serializers.SerializerMethodField()
    unsent_count = serializers.SerializerMethodField()
    preferences = NotificationPreferenceSerializer(source='notification_preference', read_only=True)
    
    def get_unread_count(self, obj):
        """Count unread notifications"""
        return obj.notifications.filter(is_read=False).count()
    
    def get_unsent_count(self, obj):
        """Count unsent notifications"""
        return obj.notifications.filter(is_sent=False).count()
