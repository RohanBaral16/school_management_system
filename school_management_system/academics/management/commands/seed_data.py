import random
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from academics.models import AcademicYear, Standard, Subject, StudentEnrollment, ClassTeacher, TeacherSubject
from activities.models import Exam, ExamSubject, Result
from accounts.models import Student, Teacher
import nepali_datetime


class Command(BaseCommand):
    help = "Seed the database with demo data for the school management system."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete existing seeded data before creating new data.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()
        Faker.seed(42)
        random.seed(42)

        if options.get("delete"):
            self.stdout.write(self.style.WARNING("Deleting existing data..."))
            Result.objects.all().delete()
            ExamSubject.objects.all().delete()
            Exam.objects.all().delete()
            TeacherSubject.objects.all().delete()
            ClassTeacher.objects.all().delete()
            StudentEnrollment.objects.all().delete()
            Subject.objects.all().delete()
            Standard.objects.all().delete()
            AcademicYear.objects.all().delete()
            Teacher.objects.all().delete()
            Student.objects.all().delete()

        self.stdout.write(self.style.MIGRATE_HEADING("Creating academic year and standards..."))
        current_nepali_date = nepali_datetime.date.today()
        current_year_name = str(current_nepali_date.year)

        academic_year, _ = AcademicYear.objects.get_or_create(
            name=current_year_name,
            defaults={
                "year_start_date": current_nepali_date,
                "year_end_date": current_nepali_date,
                "is_current": True,
                "status": "active",
            },
        )
        if not academic_year.is_current:
            academic_year.is_current = True
            academic_year.save(update_fields=["is_current"])

        standards = []
        for class_number in range(1, 11):
            standard, _ = Standard.objects.get_or_create(
                name=f"Class {class_number}",
                section="A",
                defaults={"status": "active"},
            )
            standards.append(standard)

        self.stdout.write(self.style.MIGRATE_HEADING("Creating teachers..."))
        teachers = []
        for _ in range(15):
            teacher = Teacher.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                designation=fake.job(),
                email=fake.unique.email(),
                phone=self._safe_phone(fake),
                status="active",
            )
            teachers.append(teacher)

        self.stdout.write(self.style.MIGRATE_HEADING("Creating subjects per standard..."))
        subjects = []
        for standard in standards:
            for idx in range(1, 6):
                short_class = str(standard.name).replace("Class ", "C").replace(" ", "")
                short_word = fake.word()[:3].upper()
                short_code = f"{short_class}{idx}{random.randint(0, 9)}{short_word}"
                subject = Subject.objects.create(
                    name=f"{fake.word().title()} {idx}",
                    code=short_code[:10],
                    standard=standard,
                    credit_hours=Decimal("4.0"),
                    curriculum_version=current_year_name,
                )
                subjects.append(subject)

        self.stdout.write(self.style.MIGRATE_HEADING("Assigning teachers to subjects..."))
        for subject in subjects:
            TeacherSubject.objects.create(
                teacher=random.choice(teachers),
                subject=subject,
                academic_year=academic_year,
            )

        self.stdout.write(self.style.MIGRATE_HEADING("Creating students and enrollments..."))
        enrollments = []
        admission_counter = 1
        for standard in standards:
            roll_counter = 1
            for _ in range(20):
                dob_ad = fake.date_between(start_date="-18y", end_date="-10y")
                try:
                    dob_bs = nepali_datetime.date.from_datetime_date(dob_ad)
                except Exception:
                    dob_bs = current_nepali_date

                student = Student.objects.create(
                    first_name=fake.first_name(),
                    middle_name=fake.first_name() if random.random() < 0.3 else "",
                    last_name=fake.last_name(),
                    gender=random.choice(["male", "female", "other"]),
                    email=fake.unique.email(),
                    phone=self._safe_phone(fake),
                    date_of_birth=dob_ad,
                    date_of_birth_bs=dob_bs,
                    admission_number=f"{current_year_name}-{admission_counter:04d}",
                )
                admission_counter += 1

                enrollment = StudentEnrollment.objects.create(
                    student=student,
                    standard=standard,
                    roll_number=str(roll_counter).zfill(2),
                    academic_year=academic_year,
                    status="enrolled",
                )
                enrollments.append(enrollment)
                roll_counter += 1

        self.stdout.write(self.style.MIGRATE_HEADING("Creating exams and exam subjects..."))
        exams = []
        for term, label in [("first_term", "First Term"), ("final_term", "Final Term")]:
            exam = Exam.objects.create(
                name=f"{label} Examination {current_year_name}",
                term=term,
                academic_year=academic_year,
                start_date=current_nepali_date,
                end_date=current_nepali_date,
                is_published=False,
            )
            exams.append(exam)

            for subject in subjects:
                ExamSubject.objects.create(
                    exam=exam,
                    subject=subject,
                    exam_date=current_nepali_date,
                    full_marks_theory=Decimal("75.0"),
                    pass_marks_theory=Decimal("27.0"),
                    full_marks_practical=Decimal("25.0"),
                    pass_marks_practical=Decimal("9.0"),
                    standard=subject.standard,
                )

        self.stdout.write(self.style.MIGRATE_HEADING("Creating results..."))
        exam_subjects_by_standard = {}
        for exam_subject in ExamSubject.objects.select_related("subject"):
            exam_subjects_by_standard.setdefault(exam_subject.subject.standard_id, []).append(exam_subject)

        for enrollment in enrollments:
            for exam_subject in exam_subjects_by_standard.get(enrollment.standard_id, []):
                full_theory = exam_subject.full_marks_theory
                full_practical = exam_subject.full_marks_practical

                if random.random() < 0.2:
                    theory_score = self._random_decimal(Decimal("0"), full_theory * Decimal("0.34"))
                    practical_score = self._random_decimal(Decimal("0"), full_practical * Decimal("0.34"))
                else:
                    theory_score = self._random_decimal(full_theory * Decimal("0.4"), full_theory)
                    practical_score = self._random_decimal(full_practical * Decimal("0.4"), full_practical)

                Result.objects.create(
                    student=enrollment,
                    exam_subject=exam_subject,
                    marks_obtained_theory=theory_score,
                    marks_obtained_practical=practical_score,
                )

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully."))

    @staticmethod
    def _random_decimal(min_value: Decimal, max_value: Decimal) -> Decimal:
        if max_value < min_value:
            min_value, max_value = max_value, min_value
        value = Decimal(str(random.uniform(float(min_value), float(max_value))))
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _safe_phone(fake: Faker) -> str:
        raw = fake.msisdn()  # digits only
        if not raw:
            return ""
        return raw[:15]
