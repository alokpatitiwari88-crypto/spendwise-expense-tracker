/**
 * SpendWise - Expense Tracker Frontend Application
 * Vanilla JavaScript (ES6+) with Fetch API & Chart.js
 */

// Category Definitions with Emojis & Colors
const CATEGORIES = {
    expense: [
        { name: "Groceries", emoji: "🛒", color: "#10b981" },
        { name: "Housing", emoji: "🏠", color: "#6366f1" },
        { name: "Utilities", emoji: "💡", color: "#f59e0b" },
        { name: "Transportation", emoji: "🚗", color: "#06b6d4" },
        { name: "Food & Dining", emoji: "🍔", color: "#f97316" },
        { name: "Entertainment", emoji: "🎬", color: "#ec4899" },
        { name: "Health & Fitness", emoji: "💪", color: "#8b5cf6" },
        { name: "Education", emoji: "📚", color: "#3b82f6" },
        { name: "Shopping", emoji: "🛍️", color: "#14b8a6" },
        { name: "Travel", emoji: "✈️", color: "#eab308" },
        { name: "Personal Care", emoji: "✨", color: "#d946ef" },
        { name: "Other", emoji: "📦", color: "#64748b" },
    ],
    income: [
        { name: "Salary", emoji: "💼", color: "#10b981" },
        { name: "Freelance", emoji: "💻", color: "#3b82f6" },
        { name: "Investments", emoji: "📈", color: "#8b5cf6" },
        { name: "Business", emoji: "🏢", color: "#06b6d4" },
        { name: "Rental", emoji: "🔑", color: "#f59e0b" },
        { name: "Gifts", emoji: "🎁", color: "#ec4899" },
        { name: "Other", emoji: "💰", color: "#64748b" },
    ]
};

// Global App State
const AppState = {
    currency: localStorage.getItem("spendwise_currency") || "₹",
    theme: localStorage.getItem("spendwise_theme") || "light",
    transactions: [],
    summaryData: null,
    deleteTargetId: null,
    chartTab: "categories", // "categories" or "trends"
    categoryChartInstance: null,
    trendChartInstance: null,
};

