"""
modules/2_slots.py
--------------------
Module 2 of 8: Parking slot management.

Responsible for the visual display of which slots are free/occupied,
finding a free slot, and marking slots occupied/free as vehicles come
and go.
"""

import importlib

db = importlib.import_module("database.db")


def get_all_slots():
    """
    Return the status of every slot, e.g.:
    [{"slot_number": 1, "is_occupied": False}, ...]
    This is what the slots.html page displays to drivers.
    """
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT slot_number, is_occupied FROM slots ORDER BY slot_number")
    rows = cursor.fetchall()
    connection.close()

    return [
        {"slot_number": row["slot_number"], "is_occupied": bool(row["is_occupied"])}
        for row in rows
    ]


def count_available_slots():
    """Return how many slots are currently free."""
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) AS free_count FROM slots WHERE is_occupied = 0")
    result = cursor.fetchone()["free_count"]
    connection.close()
    return result


def find_free_slot():
    """Find the first available slot number, or None if the lot is full."""
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT slot_number FROM slots WHERE is_occupied = 0 ORDER BY slot_number LIMIT 1"
    )
    row = cursor.fetchone()
    connection.close()
    return row["slot_number"] if row else None


def occupy_slot(slot_number):
    """Mark a slot as occupied (called when a vehicle enters it)."""
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE slots SET is_occupied = 1 WHERE slot_number = ?", (slot_number,))
    connection.commit()
    connection.close()


def free_slot(slot_number):
    """Mark a slot as free again (called when a vehicle exits)."""
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE slots SET is_occupied = 0 WHERE slot_number = ?", (slot_number,))
    connection.commit()
    connection.close()
