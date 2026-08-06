# QUICK REFERENCE: Advanced Loan Features

## NEW DATABASE FUNCTIONS

### 1. Check Member Eligibility
```python
from database.connection import can_member_take_loan

can_take, reason = can_member_take_loan(member_id)
# Returns: (True, "Member is eligible for loan")
# OR: (False, "Member status is Suspended...")
```

### 2. Calculate Loan Details
```python
from database.connection import calculate_loan_details

details = calculate_loan_details(amount=150000, interest_rate=8, duration_months=6)
# Returns: {
#   'principal': 150000,
#   'interest_rate_percentage': 8.0,
#   'total_interest': 12000,
#   'total_due': 162000,
#   'monthly_payment': 27000,
#   'duration_months': 6
# }
```

### 3. Create Loan with Full Validation
```python
from database.connection import create_loan_with_validation

success, result, info = create_loan_with_validation(
    member_id=11,
    amount=150000,
    interest_rate=8,
    duration_months=6,
    batch_number="BATCH001",
    cheque_number="CHQ001",
    guarantor_name="John Guarantor",
    guarantor_phone="08012345678"
)

if success:
    print(f"Loan ID: {info['loan_id']}, Total Due: {info['total_due']}")
else:
    print(f"Error: {result}")
```

### 4. Process Repayment with Overpayment Handling
```python
from database.connection import process_repayment_advanced

result = process_repayment_advanced(
    loan_id=17,
    amount_paid=50000,
    payment_date=datetime.now(),
    notes="Monthly payment"
)

# Check result
if result['success']:
    print(f"Status: {result['loan_status']}")
    print(f"Balance: {result['balance_remaining']}")
    if result['refund_created']:
        print(f"Refund created: {result['refund_amount']}")
    if result['loan_fully_paid']:
        print("Loan has been fully paid!")
```

### 5. Get Comprehensive Loan Summary
```python
from database.connection import get_loan_summary

summary = get_loan_summary(loan_id=17)
# Returns:
# {
#   'loan_id': 17,
#   'principal_amount': 150000,
#   'amount_repaid': 100000,
#   'balance_remaining': 62000,
#   'percentage_paid': 61.7,
#   'status': 'ACTIVE',
#   'is_overdue': True,
#   'days_overdue': 5,
#   ...
# }
```

### 6. Get Member Loan Status
```python
from database.connection import get_member_loan_status

status = get_member_loan_status(member_id=11)
# Returns:
# {
#   'member_name': 'John Active',
#   'can_take_loan': True,
#   'total_loans': 3,
#   'active_loans': 2,
#   'total_outstanding_debt': 100000,
#   ...
# }
```

### 7. Get Overdue Loans
```python
from database.connection import get_overdue_loans_list

overdue = get_overdue_loans_list()
# Returns: List of Loan objects with end_date < today and status=ACTIVE
```

---

## VALIDATION UTILITIES

### Centralized Validation Module
```python
from components.validation import Validator, format_error_message

# Validate loan amount
valid, msg = Validator.validate_loan_amount(150000)

# Validate interest rate
valid, msg = Validator.validate_interest_rate(8)

# Validate duration
valid, msg = Validator.validate_duration(6)

# Comprehensive loan validation
errors = Validator.validate_loan_creation(
    member_id=11,
    amount=150000,
    interest_rate=8,
    duration=6,
    guarantor_name="John",
    guarantor_phone="08012345678"
)

if errors:
    print(format_error_message(errors))
    # Output: "✗ Please fix the following errors:\n1. Error 1\n2. Error 2"
```

---

## BUSINESS RULES ENFORCED

1. **Member Eligibility**
   - Only ACTIVE members can take loans
   - Suspended/Inactive members are blocked

2. **Amount Limits**
   - Loan amount: 0 < amount <= 10,000,000
   - Contribution: 0 < amount <= 1,000,000
   - Repayment: 0 < amount <= total_due * 2

