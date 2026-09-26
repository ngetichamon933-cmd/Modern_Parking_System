"""
modules/8_reports.py
----------------------
Module 8 of 8: Reports and dashboard statistics for management.

Provides the numbers shown on dashboard.html and reports.html: today's
revenue, vehicles served, current occupancy, and a short list of recent
activity.
"""

import importlib

db = importlib.import_module("database.db")


def get_today_revenue():
    """Total Kshs collected today (sum of today's payments)."""
    today = db.now().strftime("%Y-%m-%d")

    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE paid_at LIKE ?",
        (f"{today}%",)
    )
    total = cursor.fetchone()["total"]
    connection.close()
    return total


def get_today_vehicle_count():
    """How many vehicles have entered the parking lot today."""
    today = db.now().strftime("%Y-%m-%d")

    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) AS count FROM sessions WHERE entry_time LIKE ?",
        (f"{today}%",)
    )
    count = cursor.fetchone()["count"]
    connection.close()
    return count


def get_occupancy_summary():
    """How many slots are occupied vs total, for a quick dashboard stat."""
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM slots")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS occupied FROM slots WHERE is_occupied = 1")
    occupied = cursor.fetchone()["occupied"]
    connection.close()

    return {"total_slots": total, "occupied_slots": occupied, "free_slots": total - occupied}


def get_recent_sessions(limit=10):
    """Return the most recent parking sessions (parked or completed)."""
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM sessions ORDER BY entry_time DESC LIMIT ?", (limit,)
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_daily_report():
    """Combine the above into one report dictionary for the dashboard/reports page."""
    return {
        "date": db.now().strftime("%Y-%m-%d"),
        "revenue_today": get_today_revenue(),
        "vehicles_today": get_today_vehicle_count(),
        "occupancy": get_occupancy_summary(),
        "recent_sessions": get_recent_sessions()
    }
