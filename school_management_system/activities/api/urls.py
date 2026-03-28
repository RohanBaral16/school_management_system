"""
URL configuration for Activities API.
Exports viewsets for main router in urls.py
"""

from .views import (
    ExamViewSet,
    ExamSubjectViewSet,
    SubjectResultViewSet,
    StudentResultSummaryViewSet,
    AttendanceViewSet,
    SubjectResultReadOnlyViewSet,
    ExamSubjectReadOnlyViewSet,
    StudentResultSummaryReadOnlyViewSet,
    ExamReadOnlyViewSet,
    AttendanceReadOnlyViewSet,
    MarksheetDetailReadOnlyViewSet,
)

# Export viewsets for main router
api_viewsets = [
    ('exams', ExamViewSet, 'exams'),
    ('exam-subjects', ExamSubjectViewSet, 'exam-subjects'),
    ('subject-results', SubjectResultViewSet, 'subject-results'),
    ('result-summaries', StudentResultSummaryViewSet, 'result-summaries'),
    ('attendance', AttendanceViewSet, 'attendance'),
    ('subjectresults-readonly', SubjectResultReadOnlyViewSet, 'subjectresults-readonly'),
    ('examsubject-readonly', ExamSubjectReadOnlyViewSet, 'examsubject-readonly'),
    ('resultsummary-readonly', StudentResultSummaryReadOnlyViewSet, 'resultsummary-readonly'),
    ('exam-readonly', ExamReadOnlyViewSet, 'exam-readonly'),
    ('attendance-readonly', AttendanceReadOnlyViewSet, 'attendance-readonly'),
    ('marksheet-readonly', MarksheetDetailReadOnlyViewSet, 'marksheet-readonly'),
]

urlpatterns = []
