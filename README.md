# SpendWise — Personal Expense & Budget Tracker

A full-stack, responsive Personal Expense and Financial Tracker web application built exclusively with **Python, HTML, CSS, and JavaScript**.

---

## 🌟 Key Features

### 1. 💰 Income & Expense Management
- Record expenses and incomes with ease.
- Fields include:
  - **Title / Description**
  - **Amount**
  - **Category** (Groceries, Housing, Dining, Transportation, Health, Salary, Freelance, Investments, etc.)
  - **Date** (defaults to today's date)
  - **Payment Method** (Cash, UPI, Credit/Debit Card, Bank Transfer, Other)
  - **Notes / Receipt info**
- Inline **Edit** and **Delete** modals with confirmation protection.

### 2. 📊 Visual Analytics & Interactive Charts
- **Category Breakdown Chart**: Interactive Doughnut chart showing percentage and total spending per category.
- **Monthly Trend Chart**: Comparative bar chart of monthly Income vs Expenses.
- **100% Offline Capability**: Includes a local standalone Chart bundle (`static/js/chart.min.js`), requiring zero internet connection at runtime.

### 3. 🎯 Monthly Budget & Spending Velocity Alerts
- Set a custom target monthly budget.
- Visual progress bar displays percentage of budget consumed.
- Automatic status badges:
  - 🟢 **On Track** (< 80% of budget spent)
  - 🟡 **Near Limit** (80% - 100% of budget spent)
  - 🔴 **Over Budget** (> 100% spent)

### 4. 🔍 Instant Search & Multi-Criteria Filtering
- Real-time search by title, note, or category keyword.
- Filter by transaction type (**All**, **Expenses Only**, **Income Only**).
- Filter by specific category.
- Custom date range filter (**From Date** — **To Date**).
- Sort options: Newest First, Oldest First, Highest Amount, Lowest Amount.
- One-click **Clear Filters** reset button.

### 5. 🌍 Multi-Currency & Dark/Light Themes
- Currency selector supporting **₹ INR**, **$ USD**, **€ EUR**, **£ GBP**, **¥ JPY**, and **C$ CAD**.
- Currency formatting applies dynamically across all cards, transaction items, and charts.
- Dark / Light mode toggle with automatic preference persistence in `localStorage`.

### 6. 📥 CSV Export & Demo Data Reset
- Download all recorded transactions in a spreadsheet-ready `.csv` file anytime.
- One-click **Reset Demo** button to seed fresh demo data for demonstrations or testing.

---

## 📁 Project Structure

```
Project 2/
├── app.py                  # Flask backend & REST API endpoints
├── database.py             # SQLite helper functions, schema, and sample data seeder
├── requirements.txt        # Python dependencies (Flask)
├── run.bat                 # 1-click Windows launcher
├── test_app.py             # Automated unit test suite (8 tests)
├── templates/
│   └── index.html          # Semantic HTML5 single-page application
└── static/
    ├── css/
    │   └── style.css       # Custom modern CSS (variables, dark mode, responsive grid)
    └── js/
        ├── chart.min.js    # Local offline Chart.js bundle
        └── app.js          # Client-side logic, API integration, DOM rendering
```

---

## 🚀 How to Run the Application

### Method 1: One-Click Launcher (Windows)
Simply double-click the **`run.bat`** file in the project folder. It will automatically detect Python/Anaconda, boot the server, and display the URL.

### Method 2: Command Line

1. Open a terminal / command prompt in this directory:
   ```powershell
   cd "c:\Users\alokp\Downloads\Internship\Project 2"
   ```

2. (Optional) Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run the application:
   ```powershell
   python app.py
   ```
   *(Or if using Anaconda: `C:\Users\alokp\anaconda3\python.exe app.py`)*

4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 🧪 Running the Unit Tests

An automated test suite (`test_app.py`) is included to verify all backend routes, database CRUD operations, and calculations:

```powershell
python test_app.py
```

All 8 tests test:
- Index HTML rendering
- Transaction retrieval
- Transaction creation & validation (bad input rejection)
- Transaction update
- Transaction deletion
- Financial summary & budget calculations
- CSV export generation

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the main UI dashboard |
| `GET` | `/api/transactions` | Query transactions (`search`, `type`, `category`, `sort_by`, `start_date`, `end_date`) |
| `GET` | `/api/transactions/<id>` | Fetch a single transaction |
| `POST` | `/api/transactions` | Create a new transaction |
| `PUT` | `/api/transactions/<id>` | Update an existing transaction |
| `DELETE` | `/api/transactions/<id>` | Delete a transaction |
| `GET` | `/api/summary` | Aggregated analytics (income, expense, balance, savings rate, breakdown, trends) |
| `GET` | `/api/budget` | Get current monthly budget target |
| `POST` | `/api/budget` | Update monthly budget target |
| `GET` | `/api/export/csv` | Download all transactions as `.csv` file |
| `POST` | `/api/reset` | Reset database to initial demo transactions |
