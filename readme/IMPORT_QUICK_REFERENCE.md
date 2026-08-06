# Import System - Quick Reference Guide

## File Format Requirements

### 📋 Loans Import

**Required Columns** (at least these three):
- `IPPIS` - Staff ID number (or: IPPIS NUMBER, STAFF ID, MEMBER ID)
- `FULL NAME` - Member's full name (or: NAME, MEMBER NAME)
- `LOAN AMOUNT` - Loan amount in numbers (or: AMOUNT, LOAN AMT)

**Optional Columns**:
- `INTEREST` - Interest rate as % or decimal (or: INTEREST RATE, INT RATE)
- `LOAN DURATION` - Duration in months (or: DURATION, MONTHS)
- `BATCH NUMBER` - Batch identifier (or: BATCH, BATCH NO)
- `CHEQUE NO` - Cheque number (or: CHEQUE NUMBER, CHQ NO)
- `LOAN DATE` - Date loan was issued (or: ISSUE DATE, START DATE, DATE)

**Supported Formats**:
- CSV (.csv)
- Excel (.xlsx)
- Auto-detects headers (no need to worry about header row position)

**Example CSV**:
```
IPPIS,FULL NAME,LOAN AMOUNT,INTEREST,LOAN DURATION,BATCH NUMBER
A001,John Doe,500000,5,24,BATCH-001
A002,Jane Smith,750000,5.5,36,BATCH-001
```

**Example Excel**:
| IPPIS | FULL NAME | LOAN AMOUNT | INTEREST | LOAN DURATION |
|-------|-----------|------------|----------|---------------|
| A001  | John Doe  | 500,000    | 5%       | 24            |
| A002  | Jane Smith| 750,000    | 5.5%     | 36            |

---

### 💰 Contributions Import

**Required Columns** (at least these two):
- `IPPIS` - Staff ID number (or: IPPIS NUMBER, STAFF ID, MEMBER ID)
- `AMOUNT` - Contribution amount (or: CONTRIBUTION, CONTRIB AMT)

**Optional Columns**:
- `TYPE` - Contribution type (or: CONTRIB TYPE, CATEGORY)
  - Accepted values: NORMAL, SPECIAL, EMERGENCY
  - Default if missing: NORMAL
- `MONTH` - Month/period (or: MONTH NAME, PERIOD)
- `DATE` - Date of contribution (or: CONTRIBUTION DATE, CONTRIB DATE)

**Supported Formats**:
- CSV (.csv)
- Excel (.xlsx)
- Auto-detects headers

**Example CSV**:
```
IPPIS,AMOUNT,TYPE,MONTH
A001,50000,NORMAL,January
A002,75000,SPECIAL,January
```

**Example Excel**:
| IPPIS | AMOUNT | TYPE | MONTH |
|-------|--------|------|-------|
| A001  | 50,000 | NORMAL | January |
| A002  | 75,000 | SPECIAL | January |

---

## Accepted Data Formats

### Currency & Numbers
- ✓ `500000` → 500,000
- ✓ `500,000` → 500,000
- ✓ `500,000.50` → 500,000.50
- ✓ `₦500000` → 500,000
- ✓ `₦500,000` → 500,000

### Percentages
- ✓ `5` → 5%
- ✓ `5%` → 5%
- ✓ `0.05` → 5%
- ✓ `5.5` → 5.5%

### Dates
- ✓ `2024-01-15`
- ✓ `15-01-2024`
- ✓ `01-15-2024`
- ✓ `15/01/2024`
- ✓ `01/15/2024`
- ✓ `15-Jan-2024`
- ✓ `15-January-2024`

---

## Import Process

### Step 1: Click "Import Data" in Settings
- Dialog shows format requirements
- Select "📋 Loans" or "💰 Contributions"
- Required/optional columns clearly labeled

### Step 2: Select File
- Choose CSV or Excel file
- Must contain valid headers
- Must have at least one data row

### Step 3: Watch Progress
- "📋 Validating file..." - System checking format
- "✓ File valid | Parsing X rows..." - Reading data
- "💾 Processing X valid records..." - Saving to database
- "✓ Results..." - Shows final outcome

