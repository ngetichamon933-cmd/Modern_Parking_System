"""
modules/5_exit.py
--------------------
Module 5 of 8: Exit handling and parking-duration fee calculation.

Fee structure (Kenyan Shillings):
    up to 30 minutes -> Free (0)
    up to 2 hours     -> 50
    up to 4 hours      -> 100
    up to 6 hours      -> 300
    over 6 hours       -> 500

Uses the shared clock (database/db.py) for "now", so the duration is
always measured against the same clock that recorded the entry time.
"""

import importlib

db = importlib.import_module("database.db")
entry = importlib.import_module("modules.4_entry")


def calculate_duration_minutes(entry_time_str, exit_time_str=None):
    """
    How many minutes a vehicle has been parked. If exit_time_str is not
    given, measures up to the current time (vehicle still parked).
    """
    entry_time = db.parse_time(entry_time_str)
    exit_time = db.parse_time(exit_time_str) if exit_time_str else db.now()

    duration = exit_time - entry_time
    minutes = duration.total_seconds() / 60
    return max(minutes, 0)  # guard against clock/data issues producing negatives


def calculate_fee(entry_time_str, exit_time_str=None):
    """Work out the parking fee in Kshs, based on total minutes parked."""
    minutes = calculate_duration_minutes(entry_time_str, exit_time_str)
    hours = minutes / 60

    if minutes <= 30:
        fee = 0
    elif hours <= 2:
        fee = 50
    elif hours <= 4:
        fee = 100
    elif hours <= 6:
        fee = 300
    else:
        fee = 500

    return {"minutes_parked": round(minutes, 2), "hours_parked": round(hours, 2), "fee": fee}


def get_exit_quote(plate_number):
    """
    Look up a parked vehicle and calculate what it currently owes.
    This does NOT charge the fee — module 6 (payment) does that once the
    driver has chosen how to pay.
    """
    session = entry.get_active_session(plate_number)
    if not session:
        return {"success": False, "message": "No active session found for this plate."}

    fee_info = calculate_fee(session["entry_time"])
    return {
        "success": True,
        "session_id": session["session_id"],
        "plate_number": session["plate_number"],
        "slot_number": session["slot_number"],
        "entry_time": session["entry_time"],
        **fee_info
    }


def get_payable_session(session_id):
    """
    Look up a session by id, make sure it's still open, and recalculate
    its fee from entry_time (never trust a client-supplied amount).
    Returns (session_dict, fee) or (None, error_dict).
    """
    session = entry.get_session_by_id(session_id)
    if session is None:
        return None, {"message": "Session not found."}
    if session["status"] != "PARKED":
        return None, {"message": "This session is already completed."}

    fee_info = calculate_fee(session["entry_time"])
    return session, fee_info["fee"]
