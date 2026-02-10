# School Management System

Django-based school management system with PostgreSQL and Docker, featuring Nepal-specific functionality including Nepali date support and CDC grading system.

## Quick Start

### Setup
1. Start DB: `docker compose up -d db`
2. Migrate: `python manage.py migrate`
3. Create admin: `python manage.py createsuperuser`
4. Run: `python manage.py runserver`

### Reset DB
```bash
docker compose down -v
docker compose up -d db
python manage.py migrate
```

## Current Features

### 👥 Accounts Module
- **Student Management**: Track student information with Nepali dates, admission numbers
- **Teacher Management**: Teacher profiles with designation and status tracking

### 📚 Academics Module
- **Academic Year Management**: Define and track academic years
- **Class/Standard Management**: Organize classes with sections
- **Subject Management**: Subject catalog with credit hours
- **Student Enrollment**: Track student enrollment per academic year
- **Teacher Assignments**: Assign class teachers and subject teachers

### 📊 Activities Module
- **Attendance Tracking**: Daily attendance with subject-level option
- **Exam Management**: Terminal and unit test tracking
- **Result Management**: Theory and practical marks with auto-grading (Nepal CDC standard)
- **Result Summary**: Overall performance tracking with GPA and rank

## 📖 Documentation

We've created comprehensive documentation to help you extend this system:

### 🎯 [QUICK_REFERENCE.md](../QUICK_REFERENCE.md)
**Start here!** Quick overview of all documentation and top priorities.

### 💡 [FEATURE_RECOMMENDATIONS.md](../FEATURE_RECOMMENDATIONS.md)
Detailed recommendations for 40+ features you can add:
- Guardian/Parent Management
- Fee Management System
- Homework & Assignments
- Library Management
- Timetable & Scheduling
- Teacher Attendance & Leave
- Behavior Tracking
- Events & Activities
- And much more!

### 🛠️ [IMPLEMENTATION_GUIDE.md](../IMPLEMENTATION_GUIDE.md)
Step-by-step implementation instructions:
- Complete code examples
- Admin configuration
- API development
- Testing guidelines
- Security best practices
- Performance optimization

### 🗄️ [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md)
Database design and architecture:
- Current schema diagrams
- Recommended extensions
- Entity relationships
- Migration strategies
- Index recommendations

## 🚀 Recommended Next Steps

Based on typical school management needs, consider implementing these features first:

1. **Guardian/Parent Management** - Essential for parent communication
2. **Fee Management** - Critical for financial operations
3. **Homework System** - Daily academic tracking
4. **Timetable** - Schedule management
5. **Notice Board** - School-wide communication

See [FEATURE_RECOMMENDATIONS.md](../FEATURE_RECOMMENDATIONS.md) for complete priority matrix.

## 🏗️ Tech Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Special**: Nepali DateTime Field for BS date support
- **Containerization**: Docker

## 📁 Project Structure

```
school_management_system/
├── accounts/          # Student & Teacher models
├── academics/         # Academic year, enrollment, subjects
├── activities/        # Attendance, exams, results
└── school_management_system/  # Settings and configuration
```

## 🤝 Contributing

When adding new features:
1. Follow existing code patterns
2. Add tests for new functionality
3. Update documentation
4. Write clear commit messages

## 📝 License

[Your License Here]

---

For questions or detailed implementation guidance, refer to the documentation files listed above.
