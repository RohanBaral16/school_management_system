"""
ViewSets for notification management API
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from core.notification_models import Notification, NotificationPreference
from core.notification_serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    NotificationBulkActionSerializer,
    NotificationSettingsSerializer
)
from core.notification_service import NotificationService


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing user notifications
    - List all notifications for the authenticated user
    - Mark notifications as read/unread
    - Delete notifications
    - Bulk actions on multiple notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only notifications for the current user"""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        """Mark a notification as unread"""
        notification = self.get_object()
        notification.is_read = False
        notification.save(update_fields=['is_read'])
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all unread notifications as read"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({
            'message': f'{count} notifications marked as read',
            'count': count
        })
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk action on multiple notifications"""
        serializer = NotificationBulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data['notification_ids']
        action_type = serializer.validated_data['action']
        
        # Get notifications for current user only
        notifications = Notification.objects.filter(
            user=request.user,
            id__in=notification_ids
        )
        
        if action_type == 'mark_read':
            count = notifications.update(is_read=True)
            return Response({
                'message': f'{count} notifications marked as read',
                'count': count
            })
        
        elif action_type == 'mark_unread':
            count = notifications.update(is_read=False)
            return Response({
                'message': f'{count} notifications marked as unread',
                'count': count
            })
        
        elif action_type == 'delete':
            count = notifications.count()
            notifications.delete()
            return Response({
                'message': f'{count} notifications deleted',
                'count': count
            })
        
        return Response(
            {'error': 'Invalid action'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response({
            'count': notifications.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def settings(self, request):
        """Get notification settings and statistics"""
        serializer = NotificationSettingsSerializer(request.user)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ViewSet):
    """
    ViewSet for managing notification preferences
    - Get current user's notification preferences
    - Update notification preferences
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get current user's notification preferences"""
        preference = NotificationService.get_or_create_preference(request.user)
        serializer = NotificationPreferenceSerializer(preference)
        return Response(serializer.data)
    
    def create(self, request):
        """Update notification preferences"""
        preference = NotificationService.get_or_create_preference(request.user)
        serializer = NotificationPreferenceSerializer(
            preference,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def get_preferences(self, request):
        """Get current user's notification preferences"""
        preference = NotificationService.get_or_create_preference(request.user)
        serializer = NotificationPreferenceSerializer(preference)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_preferences(self, request):
        """Update notification preferences"""
        preference = NotificationService.get_or_create_preference(request.user)
        serializer = NotificationPreferenceSerializer(
            preference,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Notification preferences updated successfully',
            'preferences': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def reset_to_defaults(self, request):
        """Reset all notification preferences to defaults"""
        preference = NotificationService.get_or_create_preference(request.user)
        
        # Set default values
        preference.notifications_enabled = True
        preference.result_published = True
        preference.attendance_marked = True
        preference.exam_scheduled = True
        preference.enrollment_confirmed = True
        preference.grade_updated = True
        preference.document_uploaded = False
        preference.announcement = True
        preference.system_alert = True
        preference.quiet_hours_enabled = False
        preference.digest_enabled = False
        preference.save()
        
        serializer = NotificationPreferenceSerializer(preference)
        return Response({
            'message': 'Notification preferences reset to defaults',
            'preferences': serializer.data
        })