// DOM Elements
const DOM = {
    // Theme & Currency
    html: document.documentElement,
    themeToggleBtn: document.getElementById("themeToggleBtn"),
    currencySelect: document.getElementById("currencySelect"),
    formCurrencyPrefix: document.getElementById("formCurrencyPrefix"),
    budgetCurrencyPrefix: document.getElementById("budgetCurrencyPrefix"),

    // Action Buttons
    openBudgetModalBtn: document.getElementById("openBudgetModalBtn"),
    exportCsvBtn: document.getElementById("exportCsvBtn"),
    resetDemoBtn: document.getElementById("resetDemoBtn"),

    // KPI Elements
    kpiBalance: document.getElementById("kpiBalance"),
    kpiIncome: document.getElementById("kpiIncome"),
    kpiExpense: document.getElementById("kpiExpense"),
    kpiSavingsRate: document.getElementById("kpiSavingsRate"),
    kpiMonthIncome: document.getElementById("kpiMonthIncome"),
    kpiMonthExpense: document.getElementById("kpiMonthExpense"),
    kpiBudgetBadge: document.getElementById("kpiBudgetBadge"),
    kpiBudgetLimit: document.getElementById("kpiBudgetLimit"),
    budgetProgressBar: document.getElementById("budgetProgressBar"),
    kpiBudgetSpent: document.getElementById("kpiBudgetSpent"),
    kpiBudgetRemaining: document.getElementById("kpiBudgetRemaining"),

    // Form Elements
    addTransactionForm: document.getElementById("addTransactionForm"),
    tabExpense: document.getElementById("tabExpense"),
    tabIncome: document.getElementById("tabIncome"),
    formType: document.getElementById("formType"),
    formTitle: document.getElementById("formTitle"),
    formAmount: document.getElementById("formAmount"),
    formCategory: document.getElementById("formCategory"),
    formDate: document.getElementById("formDate"),
    formPaymentMethod: document.getElementById("formPaymentMethod"),
    formNotes: document.getElementById("formNotes"),

    // Chart Elements
    chartTabCategory: document.getElementById("chartTabCategory"),
    chartTabTrends: document.getElementById("chartTabTrends"),
    categoryChartContainer: document.getElementById("categoryChartContainer"),
    trendChartContainer: document.getElementById("trendChartContainer"),
    categoryChartCanvas: document.getElementById("categoryChart"),
    trendChartCanvas: document.getElementById("trendChart"),
    categoryChartEmpty: document.getElementById("categoryChartEmpty"),
    trendChartEmpty: document.getElementById("trendChartEmpty"),

    // Transactions History & Filter Elements
    transactionsList: document.getElementById("transactionsList"),
    transactionsCount: document.getElementById("transactionsCount"),
    emptyState: document.getElementById("emptyState"),
    filterSearch: document.getElementById("filterSearch"),
    filterType: document.getElementById("filterType"),
    filterCategory: document.getElementById("filterCategory"),
    filterSort: document.getElementById("filterSort"),
    filterStartDate: document.getElementById("filterStartDate"),
    filterEndDate: document.getElementById("filterEndDate"),
    clearFiltersBtn: document.getElementById("clearFiltersBtn"),

    // Edit Modal Elements
    editModal: document.getElementById("editModal"),
    editTransactionForm: document.getElementById("editTransactionForm"),
    closeEditModalBtn: document.getElementById("closeEditModalBtn"),
    cancelEditModalBtn: document.getElementById("cancelEditModalBtn"),
    editId: document.getElementById("editId"),
    editType: document.getElementById("editType"),
    editTitle: document.getElementById("editTitle"),
    editAmount: document.getElementById("editAmount"),
    editCategory: document.getElementById("editCategory"),
    editDate: document.getElementById("editDate"),
    editPaymentMethod: document.getElementById("editPaymentMethod"),
    editNotes: document.getElementById("editNotes"),

    // Budget Modal Elements
    budgetModal: document.getElementById("budgetModal"),
    setBudgetForm: document.getElementById("setBudgetForm"),
    modalBudgetInput: document.getElementById("modalBudgetInput"),
    closeBudgetModalBtn: document.getElementById("closeBudgetModalBtn"),
    cancelBudgetModalBtn: document.getElementById("cancelBudgetModalBtn"),

    // Delete Modal Elements
    deleteModal: document.getElementById("deleteModal"),
    deleteItemPreview: document.getElementById("deleteItemPreview"),
    closeDeleteModalBtn: document.getElementById("closeDeleteModalBtn"),
    cancelDeleteModalBtn: document.getElementById("cancelDeleteModalBtn"),
    confirmDeleteBtn: document.getElementById("confirmDeleteBtn"),

    // Toast Container
    toastContainer: document.getElementById("toastContainer"),
};

// ==========================================================================
// Utility Functions
// ==========================================================================

function formatCurrency(amount) {
    const num = Number(amount) || 0;
    return `${AppState.currency}${num.toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })}`;
}

function formatDate(dateStr) {
    if (!dateStr) return "";
    try {
        const parts = dateStr.split("-");
        const date = new Date(parts[0], parts[1] - 1, parts[2]);
        return date.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric"
        });
    } catch {
        return dateStr;
    }
}

