# Moih Park Kenya

### A Web-Based Modern Parking Management System

**Language:** Python (Flask + SQLite)

---

## 1. About the System and What It Does

### 1.1 Overview

Moih Park Kenya is a web-based system that automates a parking lot's
daily operations. It is built with **Python**, using **Flask** for the
web layer and **SQLite** as the database. It runs in a browser and can
be used by a real parking attendant from day one, with no special
training beyond a five-minute walkthrough.

### 1.2 The Problem It Solves

Manually run parking lots in Kenya usually rely on a paper ticket
handed to the driver and a logbook kept by the attendant. This sounds
simple, but in practice it causes several recurring problems:

- **Drivers can't tell if the lot is full** before driving in — they
  only find out once they're already inside, sometimes blocking other
  traffic while they reverse back out.
- **Attendants calculate fees by hand.** Working out how long a car
  has been parked, then matching that against a printed tariff card,
  is slow, and easy to get wrong — especially when a queue of drivers
  is waiting to leave at the same time.
- **There is no digital record.** A lost or torn paper ticket means
  there is no way to prove how long a vehicle was actually parked. At
  the end of the day, revenue can only be checked by counting cash
  against a stack of paper stubs by hand.
- **Cash-only.** Many Kenyan drivers prefer to pay by M-Pesa rather
  than carry coins and notes, and a cash-only system loses that
  convenience entirely.

Moih Park Kenya replaces all of this with a live slot display, a fee
calculator that works the same way every single time, a permanent
digital record of every vehicle, session and payment, and support for
both cash and M-Pesa.

### 1.3 What the System Does (Step by Step)

1. A driver arrives. The attendant sees, on screen, how many slots are
   free before letting them in.
2. The attendant types the vehicle's plate number. The system assigns
   a free slot, records the exact arrival time, and opens the barrier.
3. When the driver wants to leave, the attendant looks the plate up
   again. The system calculates exactly how long the vehicle was
   parked and how much it owes.
4. The driver pays — in cash (confirmed by the attendant) or by
   M-Pesa (a payment prompt is sent straight to their phone).
5. Once paid, the slot is freed, the barrier opens, and the visit is
   logged.
6. A dashboard shows today's revenue, vehicle count, and occupancy at
   any time.

### 1.4 Fee Structure

| Duration Parked | Fee (Kshs) |
|---|---|
| Up to 30 minutes | Free |
| Up to 2 hours | 50 |
| Up to 4 hours | 100 |
| Up to 6 hours | 300 |
| Over 6 hours | 500 |

### 1.5 Key Features

- Live, auto-refreshing visual slot display (20 slots)
- Staff login with hashed (encrypted) passwords
- Automatic vehicle entry logging
- Automatic, consistent fee calculation on exit
- Cash and M-Pesa (Safaricom Daraja API) payment
- Automatic barrier control logic
- Dashboard and full reports page
- Mobile-friendly, blue-and-white themed interface
- Fully working, well-commented Python code delivered via GitHub

### 1.6 Technology Used

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Web framework | Flask |
| Database | SQLite |
| Frontend | HTML (Jinja2 templates), CSS, JavaScript |
| Payments | Cash + Safaricom Daraja API (M-Pesa STK Push) |
| Password security | Werkzeug password hashing |

### 1.7 Simple System Diagram

```
   ┌────────────┐     views slots,      ┌──────────────────────┐
   │  Attendant │────logs in, enters,──▶│   Moih Park Kenya      │
   │  (Browser) │   exits, takes payment│   (Flask web app)       │
   └────────────┘                        └──────────┬─────────────┘
                                                      │
                                                      ▼
                                          ┌──────────────────────┐
                                          │  SQLite database       │
                                          │  (parking.db)            │
                                          └──────────────────────────┘
                                                      │
                                                      ▼ (M-Pesa only)
                                          ┌──────────────────────────┐
                                          │  Safaricom Daraja API      │
                                          │  (sends STK Push to driver) │
                                          └──────────────────────────────┘
```

### 1.8 Existing System vs. Proposed System

Everything the attendant does happens through the browser. The browser
never talks to Safaricom directly — only the Flask application does,
keeping the M-Pesa credentials safely on the server side, never exposed
to whoever is using the system.

The table below compares the manual approach this system replaces
against what Moih Park Kenya actually does differently.

| Manual (existing) system | Moih Park Kenya (proposed system) |
|---|---|
| No visibility before entry | Live slot display, auto-refreshed |
| Fee calculated by hand | Fee calculated automatically, the same way every time |
| Paper ticket, easily lost | Permanent digital record in a database |
| Cash only | Cash and M-Pesa |
| End-of-day manual reconciliation | Real-time dashboard and reports |
| No accountability trail | Every entry, exit, and payment timestamped and stored |

