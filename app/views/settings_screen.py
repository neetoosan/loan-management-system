import flet as ft
from components.navigation import create_app_bar
from components.burger_menu import create_sidebar_overlay, create_burger_menu
from components.account_management import (
    create_account_dialog,
    edit_account_dialog,
    list_users_dialog,
    change_password_dialog,
)
from components.error_handler import (
    error_logger, UserFriendlyError, RetryableOperation, RetryConfig,
    ImportExportHandler, log_operation, FileOperationHandler
)
from components.ui_components import (
    ToastNotification, NotificationType, ProgressDialog, ConfirmDialog,
    OperationHistory, OperationProgressTracker
)
from components.import_validator import (
    ImportValidator, ImportProcessor, ColumnDetector, MonthlySummaryExporter,
    ImportReportGenerator
)
from database.connection import init_db, reset_all_data, get_session, get_user_by_username, create_user, DB_PATH
from database.models import LoanStatus, ContributionType, User, Member, Loan, MemberStatus
from datetime import datetime, timedelta
import os
import csv
import shutil
import threading
import time


def navigate_to(page: ft.Page, route: str):
    """Navigate to a different route (replaces deprecated page.go)"""
    page.route = route
    page.update()


try:
    from openpyxl import load_workbook
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


def SettingsScreen(page: ft.Page):
    """Settings screen with import/export, and app info"""
    
    # Operation tracking
    operation_history = OperationHistory()
    
    # Status text
    operation_status = ft.Text(
        "No operation in progress",
        size=14,
        color=ft.Colors.GREY,
        weight="normal"
    )
    
    # Import results feedback container
    import_results_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("", size=14, color=ft.Colors.WHITE, weight="bold"),  # Title
            ],
            spacing=8,
        ),
        padding=15,
        border_radius=8,
        visible=False,
        expand=False,
    )
    
    # ── Flet FilePicker (Flet 0.80+ async API) ──────────────────────
    file_picker = ft.FilePicker()
    
    def update_import_results(summary, status_type="success", error_details=None):
        """Update import results container with detailed feedback"""
        controls = []
        
        if status_type == "success":
            # Success header
            controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=26),
                        ft.Text("✓ Import Completed Successfully!", size=16, weight="bold", color=ft.Colors.GREEN_400),
                    ],
                    spacing=10,
                )
            )
            import_results_container.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREEN)
            import_results_container.border = ft.border.all(1, ft.Colors.GREEN_400)
        
        elif status_type == "warning":
            # Warning header
            controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE_400, size=26),
                        ft.Text("⚠ Import Completed With Issues", size=16, weight="bold", color=ft.Colors.ORANGE_400),
                    ],
                    spacing=10,
                )
            )
            import_results_container.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.ORANGE)
            import_results_container.border = ft.border.all(1, ft.Colors.ORANGE_400)
        
        else:  # error
            # Error header
            controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400, size=26),
                        ft.Text("✗ Import Failed", size=16, weight="bold", color=ft.Colors.RED_400),
                    ],
                    spacing=10,
                )
            )
            import_results_container.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.RED)
            import_results_container.border = ft.border.all(1, ft.Colors.RED_400)
        
        controls.append(ft.Divider(height=10))
        
        # Summary statistics
        if summary:
            stats_controls = []
            
            if summary.successful_count > 0:
                stats_controls.append(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK, color=ft.Colors.GREEN_400, size=20),
                            ft.Text(f"Successfully Imported:", size=13, weight="bold", color=ft.Colors.GREEN_400),
                            ft.Text(f"{summary.successful_count} records", size=13, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    )
                )
            
            if summary.updated_count > 0:
                stats_controls.append(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.UPDATE, color=ft.Colors.BLUE_400, size=20),
                            ft.Text(f"Updated:", size=13, weight="bold", color=ft.Colors.BLUE_400),
                            ft.Text(f"{summary.updated_count} records", size=13, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    )
                )
            
            if summary.duplicate_count > 0:
                stats_controls.append(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CONTENT_COPY, color=ft.Colors.AMBER_400, size=20),
                            ft.Text(f"Duplicates Skipped:", size=13, weight="bold", color=ft.Colors.AMBER_400),
                            ft.Text(f"{summary.duplicate_count} records", size=13, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    )
                )
            
            if summary.failed_count > 0:
                stats_controls.append(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CLOSE, color=ft.Colors.RED_400, size=20),
                            ft.Text(f"Failed Records:", size=13, weight="bold", color=ft.Colors.RED_400),
                            ft.Text(f"{summary.failed_count} records", size=13, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    )
                )
            
            if summary.warning_count > 0:
                stats_controls.append(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_400, size=20),
                            ft.Text(f"Warnings:", size=13, weight="bold", color=ft.Colors.BLUE_400),
                            ft.Text(f"{summary.warning_count} issues", size=13, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    )
                )
            
            controls.extend(stats_controls)
        
        # Error details if provided
        if error_details:
            controls.append(ft.Divider(height=10))
            controls.append(
                ft.Text("Error Details:", size=13, weight="bold", color=ft.Colors.RED_300)
            )
            
            for error in error_details[:5]:  # Show first 5 errors
                controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"• {error}",
                            size=12,
                            color=ft.Colors.RED_200,
                            selectable=True,
                        ),
                        padding=ft.padding.only(left=10),
                    )
                )
            
            if len(error_details) > 5:
                controls.append(
                    ft.Text(
                        f"... and {len(error_details) - 5} more errors",
                        size=12,
                        color=ft.Colors.GREY_400,
                        italic=True,
                    )
                )
        
        # Failed payments list (for payment imports)
        if summary and hasattr(summary, 'failed_payments') and summary.failed_payments:
            controls.append(ft.Divider(height=10))
            controls.append(
                ft.Text(
                    f"Failed Payments ({len(summary.failed_payments)}):",
                    size=13, weight="bold", color=ft.Colors.RED_300,
                )
            )
            # Table header
            controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Row", size=11, weight="bold", color=ft.Colors.GREY_400, width=40),
                            ft.Text("IPPIS", size=11, weight="bold", color=ft.Colors.GREY_400, width=80),
                            ft.Text("Name", size=11, weight="bold", color=ft.Colors.GREY_400, width=140, expand=True),
                            ft.Text("Amount", size=11, weight="bold", color=ft.Colors.GREY_400, width=80),
                            ft.Text("Reason", size=11, weight="bold", color=ft.Colors.GREY_400, width=200, expand=True),
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.only(left=10, right=10),
                )
            )
            for fp in summary.failed_payments[:15]:
                amt = fp.get('amount', 0)
                amt_str = f"\u20a6{amt:,.2f}" if isinstance(amt, (int, float)) else str(amt)
                controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(str(fp.get('row', '')), size=11, color=ft.Colors.RED_200, width=40),
                                ft.Text(str(fp.get('ippis', '')), size=11, color=ft.Colors.WHITE, width=80),
                                ft.Text(str(fp.get('name', '')), size=11, color=ft.Colors.WHITE, width=140, expand=True),
                                ft.Text(amt_str, size=11, color=ft.Colors.WHITE, width=80),
                                ft.Text(str(fp.get('reason', '')), size=11, color=ft.Colors.RED_200, width=200, expand=True),
                            ],
                            spacing=4,
                        ),
                        padding=ft.padding.only(left=10, right=10),
                    )
                )
            if len(summary.failed_payments) > 15:
                controls.append(
                    ft.Text(
                        f"... and {len(summary.failed_payments) - 15} more (see import report for full list)",
                        size=12, color=ft.Colors.GREY_400, italic=True,
                    )
                )

        # Update container
        import_results_container.content = ft.Column(controls=controls, spacing=8)
        import_results_container.visible = True
        page.update()
    
    def clear_import_results():
        """Clear import results"""
        import_results_container.visible = False
        page.update()

    def show_import_progress(message: str):
        """Show a brief progress message in the results container"""
        controls = [
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_400, size=20),
                    ft.Text(message, size=14, color=ft.Colors.WHITE),
                ],
                spacing=8,
            )
        ]
        import_results_container.content = ft.Column(controls=controls, spacing=8)
        import_results_container.bgcolor = "#1a1a1a"
        import_results_container.border = None
        import_results_container.visible = True
        page.update()
    
    
    
    def import_data_dialog():
        """Show dialog to choose import type with format guidance"""
        
        def close_type_dialog(e):
            type_dialog.open = False
            page.update()
        
        async def on_import_type_selected(data_type):
            type_dialog.open = False
            page.update()
            await show_file_picker(data_type)
        
        # Create format guidance based on data type
        loan_format_text = ft.Column(
            controls=[
                ft.Text("Loans Format:", size=14, weight="bold", color=ft.Colors.BLUE_300),
                ft.Text("Required columns: IPPIS, FULL NAME, LOAN AMOUNT", size=12, color=ft.Colors.GREY_400),
                ft.Text("Optional: INTEREST, LOAN DURATION, BATCH NUMBER, CHEQUE NO, LOAN DATE", size=12, color=ft.Colors.GREY_400),
                ft.Text("Supported formats: CSV, XLSX (auto-detects headers)", size=11, color=ft.Colors.AMBER_300),
            ],
            spacing=4,
        )
        
        contrib_format_text = ft.Column(
            controls=[
                ft.Text("Contributions Format:", size=14, weight="bold", color=ft.Colors.GREEN_300),
                ft.Text("Required columns: IPPIS, AMOUNT", size=12, color=ft.Colors.GREY_400),
                ft.Text("Optional: TYPE (NORMAL/SPECIAL/EMERGENCY), MONTH, DATE", size=12, color=ft.Colors.GREY_400),
                ft.Text("Supported formats: CSV, XLSX (auto-detects headers)", size=11, color=ft.Colors.AMBER_300),
            ],
            spacing=4,
        )
        
        payment_format_text = ft.Column(
            controls=[
                ft.Text("Monthly Payments Format:", size=14, weight="bold", color=ft.Colors.PURPLE_300),
                ft.Text("Required columns: IPPIS, FULL NAME, AMOUNT", size=12, color=ft.Colors.GREY_400),
                ft.Text("Records payment against active loan for each borrower", size=12, color=ft.Colors.GREY_400),
                ft.Text("Auto-detects overpayments and generates monthly summary", size=11, color=ft.Colors.AMBER_300),
            ],
            spacing=4,
        )
        
        type_dialog = ft.AlertDialog(
            title=ft.Text("Import Data - Select Type"),
            content=ft.Column(
                controls=[
                    ft.Text("Choose the data type to import:", size=14, color=ft.Colors.WHITE),
                    ft.Divider(height=10),
                    
                    # Loans
                    ft.Container(
                        content=loan_format_text,
                        border_radius=8,
                        padding=12,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                        border=ft.border.all(1, ft.Colors.BLUE_400),
                    ),
                    
                    # Contributions
                    ft.Container(
                        content=contrib_format_text,
                        border_radius=8,
                        padding=12,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
                        border=ft.border.all(1, ft.Colors.GREEN_400),
                    ),
                    
                    # Monthly Payments
                    ft.Container(
                        content=payment_format_text,
                        border_radius=8,
                        padding=12,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PURPLE),
                        border=ft.border.all(1, ft.Colors.PURPLE_400),
                    ),
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton(
                    "📋 Loans",
                    on_click=lambda e: page.run_task(on_import_type_selected, "loans"),
                    style=ft.ButtonStyle(color=ft.Colors.BLUE_300)
                ),
                ft.TextButton(
                    "💰 Contributions",
                    on_click=lambda e: page.run_task(on_import_type_selected, "contributions"),
                    style=ft.ButtonStyle(color=ft.Colors.GREEN_300)
                ),
                ft.TextButton(
                    "📅 Monthly Payments",
                    on_click=lambda e: page.run_task(on_import_type_selected, "payments"),
                    style=ft.ButtonStyle(color=ft.Colors.PURPLE_300)
                ),
                ft.TextButton("Cancel", on_click=close_type_dialog),
            ],
        )
        
        page.overlay.append(type_dialog)
        type_dialog.open = True
        page.update()
    
    async def show_file_picker(data_type):
        """Open Flet FilePicker for import (async, Flet 0.80+)."""
        # Show immediate feedback
        try:
            show_import_progress("Opening file dialog...")
        except Exception:
            pass

        files = await file_picker.pick_files(
            dialog_title=f"Select {data_type.title()} Import File",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx", "csv"],
            allow_multiple=False,
        )

        if files:
            file_path = files[0].path
            error_logger.info(f"File selected for import: {file_path}")
            threading.Thread(
                target=import_data_from_file,
                args=(file_path, data_type),
                daemon=True,
            ).start()
        else:
            # User cancelled
            show_import_progress("Selection cancelled")
            def hide_message():
                try:
                    import_results_container.visible = False
                    page.update()
                except Exception:
                    pass
            threading.Timer(2.0, hide_message).start()
    
    def import_data_from_file(file_path, data_type):
        """Import data from CSV or XLSX file with robust validation and error handling"""
        start_time = time.time()
        operation = operation_history.start_operation("IMPORT", f"{data_type.upper()} from {os.path.basename(file_path)}")
        
        try:
            error_logger.info(f"Starting import from {file_path}, type: {data_type}")
            
            # Validate file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Validate file extension
            if not file_path.lower().endswith(('.xlsx', '.csv')):
                raise ValueError("Unsupported file format. Use CSV or XLSX files only.")
            
            # Update status
            operation_status.value = f"📋 Validating {os.path.basename(file_path)}..."
            operation_status.color = ft.Colors.WHITE
            page.update()
            show_import_progress(operation_status.value)
            
            # Create validator
            validator = ImportValidator(data_type)
            
            # Validate file format and structure
            if file_path.lower().endswith('.xlsx'):
                is_valid, rows, warnings = validator.validate_excel_file(file_path)
            else:
                is_valid, rows, warnings = validator.validate_csv_file(file_path)
            
            # Log validation warnings
            for warning in warnings:
                error_logger.info(f"Validation info: {warning}")
                operation_status.value = f"ℹ {warning}"
                page.update()
                time.sleep(0.5)
            
            if not is_valid:
                error_msg = f"File validation failed: {', '.join(warnings)}"
                operation_status.value = f"✗ {error_msg}"
                operation_status.color = ft.Colors.RED_700
                error_logger.warning(error_msg)
                
                # Show error in results container
                update_import_results(None, status_type="error", error_details=warnings)
                
                duration = time.time() - start_time
                operation_history.end_operation(operation, success=False, error_message=error_msg, duration=duration)
                page.update()
                return
            
            # Validate and parse rows
            operation_status.value = f"✓ File valid | Parsing {len(rows)} rows..."
            operation_status.color = ft.Colors.WHITE
            page.update()
            show_import_progress(operation_status.value)
            
            valid_rows, parse_errors = validator.validate_and_parse_rows(rows)
            
            # Log parse errors
            for error in parse_errors:
                error_logger.warning(f"Parse error: {error}")
                validator.summary.add_error(error.row_number, error.field, error.error_message)
            
            if not valid_rows:
                error_msg = f"No valid records found. {len(parse_errors)} parsing errors."
                operation_status.value = f"✗ {error_msg}"
                operation_status.color = ft.Colors.ORANGE_400
                error_logger.warning(error_msg)
                update_import_results(None, status_type="error", error_details=[str(e) for e in parse_errors])
                duration = time.time() - start_time
                operation_history.end_operation(operation, success=False, error_message=error_msg, duration=duration)
                page.update()
                return
            
            # Process rows
            operation_status.value = f"💾 Processing {len(valid_rows)} valid records..."
            operation_status.color = ft.Colors.WHITE
            page.update()
            show_import_progress(operation_status.value)
            
            processor = ImportProcessor(data_type, validator)
            success = processor.process_rows(valid_rows)
            
            # Display results
            operation_status.value = processor.summary.get_summary_text()
            operation_status.color = (
                ft.Colors.GREEN_700 if processor.summary.failed_count == 0
                else ft.Colors.ORANGE_400
            )
            page.update()
            
            # Determine status type and update results container
            if processor.summary.failed_count == 0 and (processor.summary.successful_count > 0 or processor.summary.updated_count > 0):
                update_import_results(processor.summary, status_type="success")
            elif processor.summary.failed_count > 0:
                error_details = [str(e) for e in processor.summary.errors]
                update_import_results(processor.summary, status_type="warning", error_details=error_details)
            
            # Auto-generate import report log
            try:
                operation_status.value = "📋 Generating import report log..."
                page.update()
                
                report_path = ImportReportGenerator.generate_report(
                    summary=processor.summary,
                    data_type=data_type,
                    source_file=file_path
                )
                
                if import_results_container.content and hasattr(import_results_container.content, 'controls'):
                    import_results_container.content.controls.append(ft.Divider(height=10))
                    import_results_container.content.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.DESCRIPTION, color=ft.Colors.BLUE_300, size=20),
                                ft.Text("Import Report Log:", size=13, weight="bold", color=ft.Colors.BLUE_300),
                            ],
                            spacing=8,
                        )
                    )
                    import_results_container.content.controls.append(
                        ft.Text(
                            f"Saved to: {report_path}",
                            size=12, color=ft.Colors.GREY_400, selectable=True,
                        )
                    )
                
                error_logger.info(f"Import report log saved to: {report_path}")
            except Exception as ex:
                error_logger.error(f"Import report generation failed: {str(ex)}")
            
            # Auto-generate monthly summary after payment import
            if data_type == "payments" and processor.summary.successful_count > 0:
                try:
                    operation_status.value = "📊 Generating monthly summary..."
                    page.update()
                    
                    summary_data = MonthlySummaryExporter.generate_summary(
                        processed_records=processor.summary.processed_records
                    )
                    
                    export_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                    export_path = MonthlySummaryExporter.export_to_excel(summary_data, export_dir)
                    
                    stats = summary_data.get('stats', {})
                    missed = stats.get('missed', 0)
                    overpaid = stats.get('overpaid', 0)
                    paid = stats.get('fully_paid', 0)
                    total_borrowers = stats.get('total_borrowers', 0)
                    
                    summary_msg = (
                        f"📊 Monthly Summary exported: {total_borrowers} borrowers | "
                        f"{missed} missed | {overpaid} overpaid | {paid} fully paid\n"
                        f"File: {os.path.basename(export_path)}"
                    )
                    operation_status.value = summary_msg
                    operation_status.color = ft.Colors.GREEN_400
                    
                    # Show export path in results
                    if import_results_container.content and hasattr(import_results_container.content, 'controls'):
                        import_results_container.content.controls.append(ft.Divider(height=10))
                        import_results_container.content.controls.append(
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.FILE_DOWNLOAD_DONE, color=ft.Colors.PURPLE_300, size=20),
                                    ft.Text("Monthly Summary:", size=13, weight="bold", color=ft.Colors.PURPLE_300),
                                ],
                                spacing=8,
                            )
                        )
                        import_results_container.content.controls.append(
                            ft.Text(
                                f"Saved to: {export_path}",
                                size=12, color=ft.Colors.GREY_400, selectable=True,
                            )
                        )
                        import_results_container.content.controls.append(
                            ft.Text(
                                f"{missed} missed | {overpaid} overpaid | {paid} fully paid",
                                size=12, color=ft.Colors.AMBER_300,
                            )
                        )
                    
                    error_logger.info(f"Monthly summary exported to: {export_path}")
                except Exception as ex:
                    error_logger.error(f"Monthly summary export failed: {str(ex)}")
                    operation_status.value += f" | Summary export failed: {str(ex)}"
            
            # Record operation
            duration = time.time() - start_time
            operation_history.end_operation(operation, success=success, duration=duration)
        
        except FileNotFoundError as e:
            error_msg = UserFriendlyError.get_message('file_not_found', str(e))
            operation_status.value = f"✗ {error_msg}"
            operation_status.color = ft.Colors.RED_600
            error_logger.warning(f"File not found: {str(e)}")
            update_import_results(None, status_type="error", error_details=[str(e)])
            duration = time.time() - start_time
            operation_history.end_operation(operation, success=False, error_message=str(e), duration=duration)
        
        except ValueError as e:
            error_msg = UserFriendlyError.get_message('file_format_error', str(e))
            operation_status.value = f"✗ {error_msg}"
            operation_status.color = ft.Colors.RED_600
            error_logger.warning(f"Invalid file format: {str(e)}")
            update_import_results(None, status_type="error", error_details=[str(e)])
            duration = time.time() - start_time
            operation_history.end_operation(operation, success=False, error_message=str(e), duration=duration)
        
        except Exception as e:
            error_msg = UserFriendlyError.get_message('import_failed', str(e))
            operation_status.value = f"✗ Import failed: {str(e)}"
            operation_status.color = ft.Colors.RED_700
            error_logger.exception(f"Import failed: {str(e)}")
            update_import_results(None, status_type="error", error_details=[str(error_msg)])
            duration = time.time() - start_time
            operation_history.end_operation(operation, success=False, error_message=str(e), duration=duration)
        
        page.update()
    
    @log_operation('Export Data')
    def export_to_csv():
        """Export data to CSV files with comprehensive error handling and progress tracking"""
        start_time = time.time()
        operation = operation_history.start_operation("EXPORT", "All data to CSV")
        
        try:
            from database.connection import (
                get_all_members,
                get_all_loans,
                get_all_contributions,
            )
            
            ToastNotification.show(page, "Starting data export...", NotificationType.INFO)
            operation_status.value = "Preparing export..."
            operation_status.color = ft.Colors.BLUE_200
            page.update()
            
            # Create exports folder with error handling
            exports_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
            try:
                os.makedirs(exports_dir, exist_ok=True)
            except OSError as e:
                error_msg = UserFriendlyError.get_message('file_write_error', f"Cannot create exports directory: {str(e)}")
                operation_status.value = f"✗ {error_msg}"
                operation_status.color = ft.Colors.RED_700
                error_logger.error(f"Failed to create exports directory: {str(e)}")
                ToastNotification.show(page, error_msg, NotificationType.ERROR)
                duration = time.time() - start_time
                operation_history.end_operation(operation, success=False, error_message=str(e), duration=duration)
                page.update()
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exported_files = []
            
            try:
                # Export members
                operation_status.value = "Exporting members..."
                page.update()
                
                members = get_all_members()
                members_file = os.path.join(exports_dir, f"members_{timestamp}.csv")
                
                with open(members_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Name", "Contact", "Email", "Status", "Join Date"])
                    for m in members:
                        try:
                            writer.writerow([
                                m.id, m.name, m.contact or "", m.email or "",
                                m.status.value, m.join_date.strftime("%Y-%m-%d")
                            ])
                        except Exception as e:
                            error_logger.warning(f"Failed to export member {m.id}: {str(e)}")
                
                exported_files.append("members")
                error_logger.info(f"Exported {len(members)} members")
                ToastNotification.show(page, f"Exported {len(members)} members", NotificationType.SUCCESS)
            
            except Exception as e:
                error_msg = UserFriendlyError.get_message('export_failed', f"Members export: {str(e)}")
                error_logger.error(f"Members export failed: {str(e)}")
                raise
            
            try:
                # Export loans
                operation_status.value = "Exporting loans..."
                page.update()
                
                loans = get_all_loans()
                loans_file = os.path.join(exports_dir, f"loans_{timestamp}.csv")
                
                with open(loans_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ID", "Member ID", "Amount", "Interest %", "Repaid", "Status", "Start Date", "End Date"
                    ])
                    for l in loans:
                        try:
                            writer.writerow([
                                l.id, l.member_id, l.amount, l.interest_rate,
                                l.amount_repaid, l.status.value, l.start_date.strftime("%Y-%m-%d"),
                                l.end_date.strftime("%Y-%m-%d") if l.end_date else ""
                            ])
                        except Exception as e:
                            error_logger.warning(f"Failed to export loan {l.id}: {str(e)}")
                
                exported_files.append("loans")
                error_logger.info(f"Exported {len(loans)} loans")
            
            except Exception as e:
                error_msg = UserFriendlyError.get_message('export_failed', f"Loans export: {str(e)}")
                error_logger.error(f"Loans export failed: {str(e)}")
                raise
            
            try:
                # Export contributions
                operation_status.value = "Exporting contributions..."
                page.update()
                
                contributions = get_all_contributions()
                contrib_file = os.path.join(exports_dir, f"contributions_{timestamp}.csv")
                
                with open(contrib_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ID", "Member ID", "Amount", "Type", "Date", "Month"
                    ])
                    for c in contributions:
                        try:
                            writer.writerow([
                                c.id, c.member_id, c.amount, c.contribution_type.value,
                                c.contribution_date.strftime("%Y-%m-%d"), c.month or ""
                            ])
                        except Exception as e:
                            error_logger.warning(f"Failed to export contribution {c.id}: {str(e)}")
                
                exported_files.append("contributions")
                error_logger.info(f"Exported {len(contributions)} contributions")
            
            except Exception as e:
                error_msg = UserFriendlyError.get_message('export_failed', f"Contributions export: {str(e)}")
                error_logger.error(f"Contributions export failed: {str(e)}")
                raise
            
            # Success
            operation_status.value = f"✓ Export successful: {', '.join(exported_files)} files saved"
            operation_status.color = ft.Colors.GREEN_700
            ToastNotification.show(page, f"✓ Exported {', '.join(exported_files)} to {exports_dir}", NotificationType.SUCCESS)
            error_logger.info(f"Export completed successfully: {', '.join(exported_files)}")
        
        except Exception as e:
            error_msg = UserFriendlyError.get_message('export_failed', str(e))
            operation_status.value = f"✗ Export failed: {str(e)}"
            operation_status.color = ft.Colors.RED_700
            error_logger.exception(f"Export failed: {str(e)}")
            ToastNotification.show(page, error_msg, NotificationType.ERROR)
        
        page.update()
    
    def backup_database():
        """Create a backup copy of the database file"""
        try:
            if not os.path.exists(DB_PATH):
                ToastNotification.show(page, "No database file found to backup", NotificationType.WARNING)
                return
            
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"loan_manager_backup_{timestamp}.db"
            backup_path = os.path.join(downloads_dir, backup_name)
            
            shutil.copy2(DB_PATH, backup_path)
            
            ToastNotification.show(page, f"\u2713 Backup saved to Downloads/{backup_name}", NotificationType.SUCCESS)
            error_logger.info(f"Database backed up to: {backup_path}")
        except Exception as e:
            error_logger.exception(f"Backup failed: {str(e)}")
            ToastNotification.show(page, f"Backup failed: {str(e)}", NotificationType.ERROR)
    
    async def restore_database():
        """Restore database from a .db backup file using Flet FilePicker (async, Flet 0.80+)"""
        files = await file_picker.pick_files(
            dialog_title="Select Database Backup File",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["db"],
            allow_multiple=False,
        )

        if not files:
            return

        file_path = files[0].path
        if not file_path or not os.path.exists(file_path):
            return

        if not file_path.endswith(".db"):
            ToastNotification.show(page, "Please select a valid .db backup file", NotificationType.WARNING)
            return

        def do_restore(selected_path):
            try:
                shutil.copy2(selected_path, DB_PATH)
                init_db()
                ToastNotification.show(page, "✓ Database restored successfully! Restart the app to see changes.", NotificationType.SUCCESS)
                error_logger.info(f"Database restored from: {selected_path}")
            except Exception as ex:
                error_logger.exception(f"Restore failed: {str(ex)}")
                ToastNotification.show(page, f"Restore failed: {str(ex)}", NotificationType.ERROR)

        confirm_dialog = ConfirmDialog(
            title="Restore Database",
            content=f"Restore from: {os.path.basename(file_path)}?\n\nThis will REPLACE all current data with the backup. This cannot be undone!",
            confirm_text="Restore",
            cancel_text="Cancel",
            danger=True,
        )
        confirm_dialog.on_confirm(lambda: do_restore(file_path))
        confirm_dialog.show(page)
    
    def reset_database():
        """Reset database with confirmation dialog"""
        def do_reset():
            try:
                start_time = time.time()
                operation = operation_history.start_operation("DATABASE_RESET", "Reset entire database")
                
                ToastNotification.show(page, "Resetting database...", NotificationType.WARNING)
                reset_all_data()
                
                # Re-create default admin account
                try:
                    create_user(
                        username="admin",
                        email="admin@morningstar.coop",
                        password="admin123",
                        full_name="Administrator",
                        role="ADMIN",
                    )
                    error_logger.info("Default admin account recreated after reset")
                except Exception:
                    pass  # Admin may already exist
                
                duration = time.time() - start_time
                operation_history.end_operation(operation, success=True, duration=duration)
                ToastNotification.show(page, "Database reset successfully! Default admin restored.", NotificationType.SUCCESS)
                error_logger.info("Database reset completed")
            except Exception as e:
                error_logger.exception(f"Database reset failed: {str(e)}")
                ToastNotification.show(page, f"Reset failed: {str(e)}", NotificationType.ERROR)
        
        # Use new modal confirmation dialog
        confirm_dialog = ConfirmDialog(
            title="Reset Database",
            content="Are you sure you want to reset the entire database?\nThis will DELETE ALL DATA except the default admin account.\nThis cannot be undone!",
            confirm_text="Reset Database",
            cancel_text="Cancel",
            danger=True
        )
        confirm_dialog.on_confirm(do_reset)
        confirm_dialog.show(page)
    
    def show_create_account_dialog():
        """Show create account dialog"""
        def on_account_created(user):
            ToastNotification.show(page, f"Account '{user.username}' created successfully!", NotificationType.SUCCESS)

        
        dialog = create_account_dialog(page, on_success_callback=on_account_created)
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_users_list():
        """Show users list dialog"""
        dialog = list_users_dialog(page)
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_change_password_dialog():
        """Show change password dialog"""
        # Try to get current user from context or prompt
        # For now, we'll get the first admin user or current user
        try:
            session = get_session()
            current_user = session.query(User).filter(User.is_active == True).first()
            session.close()
            
            if current_user:
                dialog = change_password_dialog(page, current_user.id, current_user.username)
                page.overlay.append(dialog)
                dialog.open = True
                page.update()
            else:
                ToastNotification.show(page, "No active user found", NotificationType.WARNING)
        except Exception as e:
            ToastNotification.show(page, f"Error: {str(e)}", NotificationType.ERROR)
    
    # Settings cards
    data_management_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Data Management", size=18, weight="bold", color=ft.Colors.BLUE_200),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Import Data", size=14, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Import loan and contribution data from CSV files",
                                    size=13,
                                    color=ft.Colors.GREY
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Import from CSV",
                            icon=ft.Icons.UPLOAD,
                            on_click=lambda e: import_data_dialog(),
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Export Data", size=14, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Download all data as CSV files for backup or analysis",
                                    size=13,
                                    color=ft.Colors.GREY
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Export to CSV",
                            icon=ft.Icons.DOWNLOAD,
                            on_click=lambda e: export_to_csv(),
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                operation_status,
                import_results_container,
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Backup Database", size=14, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Save a copy of the database to Downloads",
                                    size=13,
                                    color=ft.Colors.GREY
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Backup",
                            icon=ft.Icons.BACKUP,
                            on_click=lambda e: backup_database(),
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Restore Backup", size=14, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Replace current data with a .db backup file",
                                    size=13,
                                    color=ft.Colors.GREY
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Restore",
                            icon=ft.Icons.RESTORE,
                            on_click=lambda e: page.run_task(restore_database),
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Reset Database", size=14, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Delete all data and reset (keeps default admin)",
                                    size=13,
                                    color=ft.Colors.GREY
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Reset",
                            icon=ft.Icons.DELETE,
                            color=ft.Colors.RED_700,
                            on_click=lambda e: reset_database(),
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=10,
        ),
        padding=20,
        bgcolor="#2a2a2a",
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
    )
    
    # App info card
    app_info_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("About", size=18, weight="bold", color=ft.Colors.BLUE_200),
                ft.Divider(),
                ft.Text("Loan & Contribution Management System", size=16, weight="bold", color=ft.Colors.WHITE),
                ft.Text("Version 1.0.0", size=14, color=ft.Colors.GREY),
                ft.Divider(),
                ft.Text(
                    "Customized software for Morning Star Cooperative. An offline, single-user desktop application for managing member contributions and loan lifecycles with ease and transparency.",
                    size=13,
                    color=ft.Colors.GREY,
                ),
            ],
            spacing=10,
        ),
        padding=20,
        bgcolor="#2a2a2a",
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
    )
    
    # Authentication & User Management card
    auth_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("User Management", size=18, weight="bold", color=ft.Colors.BLUE_200),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Create Account", size=14, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Create a new user account for system access",
                                    size=13,
                                    color=ft.Colors.GREY
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Create New User",
                            icon=ft.Icons.PERSON_ADD,
                            on_click=lambda e: show_create_account_dialog(),
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("View All Users", size=14, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "See all registered user accounts in the system",
                                    size=13,
                                    color=ft.Colors.GREY
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "View Users",
                            icon=ft.Icons.PEOPLE,
                            on_click=lambda e: show_users_list(),
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Change Password", size=14, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Update your current password",
                                    size=13,
                                    color=ft.Colors.GREY
                                ),
                            ],
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Change Password",
                            icon=ft.Icons.LOCK,
                            on_click=lambda e: show_change_password_dialog(),
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=10,
        ),
        padding=20,
        bgcolor="#2a2a2a",
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
    )
    
    # Main content
    content = ft.Container(
        content=ft.ListView(
            controls=[
                ft.Text("Settings", size=26, weight="bold", color=ft.Colors.BLUE_200),
                ft.Text("Manage your application and data", size=14, color=ft.Colors.GREY),
                ft.Container(height=20),
                auth_card,
                data_management_card,
                app_info_card,
            ],
            spacing=20,
            expand=True,
        ),
        padding=20,
        bgcolor="#1a1a1a",
        expand=True,
    )
    
    # Create sidebar overlay
    sidebar_wrapper, backdrop, sidebar_visible, toggle_sidebar, close_sidebar = create_sidebar_overlay(page)
    
    # Create burger menu button
    burger_button = create_burger_menu(toggle_sidebar)
    
    # Create app bar with burger menu
    app_bar = ft.AppBar(
        title=ft.Text("Settings", size=22, weight="bold", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_900,
        leading=burger_button,
        actions=[
            ft.IconButton(
                ft.Icons.LOGOUT,
                tooltip="Logout",
                on_click=lambda _: navigate_to(page, "/login"),
            )
        ],
    )
    
    return ft.View(
        route="/settings",
        controls=[
            app_bar,
            ft.Stack(
                controls=[
                    content,
                    backdrop,
                    sidebar_wrapper,
                ],
                expand=True,
            ),
        ],
    )
