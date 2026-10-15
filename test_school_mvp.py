"""Small isolated data and permission check; does not touch Stud_db."""
import unittest
from datetime import date

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from auth import password_hash, require_admin
from database import Base
from models import User
from main import update_student
from school import create_student_account, create_homework, reset_student_password, save_attendance, save_mark, student_dashboard
from schemas import AttendanceWrite, HomeworkWrite, MarkWrite, StudentAccountCreate, StudentPasswordReset, StudentUpdate


class SchoolMvpTest(unittest.TestCase):
    def test_account_link_and_isolation(self):
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            admin = User(email="admin@example.com", role="admin", hashed_password="unused")
            db.add(admin)
            db.commit()
            first = create_student_account(StudentAccountCreate(
                name="First", class_name="8",
                roll_number="1", date_of_birth=date(2013, 1, 1), gender="Female",
                guardian_name="Guardian One", guardian_phone="1234567890", address="One Street",
                admission_date=date(2026, 10, 15), password="password123"
            ), db, admin)
            second = create_student_account(StudentAccountCreate(
                name="Second", class_name="8",
                roll_number="2", date_of_birth=date(2013, 2, 1), gender="Male",
                guardian_name="Guardian Two", guardian_phone="1234567891", address="Two Street",
                admission_date=date(2026, 10, 15), password="password123"
            ), db, admin)
            duplicate_name = create_student_account(StudentAccountCreate(
                name="First", class_name="8", roll_number="3",
                date_of_birth=date(2013, 3, 1), gender="Male",
                guardian_name="Guardian Three", guardian_phone="1234567892", address="Three Street",
                admission_date=date(2026, 10, 15), password="password123"
            ), db, admin)
            first_user = db.get(User, first.user_id)
            second_user = db.get(User, second.user_id)
            self.assertEqual(first.admission_number, "2026-001")
            self.assertEqual(second.admission_number, "2026-002")
            self.assertEqual(first_user.username, "first2013")
            self.assertEqual(second_user.username, "second2013")
            self.assertEqual(duplicate_name.login_id, "first20132")
            self.assertEqual(duplicate_name.admission_number, "2026-003")
            with self.assertRaises(HTTPException) as locked:
                update_student(first.id, StudentUpdate(name="Changed", email=None, course="8"), db)
            self.assertEqual(locked.exception.status_code, 403)
            self.assertEqual(first_user.role, "student")
            self.assertNotEqual(first_user.hashed_password, "password123")
            reset_student_password(first.id, StudentPasswordReset(password="first@1234"), db, admin)
            self.assertTrue(password_hash.verify("first@1234", first_user.hashed_password))
            self.assertNotEqual(first_user.hashed_password, "first@1234")
            self.assertEqual(first_user.student.id, first.id)
            with self.assertRaises(HTTPException) as denied:
                require_admin(first_user)
            self.assertEqual(denied.exception.status_code, 403)

            save_attendance(AttendanceWrite(student_id=first.id, day=date(2026, 10, 15), status="Present"), db, admin)
            save_mark(MarkWrite(student_id=first.id, subject="Math", exam="Term 1", score=80, maximum=100), db, admin)
            create_homework(HomeworkWrite(student_id=first.id, title="Practice", description="Page 5", subject="Math", due_date=date(2026, 10, 20)), db, admin)
            own = student_dashboard(db, first_user)
            other = student_dashboard(db, second_user)
            self.assertEqual(own["profile"].id, first.id)
            self.assertEqual(len(own["attendance"]), 1)
            self.assertEqual(len(own["marks"]), 1)
            self.assertEqual(len(own["homework"]), 1)
            self.assertEqual(other["profile"].id, second.id)
            self.assertEqual(other["attendance"], [])
            self.assertEqual(other["marks"], [])
            self.assertEqual(other["homework"], [])


if __name__ == "__main__":
    unittest.main()
