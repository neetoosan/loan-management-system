# Payment & Refund System Implementation

## Overview
This document outlines the complete payment and refund system implemented for the LMS-PYTHON-FLET project.

## System Architecture

### Database Layer (models.py)

#### 1. **LoanRepayment Model** (Already Existed)
- Stores individual loan payments
- Fields: id, loan_id, amount_paid, payment_date, notes, created_at

#### 2. **LoanRefund Model** (NEW - Added)
```python
class LoanRefund(Base):
    __tablename__ = "loan_refunds"
    
    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    refund_amount = Column(Float, nullable=False)
    refund_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, PROCESSED, CANCELLED
    notes = Column(String)
    processed_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
```

### Connection Layer (connection.py)

#### 1. **record_repayment()**
- **Purpose**: Record a payment to the database
- **Parameters**:
  - `loan_id`: ID of the loan
  - `amount_paid`: Amount being paid
  - `payment_date`: Date of payment
  - `notes`: Optional notes about the payment
- **Behavior**:
  - Creates a LoanRepayment record
  - Updates `loan.amount_repaid` by adding the payment amount
  - Automatically marks loan as PAID if `amount_repaid >= total_due`
  - Saves to database

#### 2. **get_repayments_by_loan()**
- **Purpose**: Retrieve all payments for a specific loan
- **Parameters**: `loan_id`
- **Returns**: List of LoanRepayment records

#### 3. **create_refund()**
- **Purpose**: Create a refund record when customer overpays
- **Parameters**:
  - `loan_id`: ID of the loan
  - `refund_amount`: Amount to be refunded
  - `refund_date`: Date of refund (default: today)
  - `notes`: Optional notes about the refund
- **Behavior**:
  - Creates a LoanRefund record with status="PENDING"
  - Saves to database
  - Refund awaits admin processing

#### 4. **get_refunds_by_loan()**
- **Purpose**: Retrieve all refunds for a specific loan
- **Parameters**: `loan_id`
- **Returns**: List of LoanRefund records

#### 5. **process_refund()**
- **Purpose**: Admin marks a refund as processed
- **Parameters**: `refund_id`
- **Behavior**:
  - Updates refund status to "PROCESSED"
  - Sets `processed_date` to current datetime
  - Saves to database

## UI Implementation

### Loan Screen (loan_screen.py)

#### Payment Recording Dialog
- **Fields**:
  - Amount to Pay (₦) - Required
  - Payment Date (YYYY-MM-DD) - Auto-fills with today's date
  - Notes (optional) - For payment details
- **Workflow**:
  1. User enters payment amount
  2. System calculates: `total_due = loan.amount + loan.total_interest`
  3. User clicks "Confirm"
  4. **System detects overpayment**:
     - If `payment_amount > total_due`:
       - Calculate refund: `refund_amount = payment_amount - total_due`
       - Create refund record with PENDING status
       - Show message: "Payment ₦X recorded! Refund ₦Y created (PENDING)"
     - If `payment_amount <= total_due`:
       - Record payment normally
       - Show message: "Repayment of ₦X recorded on YYYY-MM-DD!"
  5. Payment and any refunds are saved to database
  6. Loan screen refreshes

#### Example Scenario
```
Loan Details:
- Principal: ₦40,000
- Interest Rate: 10%
- Total Interest: ₦4,000
- Total Due: ₦44,000

User Payment: ₦55,000
System Result:
- Creates LoanRepayment: ₦55,000 (status: REPAID)
- Creates LoanRefund: ₦11,000 (status: PENDING)
- Updates loan.amount_repaid: ₦55,000
- Loan marked as PAID (since 55,000 >= 44,000)
```

### Loan Details Dialog (loan_details_dialog.py)

#### Payment History Section (Left Column)
- **Table**: Shows all payments for the loan
  - Columns: S/N, AMOUNT (₦), DATE, NOTES
  - Total Paid display at bottom

#### Refund History Section (NEW - Left Column Below Payments)
- **Table**: Shows all refunds for the loan
  - Columns: S/N, AMOUNT (₦), DATE, STATUS, ACTION
  - Status color coding:
    - PENDING: Orange
    - PROCESSED: Green
  - "Process" button appears for PENDING refunds
- **Total Refunds display**: Shows total refund amount

#### Admin Actions
- **Process Button** (for PENDING refunds):
  - Click to mark refund as PROCESSED
  - Changes status from PENDING to PROCESSED
  - Sets processed_date timestamp
  - Updates database
  - Shows success message

## Data Flow Diagram

