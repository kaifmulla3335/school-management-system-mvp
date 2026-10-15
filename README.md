# School Management System MVP

A work-in-progress school portal for classes 1 to 10, built with React, Vite, FastAPI, PostgreSQL, SQLAlchemy, and JWT authentication. This repository captures the current MVP; attendance, marks, fees, and homework screens are planned for later development.

## Current features

- Admin and student roles with backend permission checks
- Admin dashboard with class counts and a filterable student roster
- Student creation with school and guardian details
- Automatic admission number (`2026-001` format) and separate login ID based on name and birth year (`aaravmehta2019` format)
- Admin password reset for students; passwords stored as Argon2 hashes
- Student login and a dashboard limited to the student's own profile
- Responsive sidebar with a mobile menu

The backend also has attendance, marks, and homework endpoints. Their frontend management screens are **not implemented yet**. This project is not deployed; it currently runs locally.

## Run locally

Requirements: Python 3.11+, Node.js, and PostgreSQL. Create a PostgreSQL database, then set the variables shown in [.env.example](.env.example) in your terminal or local environment. Never commit real credentials. The frontend expects the API at `http://localhost:8000` and runs at `http://localhost:5173`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# For a fresh empty database, create the current schema:
python -c "from database import Base, engine; import models; Base.metadata.create_all(bind=engine)"
python -m uvicorn main:app --reload
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

If upgrading an older database with `users` and `stud` tables, run `python migrate_school.py` instead of the fresh database schema command. The migration adds school columns without dropping existing student records. Neither path creates an admin account. To create the first admin, set `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD` in your local terminal, then run `python bootstrap_admin.py`. The bootstrap script hashes the password and does not publish it in source code. Existing accounts can be promoted using the same script. This bootstrap admin signs in using the configured email; the local demo database has a separate `admin` username. See [SCHOOL_MVP.md](SCHOOL_MVP.md) for more context.

## Verification

```powershell
cd frontend
npm run build
```

For the isolated backend check, run `python -m unittest test_school_mvp -v` with `DATABASE_URL=sqlite+pysqlite:///:memory:` in the environment. It does not touch PostgreSQL.

## Roadmap

- Admin and student views for attendance and subject marks
- Homework and fees workflows
- Safer first-login password change and account recovery
- Managed database migrations and deployment

No real student data or local database credentials belong in this repository.
