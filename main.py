
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from schemas import StudentCreate, StudentUpdate, StudentResponse
from models import Student
from auth import router as auth_router, require_admin, jwt_settings
from school import router as school_router
from fastapi.middleware.cors import CORSMiddleware
import services


@asynccontextmanager
async def lifespan(app: FastAPI):
    jwt_settings()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(school_router)


# CREATE student
@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db)
):
    return services.create_student(db, data)


# READ all students
@app.get("/students", response_model=list[StudentResponse], dependencies=[Depends(require_admin)])
def get_students(db: Session = Depends(get_db)):
    return services.list_students(db)


# READ student by ID
@app.get("/students/{student_id}", response_model=StudentResponse, dependencies=[Depends(require_admin)])
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    return services.find_student(db, student_id)


# UPDATE student
@app.put("/students/{student_id}", response_model=StudentResponse, dependencies=[Depends(require_admin)])
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db)
):
    student = services.find_student(db, student_id)
    if student.user_id is not None:
        raise HTTPException(status_code=403, detail="Student details are locked after creation; only the password can be reset")
    return services.update_student(db, student_id, data)


# DELETE student
@app.delete(
    "/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    services.delete_student(db, student_id)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
