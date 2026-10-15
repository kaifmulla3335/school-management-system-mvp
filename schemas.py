
from datetime import date
from typing import Literal
from pydantic import BaseModel, EmailStr, ConfigDict, Field, model_validator


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    course: str


class StudentUpdate(BaseModel):
    name: str
    email: EmailStr | None
    course: str
    class_name: str | None = None
    roll_number: str | None = None
    admission_number: str | None = None
    section: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    guardian_name: str | None = None
    guardian_phone: str | None = None
    address: str | None = None
    admission_date: date | None = None


class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr | None
    course: str
    class_name: str | None = None
    roll_number: str | None = None
    admission_number: str | None = None
    section: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    guardian_name: str | None = None
    guardian_phone: str | None = None
    address: str | None = None
    admission_date: date | None = None
    login_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    email: EmailStr | None
    username: str | None
    role: Literal["admin", "student"]

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    role: Literal["admin", "student"]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StudentAccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    class_name: Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    roll_number: str = Field(min_length=1, max_length=30)
    date_of_birth: date
    gender: Literal["Male", "Female", "Other"]
    guardian_name: str = Field(min_length=1, max_length=100)
    guardian_phone: str = Field(min_length=7, max_length=20)
    address: str = Field(min_length=1, max_length=500)
    admission_date: date
    password: str = Field(min_length=8, max_length=128)


class StudentPasswordReset(BaseModel):
    password: str = Field(min_length=8, max_length=128)


class AttendanceWrite(BaseModel):
    student_id: int
    day: date
    status: Literal["Present", "Absent"]


class AttendanceResponse(AttendanceWrite):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MarkWrite(BaseModel):
    student_id: int
    subject: str = Field(min_length=1, max_length=100)
    exam: str = Field(min_length=1, max_length=100)
    score: float = Field(ge=0)
    maximum: float = Field(gt=0)

    @model_validator(mode="after")
    def score_within_maximum(self):
        if self.score > self.maximum:
            raise ValueError("Score cannot exceed maximum")
        return self


class MarkResponse(MarkWrite):
    id: int
    model_config = ConfigDict(from_attributes=True)


class HomeworkWrite(BaseModel):
    student_id: int
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=2000)
    subject: str = Field(min_length=1, max_length=100)
    due_date: date


class HomeworkResponse(HomeworkWrite):
    id: int
    model_config = ConfigDict(from_attributes=True)
