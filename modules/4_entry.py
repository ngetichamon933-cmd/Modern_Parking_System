"""
modules/4_entry.py
--------------------
Module 4 of 8: Vehicle entry.

When a vehicle arrives: register/look up the vehicle (module 3), find a
free slot (module 2), and open a new parking session with the entry
time taken from the shared clock (database/db.py), so it lines up with
every other timestamp in the system.
"""

import importlib

db = importlib.import_module("database.db")
vehicles = importlib.import_module("modules.3_vehicles")
slots = importlib.import_module("modules.2_slots")


def record_entry(plate_number, owner_name=None, vehicle_type=None):
    """
    Register a vehicle entering the parking lot.

    Returns a dictionary describing the result:
      - Success: {"success": True, "session_id", "slot_number", "entry_time", "plate_number"}
      - Failure: {"success": False, "message": "..."}
    """
    if not plate_number or not plate_number.strip():
        return {"success": False, "message": "Plate number is required."}

    slot_number = slots.find_free_slot()
    if slot_number is None:
        return {"success": False, "message": "Parking lot is full. No slots available."}

    vehicle = vehicles.register_vehicle(plate_number, owner_name, vehicle_type)
    entry_time = db.now_str()

    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO sessions (vehicle_id, plate_number, slot_number, entry_time, status)
        VALUES (?, ?, ?, ?, 'PARKED')
        """,
        (vehicle["vehicle_id"], vehicle["plate_number"], slot_number, entry_time)
    )
    session_id = cursor.lastrowid
    connection.commit()
    connection.close()

    slots.occupy_slot(slot_number)

    return {
        "success": True,
        "session_id": session_id,
        "plate_number": vehicle["plate_number"],
        "slot_number": slot_number,
        "entry_time": entry_time
    }


def get_active_session(plate_number):
    """
    Find the current (still parked) session for a plate number.
    Used by module 5 (exit) when a vehicle wants to leave.
    """
    plate_number = plate_number.strip().upper()

    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM sessions
        WHERE plate_number = ? AND status = 'PARKED'
        ORDER BY entry_time DESC LIMIT 1
        """,
        (plate_number,)
    )
    row = cursor.fetchone()
    connection.close()

    return dict(row) if row else None


def get_session_by_id(session_id):
    """Look up any session (parked or completed) by its id."""
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    connection.close()
    return dict(row) if row else None
