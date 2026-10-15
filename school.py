from fastapi import APIRouter, Depends, HTTPException, status
import re
import unicodedata
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import get_current_user, password_hash, require_admin
from database import get_db
from models import Attendance, Homework, Mark, Student, User
from schemas import (
    AttendanceResponse, AttendanceWrite, HomeworkResponse, HomeworkWrite,
    MarkResponse, MarkWrite, RoleUpdate, StudentAccountCreate, StudentPasswordReset,
    StudentResponse, UserResponse,
)

router = APIRouter(tags=["school"])


@router.get("/admin/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).order_by(User.id).all()


@router.put("/admin/users/{user_id}/role", response_model=UserResponse)
def set_role(user_id: int, data: RoleUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    target = db.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == admin.id and data.role != "admin":
        raise HTTPException(status_code=400, detail="You cannot remove your own admin role")
    if data.role == "student" and target.student is None:
        raise HTTPException(status_code=400, detail="A student role requires a linked student record")
    target.role = data.role
    db.commit()
    db.refresh(target)
    return target


def existing_student(db: Session, student_id: int) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/admin/student-accounts", response_model=StudentResponse, status_code=201)
def create_student_account(data: StudentAccountCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    year = data.admission_date.year
    # Serialize admission numbers and name-based login IDs on PostgreSQL.
    if db.bind.dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": 2026001})
    numbers = db.query(Student.admission_number).filter(Student.admission_number.like(f"{year}-%")).all()
    sequence = max((int(value.split("-")[1]) for (value,) in numbers
                    if value and value.split("-")[1].isdigit()), default=0) + 1
    admission_number = f"{year}-{sequence:03d}"
    name_key = re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", data.name).encode("ascii", "ignore").decode().lower()) or "student"
    base_login = f"{name_key}{data.date_of_birth.year}"
    login_id = base_login
    suffix = 2
    while db.query(User).filter((User.username == login_id) | (User.email == login_id)).first():
        login_id = f"{base_login}{suffix}"
        suffix += 1
    user = User(username=login_id, role="student", hashed_password=password_hash.hash(data.password))
    student = Student(name=data.name, course=data.class_name, class_name=data.class_name,
                      roll_number=data.roll_number, admission_number=admission_number,
                      date_of_birth=data.date_of_birth, gender=data.gender,
                      guardian_name=data.guardian_name, guardian_phone=data.guardian_phone,
                      address=data.address, admission_date=data.admission_date, user=user)
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Login ID or student details conflict")
    db.refresh(student)
    return student


@router.put("/admin/students/{student_id}/password")
def reset_student_password(student_id: int, data: StudentPasswordReset,
                           db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    student = existing_student(db, student_id)
    if student.user is None or student.user.role != "student":
        raise HTTPException(status_code=400, detail="This student has no student login account")
    student.user.hashed_password = password_hash.hash(data.password)
    db.commit()
    return {"detail": "Student password reset"}


@router.put("/admin/attendance", response_model=AttendanceResponse)
def save_attendance(data: AttendanceWrite, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    existing_student(db, data.student_id)
    row = db.query(Attendance).filter_by(student_id=data.student_id, day=data.day).first()
    if row is None:
        row = Attendance(student_id=data.student_id, day=data.day)
        db.add(row)
    row.status = data.status
    db.commit()
    db.refresh(row)
    return row


@router.put("/admin/marks", response_model=MarkResponse)
def save_mark(data: MarkWrite, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    existing_student(db, data.student_id)
    row = db.query(Mark).filter_by(student_id=data.student_id, subject=data.subject, exam=data.exam).first()
    if row is None:
        row = Mark(student_id=data.student_id, subject=data.subject, exam=data.exam)
        db.add(row)
    row.score = data.score
    row.maximum = data.maximum
    db.commit()
    db.refresh(row)
    return row


@router.post("/admin/homework", response_model=HomeworkResponse, status_code=201)
def create_homework(data: HomeworkWrite, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    existing_student(db, data.student_id)
    row = Homework(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/admin/students/{student_id}/school")
def admin_student_school(student_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return school_records(db, existing_student(db, student_id))


def school_records(db: Session, student: Student):
    return {
        "profile": StudentResponse.model_validate(student),
        "attendance": db.query(Attendance).filter_by(student_id=student.id).order_by(Attendance.day.desc()).all(),
        "marks": db.query(Mark).filter_by(student_id=student.id).order_by(Mark.exam, Mark.subject).all(),
        "homework": db.query(Homework).filter_by(student_id=student.id).order_by(Homework.due_date).all(),
    }


@router.get("/student/dashboard")
def student_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="No student record linked to this account")
    return school_records(db, student)
