# School Management System

Django app with PostgreSQL and Docker.

## Quick start
- Start DB: `docker compose up -d db`
- Migrate: `python manage.py migrate`
- Create admin: `python manage.py createsuperuser`
- Run: `python manage.py runserver`

## Reset DB
- `docker compose down -v`
- `docker compose up -d db`
- `python manage.py migrate`
