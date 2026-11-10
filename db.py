"""MySQL connection helpers.

Reads credentials from env vars. Locally these come from .env (loaded in app.py).
On Railway, either set DB_* vars yourself or reference the MySQL service's
MYSQL* vars, which are used as a fallback.
"""
import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling

_pool = None


def _env(primary, fallback, default=None):
    return os.getenv(primary) or os.getenv(fallback) or default


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="app_pool",
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            host=_env("DB_HOST", "MYSQLHOST", "localhost"),
            port=int(_env("DB_PORT", "MYSQLPORT", "3306")),
            user=_env("DB_USER", "MYSQLUSER", "root"),
            password=_env("DB_PASSWORD", "MYSQLPASSWORD", ""),
            database=_env("DB_NAME", "MYSQLDATABASE", "auto_repair_db"),
            autocommit=False,
        )
    return _pool


def get_connection():
    return get_pool().get_connection()


def query(sql, params=None, one=False):
    """Run a SELECT and return rows as dicts (or a single dict / None if one=True)."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        if one:
            return rows[0] if rows else None
        return rows
    finally:
        conn.close()


def execute(sql, params=None):
    """Run a single INSERT/UPDATE/DELETE and commit. Returns lastrowid."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def describe_error(err):
    """Turn a known MySQL constraint error into (field, friendly_message).

    field is the form field to attach the message to, or None for a page-level
    message. Anything we don't recognize is re-raised so it shows up as a 500
    and in the logs instead of being silently swallowed.
    """
    msg = str(err).lower()
    if err.errno == 1062:  # duplicate entry on a UNIQUE column
        if "email" in msg:
            return "email", "That email is already in use by another customer."
        if "vin" in msg:
            return "vin", "A vehicle with that VIN already exists."
        return None, "That record already exists."
    if err.errno == 1451:  # delete blocked by a foreign key (ON DELETE RESTRICT)
        return None, "Can't delete this because other records still reference it. Delete those first."
    if err.errno == 1452:  # insert/update points at a row that doesn't exist
        if "customer_id" in msg:
            return "customer_id", "That customer doesn't exist."
        if "vehicle_id" in msg:
            return "vehicle_id", "That vehicle doesn't exist."
        return None, "A referenced record doesn't exist."
    if err.errno == 3819:  # CHECK constraint failed
        return None, "A value failed a database check. Double check the numbers you entered."
    raise err


@contextmanager
def transaction():
    """Multi-statement transaction. Commits on success, rolls back on any exception.

    Usage:
        with transaction() as cur:
            cur.execute("UPDATE ...", (...,))
            cur.execute("INSERT ...", (...,))
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
