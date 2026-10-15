"""One-time login rename for the five existing fictional demo students."""
import re
import unicodedata

from database import SessionLocal
from models import Student, User


def main():
    with SessionLocal() as db:
        ids = [f"2026-{index:03d}" for index in range(1, 6)]
        rows = db.query(Student).filter(Student.admission_number.in_(ids)).all()
        if {row.admission_number for row in rows} != set(ids):
            raise RuntimeError("Expected five demo records; no changes made")
        for row in rows:
            if row.user is None or row.user.username != row.admission_number or row.date_of_birth is None:
                raise RuntimeError("Demo login state differs; no changes made")
            name = re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", row.name).encode("ascii", "ignore").decode().lower())
            new_login = f"{name}{row.date_of_birth.year}"
            if db.query(User).filter((User.username == new_login) | (User.email == new_login)).first():
                raise RuntimeError(f"Login {new_login} already exists; no changes made")
            row.user.username = new_login
        db.commit()
        print("Updated five demo login IDs; admission numbers and passwords preserved.")


if __name__ == "__main__":
    main()
