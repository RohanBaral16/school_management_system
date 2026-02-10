# Database Schema & ER Diagram

## Overview

This document provides a comprehensive view of the recommended database schema for the School Management System, including existing and proposed models.

---

## Current Schema (Existing Models)

### ACCOUNTS APP

```
┌─────────────────────────────────┐
│         Student                 │
├─────────────────────────────────┤
│ PK  id                          │
│     first_name                  │
│     middle_name                 │
│     last_name                   │
│     gender                      │
│     email                       │
│     phone                       │
│     date_of_birth               │
│     date_of_birth_bs            │
│     admission_number (unique)   │
│     created_at                  │
│     updated_at                  │
└─────────────────────────────────┘
           │
           │ 1:N
           │
┌─────────────────────────────────┐
│         Teacher                 │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  user (1:1)                  │
│     first_name                  │
│     last_name                   │
│     designation                 │
│     email (unique)              │
│     phone                       │
│     status                      │
│     created_at                  │
│     updated_at                  │
└─────────────────────────────────┘
```

### ACADEMICS APP

```
┌─────────────────────────────────┐
│       AcademicYear              │
├─────────────────────────────────┤
│ PK  id                          │
│     name                        │
│     year_start_date             │
│     year_end_date               │
│     is_current                  │
│     status                      │
│     created_at                  │
│     updated_at                  │
└─────────────────────────────────┘
           │
           │ Referenced by
           ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│         Standard                │       │          Subject                │
├─────────────────────────────────┤       ├─────────────────────────────────┤
│ PK  id                          │───────│ PK  id                          │
│     name                        │  1:N  │ FK  standard                    │
│     section                     │       │     name                        │
│     status                      │       │     code (unique)               │
│     created_at                  │       │     credit_hours                │
│     updated_at                  │       │     curriculum_version          │
│ UNIQUE(name, section)           │       │     created_at                  │
└─────────────────────────────────┘       │     updated_at                  │
           │                              └─────────────────────────────────┘
           │ 1:N
           │
┌─────────────────────────────────┐
│     StudentEnrollment           │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│ FK  standard                    │
│ FK  academic_year               │
│     roll_number                 │
│     status                      │
│     created_at                  │
│     updated_at                  │
│ UNIQUE(student, academic_year)  │
│ UNIQUE(standard, academic_year, │
│        roll_number)             │
└─────────────────────────────────┘

┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│       ClassTeacher              │       │      TeacherSubject             │
├─────────────────────────────────┤       ├─────────────────────────────────┤
│ PK  id                          │       │ PK  id                          │
│ FK  standard                    │       │ FK  teacher                     │
│ FK  teacher                     │       │ FK  subject                     │
│ FK  academic_year               │       │ FK  standard                    │
│ UNIQUE(teacher, standard,       │       │ FK  academic_year               │
│        academic_year)           │       │ UNIQUE(subject, standard,       │
└─────────────────────────────────┘       │        academic_year)           │
                                          └─────────────────────────────────┘
```

### ACTIVITIES APP

```
┌─────────────────────────────────┐
│         Attendance              │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│ FK  standard                    │
│ FK  subject (nullable)          │
│ FK  recorded_by (Teacher)       │
│ FK  academic_year               │
│     date                        │
│     status                      │
│     remarks                     │
│ UNIQUE(date, student, subject,  │
│        standard)                │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│           Exam                  │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  academic_year               │
│     name                        │
│     term                        │
│     start_date                  │
│     end_date                    │
│     is_published                │
│     created_at                  │
└─────────────────────────────────┘
           │
           │ 1:N
           │
┌─────────────────────────────────┐
│        ExamSubject              │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  exam                        │
│ FK  subject                     │
│ FK  standard (auto-set)         │
│     exam_date                   │
│     full_marks_theory           │
│     pass_marks_theory           │
│     full_marks_practical        │
│     pass_marks_practical        │
│ UNIQUE(exam, subject)           │
└─────────────────────────────────┘
           │
           │ 1:N
           │
┌─────────────────────────────────┐
│          Result                 │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student (StudentEnrollment) │
│ FK  exam_subject                │
│     marks_obtained_theory       │
│     marks_obtained_practical    │
│     subject_grade_point (auto)  │
│     subject_grade (auto)        │
│ UNIQUE(student, exam_subject)   │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│       ResultSummary             │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│ FK  exam                        │
│ FK  academic_year               │
│     total_marks                 │
│     percentage                  │
│     gpa                         │
│     overall_grade               │
│     rank                        │
│ UNIQUE(student, exam)           │
└─────────────────────────────────┘
```

