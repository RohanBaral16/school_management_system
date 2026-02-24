"""
Test script for notification system
Run with: python manage.py shell < test_notifications.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management_system.settings')
django.setup()

from django.contrib.auth.models import User
from core.notification_models import Notification, NotificationPreference, NotificationType
from core.notification_service import NotificationService
from core.email_service import EmailService
from academics.models import Standard
from activities.models import Exam, Attendance, SubjectResult
from accounts.models import Student

print("=" * 80)
print("NOTIFICATION SYSTEM TEST")
print("=" * 80)

# Test 1: Check if models are accessible
print("\n[TEST 1] Checking Models...")
try:
    notification_count = Notification.objects.count()
    preference_count = NotificationPreference.objects.count()
    print(f"✓ Notification model: {notification_count} records")
    print(f"✓ NotificationPreference model: {preference_count} records")
except Exception as e:
    print(f"✗ Error accessing models: {e}")

# Test 2: Create a test user and preference
print("\n[TEST 2] Creating Test User and Preferences...")
try:
    user, created = User.objects.get_or_create(
        username='test_student',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Student'
        }
    )
    print(f"✓ User: {user.username} ({'created' if created else 'exists'})")
    
    # Create or get notification preference
    preference, created = NotificationPreference.objects.get_or_create(
        user=user,
        defaults={
            'notifications_enabled': True,
            'result_published': True,
            'attendance_marked': True,
            'exam_scheduled': True,
        }
    )
    print(f"✓ Notification Preference: {'created' if created else 'exists'}")
    print(f"  - Notifications enabled: {preference.notifications_enabled}")
    print(f"  - Result published: {preference.result_published}")
    print(f"  - Attendance marked: {preference.attendance_marked}")
    print(f"  - Exam scheduled: {preference.exam_scheduled}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Test notification creation
print("\n[TEST 3] Creating Test Notification...")
try:
    notification = Notification.objects.create(
        user=user,
        notification_type=NotificationType.RESULT_PUBLISHED,
        subject='Test Result Published',
        message='This is a test notification for result publishing.',
        context={
            'exam_name': 'Mid Term Exam',
            'result_url': 'http://example.com/results/123'
        }
    )
    print(f"✓ Notification created: #{notification.id}")
    print(f"  - Type: {notification.get_notification_type_display()}")
    print(f"  - Subject: {notification.subject}")
    print(f"  - Read: {notification.is_read}")
    print(f"  - Sent: {notification.is_sent}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Test notification preference methods
print("\n[TEST 4] Testing Notification Preference Methods...")
try:
    preference = NotificationPreference.objects.get(user=user)
    
    # Test is_preference_enabled
    result_enabled = preference.is_preference_enabled(NotificationType.RESULT_PUBLISHED)
    attendance_enabled = preference.is_preference_enabled(NotificationType.ATTENDANCE_MARKED)
    
    print(f"✓ is_preference_enabled(RESULT_PUBLISHED): {result_enabled}")
    print(f"✓ is_preference_enabled(ATTENDANCE_MARKED): {attendance_enabled}")
    
    # Test should_send_immediately
    immediate = preference.should_send_immediately()
    print(f"✓ should_send_immediately(): {immediate}")
    
    # Test is_in_quiet_hours
    quiet = preference.is_in_quiet_hours()
    print(f"✓ is_in_quiet_hours(): {quiet}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Test Email Service
print("\n[TEST 5] Testing Email Service...")
try:
    email_service = EmailService()
    
    # Test result published email
    context = {
        'student_name': 'Test Student',
        'exam_name': 'Mid Term Exam',
        'standard_name': 'Grade 10',
        'result_url': 'http://example.com/results/123'
    }
    
    result = email_service.send_result_published_email(
        user_email='test@example.com',
        context=context
    )
    
    if result:
        print(f"✓ Email service working (check console for email output)")
    else:
        print(f"✗ Email service returned False")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Test Notification Service
print("\n[TEST 6] Testing Notification Service...")
try:
    # Get a student for testing
    students = Student.objects.all()[:1]
    if students:
        student = students[0]
        
        # Create a test notification using NotificationService
        NotificationService.create_notification(
            user=user,
            notification_type=NotificationType.ANNOUNCEMENT,
            subject='Test Announcement',
            message='This is a test announcement from NotificationService.',
            context={'test': True},
            send_email=False  # Don't send actual email
        )
        print(f"✓ NotificationService.create_notification() working")
    else:
        print(f"⚠ No students found to test with")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 7: Check signal handlers exist
print("\n[TEST 7] Checking Signal Handlers...")
try:
    from django.db.models import signals
    from activities.models import Exam, Attendance
    
    # Check if signals are connected
    exam_receivers = signals.post_save._live_receivers(Exam)
    attendance_receivers = signals.post_save._live_receivers(Attendance)
    
    print(f"✓ Exam post_save signals: {len(exam_receivers)} receiver(s)")
    print(f"✓ Attendance post_save signals: {len(attendance_receivers)} receiver(s)")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 8: Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
total_notifications = Notification.objects.count()
total_preferences = NotificationPreference.objects.count()
unread_notifications = Notification.objects.filter(is_read=False).count()

print(f"Total Notifications: {total_notifications}")
print(f"Unread Notifications: {unread_notifications}")
print(f"Total Preferences: {total_preferences}")
print(f"\nNotifications by Type:")
for choice in NotificationType.choices:
    count = Notification.objects.filter(notification_type=choice[0]).count()
    if count > 0:
        print(f"  - {choice[1]}: {count}")

print("\n✓ All tests completed!")
print("=" * 80)
