"""
modules/3_vehicles.py
-----------------------
Module 3 of 8: Vehicle registration and records.

Keeps a simple record of every vehicle that has ever used the parking
lot (plate number, optional owner name, optional vehicle type), so
module 4 (entry) can look a vehicle up or register it the first time
it arrives.
"""

import importlib

db = importlib.import_module("database.db")


def get_vehicle_by_plate(plate_number):
    """Return the vehicle record for a plate number, or None if unknown."""
    plate_number = plate_number.strip().upper()

    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM vehicles WHERE plate_number = ?", (plate_number,))
    row = cursor.fetchone()
    connection.close()

    return dict(row) if row else None


def register_vehicle(plate_number, owner_name=None, vehicle_type=None):
    """
    Register a new vehicle, or return its existing record if the plate
    number is already known. This is what module 4 (entry) calls every
    time a vehicle arrives, so a vehicle only needs to be entered once.
    """
    plate_number = plate_number.strip().upper()
    existing = get_vehicle_by_plate(plate_number)
    if existing:
        return existing

    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO vehicles (plate_number, owner_name, vehicle_type, registered_at)
        VALUES (?, ?, ?, ?)
        """,
        (plate_number, owner_name, vehicle_type, db.now_str())
    )
    vehicle_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return {
        "vehicle_id": vehicle_id,
        "plate_number": plate_number,
        "owner_name": owner_name,
        "vehicle_type": vehicle_type
    }


def list_vehicles():
    """Return every vehicle ever registered, most recent first."""
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM vehicles ORDER BY registered_at DESC")
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]
