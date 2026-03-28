"""
Test email functionality
Run: python manage.py shell < test_email.py
"""
from django.contrib.auth.models import User
from core.email_service import EmailService

print("\n" + "="*80)
print("📧 EMAIL NOTIFICATION TEST")
print("="*80)

# Get or create test user
user, created = User.objects.get_or_create(
    username='test_email_user',
    defaults={
        'email': 'student@example.com',
        'first_name': 'John',
        'last_name': 'Doe'
    }
)

print(f"\n✓ Test User: {user.get_full_name()} ({user.email})")

# Test 1: Result Published Email
print("\n[TEST 1] Sending Result Published Email...")
context = {
    'student_name': user.get_full_name(),
    'exam_name': 'Mid Term Examination 2026',
    'standard_name': 'Grade 10 - Section A',
    'obtained_marks': 450,
    'total_marks': 500,
    'percentage': 90.0,
    'result_url': 'http://localhost:8000/results/123'
}

result = EmailService.send_notification_email(
    user=user,
    subject='Your Exam Results Are Published!',
    template_name='result_published',
    context=context
)

if result:
    print("✅ Email sent successfully!")
    print("📬 Check the terminal output above for the email content")
else:
    print("❌ Email sending failed")

# Test 2: Attendance Marked Email
print("\n[TEST 2] Sending Attendance Marked Email...")
context = {
    'student_name': user.get_full_name(),
    'date': '2026-02-24',
    'subject_name': 'Mathematics',
    'status': 'PRESENT',
    'remarks': 'On time',
    'attendance_url': 'http://localhost:8000/attendance/view'
}

result = EmailService.send_notification_email(
    user=user,
    subject='Your Attendance Has Been Recorded',
    template_name='attendance_marked',
    context=context
)

if result:
    print("✅ Email sent successfully!")
else:
    print("❌ Email sending failed")

# Test 3: Exam Scheduled Email
print("\n[TEST 3] Sending Exam Scheduled Email...")
context = {
    'student_name': user.get_full_name(),
    'exam_name': 'Final Examination 2026',
    'standard_name': 'Grade 10 - Section A',
    'start_date': '2026-03-15',
    'end_date': '2026-03-25',
    'exam_url': 'http://localhost:8000/exams/456'
}

result = EmailService.send_notification_email(
    user=user,
    subject='New Exam Scheduled',
    template_name='exam_scheduled',
    context=context
)

if result:
    print("✅ Email sent successfully!")
else:
    print("❌ Email sending failed")

print("\n" + "="*80)
print("✅ EMAIL TEST COMPLETED")
print("="*80)
print("\n📝 Note: Check the output above to see the actual email content")
print("   (Currently using console backend - emails print to terminal)\n")