---

## Recommended Schema Extensions

### ACCOUNTS APP - Enhanced

```
┌─────────────────────────────────┐
│         Student                 │
│      (ENHANCED)                 │
├─────────────────────────────────┤
│ PK  id                          │
│     first_name                  │
│     middle_name                 │
│     last_name                   │
│     gender                      │
│     email                       │
│     phone                       │
│     date_of_birth               │
│     date_of_birth_bs            │
│     admission_number (unique)   │
│  +  photo                       │──┐
│  +  blood_group                 │  │
│  +  nationality                 │  │
│  +  religion                    │  │
│     created_at                  │  │
│     updated_at                  │  │
└─────────────────────────────────┘  │
           │                          │
           │ 1:N                      │ 1:1
           ▼                          ▼
┌─────────────────────────────────┐  ┌─────────────────────────────────┐
│   NEW: Guardian                 │  │   NEW: MedicalRecord            │
├─────────────────────────────────┤  ├─────────────────────────────────┤
│ PK  id                          │  │ PK  id                          │
│ FK  student                     │  │ FK  student (1:1)               │
│     relationship                │  │     allergies                   │
│     first_name                  │  │     chronic_conditions          │
│     last_name                   │  │     medications                 │
│     email                       │  │     special_needs               │
│     phone                       │  │     doctor_name                 │
│     alternate_phone             │  │     doctor_phone                │
│     address                     │  │     last_updated                │
│     occupation                  │  └─────────────────────────────────┘
│     is_primary_contact          │
│     can_pick_student            │
│     is_emergency_contact        │
│     created_at                  │
│     updated_at                  │
└─────────────────────────────────┘
           │ 
           │ 1:N
           ▼
┌─────────────────────────────────┐
│   NEW: Address                  │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│     address_type                │
│     province                    │
│     district                    │
│     municipality                │
│     ward_number                 │
│     tole                        │
│     house_number                │
│     nearest_landmark            │
└─────────────────────────────────┘

Student 1:N StudentDocument
┌─────────────────────────────────┐
│   NEW: StudentDocument          │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│     document_type               │
│     file                        │
│     uploaded_at                 │
│     verified                    │
│     notes                       │
└─────────────────────────────────┘
```

### Teacher Extensions

```
┌─────────────────────────────────┐
│         Teacher                 │
│      (ENHANCED)                 │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  user (1:1)                  │
│     first_name                  │
│     last_name                   │
│     designation                 │
│     email (unique)              │
│     phone                       │
│     status                      │
│     created_at                  │
│     updated_at                  │
└─────────────────────────────────┘
           │
           │ 1:N
           ├────────────────────────┐
           │                        │
           ▼                        ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│ NEW: TeacherQualification       │ │ NEW: TeacherAttendance          │
├─────────────────────────────────┤ ├─────────────────────────────────┤
│ PK  id                          │ │ PK  id                          │
│ FK  teacher                     │ │ FK  teacher                     │
│     degree_type                 │ │     date                        │
│     degree_name                 │ │     status                      │
│     institution                 │ │     check_in_time               │
│     year_completed              │ │     check_out_time              │
│     certificate_file            │ │     remarks                     │
└─────────────────────────────────┘ │ UNIQUE(teacher, date)           │
                                    └─────────────────────────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────┐
│ NEW: Leave                      │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  teacher                     │
│ FK  approved_by (Teacher)       │
│     leave_type                  │
│     start_date                  │
│     end_date                    │
│     reason                      │
│     status                      │
│     approved_at                 │
│     created_at                  │
└─────────────────────────────────┘

Teacher 1:1 TeacherSalary
┌─────────────────────────────────┐
│ NEW: TeacherSalary              │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  teacher (1:1)               │
│     basic_salary                │
│     allowances                  │
│     provident_fund_deduction    │
│     tax_deduction               │
│     effective_from              │
└─────────────────────────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────┐
│ NEW: SalaryPayment              │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  teacher                     │
│     month                       │
│     gross_salary                │
│     deductions                  │
│     net_salary                  │
│     payment_date                │
│     payment_method              │
│     remarks                     │
│     created_at                  │
└─────────────────────────────────┘
```