function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let iconSvg = "";
    if (type === "success") {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (type === "error") {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
    } else {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    toast.innerHTML = `${iconSvg} <span>${escapeHtml(message)}</span>`;
    DOM.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = "fadeOut 0.3s ease forwards";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function getCategoryMeta(categoryName, type = "expense") {
    const list = CATEGORIES[type] || CATEGORIES.expense;
    const match = list.find((c) => c.name.toLowerCase() === categoryName.toLowerCase());
    if (match) return match;

    // Check opposite type
    const oppositeList = type === "expense" ? CATEGORIES.income : CATEGORIES.expense;
    const oppMatch = oppositeList.find((c) => c.name.toLowerCase() === categoryName.toLowerCase());
    if (oppMatch) return oppMatch;

    return { name: categoryName, emoji: "🏷️", color: "#64748b" };
}

// ==========================================================================
// Initialization & Theme Handling
// ==========================================================================

function initApp() {
    // 1. Setup Theme
    DOM.html.setAttribute("data-theme", AppState.theme);
    DOM.themeToggleBtn.addEventListener("click", toggleTheme);

    // 2. Setup Currency
    DOM.currencySelect.value = AppState.currency;
    updateCurrencyPrefixes();
    DOM.currencySelect.addEventListener("change", (e) => {
        AppState.currency = e.target.value;
        localStorage.setItem("spendwise_currency", AppState.currency);
        updateCurrencyPrefixes();
        renderSummary(AppState.summaryData);
        renderTransactions(AppState.transactions);
        updateCharts(AppState.summaryData);
        showToast(`Currency changed to ${AppState.currency}`, "info");
    });

    // 3. Default form date to today
    DOM.formDate.value = new Date().toISOString().split("T")[0];

    // 4. Populate Form & Filter Categories
    populateCategoryOptions(DOM.formCategory, "expense");
    populateFilterCategories();

    // 5. Setup Event Listeners
    setupEventListeners();

    // 6. Initial Data Load
    refreshAll();
}

function toggleTheme() {
    AppState.theme = AppState.theme === "light" ? "dark" : "light";
    DOM.html.setAttribute("data-theme", AppState.theme);
    localStorage.setItem("spendwise_theme", AppState.theme);
    if (AppState.summaryData) {
        updateCharts(AppState.summaryData);
    }
}

function updateCurrencyPrefixes() {
    DOM.formCurrencyPrefix.textContent = AppState.currency;
    DOM.budgetCurrencyPrefix.textContent = AppState.currency;
}

function populateCategoryOptions(selectElement, type, selectedValue = null) {
    selectElement.innerHTML = "";
    const categories = CATEGORIES[type] || CATEGORIES.expense;
    categories.forEach((cat) => {
        const option = document.createElement("option");
        option.value = cat.name;
        option.textContent = `${cat.emoji} ${cat.name}`;
        if (selectedValue && selectedValue.toLowerCase() === cat.name.toLowerCase()) {
            option.selected = true;
        }
        selectElement.appendChild(option);
    });
}

function populateFilterCategories() {
    const currentVal = DOM.filterCategory.value;
    DOM.filterCategory.innerHTML = `<option value="all">All Categories</option>`;

    // Merge unique categories from both expense and income
    const all = [...CATEGORIES.expense, ...CATEGORIES.income];
    const seen = new Set();

    all.forEach((cat) => {
        if (!seen.has(cat.name)) {
            seen.add(cat.name);
            const option = document.createElement("option");
            option.value = cat.name;
            option.textContent = `${cat.emoji} ${cat.name}`;
            DOM.filterCategory.appendChild(option);
        }
    });

    if (currentVal) DOM.filterCategory.value = currentVal;
}

// ==========================================================================
// Event Listeners Setup
// ==========================================================================

function setupEventListeners() {
    // Form Type Switcher (Expense / Income)
    DOM.tabExpense.addEventListener("click", () => switchFormType("expense"));
    DOM.tabIncome.addEventListener("click", () => switchFormType("income"));

    // Add Transaction Form
    DOM.addTransactionForm.addEventListener("submit", handleAddTransaction);

    // Edit Transaction Form
    DOM.editTransactionForm.addEventListener("submit", handleUpdateTransaction);
    DOM.editType.addEventListener("change", (e) => {
        populateCategoryOptions(DOM.editCategory, e.target.value);
    });

    // Close Modals
    DOM.closeEditModalBtn.addEventListener("click", closeEditModal);
    DOM.cancelEditModalBtn.addEventListener("click", closeEditModal);

    DOM.openBudgetModalBtn.addEventListener("click", openBudgetModal);
    DOM.closeBudgetModalBtn.addEventListener("click", closeBudgetModal);
    DOM.cancelBudgetModalBtn.addEventListener("click", closeBudgetModal);
    DOM.setBudgetForm.addEventListener("submit", handleSaveBudget);

    DOM.closeDeleteModalBtn.addEventListener("click", closeDeleteModal);
    DOM.cancelDeleteModalBtn.addEventListener("click", closeDeleteModal);
    DOM.confirmDeleteBtn.addEventListener("click", handleConfirmDelete);

    // Close modal on backdrop click
    [DOM.editModal, DOM.budgetModal, DOM.deleteModal].forEach((modal) => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                closeAllModals();
            }
        });
    });

    // Chart Tabs
    DOM.chartTabCategory.addEventListener("click", () => switchChartTab("categories"));
    DOM.chartTabTrends.addEventListener("click", () => switchChartTab("trends"));

    // Filter controls
    DOM.filterSearch.addEventListener("input", debounce(fetchTransactions, 300));
    DOM.filterType.addEventListener("change", fetchTransactions);
    DOM.filterCategory.addEventListener("change", fetchTransactions);
    DOM.filterSort.addEventListener("change", fetchTransactions);
    DOM.filterStartDate.addEventListener("change", fetchTransactions);
    DOM.filterEndDate.addEventListener("change", fetchTransactions);

    DOM.clearFiltersBtn.addEventListener("click", () => {
        DOM.filterSearch.value = "";
        DOM.filterType.value = "";
        DOM.filterCategory.value = "all";
        DOM.filterSort.value = "date_desc";
        DOM.filterStartDate.value = "";
        DOM.filterEndDate.value = "";
        fetchTransactions();
        showToast("Filters cleared", "info");
    });

    // Export CSV
    DOM.exportCsvBtn.addEventListener("click", () => {
        window.location.href = "/api/export/csv";
        showToast("Generating CSV export...", "success");
    });

    // Reset Demo Data
    DOM.resetDemoBtn.addEventListener("click", async () => {
        if (confirm("Reset transactions to sample demo data? Your custom transactions will be overwritten.")) {
            try {
                const res = await fetch("/api/reset", { method: "POST" });
                const data = await res.json();
                if (data.success) {
                    showToast("Database restored with sample demo data", "success");
                    refreshAll();
                }
            } catch (err) {
                showToast("Failed to reset demo data", "error");
            }
        }
    });
}

