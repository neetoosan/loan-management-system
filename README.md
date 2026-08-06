# 💰 Loan & Contribution Management System

A production-ready, cross-platform desktop application built with Python and Flet, designed for small-scale financial groups, cooperatives, and microfinance unions (specifically tailored for **Morning Star Cooperative**). It allows seamless management of member profiles, weekly/monthly contributions, loan lifecycle origination and tracking, automated repayment/refund tracking, and detailed financial reports.

---

## 🌟 Key Features

### 🏦 Loan Lifecycle & Automation
* **Automated Origination:** Setup loans with automatic interest rate application, total payback calculations, and payment durations.
* **Member vs. Non-Member Logic:** Differentiates interest calculations based on member status, including automatic interest updates for overdue non-member loans on app startup.
* **Interactive Tracking:** Comprehensive `DataTable` listing all active, pending, cleared, and overdue loans.
* **Guarantor Tracking:** Assign multiple guarantors from the member directory to secure loans.

### 💳 Automatic Payment & Refund System
* **Real-Time Payment Recording:** Repayments are logged instantly to the database, updating the outstanding balance.
* **Overpayment Detection:** If a member pays more than the total due, the system automatically marks the loan as **PAID** and calculates the overpaid amount.
* **Pending Refund Creation:** Automatically generates a refund record marked as `PENDING` (shown in orange status).
* **Admin Refund Approval:** Admins can view and process pending refunds via a single click in the Loan Details panel. Once processed, the status updates to `PROCESSED` (green) with a timestamp.
* **Complete Audit Trail:** Retain full payment and refund histories under each loan's details.

### 📈 Contribution Tracking & Visualizations
* **Savings Tracking:** Track weekly or monthly contributions for every member.
* **Financial Charts:** Real-time visual data analysis using interactive Line Charts and Pie Charts built with Flet, showing total cooperative savings and monthly contribution trends.

### 👤 Member Directory & Portfolios
* **Centralized Profiles:** Manage names, contact info, IPPIS numbers, and total financial standing.
* **Search & Filtering:** Fast filtering options to locate members by status, ID, or name.

### 📥 Excel Data Import Validator
* **Flexible Headers:** Custom `ColumnDetector` with fuzzy header matching for importing external Excel files (e.g. loan schedules).
* **Robust Conversions:** Converts string currencies, percentages, and dates automatically.
* **Duplicate Detection:** Prevents importing duplicate rows to maintain data integrity.

### 📄 Reporting & Exporters
* **Excel Summary Reports:** Export payment logs and member directories.
* **PDF Exporter:** Generate yearly loan statements and monthly contribution sheets using ReportLab.
* **Custom Date Filtering:** Filter reports by custom ranges (this week, this month, this year, or custom dates).

---

## 🛠️ Technical Stack
* **UI Framework:** [Flet](https://flet.dev) (Flutter-powered Python desktop UI)
* **Backend:** Python 3.11+
* **Database & ORM:** SQLAlchemy with SQLite
* **Report Exporters:** ReportLab (PDFs), openpyxl (Excel)
* **Packaging:** Inno Setup Compiler (installer generation)

---

## 📂 Project Structure
```text
LMS-PYTHON-FLET/
├── app/                        # Application Source Code
│   ├── assets/                 # Brand assets, icons, and splash screens
│   ├── components/             # Reusable UI widgets and dialogs
│   │   ├── burger_menu.py      # Navigation drawer
│   │   ├── import_validator.py # Excel sheet importing validator
│   │   ├── loan_details_dialog.py # Detailed view of payments and refunds
│   │   ├── magnified_chart.py  # Charts popup
│   │   ├── reporting.py        # Report generation logic
│   │   └── ui_components.py    # Common layouts, inputs, and feedback cards
│   ├── database/               # Database schemas and SQLAlchemy connection
│   │   ├── connection.py       # CRUD functions, interest updates, and connection sessions
│   │   └── models.py           # User, Member, Loan, Repayment, Refund models
│   ├── views/                  # View layouts and routing screens
│   │   ├── contribution_screen.py # Monthly contribution interface
│   │   ├── loan_screen.py      # Loan operations, payouts, and repayments
│   │   ├── login_screen.py     # Secure user login screen
│   │   └── settings_screen.py  # Cooperative rules and system config
│   ├── app.py                  # Flet run entrypoint wrapper
│   ├── main.py                 # Router, startup checks, and main window setup
│   └── init_admin.py           # Admin account database seeder
├── importdata/                 # Predefined spreadsheets for test data import
├── readme/                     # Extra documentation, diagrams, and developer guides
├── requirements.txt            # System dependencies
├── test_app.py                 # Debugging script for Flet route loading
├── test_reporting.py           # Automated test suite for the reporting system
└── .gitignore                  # Git ignore file
```

---

## 🚀 Getting Started

### Prerequisites
* Python 3.11 or higher installed on your system.
* [Git](https://git-scm.com) installed.

### Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/neetoosan/loan-management-system.git
   cd LMS-PYTHON-FLET
   ```

2. **Set Up a Virtual Environment:**
   * **Windows (Command Prompt / PowerShell):**
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database & Admin User:**
   To set up the SQLite database and create a default admin account, run:
   ```bash
   python app/init_admin.py
   ```
   *This creates a default user with:*
   * **Username:** `admin`
   * **Password:** `admin123`
   * **Role:** `ADMIN`

5. **Run the Application:**
   Run either script to start the desktop app:
   ```bash
   python app/main.py
   ```
   or
   ```bash
   python app/app.py
   ```

---

## 💻 How to Use (Core Workflows)

### 1. Recording a Repayment & Handling Overpayments
* Go to the **Loans** screen.
* Find the target loan, click the **Options (👁️)** icon, and select **Record Payment**.
* Enter the amount paid, payment date, and any notes.
* **If the client overpays**:
  * The loan is automatically marked as `PAID`.
  * An overpayment refund is calculated (e.g., if total due is `₦44,000` and payment is `₦55,000`, a refund of `₦11,000` is generated).
  * A success banner will confirm the payment and note that a pending refund has been registered.

### 2. Processing a Refund (Admin Only)
* Open the **Loan Details** view.
* Locate the **Refund History** section on the left side.
* Pending refunds display with an **orange** label.
* Click the **Process** button next to the pending refund.
* The status updates immediately to `PROCESSED` (green label) with a processed timestamp, logged to the SQLite database.

### 3. Excel Member/Loan Import
* Navigate to the import utility or use the pre-configured imports.
* Upload templates from the `importdata/` folder.
* The system checks all columns, converts currencies (e.g., `₦150,000` to `150000.0`), matches headers fuzzily, and displays a summary before committing changes to the database.

---

## 🧪 Testing

The repository contains test scripts to validate major systems:

* **Report Generator Tests:**
  Tests date filters, PDF rendering, and Excel exports.
  ```bash
  python test_reporting.py
  ```
* **Import Validator Tests:**
  Tests duplicate checker, datatype converters, and column detection.
  ```bash
  python app/test_import_validator.py
  ```
* **Flet Blank Screen Checker:**
  Helper script to dry-run route transitions.
  ```bash
  python test_app.py
  ```

---

## 📦 Desktop Installer

For client deployment, the app has been packaged into a standalone installer using Inno Setup:
* Compilation config: `installer_corrected.iss`
* Output executable: `Output/Morning_Star_Cooperative_Setup-april.exe`

---

## 📄 License
This project is licensed under the MIT License.