```
User Interface (loan_screen.py)
    |
    v
confirm_repayment() function
    |
    +-- Validate amount
    |
    +-- Calculate total_due
    |
    +-- Call record_repayment()
    |   |
    |   v
    |   [Database] LoanRepayment created
    |   [Update] loan.amount_repaid += payment
    |   [Check] if amount_repaid >= total_due: mark PAID
    |
    +-- Check for overpayment
    |   |
    |   +-- If payment > total_due:
    |   |   |
    |   |   v
    |   |   Call create_refund()
    |   |   |
    |   |   v
    |   |   [Database] LoanRefund created (PENDING)
    |   |
    |   +-- Show refund notification
    |
    v
Refresh UI (loan_screen.py)
    |
    v
User opens Loan Details
    |
    v
loan_details_dialog.py
    |
    +-- get_repayments_by_loan() -> Payment History Table
    |
    +-- get_refunds_by_loan() -> Refund History Table
    |
    v
Display both histories with admin actions
```

## Tables Created in Database

### loan_repayments table
```sql
CREATE TABLE loan_repayments (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL,
    amount_paid FLOAT NOT NULL,
    payment_date DATETIME NOT NULL,
    notes VARCHAR,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (loan_id) REFERENCES loans(id)
)
```

### loan_refunds table
```sql
CREATE TABLE loan_refunds (
    id INTEGER PRIMARY KEY,
    loan_id INTEGER NOT NULL,
    refund_amount FLOAT NOT NULL,
    refund_date DATETIME NOT NULL,
    status VARCHAR DEFAULT 'PENDING',
    notes VARCHAR,
    processed_date DATETIME,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (loan_id) REFERENCES loans(id)
)
```

## Features Implemented

### Payment Recording ✓
- Record any payment amount
- Auto-calculate remaining balance
- Save payment history to database
- Auto-mark loan as PAID when complete

### Refund Detection ✓
- Automatically detect overpayments
- Calculate refund amount: `overpayment = payment - total_due`
- Create refund records with audit trail

### Refund Management ✓
- Track refund status: PENDING → PROCESSED
- Admin can process refunds from loan details dialog
- Timestamp when refund is processed
- Display all refunds with their status

### Payment History ✓
- View all payments for a loan
- Show payment date and notes
- Display total paid amount
- Persistent database storage

### Refund History ✓
- View all refunds for a loan
- Show refund amount and date
- Display current status
- Process button for admin action
- Total refunds amount summary

## Files Modified

1. **src/database/models.py**
   - Added LoanRefund model
   - Added relationship in Loan model

2. **src/database/connection.py**
   - Added LoanRefund import
   - Added record_repayment() function
   - Added get_repayments_by_loan() function
   - Added create_refund() function
   - Added get_refunds_by_loan() function
   - Added process_refund() function

3. **src/views/loan_screen.py**
   - Updated imports to include create_refund
   - Added current_loan_for_repayment state variable
   - Updated open_repayment_dialog() to store current loan
   - Completely rewrote confirm_repayment() to:
     - Call record_repayment() to save payments
     - Detect overpayments
     - Create refund records for overpayments
     - Show appropriate success messages

4. **src/components/loan_details_dialog.py**
   - Updated imports to include refund functions
   - Added refund history section
   - Added refund history table with status and action buttons
   - Added process_refund() callback for admin actions
   - Display total refunds summary

## Testing Scenarios

### Scenario 1: Regular Payment
1. Loan amount: ₦40,000 (Principal) + ₦4,000 (Interest) = ₦44,000
2. Payment: ₦20,000
3. Result:
   - Payment recorded to database
   - Balance: ₦24,000
   - No refund created

### Scenario 2: Exact Payment
1. Loan amount: ₦44,000
2. Payment: ₦44,000
3. Result:
   - Payment recorded to database
   - Balance: ₦0
   - Loan marked as PAID
   - No refund created

### Scenario 3: Overpayment
1. Loan amount: ₦44,000
2. Payment: ₦55,000
3. Result:
   - Payment recorded: ₦55,000
   - Refund created: ₦11,000 (PENDING)
   - Balance: ₦0
   - Loan marked as PAID
   - Admin can process refund from Loan Details

### Scenario 4: Multiple Payments then Refund
1. Loan amount: ₦44,000
2. Payment 1: ₦25,000 (Balance: ₦19,000)
3. Payment 2: ₦28,000
4. Result:
   - First payment recorded normally
   - Second payment recorded
   - Refund created: ₦4,000 (₦28,000 - ₦19,000)
   - Both visible in payment history

## Benefits

1. **Audit Trail**: All payments and refunds recorded in database
2. **Overpayment Handling**: Automatic detection and refund creation
3. **Admin Control**: Can process refunds when ready
4. **History Tracking**: Complete payment and refund history per loan
5. **Data Persistence**: All transactions saved for reports and reconciliation
6. **User Transparency**: Clear display of payment and refund status

## Future Enhancements

- Partial refund processing (refund only part of overpayment)
- Refund reversal (cancel processed refunds)
- Refund payment method selection (cash, transfer, check)
- Refund report generation
- Payment frequency tracking (monthly, quarterly, etc.)
- Late payment penalties
- Payment reminders/notifications