---

## ACADEMICS APP - Enhanced

### Timetable & Schedule

```
┌─────────────────────────────────┐
│ NEW: Period                     │
├─────────────────────────────────┤
│ PK  id                          │
│     name                        │
│     start_time                  │
│     end_time                    │
│     order                       │
│     is_break                    │
└─────────────────────────────────┘
           │
           │ Referenced by
           ▼
┌─────────────────────────────────┐
│ NEW: Timetable                  │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  standard                    │
│ FK  academic_year               │
│ FK  period                      │
│ FK  subject                     │
│ FK  teacher                     │
│     day                         │
│     room_number                 │
│ UNIQUE(standard, day, period,   │
│        academic_year)           │
└─────────────────────────────────┘
```

### Homework System

```
┌─────────────────────────────────┐
│ NEW: Homework                   │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  subject                     │
│ FK  standard                    │
│ FK  teacher                     │
│ FK  academic_year               │
│     title                       │
│     description                 │
│     assigned_date               │
│     due_date                    │
│     max_marks                   │
│     attachment                  │
│     status                      │
│     created_at                  │
│     updated_at                  │
└─────────────────────────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────┐
│ NEW: HomeworkSubmission         │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  homework                    │
│ FK  student                     │
│ FK  graded_by (Teacher)         │
│     submission_date             │
│     submission_file             │
│     submission_text             │
│     status                      │
│     marks_obtained              │
│     feedback                    │
│     graded_at                   │
│     created_at                  │
│     updated_at                  │
│ UNIQUE(homework, student)       │
└─────────────────────────────────┘
```

### Fee Management

```
┌─────────────────────────────────┐
│ NEW: FeeStructure               │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  standard                    │
│ FK  academic_year               │
│     name                        │
│     fee_type                    │
│     amount                      │
│     is_mandatory                │
│     due_date                    │
│     created_at                  │
│     updated_at                  │
│ UNIQUE(name, standard,          │
│        academic_year)           │
└─────────────────────────────────┘
           │
           │ Referenced by
           ▼
┌─────────────────────────────────┐
│ NEW: FeePayment                 │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│ FK  fee_structure               │
│ FK  academic_year               │
│ FK  received_by (Teacher)       │
│     amount_due                  │
│     amount_paid                 │
│     status                      │
│     payment_date                │
│     payment_method              │
│     transaction_id              │
│     receipt_number (unique)     │
│     remarks                     │
│     created_at                  │
│     updated_at                  │
└─────────────────────────────────┘
```

### Library Management

```
┌─────────────────────────────────┐
│ NEW: Book                       │
├─────────────────────────────────┤
│ PK  id                          │
│     title                       │
│     author                      │
│     isbn (unique)               │
│     publisher                   │
│     publication_year            │
│     category                    │
│     quantity                    │
│     available_quantity          │
│     rack_location               │
│     created_at                  │
└─────────────────────────────────┘
           │
           │ Referenced by
           ▼
┌─────────────────────────────────┐
│ NEW: BookIssue                  │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  book                        │
│ FK  student                     │
│ FK  issued_by (Teacher)         │
│     issue_date                  │
│     due_date                    │
│     return_date                 │
│     status                      │
│     fine_amount                 │
└─────────────────────────────────┘
```

---

## ACTIVITIES APP - Enhanced

### Attendance Summary

```
┌─────────────────────────────────┐
│ NEW: AttendanceSummary          │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│ FK  academic_year               │
│     month                       │
│     year                        │
│     total_days                  │
│     present_days                │
│     absent_days                 │
│     late_days                   │
│     leave_days                  │
│     attendance_percentage       │
│ UNIQUE(student, month, year,    │
│        academic_year)           │
└─────────────────────────────────┘
```

