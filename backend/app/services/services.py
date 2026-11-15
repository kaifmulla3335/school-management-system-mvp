from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services import repository
from app.schemas import StudentCreate, StudentUpdate


def create_student(db: Session, data: StudentCreate):
    return repository.create(db, data)


def list_students(db: Session):
    return repository.get_all(db)


def find_student(db: Session, student_id: int):
    student = repository.get_by_id(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def update_student(db: Session, student_id: int, data: StudentUpdate):
    student = find_student(db, student_id)
    return repository.update(db, student, data)


def delete_student(db: Session, student_id: int):
    student = find_student(db, student_id)
    linked_user = student.user
    db.delete(student)
    db.flush()
    if linked_user is not None:
        db.delete(linked_user)
    db.commit()