"""
modules/1_auth.py
------------------
Module 1 of 8: Login and user management.

Handles: creating staff/admin accounts, checking a username+password at
login, and protecting pages so only logged-in staff can use them.

NOTE ON THE FILENAME: because this file starts with a digit, it cannot
be loaded with a normal "import modules.1_auth" statement (Python
identifiers cannot start with a digit). Every file that needs this
module loads it with importlib instead, e.g.:

    import importlib
    auth = importlib.import_module("modules.1_auth")

This is the only extra step the numbered filenames require — everything
else about the module works like a normal Python file.
"""

import importlib
from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

db = importlib.import_module("database.db")


def create_user(username, password, role="attendant"):
    """
    Create a new staff account. role is usually "attendant" or "admin".
    Returns {"success": True} or {"success": False, "message": "..."}.
    """
    if not username or not password:
        return {"success": False, "message": "Username and password are required."}
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters."}

    connection = db.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), role, db.now_str())
        )
        connection.commit()
        return {"success": True}
    except db.sqlite3.IntegrityError:
        return {"success": False, "message": "That username is already taken."}
    finally:
        connection.close()


def create_default_admin_if_missing():
    """
    Make sure there is always at least one admin account to log in with.
    Called once automatically when the database is first initialized.
    Default login: Sawyer / amon1234
    Change this password after first login for anything beyond a
    coursework/demo setting.
    """
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'admin'")
    has_admin = cursor.fetchone()["count"] > 0
    connection.close()

    if not has_admin:
        create_user("Sawyer", "amon1234", role="admin")


def authenticate(username, password):
    """
    Check a username/password pair.
    Returns the user's dict (without the password hash) on success, or
    None if the credentials are wrong.
    """
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()

    if user and check_password_hash(user["password_hash"], password):
        return {"id": user["id"], "username": user["username"], "role": user["role"]}
    return None


def login_required(view_function):
    """
    Decorator to protect a Flask route: redirects to /login if nobody
    is logged in. Usage:

        @app.route("/dashboard")
        @auth.login_required
        def dashboard():
            ...
    """
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)
    return wrapped_view


def get_current_user():
    """Return the logged-in user's basic info from the session, or None."""
    if "user_id" not in session:
        return None
    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "role": session.get("role")
    }
