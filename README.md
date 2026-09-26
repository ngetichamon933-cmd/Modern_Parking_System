# Moih Park Kenya

A web-based modern parking management system built with Flask and SQLite.
Drivers get a visual slot display before entry; the system records arrival,
calculates the fee automatically on exit, accepts cash or M-Pesa (Daraja
STK Push) payment, and opens the barrier once payment is confirmed.

## Fee Structure (Kshs)

| Duration        | Fee  |
|------------------|------|
| Up to 30 minutes | Free |
| Up to 2 hours    | 50   |
| Up to 4 hours    | 100  |
| Up to 6 hours    | 300  |
| Over 6 hours     | 500  |

## The 8 Modules

| # | File                     | Responsibility                                   |
|---|--------------------------|---------------------------------------------------|
| 1 | `modules/1_auth.py`      | Login, user accounts, session protection          |
| 2 | `modules/2_slots.py`     | Slot availability / visual display                |
| 3 | `modules/3_vehicles.py`  | Vehicle registration and records                  |
| 4 | `modules/4_entry.py`     | Vehicle entry, slot assignment                     |
| 5 | `modules/5_exit.py`      | Duration and fee calculation                        |
| 6 | `modules/6_payment.py`   | Cash and M-Pesa (Daraja) payment processing        |
| 7 | `modules/7_barrier.py`   | Entry/exit barrier control                           |
| 8 | `modules/8_reports.py`   | Dashboard and reporting statistics                   |

`database/db.py` holds the shared SQLite connection, table schema, and the
one shared clock function every module uses, so timestamps stay consistent
across the whole system.

### A note on the numbered filenames

Python identifiers can't start with a digit, so a normal `import modules.1_auth`
statement isn't valid. Every file that needs a numbered module loads it with
`importlib` instead:

```python
import importlib
auth = importlib.import_module("modules.1_auth")
```

This is the only adjustment the numbering requires — everything else behaves
like a normal Python module.

## Setup

```bash
cd moih_park_kenya
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

Open **http://localhost:5000** in a browser.

**Default login:** `Sawyer` / `amon1234` (change this after first login — still worth changing before production use).

The SQLite database (`database/parking.db`) and the 20 parking slots are
created automatically the first time you run the app.

## M-Pesa (Daraja) Setup

M-Pesa payment needs Safaricom Daraja sandbox credentials, set as
environment variables before starting the app:

```bash
export DARAJA_CONSUMER_KEY="your_key"
export DARAJA_CONSUMER_SECRET="your_secret"
export DARAJA_SHORTCODE="your_shortcode"
export DARAJA_PASSKEY="your_passkey"
export DARAJA_CALLBACK_URL="https://your-public-url/mpesa/callback"
```

Without these, cash payments still work normally — M-Pesa requests just
fail with a clear message instead of crashing the app.

## Pages

| Route            | Purpose                                   |
|-------------------|--------------------------------------------|
| `/login`          | Staff login                                |
| `/dashboard`      | Today's revenue, vehicle count, occupancy, recent activity |
| `/slots`          | Live visual slot map (auto-refreshes)      |
| `/entry`          | Register a vehicle arriving                |
| `/exit`           | Look up a plate and calculate the fee owed |
| `/payment/<id>`   | Pay by cash or M-Pesa                       |
| `/reports`        | Full daily report and session history       |

## Project Structure

```
moih_park_kenya/
├── app.py
├── modules/
│   ├── 1_auth.py
│   ├── 2_slots.py
│   ├── 3_vehicles.py
│   ├── 4_entry.py
│   ├── 5_exit.py
│   ├── 6_payment.py
│   ├── 7_barrier.py
│   └── 8_reports.py
├── database/
│   ├── db.py
│   └── parking.db      (created automatically)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── slots.html
│   ├── entry.html
│   ├── exit.html
│   ├── payment.html
│   └── reports.html
├── static/
│   ├── css/style.css
│   └── js/app.js
└── README.md
```