function switchFormType(type) {
    DOM.formType.value = type;
    if (type === "expense") {
        DOM.tabExpense.className = "type-tab-btn active-expense";
        DOM.tabIncome.className = "type-tab-btn";
        populateCategoryOptions(DOM.formCategory, "expense");
    } else {
        DOM.tabExpense.className = "type-tab-btn";
        DOM.tabIncome.className = "type-tab-btn active-income";
        populateCategoryOptions(DOM.formCategory, "income");
    }
}

function switchChartTab(tab) {
    AppState.chartTab = tab;
    if (tab === "categories") {
        DOM.chartTabCategory.classList.add("active");
        DOM.chartTabTrends.classList.remove("active");
        DOM.categoryChartContainer.style.display = "flex";
        DOM.trendChartContainer.style.display = "none";
    } else {
        DOM.chartTabTrends.classList.add("active");
        DOM.chartTabCategory.classList.remove("active");
        DOM.trendChartContainer.style.display = "flex";
        DOM.categoryChartContainer.style.display = "none";
    }
}

// ==========================================================================
// API Operations & Data Fetching
// ==========================================================================

async function refreshAll() {
    await Promise.all([fetchSummary(), fetchTransactions()]);
}

async function fetchSummary() {
    try {
        const res = await fetch("/api/summary");
        const json = await res.json();
        if (json.success) {
            AppState.summaryData = json.data;
            renderSummary(json.data);
            updateCharts(json.data);
        }
    } catch (err) {
        console.error("Error fetching summary:", err);
    }
}

async function fetchTransactions() {
    try {
        const params = new URLSearchParams({
            search: DOM.filterSearch.value.trim(),
            type: DOM.filterType.value,
            category: DOM.filterCategory.value,
            sort_by: DOM.filterSort.value,
            start_date: DOM.filterStartDate.value,
            end_date: DOM.filterEndDate.value,
        });

        const res = await fetch(`/api/transactions?${params.toString()}`);
        const json = await res.json();
        if (json.success) {
            AppState.transactions = json.transactions;
            renderTransactions(json.transactions);
        }
    } catch (err) {
        console.error("Error fetching transactions:", err);
    }
}

// ==========================================================================
// Render Functions
// ==========================================================================

