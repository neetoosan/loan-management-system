# Payment & Refund System - Visual Guide

## User Interface Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   LOAN SCREEN                               │
│                                                              │
│  [Loan 1]  [Loan 2]  [Loan 3]  [Loan 4]                    │
│    👁️        👁️        👁️        👁️                          │
│  ┌─────────────────────────────────────────┐               │
│  │ View Details  | Record Payment  | Edit  │               │
│  │ (eyeball menu shows options)            │               │
│  └─────────────────────────────────────────┘               │
│                                                              │
│ User clicks "Record Payment"                               │
│       ↓                                                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
        ┌──────────────────────────────────────────┐
        │   REPAYMENT DIALOG                       │
        │  ┌──────────────────────────────────────┐│
        │  │ Loan #1 - John Doe: ₦40,000         ││
        │  │                                      ││
        │  │ Amount to Pay:    [      ] ₦         ││
        │  │ Payment Date:     [2024-01-15]      ││
        │  │ Notes:            [            ]    ││
        │  │                   [            ]    ││
        │  │ ┌──────────┬──────────┬─────────┐  ││
        │  │ │ Cancel   │ Clear    │ Confirm │  ││
        │  │ └──────────┴──────────┴─────────┘  ││
        │  └──────────────────────────────────────┘│
        │                                          │
        └──────────────────────────────────────────┘
                           │
              User enters: ₦55,000
                           │
                           ↓
        ┌──────────────────────────────────────────┐
        │      SYSTEM PROCESSING                   │
        │  ┌──────────────────────────────────────┐│
        │  │ 1. Calculate total due:              ││
        │  │    ₦40,000 + ₦4,000 = ₦44,000      ││
        │  │                                      ││
        │  │ 2. Compare: ₦55,000 > ₦44,000 ✓    ││
        │  │                                      ││
        │  │ 3. Calculate refund:                ││
        │  │    ₦55,000 - ₦44,000 = ₦11,000    ││
        │  │                                      ││
        │  │ 4. Save payment to database          ││
        │  │    → LoanRepayment created          ││
        │  │                                      ││
        │  │ 5. Create refund record              ││
        │  │    → LoanRefund created (PENDING)   ││
        │  │                                      ││
        │  │ 6. Update loan.amount_repaid        ││
        │  │    → ₦55,000                        ││
        │  │                                      ││
        │  │ 7. Mark loan as PAID                ││
        │  │    → status = PAID                  ││
        │  └──────────────────────────────────────┘│
        │                                          │
        └──────────────────────────────────────────┘
                           │
                           ↓
        ┌──────────────────────────────────────────┐
        │   SUCCESS MESSAGE                        │
        │                                          │
        │   "Payment ₦55,000 recorded!            │
        │    Refund ₦11,000 created (PENDING)"    │
        │                                          │
        └──────────────────────────────────────────┘
                           │
                           ↓
        ┌──────────────────────────────────────────┐
        │   LOAN DETAILS DIALOG                    │
        │                                          │
        │  LEFT COLUMN:          RIGHT COLUMN:    │
        │  ┌──────────────────┐  ┌─────────────┐ │
        │  │ PAYMENT HISTORY  │  │ LOAN        │ │
        │  │ ┌────────────────┐  │ DETAILS     │ │
        │  │ │S/N│AMT│DATE│NT│  │             │ │
        │  │ ├────────────────┤  │ Borrower    │ │
        │  │ │ 1 │₦55K│2024-01  │ Guarantor   │ │
        │  │ └────────────────┘  │ Amount      │ │
        │  │ Total: ₦55,000      │ Status: PAID│ │
        │  │                    │             │ │
        │  │ REFUND HISTORY     │ ...etc      │ │
        │  │ ┌────────────────┐  └─────────────┘ │
        │  │ │S/N│AMT│DT│STS│   │                │
        │  │ ├────────────────┤   │                │
        │  │ │ 1 │₦11│01│PND│   │                │
        │  │ │  │  │  │ [Process]                │
        │  │ └────────────────┘  │                │
        │  │ Total: ₦11,000     │                │
        │  └──────────────────┘  │                │
        │                        │                │
        │  Admin clicks          │                │
        │  [Process] button      │                │
        │       ↓                 │                │
        │  Status → PROCESSED    │                │
        │  Timestamp recorded    │                │
        │                        │                │
        └──────────────────────────────────────────┘
```

## Database Schema

```
┌──────────────────────┐         ┌──────────────────────┐
│     LOANS TABLE      │         │ LOAN_REPAYMENTS TABLE │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)             │ 1   ─────↤ id (PK)             │
│ amount              │    ∞    │ loan_id (FK)        │
│ total_interest      │         │ amount_paid         │
│ amount_repaid       │         │ payment_date        │
│ interest_rate       │         │ notes               │
│ status (PAID)       │         │ created_at          │
│ guarantor_name      │         └──────────────────────┘
│ guarantor_phone     │
│ ...                 │
└──────────────────────┘
       │
       │ 1
       ├─────────↤ ∞
       │
