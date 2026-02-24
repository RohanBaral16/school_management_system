from django.contrib import admin
from .notification_models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing notifications
    """
    list_display = ['id', 'user', 'notification_type', 'subject', 'is_read', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_sent', 'created_at']
    search_fields = ['user__username', 'user__email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at', 'sent_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'notification_type', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'is_sent', 'sent_at')
        }),
        ('Context Data', {
            'fields': ('context',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset with related user data
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing notification preferences
    """
    list_display = ['id', 'user', 'notifications_enabled']
    list_filter = ['notifications_enabled', 'quiet_hours_enabled', 'digest_enabled']
    search_fields = ['user__username', 'user__email']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Global Settings', {
            'fields': ('notifications_enabled',)
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'),
            'description': 'Notifications will not be sent during quiet hours (24-hour format, e.g., 22:00 to 08:00)'
        }),
        ('Digest Settings', {
            'fields': ('digest_enabled', 'digest_time'),
            'description': 'Batch notifications into periodic digests instead of sending immediately'
        }),
        ('Event-Specific Preferences', {
            'fields': (
                'result_published',
                'attendance_marked',
                'exam_scheduled',
                'enrollment_confirmed',
                'grade_updated',
                'document_uploaded',
                'announcement',
                'system_alert',
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """
        Optimize queryset with related user data
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')
