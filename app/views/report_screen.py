import flet as ft
from components.navigation import create_app_bar
from components.burger_menu import create_sidebar_overlay, create_burger_menu
from components.responsive import ResponsiveConfig, get_responsive_padding, get_responsive_font_size
from components.ui_components import ToastNotification, NotificationType, ProgressDialog, ConfirmDialog
from components.error_handler import error_logger, UserFriendlyError
from components.reporting import (
    ReportGenerator, ReportExporter, ReportFilter, ReportType,
    ExportFormat, DateRange, ReportType as RT
)
from database.connection import (
    get_all_members,
    get_all_loans,
    get_all_contributions,
)
from datetime import datetime, timedelta
import os
from pathlib import Path
import threading


def navigate_to(page: ft.Page, route: str):
    """Navigate to a different route (replaces deprecated page.go)"""
    page.route = route
    page.update()


def ReportScreen(page: ft.Page):
    """Report generation screen with advanced filtering and exports"""
    
    # UI state
    progress_dialog = None
    
    # Report type dropdown
    report_type = ft.Dropdown(
        label="Report Type",
        options=[
            ft.dropdown.Option("member_summary", "Member Summary"),
            ft.dropdown.Option("loan_summary", "Loan Summary"),
            ft.dropdown.Option("contribution_summary", "Contribution Summary"),
            ft.dropdown.Option("detailed_member", "Detailed Member Report"),
            ft.dropdown.Option("loan_status", "Loan Status Report"),
            ft.dropdown.Option("ippis_ledger", "IPPIS Ledger"),
        ],
        value="member_summary",
        width=220,
    )
    
    # Export format dropdown
    export_format = ft.Dropdown(
        label="Export Format",
        options=[
            ft.dropdown.Option("csv", "CSV"),
            ft.dropdown.Option("excel", "Excel (XLSX)"),
            ft.dropdown.Option("pdf", "PDF"),
        ],
        value="csv",
        width=180,
    )
    
    # Date range preset dropdown
    date_range_preset = ft.Dropdown(
        label="Date Range",
        options=[
            ft.dropdown.Option("last_30", "Last 30 Days"),
            ft.dropdown.Option("last_90", "Last 90 Days"),
            ft.dropdown.Option("this_month", "This Month"),
            ft.dropdown.Option("this_year", "This Year"),
            ft.dropdown.Option("custom", "Custom Range"),
        ],
        value="last_90",
        width=200,
    )
    
    # Custom date inputs
    start_date_input = ft.TextField(
        label="Start Date (YYYY-MM-DD)",
        hint_text="2024-01-01",
        width=180,
        visible=False,
    )
    
    end_date_input = ft.TextField(
        label="End Date (YYYY-MM-DD)",
        hint_text="2024-12-31",
        width=180,
        visible=False,
    )
    
    # Loan status filter dropdown
    loan_status_filter = ft.Dropdown(
        label="Loan Status",
        options=[
            ft.dropdown.Option("all", "All Statuses"),
            ft.dropdown.Option("pending", "Pending"),
            ft.dropdown.Option("active", "Active"),
            ft.dropdown.Option("paid", "Paid"),
        ],
        value="all",
        width=200,
    )
    
    # Borrower type filter dropdown
    borrower_type_filter = ft.Dropdown(
        label="Borrower Type",
        options=[
            ft.dropdown.Option("all", "All (Members & Non-Members)"),
            ft.dropdown.Option("member", "Members Only"),
            ft.dropdown.Option("non_member", "Non-Members Only"),
        ],
        value="all",
        width=220,
    )
    
    # Status message
    report_status = ft.Text("Ready to generate report", size=14, color=ft.Colors.BLUE_400)
    
    def update_date_inputs_visibility(e):
        """Show/hide custom date inputs based on preset selection"""
        is_custom = date_range_preset.value == "custom"
        start_date_input.visible = is_custom
        end_date_input.visible = is_custom
        page.update()
    
    def get_date_range_filter() -> DateRange:
        """Get date range based on preset selection"""
        if date_range_preset.value == "last_30":
            return DateRange.last_30_days()
        elif date_range_preset.value == "last_90":
            return DateRange.last_90_days()
        elif date_range_preset.value == "this_month":
            return DateRange.this_month()
        elif date_range_preset.value == "this_year":
            return DateRange.this_year()
        elif date_range_preset.value == "custom":
            try:
                start = datetime.strptime(start_date_input.value, "%Y-%m-%d")
                end = datetime.strptime(end_date_input.value, "%Y-%m-%d")
                return DateRange(start, end)
            except ValueError:
                raise UserFriendlyError("Invalid date format. Use YYYY-MM-DD")
        return DateRange.last_90_days()
    
    def generate_report_thread(e):
        """Generate report in background thread"""
        # Create export overlay dialog with spinner
        export_icon = ft.Icon(ft.Icons.DOWNLOADING, size=50, color=ft.Colors.BLUE_400)
        export_spinner = ft.ProgressRing(
            width=80,
            height=80,
            stroke_width=4,
            color=ft.Colors.BLUE_400,
        )
        export_status_text = ft.Text(
            "Generating report...",
            size=15,
            color=ft.Colors.GREY_400,
            text_align=ft.TextAlign.CENTER,
        )
        export_dialog_content = ft.Column(
            controls=[
                ft.Row(
                    controls=[export_spinner],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                export_status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            width=300,
        )
        export_dialog = ft.AlertDialog(
            title=ft.Text("Exporting Report"),
            content=export_dialog_content,
            modal=True,
        )
        
        def show_export_dialog():
            page.overlay.append(export_dialog)
            export_dialog.open = True
            page.update()
        
        def update_export_status(message):
            export_status_text.value = message
            page.update()
        
        def show_done_symbol(success=True, message=""):
            """Replace spinner with ✅ or ✗"""
            if success:
                done_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, size=66, color=ft.Colors.GREEN_400)
                export_status_text.value = message or "Export complete!"
                export_status_text.color = ft.Colors.GREEN_400
            else:
                done_icon = ft.Icon(ft.Icons.ERROR, size=66, color=ft.Colors.RED_400)
                export_status_text.value = message or "Export failed"
                export_status_text.color = ft.Colors.RED_400
            
            export_dialog_content.controls[0] = ft.Row(
                controls=[done_icon],
                alignment=ft.MainAxisAlignment.CENTER,
            )
            page.update()
        
        def close_export_dialog():
            export_dialog.open = False
            page.update()
        
        try:
            show_export_dialog()
            
            # Get data
            members = get_all_members()
            loans = get_all_loans()
            contributions = get_all_contributions()
            
            # Create report filter
            report_filter = ReportFilter()
            report_filter.date_range = get_date_range_filter()
            
            # Apply borrower type filter
            if borrower_type_filter.value != "all":
                report_filter.borrower_type = borrower_type_filter.value
            
            # Apply loan status filter
            if loan_status_filter.value == "pending":
                report_filter.include_active_loans = False
                report_filter.include_paid_loans = False
            elif loan_status_filter.value == "active":
                report_filter.include_pending_loans = False
                report_filter.include_paid_loans = False
            elif loan_status_filter.value == "paid":
                report_filter.include_pending_loans = False
                report_filter.include_overdue_loans = False
            
            # Generate report based on type
            report_data = None
            update_export_status("Generating report data...")
            
            if report_type.value == "member_summary":
                report_data = ReportGenerator.generate_member_summary(members, loans, contributions, report_filter)
            elif report_type.value == "loan_summary":
                report_data = ReportGenerator.generate_loan_summary(loans, report_filter)
            elif report_type.value == "loan_status":
                report_data = ReportGenerator.generate_loan_status_report(loans, report_filter)
            elif report_type.value == "detailed_member":
                raise UserFriendlyError("Detailed member report requires selecting a specific member from the UI")
            elif report_type.value == "ippis_ledger":
                report_data = ReportGenerator.generate_ippis_ledger(members, loans, contributions)
            
            if not report_data:
                raise UserFriendlyError("Failed to generate report data")
            
            # Export report
            update_export_status("Exporting report...")
            
            downloads_dir = str(Path.home() / "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            format_ext = "xlsx" if export_format.value == "excel" else export_format.value
            filename = f"{report_type.value}_{timestamp}.{format_ext}"
            filepath = os.path.join(downloads_dir, filename)
            
            # Export based on format
            success = False
            if export_format.value == "csv":
                success = ReportExporter.export_csv(report_data, filepath)
            elif export_format.value == "excel":
                success = ReportExporter.export_excel(report_data, filepath)
            elif export_format.value == "pdf":
                success = ReportExporter.export_pdf(report_data, filepath)
            
            if success:
                # Show ✅ done symbol
                show_done_symbol(True, f"✅ Report saved: {filename}")
                report_status.value = f"✓ Report generated: {filename}"
                report_status.color = ft.Colors.GREEN_700
                error_logger.info(f"Report generated successfully: {filename}")
                
                # Auto-close dialog after 2 seconds
                import time
                time.sleep(2)
                close_export_dialog()
                
                ToastNotification.show(
                    page,
                    f"Report saved to Downloads folder",
                    NotificationType.SUCCESS
                )
            else:
                show_done_symbol(False, "✗ Export failed")
                report_status.value = "✗ Report export failed"
                report_status.color = ft.Colors.RED_700
                
                import time
                time.sleep(2)
                close_export_dialog()
                
                ToastNotification.show(
                    page,
                    "Failed to export report",
                    NotificationType.ERROR
                )
        
        except UserFriendlyError as e:
            show_done_symbol(False, f"⚠ {str(e)}")
            report_status.value = f"✗ {str(e)}"
            report_status.color = ft.Colors.ORANGE_400
            
            import time
            time.sleep(2)
            close_export_dialog()
            
            ToastNotification.show(page, str(e), NotificationType.WARNING)
            error_logger.error(f"Report generation user error: {str(e)}")
        
        except Exception as e:
            show_done_symbol(False, f"✗ Error: {str(e)[:40]}")
            report_status.value = f"✗ Error: {str(e)[:50]}..."
            report_status.color = ft.Colors.RED_700
            
            import time
            time.sleep(2)
            close_export_dialog()
            
            ToastNotification.show(
                page,
                "Failed to generate report",
                NotificationType.ERROR
            )
            error_logger.error(f"Report generation failed: {str(e)}")
        
        page.update()
    
    date_range_preset.on_select = update_date_inputs_visibility
    
    # Generate report button
    generate_btn = ft.ElevatedButton(
        "Generate Report",
        icon=ft.Icons.DOCUMENT_SCANNER,
        width=200,
    )
    
    def on_generate_click(e):
        """Handle generate button click"""
        # Run in background thread
        thread = threading.Thread(target=generate_report_thread, args=(e,))
        thread.daemon = True
        thread.start()
    
    generate_btn.on_click = on_generate_click
    
    # Report configuration card
    report_config_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Report Configuration", size=18, weight="bold", color=ft.Colors.BLUE_200),
                ft.Divider(),
                ft.Row(
                    controls=[report_type, export_format],
                    spacing=20,
                    wrap=True,
                ),
                ft.Row(
                    controls=[date_range_preset],
                    spacing=20,
                    wrap=True,
                ),
                ft.Row(
                    controls=[start_date_input, end_date_input],
                    spacing=20,
                    wrap=True,
                ),
                ft.Row(
                    controls=[loan_status_filter, borrower_type_filter],
                    spacing=20,
                    wrap=True,
                ),
                ft.Container(height=10),
                ft.Row(
                    controls=[generate_btn],
                    spacing=10,
                ),
            ],
            spacing=15,
        ),
        padding=20,
        bgcolor="#2a2a2a",
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
    )
    
    # Report status card
    report_status_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Report Status", size=18, weight="bold", color=ft.Colors.BLUE_200),
                ft.Divider(),
                report_status,
                ft.Divider(),
                ft.Text(
                    "Reports are automatically saved to your Downloads folder with timestamp.\n"
                    "Supports CSV, Excel (formatted with colors and styling), and PDF formats.",
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
    
    # Main content
    padding = get_responsive_padding(page)
    is_small_screen = ResponsiveConfig.is_small_screen(page)
    
    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Reports", size=get_responsive_font_size(page, 24), weight="bold", color=ft.Colors.BLUE_200),
                ft.Text("Generate and filter reports by date range, member, and loan status", size=14, color=ft.Colors.GREY),
                ft.Container(height=20),
                report_config_card,
                report_status_card,
            ],
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=padding,
        bgcolor="#1a1a1a",
        expand=True,
    )
    
    

    
    # Create sidebar overlay
    sidebar_wrapper, backdrop, sidebar_visible, toggle_sidebar, close_sidebar = create_sidebar_overlay(page)
    
    # Create burger menu button
    burger_button = create_burger_menu(toggle_sidebar)
    
    # Create app bar with burger menu
    app_bar = ft.AppBar(
        title=ft.Text("Reports", size=22, weight="bold", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_900,
        leading=burger_button,
        actions=[
            ft.IconButton(
                ft.Icons.LOGOUT,
                tooltip="Logout",
                on_click=lambda _: page.go("/login"),
            )
        ],
    )
    
    return ft.View(
        route="/reports",
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
