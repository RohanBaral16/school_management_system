"""
Quick notification test - Run with: python manage.py shell < quick_test.py
"""
from django.contrib.auth.models import User
from core.notification_models import Notification, NotificationPreference, NotificationType

print("\n🔔 Testing Notification System\n")

# Get or create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
)
print(f"✓ User: {user.username}")

# Create notification preference
pref, created = NotificationPreference.objects.get_or_create(user=user)
print(f"✓ Preference: notifications_enabled={pref.notifications_enabled}")

# Create test notification
notif = Notification.objects.create(
    user=user,
    notification_type=NotificationType.RESULT_PUBLISHED,
    subject='Test Notification',
    message='Your test result is available!',
    context={'exam': 'Test Exam', 'score': 95}
)
print(f"✓ Created notification #{notif.id}")

# Count notifications
total = Notification.objects.count()
unread = Notification.objects.filter(is_read=False).count()
print(f"\n📊 Stats: {total} total, {unread} unread")
print("\n✅ Test completed successfully!\n")
