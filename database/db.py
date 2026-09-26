"""
database/db.py
---------------
Shared database connection, schema, and clock for the whole system.

Every module in modules/ imports get_connection() from here, so there is
only ONE place that talks directly to SQLite, and only ONE clock
function (now / now_str) that every module uses for timestamps. That is
what keeps time consistent across the entire application.
"""

import os
import sqlite3
from datetime import datetime

# The database file lives in the database/ folder, next to this script.
DB_PATH = os.path.join(os.path.dirname(__file__), "parking.db")

TOTAL_SLOTS = 20  # Total number of parking slots in this parking lot


# ---------------------------------------------------------------------
# SHARED CLOCK — every module must use these instead of datetime.now()
# ---------------------------------------------------------------------
def now():
    """The single shared clock for the entire system."""
    return datetime.now()


def now_str():
    """Current time as a text string, ready to store in SQLite."""
    return now().strftime("%Y-%m-%d %H:%M:%S")


def parse_time(time_string):
    """Turn a stored time string back into a real datetime object."""
    return datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------
# CONNECTION
# ---------------------------------------------------------------------
def get_connection():
    """
    Open a connection to the SQLite database.
    row_factory lets modules read columns by name, e.g. row["plate_number"].
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ---------------------------------------------------------------------
# SCHEMA
# ---------------------------------------------------------------------
def init_db():
    """
    Create every table the system needs, if they don't already exist,
    and seed the slots table and a default admin account. Safe to run
    every time the app starts.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # Users — for module 1 (auth)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'attendant',
            created_at TEXT NOT NULL
        )
    """)

    # Slots — for module 2 (slots)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slots (
            slot_number INTEGER PRIMARY KEY,
            is_occupied INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Vehicles — for module 3 (vehicles)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE NOT NULL,
            owner_name TEXT,
            vehicle_type TEXT,
            registered_at TEXT NOT NULL
        )
    """)

    # Sessions — one row per parking visit, used by modules 4 and 5 (entry/exit)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            plate_number TEXT NOT NULL,
            slot_number INTEGER NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            fee_charged INTEGER,
            is_paid INTEGER NOT NULL DEFAULT 0,
            payment_method TEXT,
            status TEXT NOT NULL DEFAULT 'PARKED',
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (vehicle_id)
        )
    """)

    # Payments — for module 6 (payment)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            method TEXT NOT NULL,
            mpesa_receipt TEXT,
            paid_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
    """)

    # Seed the 20 parking slots, only once.
    cursor.execute("SELECT COUNT(*) AS count FROM slots")
    if cursor.fetchone()["count"] == 0:
        for slot_number in range(1, TOTAL_SLOTS + 1):
            cursor.execute(
                "INSERT INTO slots (slot_number, is_occupied) VALUES (?, 0)",
                (slot_number,)
            )

    connection.commit()
    connection.close()

    _create_default_admin()


def _create_default_admin():
    """
    Create a default admin login (Sawyer / amon1234) the first time the
    app runs, so there is always a way to log in. Imported here (not at
    the top of the file) to avoid a circular import with modules/1_auth.py,
    which itself imports get_connection() from this file.
    """
    import importlib
    auth = importlib.import_module("modules.1_auth")
    auth.create_default_admin_if_missing()
