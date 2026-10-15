# School MVP notes

This is an in-progress school management portal. The frontend currently covers an admin dashboard, student creation, password reset, and a student's own profile. Attendance, marks, homework, and fees need frontend workflows in a later phase.

The admin can create student records for classes 1 through 10. The backend assigns an admission number from the admission year (`2026-001`) and a separate login ID from the student's name and birth year (`aaravmehta2019`). A numeric suffix resolves duplicate login IDs. Section and student email are no longer requested in the new student form.

The admin shares the initial password manually. Argon2 hashes are stored; existing passwords cannot be viewed. Created student details and IDs are read-only, while the admin can reset a password through **View / Password**. The student dashboard loads records linked to the authenticated user.

`migration_school.sql` and `migrate_school.py` add the school columns to the original `users` and `stud` tables without dropping records. Back up the database before applying migrations. `migrate_demo_ids.py` and `migrate_demo_logins.py` were one-time guarded changes for five fictional demo records in the local database and are not part of normal setup.

Never commit real database credentials, JWT secrets, student data, or password lists. Email automation and managed migrations remain future work.
