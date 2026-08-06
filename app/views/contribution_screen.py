import flet as ft
from database.connection import (
    get_all_contributions,
    get_all_members,
    record_contribution,
    get_contributions_by_member,
)
from components.navigation import create_app_bar
from components.burger_menu import create_sidebar_overlay, create_burger_menu
from components.contribution_details_dialog import create_contribution_details_dialog
from components.responsive import ResponsiveConfig, get_responsive_padding, get_responsive_font_size
from components.error_handler import error_logger, UserFriendlyError
from components.ui_components import ToastNotification, NotificationType
from datetime import datetime
from collections import defaultdict


def navigate_to(page: ft.Page, route: str):
    """Navigate to a different route (replaces deprecated page.go)"""
    page.route = route
    page.update()


def ContributionScreen(page: ft.Page):
    """Contributions management screen with DataTable and dialogs"""
    
    # State management
    contributions_list = get_all_contributions()
    members_list = get_all_members()
    members_dict = {m.id: m.name for m in members_list}
    members_ippis = {m.id: m.ippis_number or "N/A" for m in members_list}
    
    # Build member data for searchable pickers
    def _build_member_data():
        data = []
        for m in members_list:
            label = m.name
            if m.ippis_number:
                label += f"  (IPPIS: {m.ippis_number})"
            data.append({"id": m.id, "name": m.name.lower(), "ippis": str(m.ippis_number or "").lower(), "label": label, "flagged": m.is_flagged})
        return data
    member_data = _build_member_data()

    # ==================== CONTRIBUTION MEMBER PICKER ====================
    contrib_selected_member = {"value": None}
    contrib_results_list = ft.ListView(height=150, spacing=2, padding=5)
    _contrib_chip_text = ft.Text("", size=13, color=ft.Colors.GREEN_400, weight="bold")

    def _clear_contrib_member():
        contrib_selected_member["value"] = None
        contrib_chip.visible = False
        contrib_search_field.value = ""
        contrib_results_container.visible = True
        _update_contrib_results("")
        page.update()

    contrib_chip = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREEN_400, size=16),
                _contrib_chip_text,
                ft.IconButton(ft.Icons.CLOSE, icon_size=14, icon_color=ft.Colors.RED_400,
                    tooltip="Clear selection", on_click=lambda e: _clear_contrib_member()),
            ],
            spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#1a3a1a", border_radius=6,
        padding=ft.padding.symmetric(horizontal=10, vertical=4), visible=False,
    )

    def _on_contrib_search(e):
        term = (e.control.value or "").strip().lower()
        _update_contrib_results(term)
        contrib_results_container.visible = True
        page.update()

    def _update_contrib_results(term):
        contrib_results_list.controls.clear()
        if not term:
            matches = member_data[:20]
        else:
            matches = [md for md in member_data if term in md["name"] or term in md["ippis"]][:20]
        if not matches:
            contrib_results_list.controls.append(
                ft.Container(content=ft.Text("No members found", size=12, color=ft.Colors.GREY_400, italic=True), padding=10))
        else:
            for md in matches:
                row_controls = []
                if md.get("flagged"):
                    row_controls.append(ft.Icon(ft.Icons.FLAG, color=ft.Colors.RED_400, size=14, tooltip="Flagged: Overdue 90+ days"))
                row_controls.append(ft.Text(md["label"], size=13, color=ft.Colors.WHITE))
                contrib_results_list.controls.append(
                    ft.Container(
                        content=ft.Row(row_controls, spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                        border_radius=4, bgcolor="#2a2a2a",
                        on_click=lambda e, m=md: _select_contrib_member(m), ink=True,
                    ))

    def _select_contrib_member(md):
        contrib_selected_member["value"] = md["id"]
        _contrib_chip_text.value = md["label"]
        contrib_chip.visible = True
        contrib_search_field.value = ""
        contrib_results_container.visible = False
        page.update()

    contrib_search_field = ft.TextField(
        hint_text="Type name or IPPIS to search...", prefix_icon=ft.Icons.SEARCH,
        on_change=_on_contrib_search, width=400, height=42, text_size=14, border_radius=8, dense=True,
    )
    contrib_results_container = ft.Container(
        content=contrib_results_list, bgcolor="#1e1e1e",
        border=ft.border.all(1, ft.Colors.GREY_800), border_radius=6, width=400, visible=True,
    )
    _update_contrib_results("")
    contrib_member_picker = ft.Column(controls=[
        ft.Text("Type member name or IPPIS to search:", size=12, color=ft.Colors.GREY_400),
        contrib_chip, contrib_search_field, contrib_results_container,
    ], spacing=5)

    # ==================== WITHDRAWAL MEMBER PICKER ====================
    withdraw_selected_member = {"value": None}
    withdraw_results_list = ft.ListView(height=150, spacing=2, padding=5)
    _withdraw_chip_text = ft.Text("", size=13, color=ft.Colors.GREEN_400, weight="bold")

    def _clear_withdraw_member():
        withdraw_selected_member["value"] = None
        withdraw_chip.visible = False
        withdraw_search_field.value = ""
        withdraw_results_container.visible = True
        _update_withdraw_results("")
        page.update()

    withdraw_chip = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREEN_400, size=16),
                _withdraw_chip_text,
                ft.IconButton(ft.Icons.CLOSE, icon_size=14, icon_color=ft.Colors.RED_400,
                    tooltip="Clear selection", on_click=lambda e: _clear_withdraw_member()),
            ],
            spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#1a3a1a", border_radius=6,
        padding=ft.padding.symmetric(horizontal=10, vertical=4), visible=False,
    )

    def _on_withdraw_search(e):
        term = (e.control.value or "").strip().lower()
        _update_withdraw_results(term)
        withdraw_results_container.visible = True
        page.update()

    def _update_withdraw_results(term):
        withdraw_results_list.controls.clear()
        if not term:
            matches = member_data[:20]
        else:
            matches = [md for md in member_data if term in md["name"] or term in md["ippis"]][:20]
        if not matches:
            withdraw_results_list.controls.append(
                ft.Container(content=ft.Text("No members found", size=12, color=ft.Colors.GREY_400, italic=True), padding=10))
        else:
            for md in matches:
                row_controls = []
                if md.get("flagged"):
                    row_controls.append(ft.Icon(ft.Icons.FLAG, color=ft.Colors.RED_400, size=14, tooltip="Flagged: Overdue 90+ days"))
                row_controls.append(ft.Text(md["label"], size=13, color=ft.Colors.WHITE))
                withdraw_results_list.controls.append(
                    ft.Container(
                        content=ft.Row(row_controls, spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.symmetric(horizontal=10, vertical=8),
                        border_radius=4, bgcolor="#2a2a2a",
                        on_click=lambda e, m=md: _select_withdraw_member(m), ink=True,
                    ))

    def _select_withdraw_member(md):
        withdraw_selected_member["value"] = md["id"]
        _withdraw_chip_text.value = md["label"]
        withdraw_chip.visible = True
        withdraw_search_field.value = ""
        withdraw_results_container.visible = False
        page.update()

    withdraw_search_field = ft.TextField(
        hint_text="Type name or IPPIS to search...", prefix_icon=ft.Icons.SEARCH,
        on_change=_on_withdraw_search, width=400, height=42, text_size=14, border_radius=8, dense=True,
    )
    withdraw_results_container = ft.Container(
        content=withdraw_results_list, bgcolor="#1e1e1e",
        border=ft.border.all(1, ft.Colors.GREY_800), border_radius=6, width=400, visible=True,
    )
    _update_withdraw_results("")
    withdraw_member_picker = ft.Column(controls=[
        ft.Text("Type member name or IPPIS to search:", size=12, color=ft.Colors.GREY_400),
        withdraw_chip, withdraw_search_field, withdraw_results_container,
    ], spacing=5)
    
    amount_field = ft.TextField(label="Amount", keyboard_type="number", width=400)
    
    contribution_type_dropdown = ft.Dropdown(
        label="Contribution Type",
        options=[
            ft.dropdown.Option("MONTHLY", "Monthly"),
            ft.dropdown.Option("WEEKLY", "Weekly"),
            ft.dropdown.Option("VOLUNTARY", "Voluntary"),
        ],
        value="MONTHLY",
        width=400,
    )
    
    contribution_date_field = ft.TextField(
        label="Contribution Date (YYYY-MM-DD)",
        width=400,
        value=datetime.now().strftime("%Y-%m-%d"),
        hint_text="Date contribution was made",
    )
    
    month_field = ft.TextField(label="Month (optional)", hint_text="e.g., January 2024", width=400)
    notes_field = ft.TextField(label="Notes (optional)", multiline=True, width=400, min_lines=3)
    
    contribution_dialog = ft.AlertDialog(
        title=ft.Text("Record Contribution"),
        content=ft.Column(
            controls=[
                contrib_member_picker,
                amount_field,
                contribution_type_dropdown,
                contribution_date_field,
                month_field,
                notes_field,
            ],
            width=500,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_contribution_dialog()),
            ft.TextButton("Record", on_click=lambda e: record_new_contribution()),
        ],
    )
    
    withdrawal_amount_field = ft.TextField(label="Withdrawal Amount", keyboard_type="number", width=400)
    
    withdrawal_reason_field = ft.TextField(
        label="Reason for Withdrawal", multiline=True, width=400, min_lines=3,
        hint_text="Please provide a reason for the withdrawal",
    )
    
    withdrawal_date_field = ft.TextField(
        label="Withdrawal Date (YYYY-MM-DD)", width=400,
        value=datetime.now().strftime("%Y-%m-%d"), hint_text="Date withdrawal was made",
    )
    
    withdrawal_dialog = ft.AlertDialog(
        title=ft.Text("Record Withdrawal"),
        content=ft.Column(
            controls=[
                withdraw_member_picker,
                withdrawal_amount_field,
                withdrawal_date_field,
                withdrawal_reason_field,
            ],
            width=500,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_withdrawal_dialog()),
            ft.TextButton("Record Withdrawal", on_click=lambda e: record_withdrawal()),
        ],
    )
    
    def close_contribution_dialog():
        contribution_dialog.open = False
        # Clear fields
        contrib_selected_member["value"] = None
        contrib_chip.visible = False
        contrib_search_field.value = ""
        contrib_results_container.visible = True
        _update_contrib_results("")
        amount_field.value = ""
        contribution_type_dropdown.value = "MONTHLY"
        contribution_date_field.value = datetime.now().strftime("%Y-%m-%d")
        month_field.value = ""
        notes_field.value = ""
        page.update()
    
    def close_withdrawal_dialog():
        withdrawal_dialog.open = False
        # Clear fields
        withdraw_selected_member["value"] = None
        withdraw_chip.visible = False
        withdraw_search_field.value = ""
        withdraw_results_container.visible = True
        _update_withdraw_results("")
        withdrawal_amount_field.value = ""
        withdrawal_date_field.value = datetime.now().strftime("%Y-%m-%d")
        withdrawal_reason_field.value = ""
        page.update()
    
    def record_new_contribution():
        """Record a new contribution with comprehensive error handling"""
        try:
            # Validate required fields
            if not contrib_selected_member["value"]:
                error_logger.warning("Contribution recording: no member selected")
                error_msg = UserFriendlyError.get_message('missing_required_field', "Please select a member")
                ToastNotification.show(page, f"✗ {error_msg}", NotificationType.ERROR)
                page.update()
                return
            
            member_id = contrib_selected_member["value"]
            
            # Parse and validate amount
            try:
                amount = float(amount_field.value or 0)
                if amount <= 0:
                    raise ValueError("Contribution amount must be greater than 0")
            except ValueError as e:
                error_logger.warning(f"Invalid contribution amount: {amount_field.value} - {str(e)}")
                error_msg = UserFriendlyError.get_message('validation_error', f"Invalid amount: {str(e)}")
                ToastNotification.show(page, f"✗ {error_msg}", NotificationType.ERROR)
                page.update()
                return
            
            # Get contribution type
            contrib_type = contribution_type_dropdown.value or "MONTHLY"
            
            # Parse contribution date
            contribution_date_str = contribution_date_field.value or datetime.now().strftime("%Y-%m-%d")
            try:
                contrib_date = datetime.strptime(contribution_date_str, "%Y-%m-%d")
            except ValueError:
                error_logger.warning(f"Invalid contribution date format: {contribution_date_str}")
                error_logger.info("Using current date for contribution")
                contrib_date = datetime.now()
            
            month = month_field.value or None
            notes = notes_field.value or None
            
            # Record contribution
            error_logger.info(f"Recording contribution: member_id={member_id}, amount={amount}, type={contrib_type}")
            record_contribution(member_id, amount, contrib_type, contribution_date=contrib_date, month=month, notes=notes)
            
            close_contribution_dialog()
            refresh_contributions()
            
            error_logger.info(f"Contribution recorded successfully: {amount} for member {member_id}")
            ToastNotification.show(page, f"✓ Contribution of ₦{amount:.2f} recorded successfully!", NotificationType.SUCCESS)
            page.update()
        
        except Exception as e:
            error_logger.exception(f"Error recording contribution: {str(e)}")
            error_msg = UserFriendlyError.get_message('db_commit_error', str(e))
            ToastNotification.show(page, f"✗ {error_msg}", NotificationType.ERROR)
            page.update()
    
    def record_withdrawal():
        """Record a withdrawal with comprehensive error handling"""
        try:
            # Validate required fields
            if not withdraw_selected_member["value"]:
                error_logger.warning("Withdrawal recording: no member selected")
                error_msg = UserFriendlyError.get_message('missing_required_field', "Please select a member")
                ToastNotification.show(page, f"✗ {error_msg}", NotificationType.ERROR)
                page.update()
                return
            
            member_id = withdraw_selected_member["value"]
            
            # Parse and validate amount
            try:
                amount = float(withdrawal_amount_field.value or 0)
                if amount <= 0:
                    raise ValueError("Withdrawal amount must be greater than 0")
            except ValueError as e:
                error_logger.warning(f"Invalid withdrawal amount: {withdrawal_amount_field.value} - {str(e)}")
                error_msg = UserFriendlyError.get_message('validation_error', f"Invalid amount: {str(e)}")
                ToastNotification.show(page, f"✗ {error_msg}", NotificationType.ERROR)
                page.update()
                return
            
            # Get reason
            reason = withdrawal_reason_field.value or "Withdrawal"
            
            # Parse withdrawal date
            withdrawal_date_str = withdrawal_date_field.value or datetime.now().strftime("%Y-%m-%d")
            try:
                withdrawal_date = datetime.strptime(withdrawal_date_str, "%Y-%m-%d")
            except ValueError:
                error_logger.warning(f"Invalid withdrawal date format: {withdrawal_date_str}")
                error_logger.info("Using current date for withdrawal")
                withdrawal_date = datetime.now()
            
            # Record withdrawal as negative contribution
            error_logger.info(f"Recording withdrawal: member_id={member_id}, amount={amount}, reason={reason}")
            record_contribution(
                member_id,
                -amount,
                "VOLUNTARY",
                contribution_date=withdrawal_date,
                month=withdrawal_date.strftime("%B %Y"),
                notes=reason
            )
            
            close_withdrawal_dialog()
            refresh_contributions()
            
            error_logger.info(f"Withdrawal recorded successfully: {amount} for member {member_id}")
            ToastNotification.show(page, f"✓ Withdrawal of ₦{amount:.2f} recorded successfully!", NotificationType.SUCCESS)
            page.update()
        
        except Exception as e:
            error_logger.exception(f"Error recording withdrawal: {str(e)}")
            error_msg = UserFriendlyError.get_message('db_commit_error', str(e))
            ToastNotification.show(page, f"✗ {error_msg}", NotificationType.ERROR)
            page.update()
    
    def refresh_contributions():
        nonlocal contributions_list
        contributions_list = get_all_contributions()
        update_contributions_table()
        update_chart()
    
    def update_chart():
        """Update the contribution vs withdrawal chart"""
        nonlocal total_contributed, total_withdrawn, chart_container
        total_contributed, total_withdrawn = get_chart_data()
        
        # Recreate pie chart visualization
        if total_contributed > 0 or total_withdrawn > 0:
            total = total_contributed + total_withdrawn
            contrib_percent = (total_contributed / total * 100) if total > 0 else 0
            withdraw_percent = (total_withdrawn / total * 100) if total > 0 else 0
            
            pie_chart_content = ft.Column([
                ft.Text("Contribution vs Withdrawal", size=14, weight="bold", color=ft.Colors.BLUE_200),
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        ft.Row([
                            ft.Container(width=12, height=12, bgcolor=ft.Colors.GREEN_400, border_radius=2),
                            ft.Text("Contributions", size=11, color=ft.Colors.WHITE),
                            ft.Text(f"{contrib_percent:.1f}%", size=11, color=ft.Colors.GREY),
                        ], spacing=8),
                        ft.Row([
                            ft.Container(width=12, height=12, bgcolor=ft.Colors.RED_400, border_radius=2),
                            ft.Text("Withdrawals", size=11, color=ft.Colors.WHITE),
                            ft.Text(f"{withdraw_percent:.1f}%", size=11, color=ft.Colors.GREY),
                        ], spacing=8),
                    ],
                    spacing=15,
                ),
                ft.Container(height=15),
                ft.Column([
                    ft.Row([
                        ft.Container(
                            height=20,
                            width=int(contrib_percent * 2),
                            bgcolor=ft.Colors.GREEN_400,
                            border_radius=2,
                        ),
                        ft.Container(
                            height=20,
                            width=int(withdraw_percent * 2),
                            bgcolor=ft.Colors.RED_400,
                            border_radius=2,
                        ),
                    ], spacing=0),
                ], spacing=5),
                ft.Container(height=15),
                ft.Column([
                    ft.Text(f"Total Contributed: ₦{total_contributed:.2f}", size=11, color=ft.Colors.GREEN_400, weight="bold"),
                    ft.Text(f"Total Withdrawn: ₦{total_withdrawn:.2f}", size=11, color=ft.Colors.RED_400, weight="bold"),
                    ft.Divider(height=1, color=ft.Colors.GREY_800),
                    ft.Text(f"Net Balance: ₦{(total_contributed - total_withdrawn):.2f}", size=11, color=ft.Colors.BLUE_200, weight="bold"),
                ], spacing=5),
            ], spacing=5)
        else:
            pie_chart_content = ft.Column([
                ft.Text("Contribution vs Withdrawal", size=14, weight="bold", color=ft.Colors.BLUE_200),
                ft.Container(height=20),
                ft.Text("No contribution data yet", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        chart_container.content = pie_chart_content
        page.update()
    
    def show_member_details(member_id):
        """Show detailed contribution history for a member"""
        details_dialog = create_contribution_details_dialog(member_id, page)
        page.overlay.append(details_dialog)
        details_dialog.open = True
        page.update()
    
    # Search field
    search_field = ft.TextField(
        label="Search by name or IPPIS",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        dense=True,
        on_change=lambda e: filter_contributions_table(e.control.value),
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.BLUE_200),
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.CYAN_400,
        cursor_color=ft.Colors.WHITE,
        bgcolor="#2a2a2a",
        border_radius=8,
    )
    
    def _aggregate_contributions():
        """Pre-aggregate all contributions by member in a single pass (O(N) instead of O(M*N))."""
        agg = {}  # {member_id: {'contributed': float, 'withdrawn': float, 'total': float, 'latest_date': datetime}}
        for c in contributions_list:
            mid = c.member_id
            if mid not in agg:
                agg[mid] = {'contributed': 0.0, 'withdrawn': 0.0, 'total': 0.0, 'latest_date': None}
            agg[mid]['total'] += c.amount
            if c.amount > 0:
                agg[mid]['contributed'] += c.amount
            else:
                agg[mid]['withdrawn'] += abs(c.amount)
            if agg[mid]['latest_date'] is None or c.contribution_date > agg[mid]['latest_date']:
                agg[mid]['latest_date'] = c.contribution_date
        return agg
    
    def _build_member_rows(member_ids, agg):
        """Build DataTable rows for the given member_ids using pre-aggregated data."""
        rows = []
        serial_number = 1
        for member_id in member_ids:
            member_name = members_dict.get(member_id, "Unknown")
            member_ippis = members_ippis.get(member_id, "N/A")
            stats = agg.get(member_id, {'contributed': 0.0, 'withdrawn': 0.0, 'total': 0.0, 'latest_date': None})
            
            total_color = ft.Colors.GREEN_400 if stats['total'] > 0 else (ft.Colors.RED_400 if stats['total'] < 0 else ft.Colors.WHITE)
            latest_date = stats['latest_date']
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(serial_number), color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(member_ippis, color=ft.Colors.BLUE_200, weight="bold")),
                        ft.DataCell(ft.Text(member_name, color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(f"₦{stats['contributed']:.2f}", color=ft.Colors.GREEN_400, weight="bold")),
                        ft.DataCell(ft.Text(f"₦{stats['withdrawn']:.2f}", color=ft.Colors.RED_400, weight="bold")),
                        ft.DataCell(ft.Text(f"₦{stats['total']:.2f}", color=total_color, weight="bold")),
                        ft.DataCell(ft.Text(latest_date.strftime("%Y-%m-%d") if latest_date else "N/A", color=ft.Colors.GREY)),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.Icons.VISIBILITY,
                                        tooltip="View Details",
                                        on_click=lambda e, mid=member_id: show_member_details(mid),
                                        icon_size=18,
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )
            serial_number += 1
        return rows
    
    def filter_contributions_table(search_term):
        """Filter contributions table based on search term"""
        search_lower = search_term.lower()
        agg = _aggregate_contributions()
        
        # Filter member IDs matching search
        matching_ids = []
        for member_id in sorted(agg.keys()):
            member_name = members_dict.get(member_id, "Unknown")
            member_ippis = members_ippis.get(member_id, "N/A")
            if search_lower in member_name.lower() or search_lower in str(member_ippis).lower():
                matching_ids.append(member_id)
        
        contributions_table.rows = _build_member_rows(matching_ids, agg)
        page.update()
    
    # Contributions DataTable
    contributions_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("S/N", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("IPPIS", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("NAME", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("CONTRIBUTED", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("WITHDRAWN", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("BALANCE", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("LAST DATE", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("ACTION", color=ft.Colors.WHITE, weight="bold")),
        ],
        rows=[],
        bgcolor="#1a1a1a",
        divider_thickness=1,
    )
    
    def update_contributions_table():
        """Update the contributions table with all contributions data"""
        agg = _aggregate_contributions()
        contributions_table.rows = _build_member_rows(sorted(agg.keys()), agg)
        page.update()
    
    update_contributions_table()
    
    # Pie chart for contributions vs withdrawals
    def get_chart_data():
        """Generate data for contribution vs withdrawal chart"""
        total_contributed = sum(c.amount for c in contributions_list if c.amount > 0)
        total_withdrawn = sum(abs(c.amount) for c in contributions_list if c.amount < 0)
        
        return total_contributed, total_withdrawn
    
    total_contributed, total_withdrawn = get_chart_data()
    
    # Create a pie chart visualization for contributions vs withdrawals
    if total_contributed > 0 or total_withdrawn > 0:
        total = total_contributed + total_withdrawn
        contrib_percent = (total_contributed / total * 100) if total > 0 else 0
        withdraw_percent = (total_withdrawn / total * 100) if total > 0 else 0
        
        # Create pie chart sections
        pie_chart_content = ft.Column([
            ft.Text("Contribution vs Withdrawal", size=14, weight="bold", color=ft.Colors.BLUE_200),
            ft.Container(height=10),
            # Chart legend
            ft.Row(
                controls=[
                    ft.Row([
                        ft.Container(width=12, height=12, bgcolor=ft.Colors.GREEN_400, border_radius=2),
                        ft.Text("Contributions", size=11, color=ft.Colors.WHITE),
                        ft.Text(f"{contrib_percent:.1f}%", size=11, color=ft.Colors.GREY),
                    ], spacing=8),
                    ft.Row([
                        ft.Container(width=12, height=12, bgcolor=ft.Colors.RED_400, border_radius=2),
                        ft.Text("Withdrawals", size=11, color=ft.Colors.WHITE),
                        ft.Text(f"{withdraw_percent:.1f}%", size=11, color=ft.Colors.GREY),
                    ], spacing=8),
                ],
                spacing=15,
            ),
            ft.Container(height=15),
            # Bar representation of pie chart
            ft.Column([
                ft.Row([
                    ft.Container(
                        height=20,
                        width=int(contrib_percent * 2),
                        bgcolor=ft.Colors.GREEN_400,
                        border_radius=2,
                    ),
                    ft.Container(
                        height=20,
                        width=int(withdraw_percent * 2),
                        bgcolor=ft.Colors.RED_400,
                        border_radius=2,
                    ),
                ], spacing=0),
            ], spacing=5),
            ft.Container(height=15),
            # Summary text
            ft.Column([
                ft.Text(f"Total Contributed: ₦{total_contributed:.2f}", size=11, color=ft.Colors.GREEN_400, weight="bold"),
                ft.Text(f"Total Withdrawn: ₦{total_withdrawn:.2f}", size=11, color=ft.Colors.RED_400, weight="bold"),
                ft.Divider(height=1, color=ft.Colors.GREY_800),
                ft.Text(f"Net Balance: ₦{(total_contributed - total_withdrawn):.2f}", size=11, color=ft.Colors.BLUE_200, weight="bold"),
            ], spacing=5),
        ], spacing=5)
    else:
        pie_chart_content = ft.Column([
            ft.Text("Contribution vs Withdrawal", size=14, weight="bold", color=ft.Colors.BLUE_200),
            ft.Container(height=20),
            ft.Text("No contribution data yet", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    chart_container = ft.Container(
        content=pie_chart_content,
        bgcolor="#2a2a2a",
        border_radius=10,
        padding=15,
        width=420,
        height=280,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
    )
    
    # Summary cards
    total_contributions = sum(c.amount for c in contributions_list if c.amount > 0)
    total_withdrawals = sum(abs(c.amount) for c in contributions_list if c.amount < 0)
    net_balance = total_contributions - total_withdrawals
    
    summary_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Total Contributions", size=12, color=ft.Colors.GREY),
                        ft.Text(f"₦{total_contributions:.2f}", size=18, weight="bold", color=ft.Colors.GREEN_400),
                    ],
                    spacing=5,
                ),
                padding=15,
                bgcolor="#252525",
                border_radius=10,
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Total Withdrawals", size=12, color=ft.Colors.GREY),
                        ft.Text(f"₦{total_withdrawals:.2f}", size=18, weight="bold", color=ft.Colors.RED_400),
                    ],
                    spacing=5,
                ),
                padding=15,
                bgcolor="#252525",
                border_radius=10,
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Net Balance", size=12, color=ft.Colors.GREY),
                        ft.Text(f"₦{net_balance:.2f}", size=18, weight="bold", color=ft.Colors.BLUE_200),
                    ],
                    spacing=5,
                ),
                padding=15,
                bgcolor="#252525",
                border_radius=10,
                expand=True,
            ),
        ],
        spacing=15,
    )
    
    # Add button
    def open_contribution_dialog(e):
        contribution_dialog.open = True
        page.update()
    
    def open_withdrawal_dialog(e):
        withdrawal_dialog.open = True
        page.update()
    
    add_contribution_button = ft.ElevatedButton(
        "Add Contribution",
        icon=ft.Icons.ADD,
        on_click=open_contribution_dialog,
    )
    
    # Withdrawal button
    withdrawal_button = ft.ElevatedButton(
        "Record Withdrawal",
        icon=ft.Icons.REMOVE,
        on_click=open_withdrawal_dialog,
    )
    
    # Refresh button
    refresh_button = ft.IconButton(
        ft.Icons.REFRESH,
        tooltip="Refresh",
        on_click=lambda e: refresh_contributions(),
    )
    
    # Top controls
    top_row = ft.Row(
        controls=[
            search_field,
            add_contribution_button,
            withdrawal_button,
            refresh_button,
        ],
        spacing=10,
    )
    
    # Table and Chart Row (Responsive)
    is_small_screen = ResponsiveConfig.is_small_screen(page)
    
    # Table wrapper with scrolling
    table_wrapper = ft.Container(
        content=ft.Column(
            controls=[contributions_table],
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        bgcolor="#2a2a2a",
        border_radius=10,
        padding=10,
        height=600,
        width=800,
    )
    
    if is_small_screen:
        # Mobile/Tablet: Stack vertically
        table_chart_row = ft.Column(
            controls=[
                table_wrapper,
                chart_container,
            ],
            spacing=15,
            expand=True,
        )
    else:
        # Desktop: Side by side - Table takes more space, chart on the right
        table_chart_row = ft.Row(
            controls=[
                ft.Container(
                    content=table_wrapper,
                    expand=True,
                ),
                chart_container,
            ],
            spacing=15,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
    
    # Main content
    padding = get_responsive_padding(page)
    
    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Contribution Management", size=get_responsive_font_size(page, 24), weight="bold", color=ft.Colors.BLUE_200),
                ft.Text("Manage member contributions and withdrawals", size=12, color=ft.Colors.GREY),
                summary_row,
                ft.Container(height=20),
                top_row,
                table_chart_row,
            ],
            spacing=15,
            expand=True,
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
        title=ft.Text("Contribution Management", size=20, weight="bold", color=ft.Colors.WHITE),
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
    
    page.overlay.append(contribution_dialog)
    page.overlay.append(withdrawal_dialog)
    
    return ft.View(
        route="/contributions",
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

