"""
app.py
------
Moih Park Kenya — main Flask application.

This is the "front door" of the system: it renders the HTML pages,
handles form submissions, and calls the 8 modules in modules/ to do the
actual work. It does not contain business logic itself — it just wires
everything together.

Run with:
    python app.py
Then open http://localhost:5000 in a browser.
Default login: Sawyer / amon1234
"""

import importlib
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

# --- Load the 8 numbered modules -------------------------------------
# Their filenames start with digits (as required by the project layout),
# which Python's "import x.y" statement cannot parse, so every module
# (including this file) loads them by name through importlib instead.
auth = importlib.import_module("modules.1_auth")
slots = importlib.import_module("modules.2_slots")
vehicles = importlib.import_module("modules.3_vehicles")
entry = importlib.import_module("modules.4_entry")
exit_ = importlib.import_module("modules.5_exit")
payment = importlib.import_module("modules.6_payment")
barrier = importlib.import_module("modules.7_barrier")
reports = importlib.import_module("modules.8_reports")

db = importlib.import_module("database.db")

app = Flask(__name__)
app.secret_key = "moih-park-kenya-dev-secret-change-this-in-production"


# =======================================================================
# AUTH — module 1
# =======================================================================
@app.route("/", methods=["GET"])
def index():
    """Landing route: send logged-in users to the dashboard, others to login."""
    if auth.get_current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = auth.authenticate(username, password)

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# =======================================================================
# DASHBOARD
# =======================================================================
@app.route("/dashboard")
@auth.login_required
def dashboard():
    report = reports.get_daily_report()
    return render_template("dashboard.html", report=report, user=auth.get_current_user())


# =======================================================================
# SLOTS — module 2
# =======================================================================
@app.route("/slots")
@auth.login_required
def slots_page():
    return render_template(
        "slots.html",
        slots=slots.get_all_slots(),
        available_count=slots.count_available_slots(),
        user=auth.get_current_user()
    )


@app.route("/api/slots")
@auth.login_required
def api_slots():
    """JSON endpoint used by static/js/app.js to auto-refresh the slot grid."""
    return jsonify({
        "slots": slots.get_all_slots(),
        "available_count": slots.count_available_slots()
    })


# =======================================================================
# ENTRY — modules 3 and 4
# =======================================================================
@app.route("/entry", methods=["GET", "POST"])
@auth.login_required
def entry_page():
    if request.method == "POST":
        plate_number = request.form.get("plate_number", "")
        owner_name = request.form.get("owner_name") or None
        vehicle_type = request.form.get("vehicle_type") or None

        result = entry.record_entry(plate_number, owner_name, vehicle_type)
        if result["success"]:
            barrier.open_barrier(reason="new entry")
            flash(
                f"Vehicle {result['plate_number']} assigned to slot "
                f"{result['slot_number']} at {result['entry_time']}.",
                "success"
            )
        else:
            flash(result["message"], "error")

        return redirect(url_for("entry_page"))

    return render_template("entry.html", user=auth.get_current_user())


# =======================================================================
# EXIT — module 5
# =======================================================================
@app.route("/exit", methods=["GET", "POST"])
@auth.login_required
def exit_page():
    quote = None
    if request.method == "POST":
        plate_number = request.form.get("plate_number", "")
        quote = exit_.get_exit_quote(plate_number)
        if not quote["success"]:
            flash(quote["message"], "error")
            quote = None

    return render_template("exit.html", quote=quote, user=auth.get_current_user())


# =======================================================================
# PAYMENT — modules 6 and 7
# =======================================================================
@app.route("/payment/<int:session_id>")
@auth.login_required
def payment_page(session_id):
    parked_session, fee_or_error = exit_.get_payable_session(session_id)
    if parked_session is None:
        flash(fee_or_error["message"], "error")
        return redirect(url_for("exit_page"))

    return render_template(
        "payment.html",
        session=parked_session,
        amount=fee_or_error,
        user=auth.get_current_user()
    )


@app.route("/payment/<int:session_id>/cash", methods=["POST"])
@auth.login_required
def pay_cash(session_id):
    parked_session, fee_or_error = exit_.get_payable_session(session_id)
    if parked_session is None:
        flash(fee_or_error["message"], "error")
        return redirect(url_for("exit_page"))

    amount = fee_or_error
    payment.pay_with_cash(session_id, amount)
    flash(f"Cash payment of Kshs {amount} received. Barrier opened — safe travels!", "success")
    return redirect(url_for("dashboard"))


@app.route("/payment/<int:session_id>/mpesa", methods=["POST"])
@auth.login_required
def pay_mpesa(session_id):
    phone_number = request.form.get("phone_number", "")

    parked_session, fee_or_error = exit_.get_payable_session(session_id)
    if parked_session is None:
        flash(fee_or_error["message"], "error")
        return redirect(url_for("exit_page"))

    amount = fee_or_error

    if not (phone_number.isdigit() and phone_number.startswith("254") and len(phone_number) == 12):
        flash("Phone number must be in the format 2547XXXXXXXX.", "error")
        return redirect(url_for("payment_page", session_id=session_id))

    if amount == 0:
        # Free sessions don't need an M-Pesa prompt at all.
        payment.pay_with_cash(session_id, 0)
        flash("No fee due (under 30 minutes). Barrier opened — safe travels!", "success")
        return redirect(url_for("dashboard"))

    result = payment.initiate_mpesa_payment(phone_number, amount, session_id)
    if result["success"]:
        flash(f"M-Pesa prompt sent to {phone_number}. Ask the driver to enter their PIN.", "success")
    else:
        flash(result["message"], "error")

    return redirect(url_for("payment_page", session_id=session_id))


@app.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    """
    Endpoint Safaricom's Daraja API calls once the driver has entered
    their PIN and the payment succeeds or fails. In production,
    DARAJA_CALLBACK_URL (in modules/6_payment.py) must point to this
    exact route on a publicly reachable server. No login is required
    here because Safaricom's servers call it directly, not a browser.
    """
    data = request.get_json(force=True) or {}
    session_id = data.get("session_id")
    amount = data.get("amount")
    mpesa_receipt = data.get("mpesa_receipt", "UNKNOWN")

    if session_id is None or amount is None:
        return jsonify({"success": False, "message": "Invalid callback payload."}), 400

    result = payment.confirm_mpesa_payment(session_id, amount, mpesa_receipt)
    return jsonify(result), 200


# =======================================================================
# REPORTS — module 8
# =======================================================================
@app.route("/reports")
@auth.login_required
def reports_page():
    report = reports.get_daily_report()
    return render_template("reports.html", report=report, user=auth.get_current_user())


# =======================================================================
# APP STARTUP
# =======================================================================
if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
