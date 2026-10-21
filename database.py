"""
Database helper module for the Expense Tracker application.
Uses Python's built-in sqlite3 library.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_FILE = os.path.join(os.path.dirname(__file__), "expenses.db")


def get_db_connection():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and seeds initial sample transactions if database is fresh."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Transactions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Settings table (for budget, currency, etc.)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        # Default settings if not already present
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('monthly_budget', '40000')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('currency', '₹')")

        # Check if transactions table is empty; if so, populate initial realistic sample data
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]

        if count == 0:
            seed_sample_data(cursor)

        conn.commit()


def seed_sample_data(cursor):
    """Inserts initial realistic demo transactions for the current month and previous weeks."""
    today = datetime.now()
    d = lambda days_ago: (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    samples = [
        ("Monthly Salary", 65000.0, "income", "Salary", d(20), "Bank Transfer", "Direct salary deposit"),
        ("Freelance Web Design", 18500.0, "income", "Freelance", d(10), "UPI", "Landing page project payout"),
        ("Apartment Rent", 16000.0, "expense", "Housing", d(18), "Bank Transfer", "Monthly flat rent"),
        ("Grocery Mart Supermarket", 3450.0, "expense", "Groceries", d(14), "Card", "Weekly household items & snacks"),
        ("High-Speed Fiber Internet", 1199.0, "expense", "Utilities", d(12), "UPI", "Monthly broadband bill"),
        ("Electricity Bill", 1820.0, "expense", "Utilities", d(11), "UPI", "State electricity distribution board"),
        ("Dining Out with Friends", 2150.0, "expense", "Food & Dining", d(8), "Card", "Dinner at Italian bistro"),
        ("Metro Transit Card Recharge", 800.0, "expense", "Transportation", d(6), "Cash", "Monthly travel top-up"),
        ("Fitness Club Gym Membership", 2500.0, "expense", "Health & Fitness", d(5), "Card", "Quarterly renewal installment"),
        ("Online Course - Python Masterclass", 999.0, "expense", "Education", d(4), "UPI", "Udemy certification course"),
        ("Weekend Cinema & Popcorn", 650.0, "expense", "Entertainment", d(2), "UPI", "Movie ticket with snacks"),
        ("Stock Dividend Payout", 1250.0, "income", "Investments", d(1), "Bank Transfer", "Quarterly dividend credit"),
        ("Coffee & Bakery Cafe", 240.0, "expense", "Food & Dining", d(0), "UPI", "Cappuccino and croissant"),
    ]

    cursor.executemany(
        """
        INSERT INTO transactions (title, amount, type, category, date, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        samples,
    )


# Transaction CRUD helpers
def get_all_transactions(filters=None):
    """Retrieve transactions based on optional filtering criteria."""
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if filters:
        if filters.get("type") and filters["type"] in ("income", "expense"):
            query += " AND type = ?"
            params.append(filters["type"])

        if filters.get("category") and filters["category"] != "all":
            query += " AND category = ?"
            params.append(filters["category"])

        if filters.get("search"):
            query += " AND (title LIKE ? OR notes LIKE ? OR category LIKE ?)"
            search_val = f"%{filters['search']}%"
            params.extend([search_val, search_val, search_val])

        if filters.get("start_date"):
            query += " AND date >= ?"
            params.append(filters["start_date"])

        if filters.get("end_date"):
            query += " AND date <= ?"
            params.append(filters["end_date"])

    # Sorting
    sort_by = filters.get("sort_by", "date_desc") if filters else "date_desc"
    sort_map = {
        "date_desc": "date DESC, id DESC",
        "date_asc": "date ASC, id ASC",
        "amount_desc": "amount DESC",
        "amount_asc": "amount ASC",
    }
    order_clause = sort_map.get(sort_by, "date DESC, id DESC")
    query += f" ORDER BY {order_clause}"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_transaction_by_id(transaction_id):
    """Fetch single transaction by id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_transaction(title, amount, trans_type, category, date, payment_method="Cash", notes=""):
    """Inserts a new transaction."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (title, amount, type, category, date, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title.strip(), float(amount), trans_type, category.strip(), date, payment_method, notes.strip()),
        )
        conn.commit()
        return cursor.lastrowid


