"""
auth.py  –  Application-level user authentication
Stores app users in DEV.VS_APP_USERS table (separate from Oracle DB users).
Passwords are hashed with bcrypt — plaintext is never stored.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets

import oracledb

logger = logging.getLogger(__name__)

# Table lives in the same schema as the rest of the app
_SCHEMA   = os.environ.get("ORA_SCHEMA", "DEV").upper()
_APP_USERS = f"{_SCHEMA}.VS_APP_USERS"


# ─────────────────────────────────────────────────────────
#  Password hashing  (PBKDF2-HMAC-SHA256 via stdlib)
#  No bcrypt dependency — works out of the box on Python 3.14
# ─────────────────────────────────────────────────────────
_ITERATIONS = 260_000   # OWASP 2024 recommendation for PBKDF2-SHA256

def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Return (hashed_hex, salt_hex). Generate salt if not provided."""
    if salt is None:
        salt = secrets.token_hex(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        _ITERATIONS,
    )
    return key.hex(), salt


def _verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    candidate, _ = _hash_password(password, salt)
    return hmac.compare_digest(candidate, stored_hash)


# ─────────────────────────────────────────────────────────
#  DDL
# ─────────────────────────────────────────────────────────
def ensure_users_table(conn: oracledb.Connection) -> None:
    """Create VS_APP_USERS if it doesn't exist, then seed a default admin."""
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM all_tables "
        "WHERE owner = :s AND table_name = 'VS_APP_USERS'",
        {"s": _SCHEMA},
    )
    if cur.fetchone()[0] == 0:
        cur.execute(f"""
            CREATE TABLE {_APP_USERS} (
                id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                username     VARCHAR2(100) NOT NULL,
                password_hash VARCHAR2(200) NOT NULL,
                salt         VARCHAR2(100) NOT NULL,
                full_name    VARCHAR2(200),
                is_active    NUMBER(1) DEFAULT 1 NOT NULL,
                created_at   TIMESTAMP DEFAULT SYSTIMESTAMP,
                last_login   TIMESTAMP,
                CONSTRAINT uq_vs_username UNIQUE (username)
            )
        """)
        conn.commit()
        logger.info("Created table %s", _APP_USERS)

        # Seed default admin — force password change on first login
        _create_user(conn, "admin", "Admin@1234", "Administrator")
        logger.info("Seeded default admin user (username=admin) — change password on first login")


# ─────────────────────────────────────────────────────────
#  User management
# ─────────────────────────────────────────────────────────
def _create_user(
    conn: oracledb.Connection,
    username: str,
    password: str,
    full_name: str = "",
) -> None:
    pw_hash, salt = _hash_password(password)
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {_APP_USERS} (username, password_hash, salt, full_name) "
        f"VALUES (:u, :h, :s, :f)",
        {"u": username.lower().strip(), "h": pw_hash, "s": salt, "f": full_name},
    )
    conn.commit()
    logger.info("Created app user: %s", username)


def create_user(conn: oracledb.Connection, username: str, password: str, full_name: str = "") -> None:
    """Public wrapper — call from admin UI."""
    _create_user(conn, username, password, full_name)


def login(conn: oracledb.Connection, username: str, password: str) -> dict | None:
    """
    Verify credentials. Returns user dict on success, None on failure.
    Updates last_login timestamp on successful login.
    """
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT id, username, password_hash, salt, full_name, is_active
        FROM   {_APP_USERS}
        WHERE  username = :u
        """,
        {"u": username.lower().strip()},
    )
    row = cur.fetchone()
    if row is None:
        logger.warning("Login failed — unknown user: %s", username)
        return None

    user_id, uname, pw_hash, salt, full_name, is_active = row

    if not is_active:
        logger.warning("Login failed — inactive user: %s", username)
        return None

    if not _verify_password(password, pw_hash, salt):
        logger.warning("Login failed — wrong password: %s", username)
        return None

    # Update last_login
    cur.execute(
        f"UPDATE {_APP_USERS} SET last_login = SYSTIMESTAMP WHERE id = :id",
        {"id": user_id},
    )
    conn.commit()
    logger.info("Login success: %s", uname)
    return {"id": user_id, "username": uname, "full_name": full_name or uname}


def change_password(
    conn: oracledb.Connection,
    username: str,
    old_password: str,
    new_password: str,
) -> bool:
    """Return True if password changed successfully."""
    user = login(conn, username, old_password)
    if user is None:
        return False
    pw_hash, salt = _hash_password(new_password)
    cur = conn.cursor()
    cur.execute(
        f"UPDATE {_APP_USERS} SET password_hash=:h, salt=:s WHERE username=:u",
        {"h": pw_hash, "s": salt, "u": username.lower()},
    )
    conn.commit()
    logger.info("Password changed for: %s", username)
    return True
