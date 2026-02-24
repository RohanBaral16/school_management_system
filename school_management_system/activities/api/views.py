from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Sum, Q

from ..models import SubjectResult, ExamSubject, StudentResultSummary, Attendance, Exam
from .serializers import (
    SubjectResultSerializer,
    SubjectResultWriteSerializer,
    ExamSubjectSerializer,
    ExamSubjectWriteSerializer,
    StudentResultSummarySerializer,
    StudentResultSummaryWriteSerializer,
    ExamSerializer,
    ExamWriteSerializer,
    AttendanceSerializer,
    AttendanceWriteSerializer,
    MarksheetDetailSerializer,
)
from .filters import SubjectResultFilter, ExamSubjectFilter, StudentResultSummaryFilter, MarksheetDetailFilter
from .permissions import IsAdminOrTeacher


def _update_result_summary(student, exam):
    results = SubjectResult.objects.filter(
        student=student,
        exam_subject__exam=exam,
    )

    if not results.exists():
        StudentResultSummary.objects.filter(student=student, exam=exam).delete()
        return

    aggregates = results.aggregate(
        theory=Sum('marks_obtained_theory'),
        practical=Sum('marks_obtained_practical'),
        avg_gpa=Avg('subject_grade_point'),
    )
    total_marks = (aggregates['theory'] or 0) + (aggregates['practical'] or 0)
    avg_gpa = aggregates['avg_gpa'] or 0
    has_ng = results.filter(subject_grade='NG').exists()

    StudentResultSummary.objects.update_or_create(
        student=student,
        exam=exam,
        defaults={
            'academic_year': exam.academic_year,
            'total_marks': total_marks,
            'gpa': 0 if has_ng else avg_gpa,
            'overall_grade': 'NG' if has_ng else 'PASS',
        },
    )


class ExamViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    queryset = Exam.objects.select_related('academic_year')
    ordering_fields = ['id', 'title', 'exam_date', 'academic_year']
    ordering = ['-exam_date']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ExamWriteSerializer
        return ExamSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        from accounts.models import Student, Teacher
        from academics.models import StudentEnrollment
        user = self.request.user
        
        # Admin/Superuser can see all exams
        if user.is_staff or user.is_superuser:
            return Exam.objects.select_related('academic_year')
        
        # Teachers can see all exams
        try:
            teacher = Teacher.objects.get(user=user)
            return Exam.objects.select_related('academic_year')
        except Teacher.DoesNotExist:
            pass
        
        # Students can see exams for their enrolled academic years
        try:
            student = Student.objects.get(user=user)
            enrolled_years = StudentEnrollment.objects.filter(student=student).values_list('academic_year', flat=True)
            return Exam.objects.filter(academic_year__in=enrolled_years).select_related('academic_year')
        except Student.DoesNotExist:
            pass
        
        return Exam.objects.none()


class AttendanceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    queryset = Attendance.objects.select_related(
        'student',
        'standard',
        'subject__standard',
        'recorded_by',
        'academic_year',
    )
    ordering_fields = ['id', 'student', 'date', 'status', 'standard']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AttendanceWriteSerializer
        return AttendanceSerializer


class ExamSubjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = ExamSubjectFilter
    queryset = ExamSubject.objects.select_related(
        'exam',
        'exam__academic_year',
        'subject',
        'subject__standard',
        'standard',
    )
    ordering_fields = ['id', 'exam', 'subject', 'standard', 'total_marks']
    ordering = ['exam', 'subject']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ExamSubjectWriteSerializer
        return ExamSubjectSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        from accounts.models import Student, Teacher
        from academics.models import StudentEnrollment, TeacherSubject, ClassTeacher
        user = self.request.user
        
        # Admin/Superuser can see all exam subjects
        if user.is_staff or user.is_superuser:
            return ExamSubject.objects.select_related(
                'exam', 'exam__academic_year', 'subject', 'subject__standard', 'standard'
            )
        
        # Teachers can see exam subjects for their assigned subjects/standards
        try:
            teacher = Teacher.objects.get(user=user)
            teacher_subjects = TeacherSubject.objects.filter(teacher=teacher).values_list('subject', flat=True)
            teacher_standards = ClassTeacher.objects.filter(teacher=teacher).values_list('standard', flat=True)
            return ExamSubject.objects.filter(
                Q(subject__in=teacher_subjects) | Q(standard__in=teacher_standards)
            ).select_related('exam', 'exam__academic_year', 'subject', 'subject__standard', 'standard')
        except Teacher.DoesNotExist:
            pass
        
        # Students can see exam subjects for their enrolled standards
        try:
            student = Student.objects.get(user=user)
            enrolled_standards = StudentEnrollment.objects.filter(student=student).values_list('standard', flat=True)
            return ExamSubject.objects.filter(standard__in=enrolled_standards).select_related(
                'exam', 'exam__academic_year', 'subject', 'subject__standard', 'standard'
            )
        except Student.DoesNotExist:
            pass
        
        return ExamSubject.objects.none()


class SubjectResultViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = SubjectResultFilter
    ordering_fields = ['id', 'student', 'exam_subject', 'marks_obtained_theory', 'marks_obtained_practical']
    ordering = ['-exam_subject__exam']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubjectResultWriteSerializer
        return SubjectResultSerializer

    def get_queryset(self):
        """Filter queryset based on user role."""
        from accounts.models import Student, Teacher
        from academics.models import StudentEnrollment, TeacherSubject, ClassTeacher
        user = self.request.user
        
        # Admin/Superuser can see all results
        if user.is_staff or user.is_superuser:
            return SubjectResult.objects.select_related(
                'exam_subject__exam__academic_year',
                'exam_subject__subject__standard',
                'exam_subject__standard',
                'student__student',
                'student__standard',
                'student__academic_year',
            )
        
        # Teachers can see results for their assigned students
        try:
            teacher = Teacher.objects.get(user=user)
            class_standards = ClassTeacher.objects.filter(teacher=teacher).values_list('standard', flat=True)
            subject_standards = TeacherSubject.objects.filter(teacher=teacher).values_list('subject__standard', flat=True)
            all_standards = set(list(class_standards) + list(subject_standards))
            student_enrollments = StudentEnrollment.objects.filter(standard__in=all_standards).values_list('id', flat=True)
            return SubjectResult.objects.filter(student__in=student_enrollments).select_related(
                'exam_subject__exam__academic_year',
                'exam_subject__subject__standard',
                'exam_subject__standard',
                'student__student',
                'student__standard',
                'student__academic_year',
            )
        except Teacher.DoesNotExist:
            pass
        
        # Students can see only their own results
        try:
            student = Student.objects.get(user=user)
            student_enrollments = StudentEnrollment.objects.filter(student=student).values_list('id', flat=True)
            return SubjectResult.objects.filter(student__in=student_enrollments).select_related(
                'exam_subject__exam__academic_year',
                'exam_subject__subject__standard',
                'exam_subject__standard',
                'student__student',
                'student__standard',
                'student__academic_year',
            )
        except Student.DoesNotExist:
            pass
        
        return SubjectResult.objects.none()

    def perform_create(self, serializer):
        result = serializer.save()
        _update_result_summary(result.student, result.exam_subject.exam)

    def perform_update(self, serializer):
        result = serializer.save()
        _update_result_summary(result.student, result.exam_subject.exam)

    def perform_destroy(self, instance):
        student = instance.student
        exam = instance.exam_subject.exam
        instance.delete()
        _update_result_summary(student, exam)


class StudentResultSummaryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    filterset_class = StudentResultSummaryFilter
    queryset = StudentResultSummary.objects.select_related(
        'student__student',
        'student__standard',
        'student__academic_year',
        'exam__academic_year',
        'academic_year',
    )
    ordering_fields = ['id', 'student', 'exam', 'total_marks', 'gpa', 'overall_grade']
    ordering = ['-exam']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudentResultSummaryWriteSerializer
        return StudentResultSummarySerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        from accounts.models import Student, Teacher
        from academics.models import StudentEnrollment, TeacherSubject, ClassTeacher
        user = self.request.user
        
        # Admin/Superuser can see all result summaries
        if user.is_staff or user.is_superuser:
            return StudentResultSummary.objects.select_related(
                'student__student', 'student__standard', 'student__academic_year',
                'exam__academic_year', 'academic_year'
            )
        
        # Teachers can see result summaries for their assigned students
        try:
            teacher = Teacher.objects.get(user=user)
            class_standards = ClassTeacher.objects.filter(teacher=teacher).values_list('standard', flat=True)
            subject_standards = TeacherSubject.objects.filter(teacher=teacher).values_list('subject__standard', flat=True)
            all_standards = set(list(class_standards) + list(subject_standards))
            student_enrollments = StudentEnrollment.objects.filter(standard__in=all_standards).values_list('id', flat=True)
            return StudentResultSummary.objects.filter(student__in=student_enrollments).select_related(
                'student__student', 'student__standard', 'student__academic_year',
                'exam__academic_year', 'academic_year'
            )
        except Teacher.DoesNotExist:
            pass
        
        # Students can see only their own result summaries
        try:
            student = Student.objects.get(user=user)
            student_enrollments = StudentEnrollment.objects.filter(student=student).values_list('id', flat=True)
            return StudentResultSummary.objects.filter(student__in=student_enrollments).select_related(
                'student__student', 'student__standard', 'student__academic_year',
                'exam__academic_year', 'academic_year'
            )
        except Student.DoesNotExist:
            pass
        
        return StudentResultSummary.objects.none()

    def perform_create(self, serializer):
        summary = serializer.save(academic_year=serializer.validated_data['student'].academic_year)
        _update_result_summary(summary.student, summary.exam)

    def perform_update(self, serializer):
        student = serializer.validated_data.get('student', serializer.instance.student)
        summary = serializer.save(academic_year=student.academic_year)
        _update_result_summary(summary.student, summary.exam)


class ExamReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    queryset = Exam.objects.select_related('academic_year')
    ordering_fields = ['id', 'title', 'exam_date', 'academic_year']
    ordering = ['-exam_date']


class AttendanceReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Attendance.objects.select_related(
        'student',
        'standard',
        'subject__standard',
        'recorded_by',
        'academic_year',
    )
    ordering_fields = ['id', 'student', 'date', 'status', 'standard']
    ordering = ['-date']


class MarksheetDetailReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for marksheet details - replaces StudentMarksheetReadOnlyViewSet.
    Uses SubjectResult as base model instead of the removed StudentMarksheet through table.
    
    Note: To optimize the summary field lookups in the serializer, the viewset could be enhanced
    to prefetch StudentResultSummary objects and pass them in the serializer context to avoid N+1 queries.
    """
    serializer_class = MarksheetDetailSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MarksheetDetailFilter
    ordering_fields = ['id', 'student', 'exam_subject__exam', 'marks_obtained_theory']
    ordering = ['-exam_subject__exam']
    
    def get_queryset(self):
        return SubjectResult.objects.select_related(
            'student',
            'student__student',
            'student__standard',
            'student__academic_year',
            'exam_subject',
            'exam_subject__exam',
            'exam_subject__subject',
        )


class SubjectResultReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = SubjectResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SubjectResultFilter
    ordering_fields = ['id', 'student', 'exam_subject', 'marks_obtained_theory', 'marks_obtained_practical']
    ordering = ['-exam_subject__exam']

    def get_queryset(self):
        return SubjectResult.objects.select_related(
            'exam_subject__exam__academic_year',
            'exam_subject__subject__standard',
            'exam_subject__standard',
            'student__student',
            'student__standard',
            'student__academic_year',
        )


class ExamSubjectReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = ExamSubjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ExamSubjectFilter
    ordering_fields = ['id', 'exam', 'subject', 'standard', 'total_marks']
    ordering = ['exam', 'subject']

    def get_queryset(self):
        return ExamSubject.objects.select_related(
            'exam',
            'exam__academic_year',
            'subject',
            'subject__standard',
            'standard',
        )


class StudentResultSummaryReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = StudentResultSummarySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = StudentResultSummaryFilter
    ordering_fields = ['id', 'student', 'exam', 'total_marks', 'gpa', 'overall_grade']
    ordering = ['-exam']

    def get_queryset(self):
        # No need to prefetch results anymore since we use SerializerMethodField
        # The serializer will handle fetching results dynamically with proper select_related
        return StudentResultSummary.objects.select_related(
            'student__student',
            'student__standard',
            'student__academic_year',
            'exam__academic_year',
            'academic_year',
        )