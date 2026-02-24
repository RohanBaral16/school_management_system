"""
Simple email test
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management_system.settings')
django.setup()

from django.contrib.auth.models import User
from core.email_service import EmailService

print("\n" + "="*80)
print("📧 EMAIL SYSTEM TEST")
print("="*80)

# Create test user
user, created = User.objects.get_or_create(
    username='email_test',
    defaults={
        'email': 'student@school.com',
        'first_name': 'Test',
        'last_name': 'Student'
    }
)

print(f"\n✓ User: {user.get_full_name()} <{user.email}>")

# Test Email
print("\n📨 Sending test email...")
print("-" * 80)

context = {
    'student_name': 'Test Student',
    'exam_name': 'Mid Term Exam 2026',
    'standard_name': 'Grade 10',
    'obtained_marks': 450,
    'total_marks': 500,
    'percentage': 90.0,
    'result_url': 'http://localhost:8000/results/123'
}

success = EmailService.send_notification_email(
    user=user,
    subject='Your Exam Results Are Available',
    template_name='result_published',
    context=context
)

print("-" * 80)
if success:
    print("\n✅ EMAIL SENT SUCCESSFULLY!")
    print("📬 Check console output above for email content")
else:
    print("\n❌ Email failed to send")

print("\n" + "="*80 + "\n")
