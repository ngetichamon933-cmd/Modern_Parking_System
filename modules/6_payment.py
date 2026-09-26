"""
modules/6_payment.py
----------------------
Module 6 of 8: Payment processing — cash or M-Pesa (Safaricom Daraja
API, STK Push).

Design notes:
- Cash payments are marked paid immediately (a human collects the cash).
- M-Pesa payments call Safaricom's Daraja "STK Push" endpoint, which
  sends a prompt to the driver's phone asking them to enter their PIN.
- Daraja credentials are read from environment variables so this file
  never has secrets hard-coded in it. If they're missing, M-Pesa calls
  fail cleanly instead of crashing the app (cash payments still work).
"""

import os
import base64
import importlib
from datetime import datetime

import requests

db = importlib.import_module("database.db")
slots = importlib.import_module("modules.2_slots")
barrier = importlib.import_module("modules.7_barrier")

# --- Daraja (M-Pesa) configuration, loaded from environment variables ---
DARAJA_CONSUMER_KEY = os.environ.get("DARAJA_CONSUMER_KEY")
DARAJA_CONSUMER_SECRET = os.environ.get("DARAJA_CONSUMER_SECRET")
DARAJA_SHORTCODE = os.environ.get("DARAJA_SHORTCODE")
DARAJA_PASSKEY = os.environ.get("DARAJA_PASSKEY")
DARAJA_CALLBACK_URL = os.environ.get("DARAJA_CALLBACK_URL", "https://example.com/mpesa/callback")

# Safaricom's sandbox endpoint (switch to the api.safaricom.co.ke host in production)
DARAJA_BASE_URL = "https://sandbox.safaricom.co.ke"


def _get_access_token():
    """Ask Daraja for a temporary access token needed by every API call."""
    url = f"{DARAJA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(DARAJA_CONSUMER_KEY, DARAJA_CONSUMER_SECRET), timeout=10)
    response.raise_for_status()
    return response.json()["access_token"]


def _build_password_and_timestamp():
    """Daraja's STK Push password is base64(Shortcode + Passkey + Timestamp)."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw_password = f"{DARAJA_SHORTCODE}{DARAJA_PASSKEY}{timestamp}"
    password = base64.b64encode(raw_password.encode()).decode()
    return password, timestamp


def initiate_mpesa_payment(phone_number, amount, session_id):
    """
    Trigger an STK Push prompt on the driver's phone.
    phone_number must be in the format 2547XXXXXXXX.
    """
    if not all([DARAJA_CONSUMER_KEY, DARAJA_CONSUMER_SECRET, DARAJA_SHORTCODE, DARAJA_PASSKEY]):
        return {"success": False, "message": "M-Pesa credentials are not configured."}

    try:
        access_token = _get_access_token()
        password, timestamp = _build_password_and_timestamp()

        payload = {
            "BusinessShortCode": DARAJA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": DARAJA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": DARAJA_CALLBACK_URL,
            "AccountReference": f"PARKING-{session_id}",
            "TransactionDesc": "Parking fee payment"
        }
        headers = {"Authorization": f"Bearer {access_token}"}

        url = f"{DARAJA_BASE_URL}/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {"success": True, "checkout_request_id": data.get("CheckoutRequestID")}

    except requests.RequestException as error:
        return {"success": False, "message": f"M-Pesa request failed: {error}"}


def pay_with_cash(session_id, amount):
    """Record a cash payment and mark the session as paid immediately."""
    return _finalize_payment(session_id, amount, "CASH", mpesa_receipt=None)


def confirm_mpesa_payment(session_id, amount, mpesa_receipt):
    """
    Call once Safaricom's callback confirms payment succeeded (the Flask
    route that receives Daraja's callback calls this).
    """
    return _finalize_payment(session_id, amount, "MPESA", mpesa_receipt)


def _finalize_payment(session_id, amount, method, mpesa_receipt):
    """
    Shared final step for both cash and M-Pesa: record the payment,
    mark the session complete, free the slot, and open the barrier.
    """
    paid_at = db.now_str()

    connection = db.get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO payments (session_id, amount, method, mpesa_receipt, paid_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session_id, amount, method, mpesa_receipt, paid_at)
    )
    cursor.execute(
        """
        UPDATE sessions
        SET is_paid = 1, payment_method = ?, exit_time = ?, fee_charged = ?, status = 'COMPLETED'
        WHERE session_id = ?
        """,
        (method, paid_at, amount, session_id)
    )
    cursor.execute("SELECT slot_number FROM sessions WHERE session_id = ?", (session_id,))
    slot_number = cursor.fetchone()["slot_number"]

    connection.commit()
    connection.close()

    slots.free_slot(slot_number)
    barrier.open_barrier(reason="payment confirmed, vehicle exiting")

    return {"success": True, "method": method, "amount": amount, "paid_at": paid_at}