┌──────────────────────┐
│  LOAN_REFUNDS TABLE  │
├──────────────────────┤
│ id (PK)             │
│ loan_id (FK)        │
│ refund_amount       │
│ refund_date         │
│ status (PENDING)    │
│ notes               │
│ processed_date      │
│ created_at          │
└──────────────────────┘
```

## Data Flow Diagram

```
USER INPUT
    │
    ├─ Amount to Pay: ₦55,000
    ├─ Payment Date: 2024-01-15
    └─ Notes: Monthly payment
         │
         ↓
    VALIDATION
    │
    ├─ Is amount > 0? ✓
    ├─ Is date valid? ✓
    └─ Is loan valid? ✓
         │
         ↓
    CALCULATE
    │
    ├─ total_due = loan.amount + loan.interest
    │           = 40,000 + 4,000 = 44,000
    │
    ├─ overpayment = payment - total_due
    │              = 55,000 - 44,000 = 11,000
    │
    └─ overpayment > 0? ✓ YES
         │
         ├─ YES: RECORD PAYMENT + REFUND
         │  │
         │  ├─ save LoanRepayment(55,000)
         │  │
         │  ├─ update loan.amount_repaid = 55,000
         │  │
         │  ├─ check: 55,000 >= 44,000? ✓ YES
         │  │   └─ update loan.status = PAID
         │  │
         │  └─ create LoanRefund(11,000, PENDING)
         │
         └─ NO: RECORD PAYMENT ONLY
            └─ save LoanRepayment only
                 │
                 ↓
        DATABASE PERSISTENCE
        │
        ├─ loan_repayments table ✓ saved
        ├─ loan_refunds table ✓ saved
        ├─ loans table ✓ updated
        └─ all timestamps ✓ recorded
             │
             ↓
        UI NOTIFICATION
        │
        ├─ Show success message
        ├─ Refresh loan screen
        └─ Update loan details dialog
```

## State Transitions

```
LOAN LIFECYCLE
──────────────

ACTIVE (Initial)
    │
    ├─ Payment ₦20,000 → PENDING_REPAYMENT
    │
    ├─ Payment ₦24,000 → PENDING_REPAYMENT
    │
    └─ Payment ₦44,000 → PAID (Complete)


REFUND LIFECYCLE
────────────────

PENDING (Created on overpayment)
    │
    ├─ Admin clicks "Process"
    │        ↓
    └─ PROCESSED (status updated, timestamp recorded)


PAYMENT RECORD
──────────────

When Created → Immediately in Database
    ├─ Visible in Payment History ✓
    ├─ Updates Loan Balance ✓
    └─ Triggers Loan Status Check ✓

When Refund Created → Immediately in Database
    ├─ Visible in Refund History ✓
    ├─ Status: PENDING ✓
    └─ Awaits Admin Processing ✓

When Admin Processes → Status Changed in Database
    ├─ Visible in Refund History ✓
    ├─ Status: PROCESSED ✓
    └─ Timestamp Recorded ✓
```

## Message Flow

```
USER ACTIONS
────────────

Action: Record Payment
    │
    ├─ Input: ₦55,000
    │   Output: "Payment ₦55,000 recorded! Refund ₦11,000 created (PENDING)"
    │
    ├─ Input: ₦44,000
    │   Output: "Repayment of ₦44,000 recorded on 2024-01-15!"
    │
    ├─ Input: ₦20,000
    │   Output: "Repayment of ₦20,000 recorded on 2024-01-15!"
    │
    └─ Input: ₦0 or invalid
        Output: "Please enter a valid repayment amount!"


Action: Process Refund
    │
    ├─ Valid: Refund ₦11,000 → PROCESSED
    │   Output: "Refund ₦11,000 processed!"
    │
    └─ Invalid: Error in database
        Output: "Error: [error message]"
```

## Color Coding

```
PAYMENT AMOUNTS
├─ Green: Active/Success amounts
│   └─ ₦20,000 (payment recorded)
│
├─ Orange: Warnings/Pending
│   └─ ₦11,000 (refund pending)
│
└─ Blue: Informational
    └─ ₦44,000 (total due)


STATUS INDICATORS
├─ Green: ✓ Complete
│   └─ PAID, PROCESSED
│
├─ Orange: ⟳ Pending Action
│   └─ PENDING (refund awaiting approval)
│
└─ Grey: ℹ Information
    └─ Dates, notes, optional fields
```

## Example Transactions

```
EXAMPLE 1: Overpayment
──────────────────────
Initial Loan: ₦44,000 (₦40K + ₦4K interest)

Payment: ₦55,000
    → Refund: ₦11,000 (PENDING)
    → Loan Status: PAID

Database Records:
    LoanRepayment(55,000, 2024-01-15)
    LoanRefund(11,000, 2024-01-15, PENDING)


EXAMPLE 2: Multiple Payments
─────────────────────────────
Initial Loan: ₦44,000

Payment 1: ₦20,000 → Balance: ₦24,000
Payment 2: ₦15,000 → Balance: ₦9,000
Payment 3: ₦20,000 → Refund: ₦11,000, Balance: ₦0

Database Records:
    LoanRepayment(20,000, 2024-01-10)
    LoanRepayment(15,000, 2024-01-12)
    LoanRepayment(20,000, 2024-01-15)
    LoanRefund(11,000, 2024-01-15, PENDING)


EXAMPLE 3: Partial Payments
────────────────────────────
Initial Loan: ₦44,000

Payment 1: ₦10,000 → Balance: ₦34,000
Payment 2: ₦10,000 → Balance: ₦24,000
Payment 3: ₦10,000 → Balance: ₦14,000
Payment 4: ₦14,000 → Balance: ₦0

Database Records:
    4 LoanRepayment records
    No refunds
    Loan Status: PAID
```

---

**This visual guide shows how the payment and refund system works from user input to database persistence.**