function renderSummary(data) {
    if (!data) return;

    // Net Balance
    const balance = data.balance;
    DOM.kpiBalance.textContent = (balance < 0 ? "-" : "") + formatCurrency(Math.abs(balance));
    DOM.kpiBalance.className = "kpi-value " + (balance >= 0 ? "positive" : "negative");
    DOM.kpiSavingsRate.textContent = `Savings Rate: ${data.savings_rate}%`;

    // Totals
    DOM.kpiIncome.textContent = `+${formatCurrency(data.total_income)}`;
    DOM.kpiExpense.textContent = `-${formatCurrency(data.total_expense)}`;

    // Current Month Subtext
    DOM.kpiMonthIncome.textContent = `${data.current_month.month_name}: +${formatCurrency(data.current_month.income)}`;
    DOM.kpiMonthExpense.textContent = `${data.current_month.month_name}: -${formatCurrency(data.current_month.expense)}`;

    // Monthly Budget & Velocity
    const budget = data.current_month.budget;
    const spent = data.current_month.expense;
    const pct = data.current_month.budget_percentage;
    const remaining = data.current_month.budget_remaining;

    DOM.kpiBudgetLimit.textContent = formatCurrency(budget);
    DOM.budgetProgressBar.style.width = `${Math.min(pct, 100)}%`;

    DOM.kpiBudgetSpent.textContent = `${pct}% of target spent`;
    if (remaining >= 0) {
        DOM.kpiBudgetRemaining.textContent = `Remaining: ${formatCurrency(remaining)}`;
    } else {
        DOM.kpiBudgetRemaining.textContent = `Over budget by: ${formatCurrency(Math.abs(remaining))}`;
    }

    // Badge color alert
    DOM.budgetProgressBar.className = "budget-progress-bar";
    DOM.kpiBudgetBadge.className = "budget-badge";

    if (pct > 100) {
        DOM.kpiBudgetBadge.textContent = "Over Budget";
        DOM.kpiBudgetBadge.classList.add("badge-danger");
        DOM.budgetProgressBar.classList.add("bar-danger");
    } else if (pct >= 80) {
        DOM.kpiBudgetBadge.textContent = "Near Limit";
        DOM.kpiBudgetBadge.classList.add("badge-warning");
        DOM.budgetProgressBar.classList.add("bar-warning");
    } else {
        DOM.kpiBudgetBadge.textContent = "On Track";
    }
}