### 1.9 Pages in the System

| Page | Purpose |
|---|---|
| Login | Staff sign in |
| Dashboard | Today's revenue, vehicles, occupancy, recent activity |
| Slots | Live, colour-coded slot map |
| Entry | Register an arriving vehicle |
| Exit | Look up a vehicle and see the fee owed |
| Payment | Choose cash or M-Pesa and complete payment |
| Reports | Full daily report and session history |

Every page except Login shares one common layout (navigation bar and
message area), so the system looks and feels consistent no matter
which page the attendant is on.

---

## 2. Requirements

This section lists what the system must do (functional requirements),
how it must behave (non-functional requirements), and what is needed
to run it (software and hardware requirements). Together, these are
what the finished system is measured against.

### 2.1 Functional Requirements

These map directly to what the system must do:

| # | Requirement | Where it is met |
|---|---|---|
| 1 | Show drivers a visual display of available parking slots before entry | `2_slots.py`, `slots.html` |
| 2 | Record every vehicle's arrival automatically, with the exact time | `4_entry.py` |
| 3 | Automatically calculate total time parked and fee owed on exit | `5_exit.py` |
| 4 | Open the barrier automatically on entry | `4_entry.py` + `7_barrier.py` |
| 5 | Only open the exit barrier once the fee has been paid | `6_payment.py` + `7_barrier.py` |
| 6 | Apply the fixed fee structure (see Section 1.4) | `5_exit.py` |
| 7 | Accept payment by cash | `6_payment.py` |
| 8 | Accept payment by M-Pesa (Safaricom Daraja STK Push) | `6_payment.py` |
| 9 | Prevent a session from being paid for a second time | `5_exit.py`'s payment guard |
| 10 | Show a live dashboard of today's revenue, vehicles served, and occupancy | `8_reports.py` |
| 11 | Require staff to log in before using the system | `1_auth.py` |
| 12 | Run as a web-based system, accessible from a browser | `app.py` (Flask) |

### 2.2 Non-Functional Requirements

Functional requirements describe *what* the system does; non-functional
requirements describe *how well* it does it.

| # | Requirement | Why it matters |
|---|---|---|
| 1 | Written in Python | Required by the assignment brief |
| 2 | Simple rather than complex | Easier to read, mark, and maintain |
| 3 | Well-commented throughout | Lets a reader understand the reasoning without asking the author |
| 4 | Time must be consistent everywhere (one shared clock) | Stops fee calculations from ever disagreeing with each other |
| 5 | Organised around identified use cases, modules, algorithms, and a database | Directly required by the assignment brief |
| 6 | Usable on both desktop and mobile screens | Attendants may use a phone or tablet, not only a desktop |
| 7 | Passwords never stored as plain text | Basic security expectation for any login system |
| 8 | Delivered as a functional system via GitHub | Required delivery method for the assignment |

### 2.3 Software Requirements

| Requirement | Notes |
|---|---|
| Python 3.9+ | Core language |
| Flask | Web framework |
| Werkzeug | Password hashing (installed with Flask) |
| requests | Used to call the M-Pesa Daraja API |
| SQLite | Built into Python — no separate install needed |
| A web browser | To use the system |
| Safaricom Daraja account | Only needed for M-Pesa payments |

### 2.4 Hardware Requirements

- Any computer able to run Python 3 (no special specification needed —
  the system is light enough to run on very modest hardware)
- Internet connection (for M-Pesa API calls only — everything else
  works fully offline)
- A physical barrier and controller (e.g. Raspberry Pi + relay), for a
  real deployment — the software side is ready; only the physical
  hardware connection would need adding

### 2.5 Use Cases (Summary)

| Use Case | Actor | Result |
|---|---|---|
| Log in | Attendant | Gains access to the system |
| View available slots | Attendant | Sees live slot map |
| Register vehicle entry | Attendant | Vehicle assigned a slot, barrier opens |
| Look up vehicle / calculate fee | Attendant | System shows amount owed |
| Pay by cash | Attendant | Session completed, slot freed, barrier opens |
| Pay by M-Pesa | Attendant + Driver + Safaricom | Session completed once payment confirmed |
| View dashboard / reports | Attendant | Sees today's revenue, vehicle count, occupancy |

### 2.6 How Requirements Were Verified

Each functional requirement above was checked by actually running the
system end-to-end — logging in, registering an entry, looking up an
exit, paying, and confirming the dashboard updated correctly — rather
than only checking the requirement "on paper." Details of this are in
Section 7.6 (Testing).

---

## 3. Data Types and Names

This section names every database table, every field, and every
function in the system, along with its data type — so the exact
"identified... database" and "modules" required by the assignment are
laid out clearly and precisely. Naming things exactly, with their
types, is what lets someone else pick up this code and know immediately
what each piece of data is and what shape it takes, without having to
read the full source line by line.

