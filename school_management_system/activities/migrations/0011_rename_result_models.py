# Generated manually for model renaming

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0010_merge_20260210_1130'),
    ]

    operations = [
        # Rename Result to SubjectResult
        migrations.RenameModel(
            old_name='Result',
            new_name='SubjectResult',
        ),
        # Rename ResultSummary to StudentResultSummary
        migrations.RenameModel(
            old_name='ResultSummary',
            new_name='StudentResultSummary',
        ),
        # Rename ResultSummaryResult to StudentMarksheet
        migrations.RenameModel(
            old_name='ResultSummaryResult',
            new_name='StudentMarksheet',
        ),
    ]
