# Payment & Refund Quick Reference

## Workflow Summary

### Recording a Payment (User)
```
Click "Record Payment" on Loan
    ↓
Enter: Amount, Date, Notes
    ↓
Click "Confirm"
    ↓
[System saves to database]
    ↓
Show success message
```

### What Happens Behind the Scenes
```
1. Validate payment amount (must be > 0)
2. Calculate total due = loan.amount + loan.total_interest
3. Call record_repayment(loan_id, amount, date, notes)
   → Creates LoanRepayment record
   → Updates loan.amount_repaid
   → If total_repaid >= total_due: Mark loan as PAID
4. Check for overpayment (payment > total_due)
5. If overpayment:
   → refund_amount = payment - total_due
   → Call create_refund(loan_id, refund_amount, date, notes)
   → LoanRefund record created with status="PENDING"
6. Refresh loan screen
7. Show: "Payment ₦X recorded! Refund ₦Y created (PENDING)"
```

### Processing a Refund (Admin)
```
Open Loan Details
    ↓
See Refund History section
    ↓
For PENDING refunds: Click "Process" button
    ↓
[System updates status to PROCESSED]
    ↓
Refund shows as PROCESSED with timestamp
```

## Database Tables

### loan_repayments
| Column | Type | Purpose |
|--------|------|---------|
| id | INT | Primary key |
| loan_id | INT FK | Links to loan |
| amount_paid | FLOAT | Payment amount |
| payment_date | DATETIME | When paid |
| notes | VARCHAR | Payment notes |
| created_at | DATETIME | Record creation time |

### loan_refunds
| Column | Type | Purpose |
|--------|------|---------|
| id | INT | Primary key |
| loan_id | INT FK | Links to loan |
| refund_amount | FLOAT | Amount to refund |
| refund_date | DATETIME | When refund issued |
| status | VARCHAR | PENDING/PROCESSED/CANCELLED |
| notes | VARCHAR | Refund notes |
| processed_date | DATETIME | When admin processed |
| created_at | DATETIME | Record creation time |

## Key Functions

### record_repayment(loan_id, amount_paid, payment_date, notes)
- **Purpose**: Save payment to database
- **Auto-updates**: loan.amount_repaid, loan.status
- **Called by**: confirm_repayment()

### create_refund(loan_id, refund_amount, refund_date, notes)
- **Purpose**: Create refund record for overpayments
- **Status**: Always PENDING initially
- **Called by**: confirm_repayment() when overpayment detected

### get_repayments_by_loan(loan_id)
- **Purpose**: Retrieve all payments for a loan
- **Returns**: List of LoanRepayment objects
- **Called by**: loan_details_dialog.py

### get_refunds_by_loan(loan_id)
- **Purpose**: Retrieve all refunds for a loan
- **Returns**: List of LoanRefund objects
- **Called by**: loan_details_dialog.py

### process_refund(refund_id)
- **Purpose**: Mark refund as PROCESSED
- **Updates**: status="PROCESSED", processed_date=now()
- **Called by**: Refund action button in loan_details_dialog

## UI Locations

### Payment Recording
- **Screen**: Loan Screen (loan_screen.py)
- **Component**: Repayment Dialog
- **Button**: "Record Payment" (eyeball icon → action menu)
- **Fields**: Amount, Date, Notes
- **Confirmation**: "Confirm" button

### Payment History View
- **Screen**: Loan Details Dialog (loan_details_dialog.py)
- **Location**: Left column, top section
- **Shows**: All payments with date and notes
- **Table**: S/N, AMOUNT, DATE, NOTES

### Refund History View
- **Screen**: Loan Details Dialog (loan_details_dialog.py)
- **Location**: Left column, below payment history
- **Shows**: All refunds with status
- **Table**: S/N, AMOUNT, DATE, STATUS, ACTION
- **Button**: "Process" for PENDING refunds

## Color Coding

### Payment Status
- Amount: Green (₦20,000)
- Date: Grey
- Notes: White

### Refund Status
- PENDING: Orange text with Process button
- PROCESSED: Green text, no button

## Messages Shown to User

### Successful Payment
```
"Repayment of ₦20,000 recorded on 2024-01-15!"
```

### Payment with Refund
```
"Payment ₦55,000 recorded! Refund ₦11,000 created (PENDING)"
```

### Refund Processed
```
"Refund ₦11,000 processed!"
```

## Scenarios & Examples

### Example 1: Partial Payment
```
Loan Total Due: ₦44,000
Payment: ₦20,000
Result: 
  - Balance: ₦24,000
  - No refund
  - Status: PENDING
```

### Example 2: Complete Payment
```
Loan Total Due: ₦44,000
Payment: ₦44,000
Result:
  - Balance: ₦0
  - No refund
  - Status: PAID
```

### Example 3: Overpayment
```
Loan Total Due: ₦44,000
Payment: ₦55,000
Result:
  - Balance: ₦0
  - Refund: ₦11,000 (PENDING)
  - Status: PAID
  - Admin action needed: Process refund
```

### Example 4: Multiple Payments
```
Loan Total Due: ₦44,000

Payment 1: ₦20,000 → Balance: ₦24,000
Payment 2: ₦15,000 → Balance: ₦9,000
Payment 3: ₦20,000 → Refund: ₦11,000, Balance: ₦0

All payments visible in Payment History
Refund visible in Refund History (PENDING)
```

## Implementation Details

### Overpayment Detection
```python
# In confirm_repayment()
total_due = loan.amount + loan.total_interest
if amount_paid > total_due:
    refund_amount = amount_paid - total_due
    create_refund(loan_id, refund_amount, payment_date, notes)
```

### Status Updates
```python
# In record_repayment()
loan.amount_repaid += amount_paid
if loan.amount_repaid >= total_due:
    loan.status = LoanStatus.PAID
```

### Database Persistence
- All changes committed to SQLite database
- Survives application restarts
- Available for reports and audits