### 3.1 Database Tables

The database has five tables. Four of them (`vehicles`, `sessions`,
`payments`, and indirectly `slots`) exist because of the parking
process itself; the fifth (`users`) exists purely to support login.

**Table: `users`**

| Field | Type | Meaning |
|---|---|---|
| `id` | INTEGER (PK) | Unique user id |
| `username` | TEXT | Login name |
| `password_hash` | TEXT | Encrypted password |
| `role` | TEXT | `"admin"` or `"attendant"` |
| `created_at` | TEXT | When the account was created |

**Table: `slots`**

| Field | Type | Meaning |
|---|---|---|
| `slot_number` | INTEGER (PK) | 1 to 20 |
| `is_occupied` | INTEGER (0/1) | Whether a vehicle is in it |

**Table: `vehicles`**

| Field | Type | Meaning |
|---|---|---|
| `vehicle_id` | INTEGER (PK) | Unique vehicle id |
| `plate_number` | TEXT (unique) | Number plate |
| `owner_name` | TEXT | Optional |
| `vehicle_type` | TEXT | Optional |
| `registered_at` | TEXT | First-ever entry time |

**Table: `sessions`**

| Field | Type | Meaning |
|---|---|---|
| `session_id` | INTEGER (PK) | Unique visit id |
| `vehicle_id` | INTEGER (FK) | Which vehicle |
| `plate_number` | TEXT | Copy for fast lookup |
| `slot_number` | INTEGER | Which slot was used |
| `entry_time` | TEXT | Arrival time |
| `exit_time` | TEXT | Departure time (set once paid) |
| `fee_charged` | INTEGER | Kshs charged (set once paid) |
| `is_paid` | INTEGER (0/1) | Paid or not |
| `payment_method` | TEXT | `"CASH"` or `"MPESA"` |
| `status` | TEXT | `"PARKED"` or `"COMPLETED"` |

**Table: `payments`**

| Field | Type | Meaning |
|---|---|---|
| `payment_id` | INTEGER (PK) | Unique payment id |
| `session_id` | INTEGER (FK) | Which session was paid |
| `amount` | INTEGER | Kshs paid |
| `method` | TEXT | `"CASH"` or `"MPESA"` |
| `mpesa_receipt` | TEXT | Safaricom receipt code (M-Pesa only) |
| `paid_at` | TEXT | Time of payment |

