# 💳 SpendWise — Personal Expense & Budget Tracker

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
</p>

<p align="center">
  <strong>A full-stack, responsive Personal Finance and Expense Management Web Application built strictly using Python, HTML, CSS, and Vanilla JavaScript.</strong>
</p>

---

## 📌 Project Overview

**SpendWise** is a lightweight, full-featured financial management dashboard designed to help individuals monitor income, track day-to-day expenditures, set monthly budget ceilings, and analyze spending habits through interactive visualizations.

Developed as part of the **Decode Labs Python Programming Internship (Project 2)**, this project demonstrates clean software architecture, RESTful API design, database normalization, and modern UI/UX design without relying on external frontend frameworks.

---

## ✨ Key Features

### 1. 💰 Income & Expense Tracking
- **Two-Way Transactions**: Record both expenses and income seamlessly.
- **Detailed Metadata**: Track Title, Amount, Category, Date, Payment Method (*Cash, Card, UPI, Bank Transfer*), and custom notes.
- **Full CRUD Support**: Add, view, edit, and delete transactions with instant DOM updates and confirmation modals.

### 2. 📊 Interactive Visual Analytics
- **Category Doughnut Chart**: Visualizes proportion of spending across categories (*Groceries, Rent, Utilities, Dining, Travel, etc.*).
- **Monthly Trend Chart**: Historical comparison of total monthly income vs expenditures.
- **100% Offline Capability**: Includes bundled local chart libraries—renders charts cleanly without requiring an active internet connection.

### 3. 🎯 Budget Velocity & Threshold Alerts
- Set a custom monthly budget limit.
- Real-time progress bar tracking monthly spend percentage.
- **Dynamic Status Badges**:
  - 🟢 `On Track` (< 80% spent)
  - 🟡 `Near Limit` (80% – 100% spent)
  - 🔴 `Over Budget` (> 100% spent)

### 4. 🔍 Live Search & Multi-Level Filtering
- **Real-Time Search**: Instant search filtering by title, note, or category keyword.
- **Granular Filters**: Filter by transaction type (*All / Expense / Income*), category, and custom date range (*From Date – To Date*).
- **Flexible Sorting**: Sort by date (*Newest / Oldest*) or amount (*Highest / Lowest*).
- **Quick Reset**: One-click filter clear button.

### 5. 🎨 Modern UI & Accessibility
- Clean card-based design with fluid micro-interactions and toast notifications.
- **Theme Switcher**: Dark Mode and Light Mode with persistent `localStorage` preference.
- **Multi-Currency Support**: Switch between **₹ INR**, **$ USD**, **€ EUR**, **£ GBP**, **¥ JPY**, and **C$ CAD**.

### 6. 📄 Data Portability & Demo Seeder
- **Export to CSV**: Download all transactions formatted for Excel / Google Sheets in one click.
- **Sample Data Reset**: Pre-loaded with realistic demo data for testing and immediate evaluation.

---

## 🏗️ Architecture & Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                          │
│     HTML5 Semantic Dashboard  •  CSS3 (Dark/Light Mode)     │
│              Vanilla JavaScript (ES6+ Fetch API)            │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON REST API (HTTP)
┌──────────────────────────────▼──────────────────────────────┐
│                       Server Layer                          │
│               Python 3.12  •  Flask Web Framework           │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameterized SQL
┌──────────────────────────────▼──────────────────────────────┐
│                      Database Layer                         │
│                    SQLite3 (expenses.db)                    │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.12, Flask 3.0+ | REST API, Business logic, CSV export engine |
| **Database** | SQLite3 | ACID-compliant, lightweight relational storage |
| **Frontend** | HTML5, CSS3, Vanilla JS | Responsive UI, Modal handlers, Theme & Currency state |
| **Charts** | Chart.js (Offline Bundle) | Interactive client-side canvas data visualizations |

---

## 📁 Repository Directory Structure

```
spendwise-expense-tracker/
├── app.py                  # Flask server application & RESTful API routes
├── database.py             # SQLite helper functions, schema, and sample seeder
├── requirements.txt        # Python dependency manifest
├── .gitignore              # Git ignore rules (ignores cache & local database)
├── README.md               # Comprehensive documentation
├── templates/
│   └── index.html          # Main single-page web dashboard
└── static/
    ├── css/
    │   └── style.css       # Clean styling, responsive layout, CSS variables
    └── js/
        ├── app.js          # Client-side state, API calls, DOM manipulation
        └── chart.min.js    # Local offline Chart.js bundle
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.8 or higher installed on your machine.

### Installation & Execution

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/alokpatitiwari88-crypto/spendwise-expense-tracker.git
   cd spendwise-expense-tracker
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Server**:
   ```bash
   python app.py
   ```
   *(Or on macOS/Linux: `python3 app.py`)*

4. **Access the Dashboard**:
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 🔌 REST API Endpoints

| HTTP Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the main web dashboard |
| `GET` | `/api/transactions` | Query transactions (supports `search`, `type`, `category`, `sort_by`, `start_date`, `end_date`) |
| `GET` | `/api/transactions/<id>` | Fetch a single transaction by ID |
| `POST` | `/api/transactions` | Create a new income/expense transaction |
| `PUT` | `/api/transactions/<id>` | Update an existing transaction |
| `DELETE` | `/api/transactions/<id>` | Delete a transaction |
| `GET` | `/api/summary` | Aggregated analytics (totals, savings rate, breakdown, trends) |
| `GET` | `/api/budget` | Get current monthly budget target |
| `POST` | `/api/budget` | Update monthly budget target |
| `GET` | `/api/export/csv` | Download all transactions as a CSV spreadsheet |
| `POST` | `/api/reset` | Restore initial sample demo dataset |

---

## 👨‍💻 Author & Submission Details

- **Intern**: Alok
- **Program**: Decode Labs Python Programming Internship
- **Assignment**: Project 2 — Personal Expense Tracker
- **GitHub Repository**: [spendwise-expense-tracker](https://github.com/alokpatitiwari88-crypto/spendwise-expense-tracker)
