from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Student(Base):
    __tablename__ = "stud"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(150), unique=True, index=True, nullable=True)
    course: Mapped[str] = mapped_column(String(100))
    class_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    roll_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    admission_number: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True)
    section: Mapped[str | None] = mapped_column(String(10), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    guardian_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guardian_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    admission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    user: Mapped["User | None"] = relationship(back_populates="student")

    @property
    def login_id(self) -> str | None:
        return self.user.username if self.user else None


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str | None] = mapped_column(String(150), unique=True, index=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(80), unique=True, index=True, nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    hashed_password: Mapped[str] = mapped_column(String(255))
    student: Mapped["Student | None"] = relationship(back_populates="user", uselist=False)


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("student_id", "day"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("stud.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(10))
    student: Mapped[Student] = relationship()


class Mark(Base):
    __tablename__ = "marks"
    __table_args__ = (UniqueConstraint("student_id", "subject", "exam"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("stud.id", ondelete="CASCADE"))
    subject: Mapped[str] = mapped_column(String(100))
    exam: Mapped[str] = mapped_column(String(100))
    score: Mapped[float] = mapped_column()
    maximum: Mapped[float] = mapped_column()
    student: Mapped[Student] = relationship()


class Homework(Base):
    __tablename__ = "homework"
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("stud.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(2000))
    subject: Mapped[str] = mapped_column(String(100))
    due_date: Mapped[date] = mapped_column(Date)
    student: Mapped[Student] = relationship()
