import flet as ft
from database.connection import (
    get_all_loans,
    get_member_by_id,
    get_non_member_by_id,
    record_loan_topup,
    get_loan_total_due_amount,
    get_loan_balance_amount,
)
from database.models import LoanStatus
from datetime import datetime, timedelta
from components.ui_components import ToastNotification, NotificationType


def create_top_up_loan_dialog(page: ft.Page):
    """Create a dialog for topping up an existing loan"""
    
    all_loans_state = {"value": []}
    active_loans_state = {"value": []}
    loan_data_state = {"value": []}
    
    # Build searchable loan data
    def _build_loan_data():
        data = []
        for loan in active_loans_state["value"]:
            flagged = False
            if loan.is_member and loan.member_id:
                member = get_member_by_id(loan.member_id)
                member_name = member.name if member else "Unknown"
                flagged = member.is_flagged if member else False
            elif not loan.is_member and loan.non_member_id:
                non_member = get_non_member_by_id(loan.non_member_id)
                member_name = non_member.name if non_member else "Unknown"
                flagged = non_member.is_flagged if non_member else False
            else:
                member_name = "Unknown"
            label = f"Loan #{loan.id} - {member_name} (₦{loan.amount:,.2f})"
            data.append({"loan": loan, "name": member_name.lower(), "label": label, "id": loan.id, "flagged": flagged})
        return data
    def refresh_loans_list():
        """Reload active loans and rebuild searchable results."""
        all_loans_state["value"] = get_all_loans()
        active_loans_state["value"] = [
            loan for loan in all_loans_state["value"]
            if loan.status != LoanStatus.PAID
        ]
        loan_data_state["value"] = _build_loan_data()
        if "loan_results_list" in locals():
            _update_results((search_field.value or "").strip().lower())
        if "selected_loan" in locals() and selected_loan["value"]:
            selected_id = selected_loan["value"].id
            refreshed_item = next(
                (item for item in loan_data_state["value"] if item["id"] == selected_id),
                None,
            )
            if refreshed_item:
                _select_loan(refreshed_item)
            else:
                clear_loan_selection()

    refresh_loans_list()

    # ==================== SEARCHABLE LOAN PICKER ====================
    selected_loan = {"value": None}
    loan_results_list = ft.ListView(height=150, spacing=2, padding=5)

    _selected_chip_text = ft.Text("", size=15, color=ft.Colors.GREEN_400, weight="bold")

    def _fmt_currency(value: float) -> str:
        return f"₦{value:,.2f}"

    def _get_due_date_text(loan) -> str:
        return loan.end_date.strftime("%Y-%m-%d") if loan.end_date else "N/A"

    def _get_remaining_months_text(loan) -> str:
        if not loan.end_date:
            return "N/A"
        today = datetime.now().date()
        end_date = loan.end_date.date() if hasattr(loan.end_date, "date") else loan.end_date
        months_delta = (end_date.year - today.year) * 12 + (end_date.month - today.month)
        if end_date < today:
            overdue_months = abs(months_delta)
            return f"Overdue ({overdue_months} month{'s' if overdue_months != 1 else ''})"
        if months_delta > 0:
            return f"{months_delta} month{'s' if months_delta != 1 else ''} remaining"
        return "Due this month"

    def clear_loan_selection():
        selected_loan["value"] = None
        current_amount_field.value = ""
        current_interest_field.value = ""
        current_total_field.value = ""
        current_balance_field.value = ""
        current_status_field.value = ""
        current_due_date_field.value = ""
        current_remaining_months_field.value = ""
        new_amount_field.value = ""
        new_interest_field.value = ""
        new_total_field.value = ""
        new_due_date_field.value = ""
        topup_amount_field.value = ""
        topup_duration_field.value = "12"
        topup_interest_rate_field.value = "3"
        due_date_extension_field.value = "0"
        selected_chip.visible = False
        search_field.value = ""
        results_container.visible = True
        _update_results("")
        page.update()

    selected_chip = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.RECEIPT_LONG, color=ft.Colors.GREEN_400, size=18),
                _selected_chip_text,
                ft.IconButton(
                    ft.Icons.CLOSE, icon_size=16, icon_color=ft.Colors.RED_400,
                    tooltip="Clear selection",
                    on_click=lambda e: clear_loan_selection(),
                ),
            ],
            spacing=5,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#1a3a1a",
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        visible=False,
    )

    def _on_search_change(e):
        term = (e.control.value or "").strip().lower()
        _update_results(term)
        results_container.visible = True
        page.update()

    def _update_results(term):
        loan_results_list.controls.clear()
        if not term:
            matches = loan_data_state["value"][:20]
        else:
            matches = [
                ld for ld in loan_data_state["value"]
                if term in ld["name"] or term in str(ld["id"]) or term in ld["label"].lower()
            ][:20]
        if not matches:
            loan_results_list.controls.append(
                ft.Container(
                    content=ft.Text("No loans found", size=14, color=ft.Colors.GREY_400, italic=True),
                    padding=10,
                )
            )
        else:
            for ld in matches:
                row_controls = []
                if ld.get("flagged"):
                    row_controls.append(ft.Icon(ft.Icons.FLAG, color=ft.Colors.RED_400, size=16, tooltip="Flagged: Overdue 90+ days"))
                row_controls.append(ft.Text(ld["label"], size=15, color=ft.Colors.WHITE))
                loan_results_list.controls.append(
                    ft.Container(
                        content=ft.Row(row_controls, spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                        border_radius=4,
                        bgcolor="#2a2a2a",
                        on_click=lambda e, item=ld: _select_loan(item),
                        ink=True,
                    )
                )

    def _select_loan(ld):
        loan = ld["loan"]
        selected_loan["value"] = loan
        _selected_chip_text.value = ld["label"]
        selected_chip.visible = True
        search_field.value = ""
        results_container.visible = False
        # Populate current loan details
        total_due = get_loan_total_due_amount(loan)
        current_amount_field.value = _fmt_currency(loan.amount)
        current_interest_field.value = _fmt_currency(loan.total_interest)
        current_total_field.value = _fmt_currency(total_due)
        current_balance_field.value = _fmt_currency(get_loan_balance_amount(loan))
        current_status_field.value = str(loan.status.value) if hasattr(loan.status, 'value') else str(loan.status)
        current_due_date_field.value = _get_due_date_text(loan)
        current_remaining_months_field.value = _get_remaining_months_text(loan)
        topup_amount_field.value = ""
        topup_interest_rate_field.value = "3"
        topup_duration_field.value = "12"
        due_date_extension_field.value = "0"
        new_amount_field.value = ""
        new_interest_field.value = ""
        new_total_field.value = _fmt_currency(total_due)
        new_due_date_field.value = _get_due_date_text(loan)
        page.update()

    search_field = ft.TextField(
        hint_text="Type borrower name or loan # to search...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=_on_search_change,
        width=450,
        height=42,
        text_size=16,
        border_radius=8,
        dense=True,
    )

    results_container = ft.Container(
        content=loan_results_list,
        bgcolor="#1e1e1e",
        border=ft.border.all(1, ft.Colors.GREY_800),
        border_radius=6,
        width=450,
        visible=True,
    )

    _update_results("")

    loan_search_container = ft.Column(
        controls=[
            selected_chip,
            search_field,
            results_container,
        ],
        spacing=5,
    )
    
    # Display current loan details (read-only)
    current_amount_field = ft.TextField(
        label="Current Loan Amount (₦)",
        read_only=True,
        width=450,
        dense=True,
    )
    
    current_interest_field = ft.TextField(
        label="Current Interest (₦)",
        read_only=True,
        width=450,
        dense=True,
    )
    
    current_total_field = ft.TextField(
        label="Current Total (₦)",
        read_only=True,
        width=450,
        dense=True,
    )
    
    current_balance_field = ft.TextField(
        label="Remaining Balance (₦)",
        read_only=True,
        width=450,
        dense=True,
    )
    
    current_status_field = ft.TextField(
        label="Loan Status",
        read_only=True,
        width=450,
        dense=True,
    )

    current_due_date_field = ft.TextField(
        label="Current Due Date",
        read_only=True,
        width=450,
        dense=True,
    )

    current_remaining_months_field = ft.TextField(
        label="Current Remaining / Overdue Months",
        read_only=True,
        width=450,
        dense=True,
    )
    
    # Top-up amount
    topup_amount_field = ft.TextField(
        label="Top-up Amount (₦)",
        keyboard_type="number",
        width=450,
        dense=True,
        on_change=lambda e: calculate_new_totals(),
    )
    
    # Interest rate for the top-up
    topup_interest_rate_field = ft.TextField(
        label="Interest Rate (%)",
        keyboard_type="number",
        width=450,
        dense=True,
        value="3",
        on_change=lambda e: calculate_new_totals(),
    )
    
    # Duration for non-member interest calculation
    topup_duration_field = ft.TextField(
        label="Duration (Months - Applies to Non-Members)",
        keyboard_type="number",
        width=450,
        dense=True,
        value="12",
        on_change=lambda e: calculate_new_totals(),
    )

    due_date_extension_field = ft.TextField(
        label="Extend Due Date By (Months - Optional)",
        keyboard_type="number",
        width=450,
        dense=True,
        value="0",
        on_change=lambda e: calculate_new_totals(),
    )
    
    # New totals display (calculated)
    new_amount_field = ft.TextField(
        label="New Total Loan Amount (₦)",
        read_only=True,
        width=450,
        dense=True,
    )
    
    new_interest_field = ft.TextField(
        label="New Total Interest (₦)",
        read_only=True,
        width=450,
        dense=True,
    )
    
    new_total_field = ft.TextField(
        label="New Grand Total (₦)",
        read_only=True,
        width=450,
        dense=True,
    )

    new_due_date_field = ft.TextField(
        label="New Due Date",
        read_only=True,
        width=450,
        dense=True,
    )
    
    # Dialog
    dialog = ft.AlertDialog(
        title=ft.Text("Top-up Loan"),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Search for Loan", weight="bold", size=14),
                    ft.Text("Type borrower name or loan # to search:", size=14, color=ft.Colors.GREY_400),
                    loan_search_container,
                    
                    ft.Divider(height=20),
                    
                    ft.Text("Current Loan Details", weight="bold", size=14),
                    current_amount_field,
                    current_interest_field,
                    current_total_field,
                    current_balance_field,
                    current_status_field,
                    current_due_date_field,
                    current_remaining_months_field,
                    
                    ft.Divider(height=20),
                    
                    ft.Text("Top-up Details", weight="bold", size=14),
                    topup_amount_field,
                    ft.Text("Interest Rate & Duration:", weight="bold", size=14),
                    topup_interest_rate_field,
                    topup_duration_field,
                    due_date_extension_field,
                    
                    ft.Divider(height=20),
                    
                    ft.Text("New Loan Details", weight="bold", size=14, color=ft.Colors.GREEN_400),
                    new_amount_field,
                    new_interest_field,
                    new_total_field,
                    new_due_date_field,
                ],
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                tight=True,
            ),
            padding=15,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
            ft.TextButton("Confirm Top-up", on_click=lambda e: confirm_topup()),
        ],
    )
    
    def calculate_new_totals():
        """Calculate and display new loan totals"""
        if not selected_loan["value"]:
            return
        
        try:
            loan = selected_loan["value"]
            topup_str = topup_amount_field.value or "0"
            interest_rate = float(topup_interest_rate_field.value or "0")
            duration_months = int(topup_duration_field.value or "1")
            due_date_extension_months = int(due_date_extension_field.value or "0")
            
            topup_amount = float(topup_str)
            if duration_months <= 0:
                duration_months = 1
            if due_date_extension_months < 0:
                due_date_extension_months = 0
            
            # New loan amount = current amount + top-up amount
            new_amount = loan.amount + topup_amount
            
            # Interest calculation:
            current_interest = loan.total_interest
            if loan.is_member:
                new_topup_interest = (topup_amount * interest_rate) / 100
            else:
                new_topup_interest = ((topup_amount * interest_rate) / 100) * duration_months
                
            new_total_interest = current_interest + new_topup_interest
            new_total_due = new_amount + new_total_interest + (getattr(loan, "overdue_penalty", 0.0) or 0.0)

            if loan.end_date:
                new_due_date = loan.end_date + timedelta(days=30 * due_date_extension_months)
                new_due_date_field.value = new_due_date.strftime("%Y-%m-%d")
            else:
                new_due_date_field.value = "N/A"

            new_amount_field.value = _fmt_currency(new_amount)
            new_interest_field.value = _fmt_currency(new_total_interest)
            new_total_field.value = _fmt_currency(new_total_due)
            
            page.update()
        except Exception as ex:
            print(f"Error calculating totals: {ex}")
    
    def confirm_topup():
        """Confirm and process the loan top-up"""
        if not selected_loan["value"]:
            ToastNotification.show(page, "Please select a loan to top-up!", NotificationType.WARNING)
            return
        
        try:
            topup_str = topup_amount_field.value or "0"
            topup_amount = float(topup_str)
            interest_rate = float(topup_interest_rate_field.value or "0")
            duration_months = int(topup_duration_field.value or "1")
            due_date_extension_months = int(due_date_extension_field.value or "0")
            
            # Validate cap (50% max for both members and non-members)
            if interest_rate > 50:
                ToastNotification.show(page, "✗ Interest rate capped at 50%", NotificationType.WARNING)
                return
            
            if topup_amount <= 0:
                ToastNotification.show(page, "Please enter a valid top-up amount!", NotificationType.WARNING)
                return
            if duration_months <= 0:
                ToastNotification.show(page, "Please enter a valid duration in months!", NotificationType.WARNING)
                return
            if due_date_extension_months < 0:
                ToastNotification.show(page, "Due date extension cannot be negative!", NotificationType.WARNING)
                return
            
            loan = selected_loan["value"]
            
            # Calculate interest conditionally on membership type relative to time duration
            if loan.is_member:
                interest_on_topup = (topup_amount * interest_rate) / 100
            else:
                interest_on_topup = ((topup_amount * interest_rate) / 100) * duration_months
            
            # Record the top-up transaction in database (this also updates loan amounts)
            topup_record = record_loan_topup(
                loan_id=loan.id,
                topup_amount=topup_amount,
                interest_rate=interest_rate,
                interest_on_topup=interest_on_topup,
                topup_date=datetime.now(),
                due_date_extension_months=due_date_extension_months,
                notes=f"Loan top-up of ₦{topup_amount:.2f} at {interest_rate}% interest"
            )
            
            if not topup_record:
                ToastNotification.show(page, "✗ Error recording top-up. Please try again.", NotificationType.ERROR)
                return
            
            refresh_loans_list()
            updated_loan = next((item["loan"] for item in loan_data_state["value"] if item["id"] == loan.id), None)
            if updated_loan:
                loan = updated_loan

            close_dialog()
            ToastNotification.show(page, f"✓ Loan #{loan.id} topped up by ₦{topup_amount:.2f}! New total: {_fmt_currency(get_loan_total_due_amount(loan))}", NotificationType.SUCCESS)
            
        except ValueError as ve:
            ToastNotification.show(page, f"✗ Please enter valid numbers: {str(ve)}", NotificationType.ERROR)
        except Exception as ex:
            print(f"Error confirming top-up: {ex}")
            ToastNotification.show(page, f"✗ Error: {str(ex)}", NotificationType.ERROR)
    
    def close_dialog():
        """Close the dialog"""
        dialog.open = False
        selected_loan["value"] = None
        selected_chip.visible = False
        search_field.value = ""
        results_container.visible = True
        _update_results("")
        current_amount_field.value = ""
        current_interest_field.value = ""
        current_total_field.value = ""
        current_balance_field.value = ""
        current_status_field.value = ""
        current_due_date_field.value = ""
        current_remaining_months_field.value = ""
        topup_amount_field.value = ""
        topup_interest_rate_field.value = "3"
        topup_duration_field.value = "12"
        due_date_extension_field.value = "0"
        new_amount_field.value = ""
        new_interest_field.value = ""
        new_total_field.value = ""
        new_due_date_field.value = ""
        refresh_loans_list()
        page.update()
    
    return dialog, close_dialog, refresh_loans_list