function renderTransactions(transactions) {
    DOM.transactionsCount.textContent = `${transactions.length} ${transactions.length === 1 ? "entry" : "entries"}`;

    if (!transactions || transactions.length === 0) {
        DOM.transactionsList.innerHTML = "";
        DOM.emptyState.style.display = "block";
        return;
    }

    DOM.emptyState.style.display = "none";
    DOM.transactionsList.innerHTML = "";

    transactions.forEach((tx) => {
        const meta = getCategoryMeta(tx.category, tx.type);
        const isIncome = tx.type === "income";

        const li = document.createElement("li");
        li.className = "tx-item";
        li.innerHTML = `
            <div class="tx-left">
                <div class="tx-category-badge" style="background-color: ${meta.color}20; color: ${meta.color};">
                    ${meta.emoji}
                </div>
                <div class="tx-info">
                    <span class="tx-title" title="${escapeHtml(tx.title)}">${escapeHtml(tx.title)}</span>
                    <div class="tx-meta">
                        <span>${formatDate(tx.date)}</span>
                        <span>•</span>
                        <span class="tx-method-pill">${escapeHtml(tx.payment_method || "Cash")}</span>
                        ${tx.notes ? `<span>•</span><span class="tx-notes-preview" title="${escapeHtml(tx.notes)}">${escapeHtml(tx.notes)}</span>` : ""}
                    </div>
                </div>
            </div>
            <div class="tx-right">
                <span class="tx-amount ${isIncome ? "amount-income" : "amount-expense"}">
                    ${isIncome ? "+" : "-"}${formatCurrency(tx.amount)}
                </span>
                <div class="tx-actions">
                    <button class="action-icon-btn edit-btn" data-id="${tx.id}" title="Edit transaction">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 20h9"></path>
                            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                        </svg>
                    </button>
                    <button class="action-icon-btn delete-btn" data-id="${tx.id}" title="Delete transaction">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        // Action button triggers
        li.querySelector(".edit-btn").addEventListener("click", () => openEditModal(tx));
        li.querySelector(".delete-btn").addEventListener("click", () => openDeleteModal(tx));

        DOM.transactionsList.appendChild(li);
    });
}

// ==========================================================================
// Chart.js Visualizations
// ==========================================================================

function updateCharts(summary) {
    if (!window.Chart || !summary) return;

    const isDark = DOM.html.getAttribute("data-theme") === "dark";
    const textColor = isDark ? "#cbd5e1" : "#475569";
    const gridColor = isDark ? "#273449" : "#e2e8f0";

    // 1. Category Doughnut Chart (Expenses)
    const expenseCats = summary.expense_by_category || [];
    if (expenseCats.length === 0) {
        DOM.categoryChartCanvas.style.display = "none";
        DOM.categoryChartEmpty.style.display = "block";
    } else {
        DOM.categoryChartCanvas.style.display = "block";
        DOM.categoryChartEmpty.style.display = "none";

        const labels = expenseCats.map((c) => c.category);
        const amounts = expenseCats.map((c) => c.total);
        const colors = expenseCats.map((c) => getCategoryMeta(c.category, "expense").color);

        if (AppState.categoryChartInstance) {
            AppState.categoryChartInstance.destroy();
        }

        AppState.categoryChartInstance = new Chart(DOM.categoryChartCanvas, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: amounts,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: isDark ? "#151c2c" : "#ffffff",
                    hoverOffset: 6,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "right",
                        labels: {
                            color: textColor,
                            font: { family: "-apple-system, BlinkMacSystemFont, Segoe UI", size: 12 },
                            boxWidth: 14,
                            padding: 10,
                        },
                    },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                const val = ctx.raw || 0;
                                const total = amounts.reduce((a, b) => a + b, 0);
                                const percentage = ((val / total) * 100).toFixed(1);
                                return ` ${ctx.label}: ${formatCurrency(val)} (${percentage}%)`;
                            },
                        },
                    },
                },
                cutout: "68%",
            },
        });
    }

    // 2. Monthly Trend Chart (Income vs Expense)
    const trends = summary.monthly_trends || [];
    if (trends.length === 0) {
        DOM.trendChartCanvas.style.display = "none";
        DOM.trendChartEmpty.style.display = "block";
    } else {
        DOM.trendChartCanvas.style.display = "block";
        DOM.trendChartEmpty.style.display = "none";

        const trendLabels = trends.map((t) => {
            const parts = t.month.split("-");
            const d = new Date(parts[0], parts[1] - 1);
            return d.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
        });
        const incomeData = trends.map((t) => t.income);
        const expenseData = trends.map((t) => t.expense);

        if (AppState.trendChartInstance) {
            AppState.trendChartInstance.destroy();
        }

        AppState.trendChartInstance = new Chart(DOM.trendChartCanvas, {
            type: "bar",
            data: {
                labels: trendLabels,
                datasets: [
                    {
                        label: "Income",
                        data: incomeData,
                        backgroundColor: "#10b981",
                        borderRadius: 6,
                    },
                    {
                        label: "Expense",
                        data: expenseData,
                        backgroundColor: "#f43f5e",
                        borderRadius: 6,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: textColor },
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            callback: function (val) {
                                return AppState.currency + val;
                            },
                        },
                    },
                },
                plugins: {
                    legend: {
                        position: "top",
                        labels: { color: textColor, boxWidth: 12 },
                    },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`;
                            },
                        },
                    },
                },
            },
        });
    }
}

// ==========================================================================
// Form Handlers & CRUD Logic
// ==========================================================================

