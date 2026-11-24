import os
import random
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(os.getenv("BANKING_DB_PATH", "data/banking.db"))


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, risk_tier TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, account_type TEXT NOT NULL,
            created_at TEXT NOT NULL, FOREIGN KEY(customer_id) REFERENCES customers(id)
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY, from_account TEXT NOT NULL, to_account TEXT NOT NULL,
            amount REAL NOT NULL, currency TEXT NOT NULL, channel TEXT NOT NULL,
            device_id TEXT NOT NULL, location TEXT NOT NULL, occurred_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY, transaction_id TEXT, alert_type TEXT NOT NULL,
            risk_score INTEGER NOT NULL, risk_level TEXT NOT NULL, reasons TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY, alert_id TEXT NOT NULL, title TEXT NOT NULL,
            priority TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open',
            analyst_note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
        );
        """)


def _now():
    return datetime.now(timezone.utc)


def seed_demo_data():
    init_db()
    with connect() as db:
        existing = db.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        if existing:
            return {"created": False, "message": "Demo data already exists", "transactions": existing}

        rng = random.Random(42)
        names = ["Aarav Sharma", "Diya Patel", "Kabir Singh", "Anaya Gupta", "Arjun Mehta",
                 "Ishita Rao", "Vivaan Kumar", "Saanvi Shah", "Reyansh Das", "Aditi Verma"]
        customer_ids, account_ids = [], []
        for i, name in enumerate(names):
            cid, aid = f"C{i+1:03}", f"A{i+1:03}"
            customer_ids.append(cid)
            account_ids.append(aid)
            db.execute("INSERT INTO customers VALUES (?, ?, ?)",
                       (cid, name, "high" if i in (2, 7) else "standard"))
            db.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)",
                       (aid, cid, "current", (_now() - timedelta(days=365-i*11)).isoformat()))

        locations = ["Ludhiana", "Delhi", "Mumbai", "Bengaluru", "Chandigarh", "Pune"]
        base = _now() - timedelta(days=2)
        rows = []
        for i in range(180):
            src = rng.choice(account_ids)
            dst = rng.choice([a for a in account_ids if a != src])
            when = base + timedelta(minutes=i * 14)
            amount = round(rng.uniform(250, 18000), 2)
            rows.append((f"T{i+1:04}", src, dst, amount, "INR", rng.choice(["UPI", "NEFT", "IMPS"]),
                         f"DEV-{rng.randint(1,18):02}", rng.choice(locations), when.isoformat()))

        suspicious = [
            ("TAML001", "A003", "A004", 48000.0, "INR", "IMPS", "DEV-99", "Mumbai", (_now()-timedelta(minutes=35)).isoformat()),
            ("TAML002", "A003", "A005", 47000.0, "INR", "IMPS", "DEV-99", "Mumbai", (_now()-timedelta(minutes=30)).isoformat()),
            ("TAML003", "A003", "A006", 46500.0, "INR", "IMPS", "DEV-99", "Mumbai", (_now()-timedelta(minutes=25)).isoformat()),
            ("TAML004", "A004", "A010", 45500.0, "INR", "NEFT", "DEV-41", "Mumbai", (_now()-timedelta(minutes=20)).isoformat()),
            ("TAML005", "A005", "A010", 44500.0, "INR", "NEFT", "DEV-42", "Mumbai", (_now()-timedelta(minutes=18)).isoformat()),
            ("TAML006", "A006", "A010", 43500.0, "INR", "NEFT", "DEV-43", "Mumbai", (_now()-timedelta(minutes=15)).isoformat()),
            ("TFRAUD01", "A008", "A001", 195000.0, "INR", "UPI", "DEV-UNKNOWN", "Delhi", (_now()-timedelta(hours=2)).replace(hour=2).isoformat()),
        ]
        rows.extend(suspicious)
        db.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    analyze_all()
    return {"created": True, "customers": 10, "accounts": 10, "transactions": len(rows)}


def _risk_level(score):
    return "high" if score >= 70 else "medium" if score >= 40 else "low"


def analyze_all():
    init_db()
    with connect() as db:
        db.execute("DELETE FROM alerts")
        txs = [dict(r) for r in db.execute("SELECT * FROM transactions ORDER BY occurred_at")]
        by_source = {}
        for tx in txs:
            by_source.setdefault(tx["from_account"], []).append(tx)

        for tx in txs:
            score, reasons = 0, []
            if tx["amount"] >= 100000:
                score += 55; reasons.append("Very high transaction amount (>= INR 100,000)")
            elif tx["amount"] >= 50000:
                score += 30; reasons.append("High transaction amount (>= INR 50,000)")
            hour = datetime.fromisoformat(tx["occurred_at"]).hour
            if hour < 5:
                score += 25; reasons.append("Transaction occurred between 00:00 and 04:59 UTC")
            if tx["device_id"] in ("DEV-UNKNOWN", "DEV-99"):
                score += 25; reasons.append("Unrecognized/demo flagged device")
            recent = [x for x in by_source[tx["from_account"]]
                      if abs((datetime.fromisoformat(x["occurred_at"]) -
                              datetime.fromisoformat(tx["occurred_at"])).total_seconds()) <= 3600]
            if len(recent) >= 4:
                score += 20; reasons.append("High sender transaction velocity (4+ per hour)")
            score = min(score, 100)
            if score >= 40:
                db.execute("""INSERT INTO alerts
                    (id, transaction_id, alert_type, risk_score, risk_level, reasons, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'open', ?)""",
                    (str(uuid.uuid4()), tx["id"], "transaction_fraud", score, _risk_level(score),
                     " | ".join(reasons), _now().isoformat()))

        incoming = {}
        for tx in txs:
            incoming.setdefault(tx["to_account"], []).append(tx)
        for account, transfers in incoming.items():
            recent = [t for t in transfers if datetime.fromisoformat(t["occurred_at"]) >= _now()-timedelta(hours=3)]
            senders = {t["from_account"] for t in recent}
            if len(senders) >= 3:
                score = min(95, 45 + 10 * len(senders))
                db.execute("""INSERT INTO alerts
                    (id, transaction_id, alert_type, risk_score, risk_level, reasons, status, created_at)
                    VALUES (?, NULL, 'aml_network_pattern', ?, ?, ?, 'open', ?)""",
                    (str(uuid.uuid4()), score, _risk_level(score),
                     f"Potential funnel account: received recent transfers from {len(senders)} distinct accounts ({account})",
                     _now().isoformat()))
    return {"analyzed_transactions": len(txs)}


def dashboard():
    with connect() as db:
        count = lambda table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        alerts = [dict(r) for r in db.execute(
            "SELECT risk_level, COUNT(*) AS count FROM alerts GROUP BY risk_level")]
        return {
            "customers": count("customers"), "accounts": count("accounts"),
            "transactions": count("transactions"), "alerts": count("alerts"),
            "open_alerts": db.execute("SELECT COUNT(*) FROM alerts WHERE status='open'").fetchone()[0],
            "cases": count("cases"), "alerts_by_level": alerts,
            "disclaimer": "Local generated transaction source; risk indicators require human investigation."
        }


def list_rows(table, limit=100):
    allowed = {"transactions": "occurred_at", "alerts": "created_at", "cases": "created_at"}
    if table not in allowed:
        raise ValueError("Unsupported table")
    with connect() as db:
        return [dict(r) for r in db.execute(
            f"SELECT * FROM {table} ORDER BY {allowed[table]} DESC LIMIT ?", (limit,))]


def search_transactions(query=None, channel=None, min_amount=None, max_amount=None, limit=200):
    clauses, params = [], []
    if query:
        pattern = f"%{query.strip()}%"
        clauses.append("(t.id LIKE ? OR t.from_account LIKE ? OR t.to_account LIKE ? OR t.device_id LIKE ? OR t.location LIKE ?)")
        params.extend([pattern] * 5)
    if channel:
        clauses.append("t.channel = ?")
        params.append(channel)
    if min_amount is not None:
        clauses.append("t.amount >= ?")
        params.append(min_amount)
    if max_amount is not None:
        clauses.append("t.amount <= ?")
        params.append(max_amount)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with connect() as db:
        rows = db.execute(
            "SELECT t.*, fa.customer_id AS from_customer_id, ca.name AS from_customer_name, "
            "ta.customer_id AS to_customer_id, cb.name AS to_customer_name "
            "FROM transactions t "
            "LEFT JOIN accounts fa ON fa.id=t.from_account "
            "LEFT JOIN customers ca ON ca.id=fa.customer_id "
            "LEFT JOIN accounts ta ON ta.id=t.to_account "
            "LEFT JOIN customers cb ON cb.id=ta.customer_id"
            + where + " ORDER BY t.occurred_at DESC LIMIT ?",
            (*params, limit)
        ).fetchall()
        return [dict(row) for row in rows]


def get_transaction(transaction_id):
    rows = search_transactions(query=transaction_id, limit=500)
    return next((row for row in rows if row["id"] == transaction_id), None)


def create_case(alert_id):
    with connect() as db:
        alert = db.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
        if not alert:
            return None
        existing = db.execute("SELECT * FROM cases WHERE alert_id=?", (alert_id,)).fetchone()
        if existing:
            return dict(existing)
        case_id = str(uuid.uuid4())
        title = f"Investigate {alert['alert_type']} alert"
        db.execute("""INSERT INTO cases
            (id, alert_id, title, priority, status, analyst_note, created_at)
            VALUES (?, ?, ?, ?, 'open', '', ?)""",
            (case_id, alert_id, title, alert["risk_level"], _now().isoformat()))
        db.execute("UPDATE alerts SET status='case_open' WHERE id=?", (alert_id,))
        return dict(db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone())


def update_case(case_id, status, analyst_note):
    if status not in {"open", "investigating", "closed"}:
        raise ValueError("status must be open, investigating, or closed")
    with connect() as db:
        cur = db.execute("UPDATE cases SET status=?, analyst_note=? WHERE id=?",
                         (status, analyst_note, case_id))
        if cur.rowcount == 0:
            return None
        return dict(db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone())
