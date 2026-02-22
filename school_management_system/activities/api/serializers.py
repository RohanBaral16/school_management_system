from rest_framework import serializers

from academics.api.serializers import (
    StudentEnrollmentSerializer,
    StandardSerializer,
    AcademicYearSerializer,
)
from accounts.api.serializers import StudentSerializer, TeacherSerializer
from ..models import SubjectResult, ExamSubject, StudentResultSummary, Attendance, Exam
from academics.models import ClassTeacher, Subject


class ExamSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=Exam.objects.none(),
        write_only=True,
    )

    class Meta:
        model = Exam
        fields = [
            'id',
            'name',
            'term',
            'academic_year',
            'academic_year_id',
            'start_date',
            'end_date',
            'is_published',
            'created_at',
        ]


class ExamWriteSerializer(serializers.ModelSerializer):
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYearSerializer.Meta.model.objects.all(),
    )

    class Meta:
        model = Exam
        fields = [
            'id',
            'name',
            'term',
            'academic_year_id',
            'start_date',
            'end_date',
            'is_published',
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=StudentSerializer.Meta.model.objects.all(),
        write_only=True,
    )
    standard = StandardSerializer(read_only=True)
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=StandardSerializer.Meta.model.objects.all(),
        write_only=True,
    )
    subject = serializers.SerializerMethodField(read_only=True)
    subject_id = serializers.IntegerField(write_only=True, required=False)
    recorded_by = TeacherSerializer(read_only=True)
    recorded_by_id = serializers.PrimaryKeyRelatedField(
        source='recorded_by',
        queryset=TeacherSerializer.Meta.model.objects.all(),
        write_only=True,
        required=False,
    )
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYearSerializer.Meta.model.objects.all(),
        write_only=True,
    )

    def get_subject(self, obj):
        from academics.api.serializers import SubjectSerializer
        return SubjectSerializer(obj.subject, read_only=True).data if obj.subject else None

    class Meta:
        model = Attendance
        fields = [
            'id',
            'date',
            'student',
            'student_id',
            'standard',
            'standard_id',
            'subject',
            'subject_id',
            'status',
            'recorded_by',
            'recorded_by_id',
            'academic_year',
            'academic_year_id',
            'remarks',
        ]


class AttendanceWriteSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=StudentSerializer.Meta.model.objects.all(),
    )
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=StandardSerializer.Meta.model.objects.all(),
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject',
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True,
    )
    recorded_by_id = serializers.PrimaryKeyRelatedField(
        source='recorded_by',
        queryset=TeacherSerializer.Meta.model.objects.all(),
        required=False,
        allow_null=True,
    )
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=AcademicYearSerializer.Meta.model.objects.all(),
    )

    class Meta:
        model = Attendance
        fields = [
            'id',
            'date',
            'student_id',
            'standard_id',
            'subject_id',
            'status',
            'recorded_by_id',
            'academic_year_id',
            'remarks',
        ]


class ExamSubjectSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam',
        queryset=Exam.objects.all(),
        write_only=True,
    )
    subject = serializers.SerializerMethodField(read_only=True)
    subject_id = serializers.IntegerField(write_only=True, required=False)
    standard = StandardSerializer(read_only=True)
    standard_id = serializers.IntegerField(write_only=True, required=False)

    def get_subject(self, obj):
        from academics.api.serializers import SubjectSerializer
        return SubjectSerializer(obj.subject, read_only=True).data if obj.subject else None

    class Meta:
        model = ExamSubject
        fields = [
            'id',
            'exam',
            'exam_id',
            'subject',
            'subject_id',
            'standard',
            'standard_id',
            'exam_date',
            'full_marks_theory',
            'pass_marks_theory',
            'full_marks_practical',
            'pass_marks_practical',
        ]


class ExamSubjectWriteSerializer(serializers.ModelSerializer):
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam',
        queryset=Exam.objects.all(),
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject',
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True,
    )
    standard_id = serializers.PrimaryKeyRelatedField(
        source='standard',
        queryset=StandardSerializer.Meta.model.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ExamSubject
        fields = [
            'id',
            'exam_id',
            'subject_id',
            'standard_id',
            'exam_date',
            'full_marks_theory',
            'pass_marks_theory',
            'full_marks_practical',
            'pass_marks_practical',
        ]


class SubjectResultSerializer(serializers.ModelSerializer):
    student = StudentEnrollmentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=StudentResultSummary.objects.none(),
        write_only=True,
    )
    exam_subject = ExamSubjectSerializer(read_only=True)
    exam_subject_id = serializers.PrimaryKeyRelatedField(
        source='exam_subject',
        queryset=ExamSubject.objects.all(),
        write_only=True,
    )

    class Meta:
        model = SubjectResult
        fields = [
            'id',
            'student',
            'student_id',
            'exam_subject',
            'exam_subject_id',
            'marks_obtained_theory',
            'marks_obtained_practical',
            'subject_grade',
            'subject_grade_point',
        ]
        read_only_fields = ['subject_grade', 'subject_grade_point']


class SubjectResultWriteSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=StudentEnrollmentSerializer.Meta.model.objects.all(),
    )
    exam_subject_id = serializers.PrimaryKeyRelatedField(
        source='exam_subject',
        queryset=ExamSubject.objects.all(),
    )

    class Meta:
        model = SubjectResult
        fields = [
            'id',
            'student_id',
            'exam_subject_id',
            'marks_obtained_theory',
            'marks_obtained_practical',
        ]