async function handleAddTransaction(e) {
    e.preventDefault();

    const payload = {
        title: DOM.formTitle.value.trim(),
        amount: parseFloat(DOM.formAmount.value),
        type: DOM.formType.value,
        category: DOM.formCategory.value,
        date: DOM.formDate.value,
        payment_method: DOM.formPaymentMethod.value,
        notes: DOM.formNotes.value.trim(),
    };

    if (!payload.title || isNaN(payload.amount) || payload.amount <= 0) {
        showToast("Please enter a valid title and positive amount", "error");
        return;
    }

    try {
        const res = await fetch("/api/transactions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const json = await res.json();

        if (json.success) {
            showToast(`${payload.type === "income" ? "Income" : "Expense"} recorded successfully`, "success");
            DOM.formTitle.value = "";
            DOM.formAmount.value = "";
            DOM.formNotes.value = "";
            refreshAll();
        } else {
            showToast(json.error || "Failed to add transaction", "error");
        }
    } catch (err) {
        showToast("Network error while adding transaction", "error");
    }
}

function openEditModal(tx) {
    DOM.editId.value = tx.id;
    DOM.editType.value = tx.type;
    populateCategoryOptions(DOM.editCategory, tx.type, tx.category);
    DOM.editTitle.value = tx.title;
    DOM.editAmount.value = tx.amount;
    DOM.editDate.value = tx.date;
    DOM.editPaymentMethod.value = tx.payment_method || "Cash";
    DOM.editNotes.value = tx.notes || "";

    DOM.editModal.classList.add("active");
    DOM.editModal.setAttribute("aria-hidden", "false");
}

function closeEditModal() {
    DOM.editModal.classList.remove("active");
    DOM.editModal.setAttribute("aria-hidden", "true");
}

async function handleUpdateTransaction(e) {
    e.preventDefault();
    const id = DOM.editId.value;

    const payload = {
        title: DOM.editTitle.value.trim(),
        amount: parseFloat(DOM.editAmount.value),
        type: DOM.editType.value,
        category: DOM.editCategory.value,
        date: DOM.editDate.value,
        payment_method: DOM.editPaymentMethod.value,
        notes: DOM.editNotes.value.trim(),
    };

    try {
        const res = await fetch(`/api/transactions/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const json = await res.json();

        if (json.success) {
            showToast("Transaction updated successfully", "success");
            closeEditModal();
            refreshAll();
        } else {
            showToast(json.error || "Failed to update transaction", "error");
        }
    } catch (err) {
        showToast("Error updating transaction", "error");
    }
}

function openDeleteModal(tx) {
    AppState.deleteTargetId = tx.id;
    DOM.deleteItemPreview.innerHTML = `
        <strong>${escapeHtml(tx.title)}</strong><br>
        <span style="color: ${tx.type === "income" ? "var(--success)" : "var(--danger)"}">
            ${tx.type === "income" ? "+" : "-"}${formatCurrency(tx.amount)}
        </span> • ${formatDate(tx.date)}
    `;
    DOM.deleteModal.classList.add("active");
    DOM.deleteModal.setAttribute("aria-hidden", "false");
}

function closeDeleteModal() {
    AppState.deleteTargetId = null;
    DOM.deleteModal.classList.remove("active");
    DOM.deleteModal.setAttribute("aria-hidden", "true");
}

async function handleConfirmDelete() {
    if (!AppState.deleteTargetId) return;

    try {
        const res = await fetch(`/api/transactions/${AppState.deleteTargetId}`, {
            method: "DELETE",
        });
        const json = await res.json();

        if (json.success) {
            showToast("Transaction deleted", "info");
            closeDeleteModal();
            refreshAll();
        } else {
            showToast(json.error || "Failed to delete transaction", "error");
        }
    } catch (err) {
        showToast("Error deleting transaction", "error");
    }
}

// Budget Modal Handlers
async function openBudgetModal() {
    try {
        const res = await fetch("/api/budget");
        const json = await res.json();
        if (json.success) {
            DOM.modalBudgetInput.value = json.budget;
        }
    } catch {
        DOM.modalBudgetInput.value = 40000;
    }
    DOM.budgetModal.classList.add("active");
    DOM.budgetModal.setAttribute("aria-hidden", "false");
}

function closeBudgetModal() {
    DOM.budgetModal.classList.remove("active");
    DOM.budgetModal.setAttribute("aria-hidden", "true");
}

async function handleSaveBudget(e) {
    e.preventDefault();
    const budgetVal = parseFloat(DOM.modalBudgetInput.value);

    if (isNaN(budgetVal) || budgetVal < 0) {
        showToast("Please enter a valid budget amount", "error");
        return;
    }

    try {
        const res = await fetch("/api/budget", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ monthly_budget: budgetVal }),
        });
        const json = await res.json();

        if (json.success) {
            showToast("Monthly budget updated successfully", "success");
            closeBudgetModal();
            refreshAll();
        } else {
            showToast(json.error || "Failed to update budget", "error");
        }
    } catch (err) {
        showToast("Error updating budget", "error");
    }
}

function closeAllModals() {
    closeEditModal();
    closeBudgetModal();
    closeDeleteModal();
}

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Start application when DOM is ready
document.addEventListener("DOMContentLoaded", initApp);
