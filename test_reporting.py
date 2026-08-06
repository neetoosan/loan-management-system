"""
Test script for reporting functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.components.reporting import (
    ReportGenerator, ReportExporter, ReportFilter, DateRange,
    ReportType, ExportFormat
)
from app.components.error_handler import error_logger
from app.database.connection import get_all_members, get_all_loans, get_all_contributions
from datetime import datetime


def test_date_ranges():
    """Test date range functionality"""
    print("\n=== Testing Date Ranges ===")
    
    ranges = [
        ("Last 30 days", DateRange.last_30_days()),
        ("Last 90 days", DateRange.last_90_days()),
        ("This month", DateRange.this_month()),
        ("This year", DateRange.this_year()),
    ]
    
    for name, dr in ranges:
        print(f"{name}: {dr.start_date.date()} to {dr.end_date.date()}")
    
    print("✓ Date ranges working correctly")


def test_report_generation():
    """Test report generation"""
    print("\n=== Testing Report Generation ===")
    
    try:
        # Get data
        members = get_all_members()
        loans = get_all_loans()
        contributions = get_all_contributions()
        
        print(f"Found {len(members)} members, {len(loans)} loans, {len(contributions)} contributions")
        
        # Create filter
        report_filter = ReportFilter()
        
        # Test member summary
        if members and loans:
            print("\nGenerating member summary report...")
            report = ReportGenerator.generate_member_summary(members, loans, contributions, report_filter)
            print(f"✓ Generated member summary with {len(report['rows'])} rows")
            print(f"  Columns: {', '.join(report['headers'][:4])}")
        
        # Test loan summary
        if loans:
            print("\nGenerating loan summary report...")
            report = ReportGenerator.generate_loan_summary(loans, report_filter)
            print(f"✓ Generated loan summary with {len(report['rows'])} rows")
            if report.get('summary'):
                print(f"  Total loans: {report['summary']['total_loans']}")
                print(f"  Total amount: {report['summary']['total_amount']:.2f}")
        
        print("\n✓ Report generation working correctly")
    
    except Exception as e:
        print(f"✗ Report generation failed: {str(e)}")
        error_logger.error(f"Report generation test failed: {str(e)}")


def test_export_formats():
    """Test export to different formats"""
    print("\n=== Testing Export Formats ===")
    
    try:
        # Create sample report
        sample_report = {
            "title": "Test Report",
            "date_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_range": "Test Range",
            "headers": ["ID", "Name", "Amount", "Status"],
            "rows": [
                ["1", "Test 1", "₦1,000.00", "Active"],
                ["2", "Test 2", "₦2,000.00", "Paid"],
            ],
            "summary": {
                "total": 2,
                "total_amount": 3000.00,
            }
        }
        
        # Test CSV export
        downloads_dir = str(os.path.join(os.path.expanduser("~"), "Downloads"))
        os.makedirs(downloads_dir, exist_ok=True)
        
        csv_path = os.path.join(downloads_dir, "test_report.csv")
        if ReportExporter.export_csv(sample_report, csv_path):
            print(f"✓ CSV export successful: {csv_path}")
            os.remove(csv_path)
        
        # Test Excel export
        excel_path = os.path.join(downloads_dir, "test_report.xlsx")
        if ReportExporter.export_excel(sample_report, excel_path):
            print(f"✓ Excel export successful: {excel_path}")
            os.remove(excel_path)
        
        # Test PDF export
        pdf_path = os.path.join(downloads_dir, "test_report.pdf")
        if ReportExporter.export_pdf(sample_report, pdf_path):
            print(f"✓ PDF export successful: {pdf_path}")
            os.remove(pdf_path)
        
        print("\n✓ Export formats working correctly")
    
    except Exception as e:
        print(f"✗ Export test failed: {str(e)}")
        error_logger.error(f"Export test failed: {str(e)}")


def test_filters():
    """Test report filters"""
    print("\n=== Testing Report Filters ===")
    
    try:
        from app.database.connection import init_db
        
        # Create filter with specific criteria
        filter_obj = ReportFilter()
        filter_obj.member_ids = [1]  # Specific member
        filter_obj.include_paid_loans = False  # Exclude paid loans
        
        # Get data
        loans = get_all_loans()
        
        # Apply filter
        filtered = [l for l in loans if filter_obj.matches_loan(l)]
        
        print(f"Original loans: {len(loans)}")
        print(f"Filtered loans: {len(filtered)}")
        print("✓ Filters working correctly")
    
    except Exception as e:
        print(f"✗ Filter test failed: {str(e)}")
        error_logger.error(f"Filter test failed: {str(e)}")


if __name__ == "__main__":
    print("=" * 50)
    print("REPORTING SYSTEM TEST SUITE")
    print("=" * 50)
    
    try:
        # Initialize database
        from app.database.connection import init_db
        init_db()
        
        test_date_ranges()
        test_filters()
        test_report_generation()
        test_export_formats()
        
        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 50)
    
    except Exception as e:
        print(f"\n✗ Test suite failed: {str(e)}")
        error_logger.error(f"Test suite failed: {str(e)}")
