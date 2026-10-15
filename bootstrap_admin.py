"""Promote an existing email account, or create the first admin offline."""
import os

from sqlalchemy import text
from pwdlib import PasswordHash

from database import engine

email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
if not email:
    raise SystemExit("Set BOOTSTRAP_ADMIN_EMAIL to an existing account email")

with engine.begin() as connection:
    result = connection.execute(
        text("UPDATE users SET role = 'admin' WHERE lower(email) = :email"),
        {"email": email},
    )
    if result.rowcount > 1:
        raise SystemExit("Multiple case-insensitive email matches found; no role change committed")
    if result.rowcount == 0:
        password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "")
        if len(password) < 8:
            raise SystemExit("Account not found. Set BOOTSTRAP_ADMIN_PASSWORD (at least 8 characters) to create it")
        connection.execute(
            text("INSERT INTO users (email, hashed_password, role) VALUES (:email, :hash, 'admin')"),
            {"email": email, "hash": PasswordHash.recommended().hash(password)},
        )

print("Admin account ready")