### 3.1.1 Full SQL Schema

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'attendant',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS slots (
    slot_number INTEGER PRIMARY KEY,
    is_occupied INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT UNIQUE NOT NULL,
    owner_name TEXT,
    vehicle_type TEXT,
    registered_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    plate_number TEXT NOT NULL,
    slot_number INTEGER NOT NULL,
    entry_time TEXT NOT NULL,
    exit_time TEXT,
    fee_charged INTEGER,
    is_paid INTEGER NOT NULL DEFAULT 0,
    payment_method TEXT,
    status TEXT NOT NULL DEFAULT 'PARKED',
    FOREIGN KEY (vehicle_id) REFERENCES vehicles (vehicle_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    method TEXT NOT NULL,
    mpesa_receipt TEXT,
    paid_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
);
```

This exact schema is what `database/db.py`'s `init_db()` function runs
automatically the first time the system starts.

### 3.2 Module Names and Function Signatures

Every function below is named clearly for what it does — a reader
should be able to guess roughly what a function does just from its
name, before even reading its code. Each one lists its parameters
(inputs) and what it returns (output), with the Python type of each.

**Module 1 — `modules/1_auth.py` (Authentication)**

| Function | Parameters → Returns |
|---|---|
| `create_user` | `(username: str, password: str, role: str) → dict` |
| `authenticate` | `(username: str, password: str) → dict or None` |
| `login_required` | `(view_function) → function` (decorator) |
| `get_current_user` | `() → dict or None` |

**Module 2 — `modules/2_slots.py` (Slots)**

| Function | Parameters → Returns |
|---|---|
| `get_all_slots` | `() → list of dict` |
| `count_available_slots` | `() → int` |
| `find_free_slot` | `() → int or None` |
| `occupy_slot` | `(slot_number: int) → None` |
| `free_slot` | `(slot_number: int) → None` |

**Module 3 — `modules/3_vehicles.py` (Vehicles)**

| Function | Parameters → Returns |
|---|---|
| `get_vehicle_by_plate` | `(plate_number: str) → dict or None` |
| `register_vehicle` | `(plate_number: str, owner_name: str, vehicle_type: str) → dict` |
| `list_vehicles` | `() → list of dict` |

**Module 4 — `modules/4_entry.py` (Entry)**

| Function | Parameters → Returns |
|---|---|
| `record_entry` | `(plate_number: str, owner_name: str, vehicle_type: str) → dict` |
| `get_active_session` | `(plate_number: str) → dict or None` |
| `get_session_by_id` | `(session_id: int) → dict or None` |

**Module 5 — `modules/5_exit.py` (Exit & Fee)**

| Function | Parameters → Returns |
|---|---|
| `calculate_duration_minutes` | `(entry_time_str: str, exit_time_str: str) → float` |
| `calculate_fee` | `(entry_time_str: str, exit_time_str: str) → dict` |
| `get_exit_quote` | `(plate_number: str) → dict` |
| `get_payable_session` | `(session_id: int) → tuple(dict, int)` |

**Module 6 — `modules/6_payment.py` (Payment)**

| Function | Parameters → Returns |
|---|---|
| `pay_with_cash` | `(session_id: int, amount: int) → dict` |
| `initiate_mpesa_payment` | `(phone_number: str, amount: int, session_id: int) → dict` |
| `confirm_mpesa_payment` | `(session_id: int, amount: int, mpesa_receipt: str) → dict` |

**Module 7 — `modules/7_barrier.py` (Barrier)**

| Function | Parameters → Returns |
|---|---|
| `open_barrier` | `(reason: str) → dict` |
| `close_barrier` | `() → dict` |
| `allow_exit_if_paid` | `(session: dict) → dict` |

**Module 8 — `modules/8_reports.py` (Reports)**

| Function | Parameters → Returns |
|---|---|
| `get_today_revenue` | `() → int` |
| `get_today_vehicle_count` | `() → int` |
| `get_occupancy_summary` | `() → dict` |
| `get_recent_sessions` | `(limit: int) → list of dict` |
| `get_daily_report` | `() → dict` |

**Shared — `database/db.py` (Database + Clock)**

| Function | Parameters → Returns |
|---|---|
| `now` | `() → datetime` |
| `now_str` | `() → str` |
| `parse_time` | `(time_string: str) → datetime` |
| `get_connection` | `() → sqlite3.Connection` |
| `init_db` | `() → None` |

### 3.3 Why These Data Types Were Chosen

- **Timestamps are stored as TEXT, not a special date type.** SQLite
  has no dedicated date/time type — storing a fixed-format string
  (`"YYYY-MM-DD HH:MM:SS"`) is simple, sortable, and easy to read
  directly in the database without any conversion.
- **Booleans are stored as INTEGER (0 or 1).** SQLite has no true
  boolean type either — 0/1 is the standard, lightweight way to
  represent yes/no values (`is_occupied`, `is_paid`).
- **IDs are all INTEGER, auto-incrementing.** This guarantees every
  row has a simple, unique, ever-increasing identifier with no extra
  code needed to generate one.
- **Money (fees, amounts) is stored as INTEGER, not a decimal type.**
  Kenyan Shilling amounts in this system are always whole numbers
  (50, 100, 300, 500), so there is no need for decimal places, and
  using plain integers avoids any floating-point rounding issues.

---

## 4. Algorithms

This section spells out, step by step, exactly how the system's core
logic works — the same process a marker could follow by hand to check
the system is doing the right thing at each stage. Each algorithm is
kept deliberately short and linear, in line with the requirement that
the system be "simple rather than complex."

### 4.1 Slot Assignment Algorithm (First-Fit)

Decides which parking slot a newly arrived vehicle is given.

```
1. Look through the slots table for rows where is_occupied = 0.
2. Sort by slot_number, smallest first.
3. Return the first (lowest-numbered) free slot.
4. If none are free, return None (lot is full).
```
Complexity: O(n), n = 20 — effectively instant.

**Why first-fit, and not something more complex?** A first-fit
algorithm — always take the lowest-numbered free slot — was chosen
over alternatives like nearest-to-entrance or round-robin rotation for
three reasons: it's trivially easy to check by eye during a demo
(slot 1 always fills before slot 2), it needs no extra memory or state
beyond what's already stored in the `slots` table, and for a lot of
only 20 spaces, a smarter algorithm would give no meaningful real-world
benefit over this simple one.

### 4.2 Vehicle Entry Algorithm

Runs the moment a vehicle arrives — this is the busiest, most
time-sensitive operation the system performs.

```
1. Reject if plate_number is empty.
2. Run the Slot Assignment Algorithm.
   → If no slot is free, stop: "Parking lot is full."
3. Look up the vehicle by plate number.
   - If it exists, reuse it.
   - If not, create a new vehicle record.
4. Get the current time from the shared clock.
5. Create a new session: vehicle_id, plate_number, slot_number,
   entry_time, status = "PARKED".
6. Mark the assigned slot as occupied.
7. Open the barrier.
8. Return the session id, slot number, and entry time.
`''