### Behavior Tracking

```
┌─────────────────────────────────┐
│ NEW: Behavior                   │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│ FK  reported_by (Teacher)       │
│     date                        │
│     behavior_type               │
│     severity                    │
│     title                       │
│     description                 │
│     action_taken                │
│     parents_notified            │
│     created_at                  │
└─────────────────────────────────┘
```

### Notice & Events

```
┌─────────────────────────────────┐
│ NEW: Notice                     │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  created_by (Teacher)        │
│ M2M target_standards            │
│     title                       │
│     content                     │
│     notice_type                 │
│     target_audience             │
│     publish_date                │
│     expiry_date                 │
│     attachment                  │
│     is_active                   │
│     created_at                  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ NEW: Event                      │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  coordinator (Teacher)       │
│ M2M participating_standards     │
│     name                        │
│     event_type                  │
│     description                 │
│     start_date                  │
│     end_date                    │
│     venue                       │
│     open_to_all                 │
│     created_at                  │
└─────────────────────────────────┘
           │
           │ N:M (via EventParticipation)
           ▼
┌─────────────────────────────────┐
│ NEW: EventParticipation         │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  event                       │
│ FK  student                     │
│     position                    │
│     remarks                     │
│ UNIQUE(event, student)          │
└─────────────────────────────────┘
```

### Transport Management

```
┌─────────────────────────────────┐
│ NEW: TransportRoute             │
├─────────────────────────────────┤
│ PK  id                          │
│     route_name                  │
│     route_number (unique)       │
│     start_point                 │
│     end_point                   │
│     stops                       │
│     vehicle_number              │
│     driver_name                 │
│     driver_phone                │
│     monthly_fee                 │
│     is_active                   │
└─────────────────────────────────┘
           │
           │ Referenced by
           ▼
┌─────────────────────────────────┐
│ NEW: StudentTransport           │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student                     │
│ FK  route                       │
│ FK  academic_year               │
│     pickup_point                │
│     drop_point                  │
│     is_active                   │
│ UNIQUE(student, academic_year)  │
└─────────────────────────────────┘
```

### Enhanced Report Card

```
┌─────────────────────────────────┐
│ NEW: ReportCard                 │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  student (StudentEnrollment) │
│ FK  exam                        │
│ FK  academic_year               │
│     total_marks                 │
│     percentage                  │
│     gpa                         │
│     overall_grade               │
│     rank                        │
│     attendance_percentage       │
│     class_teacher_remarks       │
│     principal_remarks           │
│     generated_at                │
│     is_published                │
│ UNIQUE(student, exam)           │
└─────────────────────────────────┘
```

---

## Communication Module (New)

```
┌─────────────────────────────────┐
│ NEW: Message                    │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  sender_user                 │
│ FK  recipient_user              │
│ FK  related_student (nullable)  │
│     message_type                │
│     subject                     │
│     body                        │
│     is_read                     │
│     read_at                     │
│     created_at                  │
└─────────────────────────────────┘
```

---

## Authentication & Roles (New)

```
┌─────────────────────────────────┐
│ Django User (Built-in)          │
├─────────────────────────────────┤
│ PK  id                          │
│     username                    │
│     email                       │
│     password                    │
│     is_active                   │
│     is_staff                    │
│     is_superuser                │
└─────────────────────────────────┘
           │
           │ 1:1
           ▼
┌─────────────────────────────────┐
│ NEW: UserRole                   │
├─────────────────────────────────┤
│ PK  id                          │
│ FK  user (1:1)                  │
│ FK  teacher (nullable)          │
│ FK  student (nullable)          │
│     role                        │
│     is_active                   │
│     created_at                  │
└─────────────────────────────────┘
```

---

## Relationships Summary

### Key Foreign Key Relationships

