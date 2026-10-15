"""One-time rename of the five fictional demo IDs; preserves all other records."""
from database import SessionLocal
from models import Student, User


def main():
    with SessionLocal() as db:
        rows = db.query(Student).filter(Student.admission_number.like("DEMO-2026-%")).all()
        expected = {f"DEMO-2026-{index:03d}": f"2026-{index:03d}" for index in range(1, 6)}
        if {row.admission_number for row in rows} != set(expected):
            raise RuntimeError("Demo records differ from the expected five; no changes made")
        for row in rows:
            new_id = expected[row.admission_number]
            if row.user is None or db.query(Student).filter_by(admission_number=new_id).first() or db.query(User).filter_by(username=new_id).first():
                raise RuntimeError(f"Cannot safely assign {new_id}; no changes made")
            row.admission_number = new_id
            row.user.username = new_id
        db.commit()
        print("Updated five demo admission numbers and login IDs; passwords and profiles preserved.")


if __name__ == "__main__":
    main()
