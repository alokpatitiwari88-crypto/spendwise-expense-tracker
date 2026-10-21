"""
Flask Server Application for the Expense Tracker.
Combines Python backend with pure HTML, CSS, and Vanilla JS frontend.
"""

import io
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response

import database

app = Flask(__name__)

# Initialize database on startup
database.init_db()


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
    transactions = database.get_all_transactions(filters)
    return jsonify({"success": True, "transactions": transactions, "count": len(transactions)})


@app.route("/api/transactions/<int:trans_id>", methods=["GET"])
def get_transaction(trans_id):
    """Retrieve a single transaction."""
    item = database.get_transaction_by_id(trans_id)
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

    # Validation
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
        # Validate date format YYYY-MM-DD
        try:
            datetime.strptime(date_val, "%Y-%m-%d")
        except ValueError:
            return jsonify({"success": False, "error": "Date must be in YYYY-MM-DD format"}), 400

    new_id = database.add_transaction(
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
def update_transaction(trans_id):
    """Update an existing transaction."""
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data:
        return jsonify({"success": False, "error": "Missing request payload"}), 400

    existing = database.get_transaction_by_id(trans_id)
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

    database.update_transaction(
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
def delete_transaction(trans_id):
    """Delete a transaction by ID."""
    existing = database.get_transaction_by_id(trans_id)
    if not existing:
        return jsonify({"success": False, "error": "Transaction not found"}), 404

    database.delete_transaction(trans_id)
    return jsonify({"success": True, "message": "Transaction deleted successfully"})


@app.route("/api/summary", methods=["GET"])
def summary():
    """Get aggregated analytics summary, budget status, and chart datasets."""
    data = database.get_analytics_summary()
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
            database.set_setting("monthly_budget", str(budget_val))
            return jsonify({"success": True, "message": "Budget updated successfully", "budget": budget_val})
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid budget value"}), 400

    # GET
    budget_val = float(database.get_setting("monthly_budget", 40000))
    return jsonify({"success": True, "budget": budget_val})


@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """Exports all transactions as a downloadable CSV spreadsheet."""
    transactions = database.get_all_transactions({"sort_by": "date_desc"})

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
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
    database.reset_to_sample_data()
    return jsonify({"success": True, "message": "Database reset to sample demo data"})


if __name__ == "__main__":
    print("==================================================")
    print(" Starting SpendWise Expense Tracker Server...   ")
    print(" Open your browser at: http://127.0.0.1:5000     ")
    print("==================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