1. **Student → Guardian**: One-to-Many (One student has multiple guardians)
2. **Student → Address**: One-to-Many (Permanent and Temporary addresses)
3. **Student → MedicalRecord**: One-to-One
4. **Student → StudentEnrollment**: One-to-Many (One student can enroll multiple years)
5. **StudentEnrollment → Standard**: Many-to-One
6. **StudentEnrollment → AcademicYear**: Many-to-One
7. **Standard → Subject**: One-to-Many
8. **Teacher → TeacherQualification**: One-to-Many
9. **Teacher → Leave**: One-to-Many
10. **Teacher → TeacherSalary**: One-to-One
11. **Exam → ExamSubject**: One-to-Many
12. **ExamSubject → Result**: One-to-Many
13. **Student → FeePayment**: One-to-Many
14. **FeeStructure → FeePayment**: One-to-Many
15. **Book → BookIssue**: One-to-Many

### Many-to-Many Relationships

1. **Notice ↔ Standard**: Through Django's M2M (target_standards)
2. **Event ↔ Standard**: Through Django's M2M (participating_standards)
3. **Event ↔ Student**: Through EventParticipation junction table

---

## Database Indexes Recommendation

### High Priority Indexes

```sql
-- Student lookups
CREATE INDEX idx_student_admission_number ON accounts_student(admission_number);
CREATE INDEX idx_student_name ON accounts_student(first_name, last_name);

-- Enrollment queries
CREATE INDEX idx_enrollment_student_year ON academics_studentenrollment(student_id, academic_year_id);
CREATE INDEX idx_enrollment_standard_year ON academics_studentenrollment(standard_id, academic_year_id);

-- Attendance queries
CREATE INDEX idx_attendance_student_date ON activities_attendance(student_id, date);
CREATE INDEX idx_attendance_standard_date ON activities_attendance(standard_id, date);

-- Result lookups
CREATE INDEX idx_result_student_exam ON activities_result(student_id, exam_subject_id);

-- Fee payment tracking
CREATE INDEX idx_fee_payment_student ON academics_feepayment(student_id, status);
CREATE INDEX idx_fee_payment_receipt ON academics_feepayment(receipt_number);

-- Teacher schedules
CREATE INDEX idx_timetable_day_period ON academics_timetable(day, period_id);
CREATE INDEX idx_timetable_teacher ON academics_timetable(teacher_id, academic_year_id);
```

---

## Data Integrity Constraints

### Business Rules Enforced at Database Level

1. **Unique Constraints**:
   - Student admission_number
   - Teacher email
   - Subject code
   - FeePayment receipt_number
   - (student, academic_year) in StudentEnrollment
   - (standard, academic_year, roll_number) in StudentEnrollment

2. **Foreign Key Constraints**:
   - CASCADE: When deleting auxiliary data (e.g., Guardian, Documents)
   - PROTECT: When deleting core entities that should never be orphaned (e.g., AcademicYear, Standard)
   - SET_NULL: For optional relationships (e.g., Teacher assignments)

3. **Check Constraints** (Application Level):
   - Marks obtained ≤ full marks
   - End date > Start date
   - Amount paid ≤ Amount due
   - Age validation for students

---

## Migration Strategy

### Step 1: Core Extensions (Phase 1)
1. Add Guardian model
2. Add FeeStructure and FeePayment
3. Add Homework and HomeworkSubmission
4. Add Teacher attendance and leave models

### Step 2: Academic Features (Phase 2)
5. Add Period and Timetable
6. Add Library models (Book, BookIssue)
7. Add enhanced Student fields (photo, blood_group, etc.)

### Step 3: Administrative Features (Phase 3)
8. Add Notice and Event models
9. Add Behavior tracking
10. Add Transport models

### Step 4: Advanced Features (Phase 4)
11. Add ReportCard model
12. Add Message system
13. Add UserRole
14. Add Teacher salary models

---

## Storage Considerations

### File Storage Requirements

1. **Student Photos**: ~100 KB each → ~100 MB for 1000 students
2. **Documents**: ~500 KB each, 3 docs per student → ~1.5 GB for 1000 students
3. **Homework Attachments**: ~2 MB each → Plan for storage growth
4. **Book Files** (if digital library): Variable, can be large

### Recommended Setup
- Use Django's FileField with proper upload_to paths
- Consider cloud storage (AWS S3, Google Cloud Storage) for production
- Implement file size validators
- Add virus scanning for uploaded files

---

**Document Version**: 1.0  
**Last Updated**: February 10, 2026
