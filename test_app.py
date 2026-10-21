"""
Comprehensive test suite verifying backend APIs, database interactions,
calculations, and error handling for SpendWise Expense Tracker.
"""

import unittest
import json
import os
import database
from app import app


class ExpenseTrackerTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config["TESTING"] = True
        self.client = app.test_client()

        # Re-initialize database
        database.init_db()

    def test_01_index_route(self):
        """Test home route serves HTML successfully."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SpendWise", response.data)
        self.assertIn(b"Add Transaction", response.data)

    def test_02_get_transactions(self):
        """Test retrieving transactions list."""
        response = self.client.get("/api/transactions")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIsInstance(data["transactions"], list)
        self.assertGreater(len(data["transactions"]), 0)

    def test_03_create_transaction(self):
        """Test creating a valid expense and income transaction."""
        # Create Expense
        new_expense = {
            "title": "Unit Test Coffee",
            "amount": 150.50,
            "type": "expense",
            "category": "Food & Dining",
            "date": "2026-10-21",
            "payment_method": "UPI",
            "notes": "Testing note"
        }
        res = self.client.post("/api/transactions", json=new_expense)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        created_id = data["id"]

        # Verify it can be fetched
        fetch_res = self.client.get(f"/api/transactions/{created_id}")
        self.assertEqual(fetch_res.status_code, 200)
        item = json.loads(fetch_res.data)["transaction"]
        self.assertEqual(item["title"], "Unit Test Coffee")
        self.assertEqual(float(item["amount"]), 150.50)

        # Create Income
        new_income = {
            "title": "Unit Test Bonus",
            "amount": 5000.0,
            "type": "income",
            "category": "Salary",
            "date": "2026-10-21",
            "payment_method": "Bank Transfer",
            "notes": "Bonus"
        }
        res2 = self.client.post("/api/transactions", json=new_income)
        self.assertEqual(res2.status_code, 201)

    def test_04_create_transaction_validation(self):
        """Test error handling for invalid payloads."""
        # Missing title
        bad_req = {"title": "", "amount": 100, "type": "expense", "category": "Food & Dining"}
        res = self.client.post("/api/transactions", json=bad_req)
        self.assertEqual(res.status_code, 400)

        # Invalid amount (zero or negative)
        bad_amt = {"title": "Test", "amount": -50, "type": "expense", "category": "Food & Dining"}
        res = self.client.post("/api/transactions", json=bad_amt)
        self.assertEqual(res.status_code, 400)

        # Invalid type
        bad_type = {"title": "Test", "amount": 100, "type": "unknown", "category": "Food & Dining"}
        res = self.client.post("/api/transactions", json=bad_type)
        self.assertEqual(res.status_code, 400)

    def test_05_update_transaction(self):
        """Test updating an existing transaction."""
        # Create item to update
        res = self.client.post("/api/transactions", json={
            "title": "Update Target",
            "amount": 200,
            "type": "expense",
            "category": "Groceries",
            "date": "2026-10-21",
            "payment_method": "Cash"
        })
        item_id = json.loads(res.data)["id"]

        # Update it
        update_data = {
            "title": "Updated Grocery Title",
            "amount": 275.50,
            "type": "expense",
            "category": "Groceries",
            "date": "2026-10-21",
            "payment_method": "Card",
            "notes": "Updated note"
        }
        put_res = self.client.put(f"/api/transactions/{item_id}", json=update_data)
        self.assertEqual(put_res.status_code, 200)

        # Verify updated values
        get_res = self.client.get(f"/api/transactions/{item_id}")
        item = json.loads(get_res.data)["transaction"]
        self.assertEqual(item["title"], "Updated Grocery Title")
        self.assertEqual(float(item["amount"]), 275.50)
        self.assertEqual(item["payment_method"], "Card")

    def test_06_delete_transaction(self):
        """Test deleting a transaction."""
        # Create item
        res = self.client.post("/api/transactions", json={
            "title": "To Delete",
            "amount": 99,
            "type": "expense",
            "category": "Entertainment",
            "date": "2026-10-21"
        })
        item_id = json.loads(res.data)["id"]

        # Delete it
        del_res = self.client.delete(f"/api/transactions/{item_id}")
        self.assertEqual(del_res.status_code, 200)

        # Confirm 404
        get_res = self.client.get(f"/api/transactions/{item_id}")
        self.assertEqual(get_res.status_code, 404)

    def test_07_summary_and_budget(self):
        """Test summary analytics calculation and budget endpoints."""
        # Check summary
        res = self.client.get("/api/summary")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)["data"]
        self.assertIn("total_income", data)
        self.assertIn("total_expense", data)
        self.assertIn("balance", data)
        self.assertIn("savings_rate", data)
        self.assertIn("expense_by_category", data)
        self.assertIn("monthly_trends", data)

        # Test set budget
        budget_res = self.client.post("/api/budget", json={"monthly_budget": 55000})
        self.assertEqual(budget_res.status_code, 200)

        # Test get budget
        get_b_res = self.client.get("/api/budget")
        self.assertEqual(get_b_res.status_code, 200)
        self.assertEqual(json.loads(get_b_res.data)["budget"], 55000)

    def test_08_csv_export(self):
        """Test CSV export stream."""
        res = self.client.get("/api/export/csv")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "text/csv")
        self.assertIn(b"ID,Date,Description,Type,Category,Amount", response_start := res.data[:100])


if __name__ == "__main__":
    unittest.main()