3. **Interest Rate**
   - Must be between 0% and 100%
   - Automatically converts decimal to percentage

4. **Duration**
   - Must be 1 to 60 months
   - End date calculated as: start_date + (30 * duration_months)

5. **Status Transitions**
   - PENDING -> ACTIVE (on disbursement)
   - ACTIVE -> PAID (when fully repaid)
   - ACTIVE -> DEFAULTED (when overdue)

---

## ERROR HANDLING

All functions include:
- Input validation
- Business rule checking
- Database transaction management
- Clear error messages
- Proper rollback on failure

### Typical Error Response:
```python
# On failure
(False, "Error message describing what went wrong", {})

# Or dictionary with 'success': False
{
    'success': False,
    'message': 'Descriptive error message',
    'repayment_id': None,
    ...
}
```

---

## CALCULATION FORMULAS

### Interest Calculation:
```
Total Interest = (Principal * Interest Rate) / 100
```

### End Date:
```
End Date = Start Date + (30 days * Duration Months)
```

### Monthly Payment:
```
Monthly Payment = (Principal + Total Interest) / Duration Months
```

### Balance Remaining:
```
Balance = Total Due - Amount Repaid
Where: Total Due = Principal + Total Interest
```

### Percentage Paid:
```
Percentage Paid = (Amount Repaid / Total Due) * 100
```

---

## DATABASE SCHEMA UPDATES

### New Columns Used:
- `Loan.total_interest` - Calculated on creation
- `Loan.amount_repaid` - Updated on each repayment
- `Loan.status` - Automatic transitions
- `LoanRepayment.payment_date` - Track exact payment timing
- `LoanRefund.status` - Track refund processing

---

## INTEGRATION EXAMPLES

### UI: Adding New Loan (with validation)
```python
# From loan_screen.py
success, result, info = create_loan_with_validation(
    member_id=selected_member_id,
    amount=float(amount_field.value),
    interest_rate=interest_spinbox.value,
    duration_months=int(duration_field.value),
    guarantor_name=guarantor_field.value,
    guarantor_phone=phone_field.value
)

if success:
    page.snack_bar = ft.SnackBar(ft.Text(f"Loan created! Total: {info['total_due']}"))
else:
    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {result}"))
```

### UI: Recording Payment (with overpayment)
```python
# From loan_screen.py
result = process_repayment_advanced(
    loan_id=loan.id,
    amount_paid=float(repayment_amount.value),
    payment_date=datetime.strptime(date_field.value, "%Y-%m-%d"),
    notes=notes_field.value
)

if result['success']:
    msg = f"Payment recorded! Balance: {result['balance_remaining']}"
    if result['refund_created']:
        msg += f"\nRefund: {result['refund_amount']}"
    page.snack_bar = ft.SnackBar(ft.Text(msg))
else:
    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {result['message']}"))
```

---

## TESTING

Run the test suite:
```bash
.venv\Scripts\python.exe app\test_advanced_loans.py
```

Tests verify:
- Business rules enforcement
- Loan calculations accuracy
- Validation error handling
- Repayment processing
- Overpayment handling
- Loan status reporting

---

## MIGRATION NOTES

Existing database will work without changes. New functions are backward compatible:
- Existing loans with NULL values will be handled gracefully
- New loans will have all calculated fields populated
- Repayment processing works with old and new loans

---

## PERFORMANCE CONSIDERATIONS

- Each repayment creates a new LoanRepayment record (not updated)
- Status updates are in-memory until commit
- get_loan_summary() calculates on-the-fly (could be cached)
- get_overdue_loans_list() queries all active loans (index on end_date recommended)

---

## NEXT ENHANCEMENTS

Priority implementations:
1. Audit logging for all operations
2. Email notifications for milestone events
3. Interest accrual for overdue loans
4. Loan restructuring/rescheduling
5. Default/recovery workflow

