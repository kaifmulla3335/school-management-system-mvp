from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.database import get_db
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
from app.services import services

router = APIRouter(tags=["students"])


@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    return services.create_student(db, data)


@router.get("/students", response_model=list[StudentResponse], dependencies=[Depends(require_admin)])
def get_students(db: Session = Depends(get_db)):
    return services.list_students(db)


@router.get("/students/{student_id}", response_model=StudentResponse, dependencies=[Depends(require_admin)])
def get_student(student_id: int, db: Session = Depends(get_db)):
    return services.find_student(db, student_id)


@router.put("/students/{student_id}", response_model=StudentResponse, dependencies=[Depends(require_admin)])
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = services.find_student(db, student_id)
    if student.user_id is not None:
        raise HTTPException(status_code=403, detail="Student details are locked after creation; only the password can be reset")
    return services.update_student(db, student_id, data)


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    services.delete_student(db, student_id)