class StudentResultSummarySerializer(serializers.ModelSerializer):
    student = StudentEnrollmentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=StudentResultSummary.objects.none(),
        write_only=True,
    )
    exam = ExamSerializer(read_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam',
        queryset=Exam.objects.all(),
        write_only=True,
    )
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        source='academic_year',
        queryset=StudentResultSummary.objects.none(),
        write_only=True,
    )
    results = serializers.SerializerMethodField()
    
    def get_results(self, obj):
        """Fetch subject results dynamically instead of using M2M."""
        results = SubjectResult.objects.filter(
            student=obj.student,
            exam_subject__exam=obj.exam
        ).select_related(
            'exam_subject__exam__academic_year',
            'exam_subject__subject__standard',
            'exam_subject__standard',
            'student__student',
            'student__standard',
            'student__academic_year',
        )
        return SubjectResultSerializer(results, many=True, context=self.context).data

    class Meta:
        model = StudentResultSummary
        fields = [
            'id',
            'student',
            'student_id',
            'exam',
            'exam_id',
            'academic_year',
            'academic_year_id',
            'total_marks',
            'percentage',
            'gpa',
            'overall_grade',
            'rank',
            'results',
        ]
        read_only_fields = ['results', 'total_marks', 'percentage', 'gpa', 'overall_grade', 'rank']


class StudentResultSummaryWriteSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        source='student',
        queryset=StudentEnrollmentSerializer.Meta.model.objects.all(),
    )
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam',
        queryset=Exam.objects.all(),
    )

    class Meta:
        model = StudentResultSummary
        fields = [
            'id',
            'student_id',
            'exam_id',
        ]


class MarksheetDetailSerializer(serializers.Serializer):
    """
    Serializer for marksheet details - replaces StudentMarksheetSerializer.
    Fetches data from SubjectResult and StudentResultSummary without a through table.
    """
    id = serializers.IntegerField(source='pk', read_only=True)
    student_id = serializers.IntegerField(source='student.student.id', read_only=True)
    student_enrollment_id = serializers.IntegerField(source='student.id', read_only=True)
    student_full_name = serializers.CharField(source='student.student.full_name', read_only=True)
    standard_id = serializers.IntegerField(source='student.standard.id', read_only=True)
    standard = serializers.SerializerMethodField(read_only=True)
    roll_no = serializers.CharField(source='student.roll_number', read_only=True)

    exam_id = serializers.IntegerField(source='exam_subject.exam.id', read_only=True)
    exam_name = serializers.CharField(source='exam_subject.exam.name', read_only=True)
    
    subject_id = serializers.IntegerField(source='exam_subject.subject.id', read_only=True)
    subject_name = serializers.CharField(source='exam_subject.subject.name', read_only=True)
    full_marks_theory = serializers.DecimalField(
        source='exam_subject.full_marks_theory',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    pass_marks_theory = serializers.DecimalField(
        source='exam_subject.pass_marks_theory',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    full_marks_practical = serializers.DecimalField(
        source='exam_subject.full_marks_practical',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    pass_marks_practical = serializers.DecimalField(
        source='exam_subject.pass_marks_practical',
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    marks_obtained_theory = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    marks_obtained_practical = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )
    subject_grade = serializers.CharField(read_only=True)
    subject_grade_point = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        read_only=True,
    )
    
    # Summary fields - fetched via annotation or passed in context
    resultsummary_id = serializers.SerializerMethodField()
    summary_gpa = serializers.SerializerMethodField()
    summary_overall_grade = serializers.SerializerMethodField()
    summary_rank = serializers.SerializerMethodField()

    class_teacher_id = serializers.SerializerMethodField(read_only=True)
    class_teacher_name = serializers.SerializerMethodField(read_only=True)

    def get_standard(self, obj):
        standard = obj.student.standard
        if not standard:
            return None
        return f"{standard.name} {standard.section}".strip()

    def _get_summary(self, obj):
        """Get or cache the result summary for this subject result."""
        cache = self.context.setdefault('_summary_cache', {})
        key = (obj.student_id, obj.exam_subject.exam_id)
        
        if key not in cache:
            # If we're serializing multiple objects, we might want to bulk fetch summaries
            # For now, we fetch individually but cache the result
            cache[key] = StudentResultSummary.objects.filter(
                student_id=obj.student_id,
                exam_id=obj.exam_subject.exam_id
            ).first()
        
        return cache[key]

    def get_resultsummary_id(self, obj):
        summary = self._get_summary(obj)
        return summary.id if summary else None

    def get_summary_gpa(self, obj):
        summary = self._get_summary(obj)
        return summary.gpa if summary else None

    def get_summary_overall_grade(self, obj):
        summary = self._get_summary(obj)
        return summary.overall_grade if summary else None

    def get_summary_rank(self, obj):
        summary = self._get_summary(obj)
        return summary.rank if summary else None

    def _get_class_teacher(self, obj):
        cache = self.context.setdefault('_class_teacher_cache', {})
        standard_id = obj.student.standard_id
        academic_year_id = obj.student.academic_year_id
        key = (standard_id, academic_year_id)

        if key not in cache:
            cache[key] = (
                ClassTeacher.objects
                .select_related('teacher')
                .filter(standard_id=standard_id, academic_year_id=academic_year_id)
                .first()
            )

        return cache[key]

    def get_class_teacher_id(self, obj):
        class_teacher = self._get_class_teacher(obj)
        return class_teacher.teacher_id if class_teacher else None

    def get_class_teacher_name(self, obj):
        class_teacher = self._get_class_teacher(obj)
        return class_teacher.teacher.full_name if class_teacher else None