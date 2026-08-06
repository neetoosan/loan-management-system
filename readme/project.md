
---

# 💰 Loan & Contribution Management System

A professional cross-platform desktop application designed for small-scale financial groups, cooperatives, and microfinance unions to manage member contributions and loan lifecycles with ease and transparency.

## 🌟 Key Features

### 🏦 Loan Management

* **Automated Origination:** Create new loans with automated interest and repayment schedule calculations.
* **Loan Tracking:** A dedicated `DataTable` to monitor active, pending, and cleared loans.
* **Detailed Audit:** View deep-dive histories for individual loans, including partial payments.

### 📈 Contribution Tracking

* **Member Portfolios:** Track monthly or weekly contributions for every member.
* **Real-time Visualization:** Interactive `LineCharts` and `PieCharts` to visualize total group savings and contribution trends over time.

### 👤 Member Directory

* **Centralized Database:** Manage member profiles, contact information, and their total financial standing.
* **Search & Filter:** Quickly find members by name, ID, or status.

### 🛡️ Security & Integrity

* **Role-Based Access:** Secure login system to differentiate between Admin and Staff users.
* **SQLAlchemy ORM:** Ensures data integrity and provides a robust layer between the UI and the database.

---

## 🏗️ Technical Stack

* **Frontend:** [Flet](https://flet.dev) (Flutter-based UI for Python)
* **Backend:** Python 3.11+
* **Database/ORM:** SQLAlchemy with SQLite 
* **Visualizations:** Flet Built-in Charts

---

## 📂 Project Structure

```text
loan_manager_app/
├── src/
│   ├── main.py              # Application Entry & Router
│   ├── main_window.py       # Main Dashboard Logic
│   ├── database/            # Models & DB Connection
│   ├── views/               # Individual Screens (Login, Tables, Settings)
│   └── components/          # Reusable Dialogs and Widgets
├── assets/                  # Branding and Icons
└── requirements.txt         # Project Dependencies

```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.11 or higher installed.
* Virtual environment (recommended).

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/neetoosan/loan-manager-flet.git
cd loan-manager-flet

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Run the application:**
```bash
python src/main.py

```



---

## 📸 Screenshots

*(Add your screenshots here once the UI is ready)*

> **Tip:** Use `Cmd + Shift + 4` (Mac) or `Win + Shift + S` (Windows) to capture specific areas of your Flet app for the README.

---

## 🗺️ Roadmap

* [ ] Implement PDF report generation for monthly statements.
* [ ] Add SMS/Email notifications for overdue loan repayments.
* [ ] Integrate a "Google Login" option for staff members.
* [ ] Cloud synchronization via PostgreSQL/Supabase.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

---

**Would you like me to help you generate the `requirements.txt` file and the `connection.py` logic to link SQLAlchemy to this structure?**