### Step 4: Review Results
**Success Message**:
```
✓ Imported 145 records | 2 duplicates skipped
```

**Partial Success**:
```
✓ Imported 145 records | ⚠ 2 duplicates skipped | ✗ 3 failed
```

---

## Error Messages & Solutions

### "Missing required column LOAN AMOUNT"
- **Problem**: File doesn't have a "LOAN AMOUNT" column
- **Solution**: Add column with exact name or alias (AMOUNT, LOAN AMT)

### "Row 5: Invalid number format in LOAN AMOUNT"
- **Problem**: Value like "ABC" or empty cell
- **Solution**: Ensure all amounts are numbers (500000 or 500,000)

### "Row 12: Member not found"
- **Problem**: Contributing member doesn't exist (contributions only)
- **Solution**: Import members first, or use correct IPPIS number

### "Row 3: Duplicate loan for A001"
- **Problem**: This loan already exists for this member
- **Solution**: File skips duplicate (continues with others)

### "Row 8: Invalid percentage: 150%"
- **Problem**: Interest rate > 100%
- **Solution**: Use value between 0-100 (or 0-1 for decimals)

### "File not found: C:/path/to/file.csv"
- **Problem**: File doesn't exist at that location
- **Solution**: Check file path and try again

---

## Tips for Best Results

1. **Use Exact Headers**
   - IPPIS (not EMPLOYEE ID)
   - FULL NAME (not NAME)
   - LOAN AMOUNT (not AMOUNT)

2. **Keep Formatting Consistent**
   - All amounts as numbers or all as text with comma separators
   - All dates in same format
   - All percentages with or without % sign

3. **Validate Before Import**
   - No empty required cells
   - No typos in member IDs
   - Amounts > 0
   - Interest rates 0-100

4. **Check Import Results**
   - Review success/failure counts
   - Note any duplicate warnings
   - Check operation history (Settings > View History)

5. **Handle Errors**
   - Fix only error rows
   - Re-import corrected file
   - Successful rows won't be re-imported (duplicates detected)

---

## Column Alternatives (Aliases)

### IPPIS can be named:
- IPPIS
- IPPIS NUMBER
- STAFF ID
- MEMBER ID
- EMPLOYEE ID

### FULL NAME can be named:
- FULL NAME
- NAME
- MEMBER NAME
- EMPLOYEE NAME

### LOAN AMOUNT can be named:
- LOAN AMOUNT
- AMOUNT
- LOAN AMT
- PRINCIPAL

### INTEREST can be named:
- INTEREST
- INTEREST RATE
- INT RATE
- RATE

And many more! System is flexible with column names.

---

## Troubleshooting

**Q: File has extra columns I don't need - OK?**
A: Yes! Extra columns are ignored. Only required/optional columns used.

**Q: Can columns be in different order?**
A: Yes! System auto-detects column positions. Order doesn't matter.

**Q: What if my header is on row 5, not row 1?**
A: No problem! System auto-detects headers anywhere in first 10 rows.

**Q: Some members already exist - will they be skipped?**
A: For loans: Creates loans for existing members. For contributions: Skips if member missing.

**Q: Can I import same file twice?**
A: No - duplicates detected and skipped with warning. Safe to re-import.

**Q: What if import fails halfway?**
A: Database unchanged. All successful rows either saved together or nothing saved.

---

## Sample Files

### Loans Template (loans_template.csv)
```csv
IPPIS,FULL NAME,LOAN AMOUNT,INTEREST,LOAN DURATION
A001,John Doe,500000,5,24
A002,Jane Smith,750000,5.5,36
A003,Bob Johnson,1000000,6,48
```

### Contributions Template (contributions_template.csv)
```csv
IPPIS,AMOUNT,TYPE,MONTH
A001,50000,NORMAL,January
A002,75000,SPECIAL,January
A001,50000,NORMAL,February
```

---

**Need Help?** Check the error message details or contact system administrator.
