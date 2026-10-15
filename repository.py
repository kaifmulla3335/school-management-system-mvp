
from sqlalchemy.orm import Session

from models import Student
from schemas import StudentCreate, StudentUpdate


# Get all students
def get_all(db: Session):
    return db.query(Student).all()


# Get student by ID
def get_by_id(db: Session, student_id: int):
    return (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )


# Create student
def create(db: Session, data: StudentCreate):
    student = Student(**data.model_dump())

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


# Update student
def update(
    db: Session,
    student: Student,
    data: StudentUpdate
):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)

    return student


# Delete student
def delete(db: Session, student: Student):
    db.delete(student)
    db.commit()