def update_transaction(transaction_id, title, amount, trans_type, category, date, payment_method="Cash", notes=""):
    """Updates an existing transaction."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE transactions
            SET title = ?, amount = ?, type = ?, category = ?, date = ?, payment_method = ?, notes = ?
            WHERE id = ?
            """,
            (title.strip(), float(amount), trans_type, category.strip(), date, payment_method, notes.strip(), transaction_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_transaction(transaction_id):
    """Deletes a transaction by id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        return cursor.rowcount > 0


def reset_to_sample_data():
    """Clears all transactions and re-seeds sample data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        seed_sample_data(cursor)
        conn.commit()


def get_setting(key, default=None):
    """Get setting value by key."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    """Set or update setting value."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value)),
        )
        conn.commit()


def get_analytics_summary():
    """Calculates overall metrics, category breakdown, monthly trends, and budget stats."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Overall income & expense totals
        cursor.execute("SELECT type, SUM(amount) as total FROM transactions GROUP BY type")
        totals_map = {row["type"]: float(row["total"]) for row in cursor.fetchall()}
        total_income = totals_map.get("income", 0.0)
        total_expense = totals_map.get("expense", 0.0)
        balance = total_income - total_expense
        savings_rate = round(((total_income - total_expense) / total_income * 100), 1) if total_income > 0 else 0.0

        # Current Month totals
        current_month_str = datetime.now().strftime("%Y-%m")
        cursor.execute(
            """
            SELECT type, SUM(amount) as total 
            FROM transactions 
            WHERE strftime('%Y-%m', date) = ?
            GROUP BY type
            """,
            (current_month_str,),
        )
        cur_month_map = {row["type"]: float(row["total"]) for row in cursor.fetchall()}
        cur_month_income = cur_month_map.get("income", 0.0)
        cur_month_expense = cur_month_map.get("expense", 0.0)

        # Category breakdown for expenses
        cursor.execute(
            """
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions
            WHERE type = 'expense'
            GROUP BY category
            ORDER BY total DESC
            """
        )
        expense_by_category = [
            {"category": row["category"], "total": round(float(row["total"]), 2), "count": row["count"]}
            for row in cursor.fetchall()
        ]

        # Category breakdown for income
        cursor.execute(
            """
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM transactions
            WHERE type = 'income'
            GROUP BY category
            ORDER BY total DESC
            """
        )
        income_by_category = [
            {"category": row["category"], "total": round(float(row["total"]), 2), "count": row["count"]}
            for row in cursor.fetchall()
        ]

        # Monthly Trends (last 6 months)
        cursor.execute(
            """
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
            """
        )
        monthly_trends = [
            {"month": row["month"], "income": round(float(row["income"]), 2), "expense": round(float(row["expense"]), 2)}
            for row in cursor.fetchall()
        ]
        monthly_trends.reverse()  # Chronological order

        # Payment methods distribution
        cursor.execute(
            """
            SELECT payment_method, COUNT(*) as count, SUM(amount) as total
            FROM transactions
            WHERE type = 'expense'
            GROUP BY payment_method
            ORDER BY count DESC
            """
        )
        payment_methods = [
            {"method": row["payment_method"], "count": row["count"], "total": round(float(row["total"]), 2)}
            for row in cursor.fetchall()
        ]

        # Budget info
        monthly_budget = float(get_setting("monthly_budget", 40000))
        budget_remaining = monthly_budget - cur_month_expense
        budget_percentage = round((cur_month_expense / monthly_budget * 100), 1) if monthly_budget > 0 else 0

        return {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "balance": round(balance, 2),
            "savings_rate": savings_rate,
            "current_month": {
                "month_name": datetime.now().strftime("%B %Y"),
                "income": round(cur_month_income, 2),
                "expense": round(cur_month_expense, 2),
                "budget": monthly_budget,
                "budget_remaining": round(budget_remaining, 2),
                "budget_percentage": budget_percentage,
            },
            "expense_by_category": expense_by_category,
            "income_by_category": income_by_category,
            "monthly_trends": monthly_trends,
            "payment_methods": payment_methods,
        }
