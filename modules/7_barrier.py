"""
modules/7_barrier.py
----------------------
Module 7 of 8: Controls the physical entry/exit barrier.

In a real installation this would send a signal to hardware (e.g. a
relay wired to a motor/servo via GPIO pins on a Raspberry Pi). That
call is kept in one small, clearly-marked function so it can be swapped
for real GPIO code later without touching anything else in the system.
"""

import importlib

db = importlib.import_module("database.db")


def _send_signal_to_hardware(action):
    """
    Placeholder for the real hardware call (e.g. GPIO.output(PIN, HIGH)).
    Replace this function's body with real hardware control code when
    wiring the system to a physical barrier.
    """
    print(f"[BARRIER HARDWARE] Signal sent: {action}")


def open_barrier(reason="vehicle authorized"):
    """Open the barrier (on entry, or on exit after successful payment)."""
    _send_signal_to_hardware("OPEN")
    return {"status": "OPEN", "reason": reason, "time": db.now_str()}


def close_barrier():
    """Close the barrier after the vehicle has passed through."""
    _send_signal_to_hardware("CLOSE")
    return {"status": "CLOSED", "time": db.now_str()}


def allow_exit_if_paid(session):
    """
    Business rule: the barrier only opens for exit once the session is
    marked paid. Takes a session dictionary and returns whether it opened.
    """
    if session.get("is_paid"):
        return open_barrier(reason="payment confirmed")
    return {"status": "CLOSED", "reason": "payment required before exit"}
