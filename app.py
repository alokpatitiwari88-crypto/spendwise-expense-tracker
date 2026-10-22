"""
SpendWise - Personal Expense Tracker
Single-file Flask Backend & SQLite Database Handler.
Strictly built using Python, HTML, CSS, and JavaScript.
"""

import os
import io
import csv
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, Response

# ==============================================================================
# Database Configuration & SQLite Engine
# ==============================================================================
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

        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('monthly_budget', '40000')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('currency', '₹')")

        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        if count == 0:
            seed_sample_data(cursor)

        conn.commit()


def seed_sample_data(cursor):
    """Inserts initial realistic demo transactions."""
    today = datetime.now()
    d = lambda days_ago: (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    samples = [
        ("Monthly Salary", 65000.0, "income", "Salary", d(20), "Bank Transfer", "Direct salary deposit"),
        ("Freelance Web Design", 18500.0, "income", "Freelance", d(10), "UPI", "Landing page project payout"),
        ("Apartment Rent", 16000.0, "expense", "Housing", d(18), "Bank Transfer", "Monthly flat rent"),
        ("Grocery Mart Supermarket", 3450.0, "expense", "Groceries", d(14), "Card", "Weekly household items"),
        ("High-Speed Fiber Internet", 1199.0, "expense", "Utilities", d(12), "UPI", "Monthly broadband bill"),
        ("Electricity Bill", 1820.0, "expense", "Utilities", d(11), "UPI", "Power distribution bill"),
        ("Dining Out with Friends", 2150.0, "expense", "Food & Dining", d(8), "Card", "Dinner bistro"),
        ("Metro Transit Card", 800.0, "expense", "Transportation", d(6), "Cash", "Monthly travel top-up"),
        ("Gym Membership", 2500.0, "expense", "Health & Fitness", d(5), "Card", "Renewal installment"),
        ("Python Masterclass Course", 999.0, "expense", "Education", d(4), "UPI", "Certification course"),
        ("Weekend Cinema & Snacks", 650.0, "expense", "Entertainment", d(2), "UPI", "Movie tickets"),
        ("Stock Dividend Payout", 1250.0, "income", "Investments", d(1), "Bank Transfer", "Quarterly dividend"),
        ("Coffee & Bakery", 240.0, "expense", "Food & Dining", d(0), "UPI", "Cappuccino and snack"),
    ]

    cursor.executemany(
        """
        INSERT INTO transactions (title, amount, type, category, date, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        samples,
    )


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
        return [dict(row) for row in cursor.fetchall()]


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
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default


def set_setting(key, value):
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

        cursor.execute("SELECT type, SUM(amount) as total FROM transactions GROUP BY type")
        totals_map = {row["type"]: float(row["total"]) for row in cursor.fetchall()}
        total_income = totals_map.get("income", 0.0)
        total_expense = totals_map.get("expense", 0.0)
        balance = total_income - total_expense
        savings_rate = round(((total_income - total_expense) / total_income * 100), 1) if total_income > 0 else 0.0

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
        monthly_trends.reverse()

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


# ==============================================================================
# Flask Application & REST API Routing
# ==============================================================================
app = Flask(__name__)

# Initialize database
init_db()


@app.route("/")
def index():
    """Serves the main single-page application dashboard."""
    return render_template("index.html")


@app.route("/api/transactions", methods=["GET"])
def list_transactions():
    """Get transactions with optional query filters."""
    filters = {
        "type": request.args.get("type", "").strip(),
        "category": request.args.get("category", "").strip(),
        "search": request.args.get("search", "").strip(),
        "start_date": request.args.get("start_date", "").strip(),
        "end_date": request.args.get("end_date", "").strip(),
        "sort_by": request.args.get("sort_by", "date_desc").strip(),
    }
    transactions = get_all_transactions(filters)
    return jsonify({"success": True, "transactions": transactions, "count": len(transactions)})


@app.route("/api/transactions/<int:trans_id>", methods=["GET"])
def get_transaction(trans_id):
    """Retrieve a single transaction."""
    item = get_transaction_by_id(trans_id)
    if not item:
        return jsonify({"success": False, "error": "Transaction not found"}), 404
    return jsonify({"success": True, "transaction": item})


@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    """Create a new income or expense transaction."""
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"success": False, "error": "Missing request payload"}), 400

    title = data.get("title", "").strip()
    amount_str = str(data.get("amount", "")).strip()
    trans_type = data.get("type", "").strip().lower()
    category = data.get("category", "").strip()
    date_val = data.get("date", "").strip()
    payment_method = data.get("payment_method", "Cash").strip()
    notes = data.get("notes", "").strip()

    if not title:
        return jsonify({"success": False, "error": "Description/Title is required"}), 400

    try:
        amount = float(amount_str)
        if amount <= 0:
            return jsonify({"success": False, "error": "Amount must be greater than zero"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Invalid amount number"}), 400

    if trans_type not in ("income", "expense"):
        return jsonify({"success": False, "error": "Type must be either 'income' or 'expense'"}), 400

    if not category:
        return jsonify({"success": False, "error": "Category is required"}), 400

    if not date_val:
        date_val = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date_val, "%Y-%m-%d")
        except ValueError:
            return jsonify({"success": False, "error": "Date must be in YYYY-MM-DD format"}), 400

    new_id = add_transaction(
        title=title,
        amount=amount,
        trans_type=trans_type,
        category=category,
        date=date_val,
        payment_method=payment_method,
        notes=notes,
    )

    return jsonify({"success": True, "message": "Transaction added successfully", "id": new_id}), 201


@app.route("/api/transactions/<int:trans_id>", methods=["PUT"])
def update_transaction_route(trans_id):
    """Update an existing transaction."""
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"success": False, "error": "Missing request payload"}), 400

    existing = get_transaction_by_id(trans_id)
    if not existing:
        return jsonify({"success": False, "error": "Transaction not found"}), 404

    title = data.get("title", existing["title"]).strip()
    try:
        amount = float(data.get("amount", existing["amount"]))
        if amount <= 0:
            return jsonify({"success": False, "error": "Amount must be greater than zero"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Invalid amount number"}), 400

    trans_type = data.get("type", existing["type"]).strip().lower()
    if trans_type not in ("income", "expense"):
        return jsonify({"success": False, "error": "Invalid transaction type"}), 400

    category = data.get("category", existing["category"]).strip()
    date_val = data.get("date", existing["date"]).strip()
    try:
        datetime.strptime(date_val, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "error": "Invalid date format (expected YYYY-MM-DD)"}), 400

    payment_method = data.get("payment_method", existing["payment_method"]).strip()
    notes = data.get("notes", existing["notes"]).strip()

    update_transaction(
        transaction_id=trans_id,
        title=title,
        amount=amount,
        trans_type=trans_type,
        category=category,
        date=date_val,
        payment_method=payment_method,
        notes=notes,
    )

    return jsonify({"success": True, "message": "Transaction updated successfully"})


@app.route("/api/transactions/<int:trans_id>", methods=["DELETE"])
def delete_transaction_route(trans_id):
    """Delete a transaction by ID."""
    existing = get_transaction_by_id(trans_id)
    if not existing:
        return jsonify({"success": False, "error": "Transaction not found"}), 404

    delete_transaction(trans_id)
    return jsonify({"success": True, "message": "Transaction deleted successfully"})


@app.route("/api/summary", methods=["GET"])
def summary():
    """Get aggregated analytics summary, budget status, and chart datasets."""
    data = get_analytics_summary()
    return jsonify({"success": True, "data": data})


@app.route("/api/budget", methods=["GET", "POST"])
def budget_route():
    """Get or update monthly budget."""
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form.to_dict()
        try:
            budget_val = float(data.get("monthly_budget", 0))
            if budget_val < 0:
                return jsonify({"success": False, "error": "Budget cannot be negative"}), 400
            set_setting("monthly_budget", str(budget_val))
            return jsonify({"success": True, "message": "Budget updated successfully", "budget": budget_val})
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid budget value"}), 400

    budget_val = float(get_setting("monthly_budget", 40000))
    return jsonify({"success": True, "budget": budget_val})


@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """Exports all transactions as a downloadable CSV spreadsheet."""
    transactions = get_all_transactions({"sort_by": "date_desc"})

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Description", "Type", "Category", "Amount", "Payment Method", "Notes"])

    for tx in transactions:
        writer.writerow([
            tx["id"],
            tx["date"],
            tx["title"],
            tx["type"].capitalize(),
            tx["category"],
            f"{tx['amount']:.2f}",
            tx.get("payment_method", "Cash"),
            tx.get("notes", ""),
        ])

    csv_data = output.getvalue()
    filename = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/api/reset", methods=["POST"])
def reset_data():
    """Resets the transactions table with sample demo data."""
    reset_to_sample_data()
    return jsonify({"success": True, "message": "Database reset to sample demo data"})


if __name__ == "__main__":
    print("Starting SpendWise Server at http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
