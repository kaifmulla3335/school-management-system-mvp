# School Management System (MVP)

A school portal for classes 1 to 10. Backend: **FastAPI + PostgreSQL + SQLAlchemy + JWT (Argon2 password hashing)**. Frontend: **React + Vite + Tailwind CSS + React Router**.

> Status: work in progress, runs locally only (not deployed).

## Features

**Working now**
- Admin and student roles, enforced on the backend
- Login with a school login ID (students) or email (admin)
- Admin: view all students, add a student account in one step
- Automatic admission number (`2026-001`) and login ID from name + birth year (`aaravmehta2019`)
- Student dashboard showing only the student's own profile
- Backend APIs for attendance, marks, homework, role change and password reset (no frontend screens for these yet)

**Planned / not in the UI yet**
- Delete student and reset password screens (APIs already exist)
- Class-wise filter on the admin dashboard
- Attendance, marks, homework and fees screens

## Project structure

```
school-management-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, router registration
│   │   ├── config.py            # Reads .env (DATABASE_URL, JWT_SECRET, ...)
│   │   ├── api/                 # Routes: auth.py, students.py, school.py
│   │   ├── core/security.py     # JWT, password hash, get_current_user, require_admin
│   │   ├── db/                  # database.py (engine, session), models.py (tables)
│   │   ├── schemas/             # Pydantic request/response models
│   │   └── services/            # services.py (logic), repository.py (queries)
│   ├── scripts/bootstrap_admin.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Routes
│   │   ├── api/                 # axios.js, auth.js, students.js
│   │   ├── context/AuthContext.jsx
│   │   ├── routes/ProtectedRoute.jsx
│   │   ├── components/Sidebar.jsx
│   │   └── pages/               # Login, AdminDashboard, AddStudent, StudentDashboard
│   ├── vite.config.js
│   └── package.json
├── migration_school.sql         # Only for upgrading an OLD database
├── SCHOOL_MVP.md
└── README.md
```

Frontend routes: `/` (login), `/admin`, `/admin/add-student`, `/student`.

## Requirements

- Python 3.11+
- Node.js 18+
- PostgreSQL (create an empty database first)

## Run locally

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env                # macOS/Linux: cp .env.example .env
```

Edit `backend/.env`:

| Variable | Description |
|---|---|
| `DATABASE_URL` | e.g. `postgresql+psycopg://USER:PASSWORD@localhost:5432/DATABASE` |
| `JWT_SECRET` | Long random string. Generate: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Optional, default `30` |

Start the API (run from the `backend/` folder):

```powershell
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

Tables are created automatically on startup for a fresh database.

### 2. Create the first admin

```powershell
# still inside backend/
$env:BOOTSTRAP_ADMIN_EMAIL="admin@example.com"
$env:BOOTSTRAP_ADMIN_PASSWORD="choose-a-strong-password"
python scripts/bootstrap_admin.py
```

macOS/Linux:

```bash
BOOTSTRAP_ADMIN_EMAIL=admin@example.com BOOTSTRAP_ADMIN_PASSWORD=choose-a-strong-password python scripts/bootstrap_admin.py
```

If an account with that email already exists it is promoted to admin. Otherwise a new admin is created. Log in on the website with that email and password.

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend expects the API at `http://localhost:8000`, and the backend only allows requests from `http://localhost:5173`.

## Upgrading an old database

Only if you already have `users` and `stud` tables from the first version. This adds the school columns and keeps existing rows. Run it once from the project root:

```bash
psql -U USER -d DATABASE -f migration_school.sql
```

## Build check

```powershell
cd frontend
npm run build
```

## API overview

| Method | Path | Who | Purpose |
|---|---|---|---|
| POST | `/auth/login` | public | Get access token |
| GET | `/auth/me` | logged in | Current user |
| GET, POST | `/students` | admin | List / create student |
| GET, PUT, DELETE | `/students/{id}` | admin | Read / update / delete |
| POST | `/admin/student-accounts` | admin | Create student + login |
| PUT | `/admin/students/{id}/password` | admin | Reset student password |
| GET | `/admin/students/{id}/school` | admin | Student's full school record |
| GET | `/admin/users` | admin | List users |
| PUT | `/admin/users/{id}/role` | admin | Change role |
| PUT | `/admin/attendance` | admin | Save attendance |
| PUT | `/admin/marks` | admin | Save marks |
| POST | `/admin/homework` | admin | Add homework |
| GET | `/student/dashboard` | student | Own profile and records |

Full details are at `/docs` while the server is running.

## Security notes

- Never commit `.env` or real credentials (already in `.gitignore`).
- Passwords are stored only as Argon2 hashes. Initial passwords must be shared with students manually.
- Use a long random `JWT_SECRET` and back up the database before running migrations on real data.

See [SCHOOL_MVP.md](SCHOOL_MVP.md) for more product context.