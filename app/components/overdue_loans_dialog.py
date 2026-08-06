"""
Overdue Loans Dialog - Shows a list of overdue loans when clicking
the Overdue Loans card on the dashboard.
"""
import flet as ft
from database.connection import (
    get_all_loans,
    get_all_members,
    get_all_non_members,
    update_overdue_non_member_interest,
)
from datetime import datetime
from components.ui_components import ToastNotification, NotificationType


def get_overdue_loans_detailed():
    """Get overdue loans with borrower name and full details."""
    # Recalculate interest for overdue non-member loans before listing
    try:
        update_overdue_non_member_interest()
    except Exception as e:
        print(f"Warning: Could not update overdue interest: {e}")
    
    loans = get_all_loans()
    
    # Pre-build name lookup dicts (2 queries total instead of N per overdue loan)
    members = get_all_members()
    non_members = get_all_non_members()
    members_dict = {m.id: m.name for m in members}
    non_members_dict = {nm.id: nm.name for nm in non_members}
    
    overdue = []
    today = datetime.now()

    for loan in loans:
        if loan.end_date and loan.end_date < today and loan.status.value != "Paid":
            balance = max(0, (loan.amount + loan.total_interest + (getattr(loan, "overdue_penalty", 0.0) or 0.0)) - loan.amount_repaid)
            if balance > 0:
                # Get borrower name from pre-built dicts (O(1) lookup)
                if loan.is_member and loan.member_id:
                    borrower_name = members_dict.get(loan.member_id, "Unknown")
                elif not loan.is_member and loan.non_member_id:
                    borrower_name = non_members_dict.get(loan.non_member_id, "Unknown")
                else:
                    borrower_name = "Unknown"

                overdue.append({
                    "id": loan.id,
                    "borrower": borrower_name,
                    "is_member": loan.is_member,
                    "amount": loan.amount,
                    "total_interest": loan.total_interest,
                    "amount_repaid": loan.amount_repaid,
                    "balance": balance,
                    "end_date": loan.end_date,
                    "days_overdue": (today - loan.end_date).days,
                })

    return sorted(overdue, key=lambda x: x["days_overdue"], reverse=True)


def _severity_color(days: int):
    """Return color based on how overdue the loan is."""
    if days > 365:
        return ft.Colors.RED_600
    elif days > 180:
        return ft.Colors.RED_400
    elif days > 90:
        return ft.Colors.ORANGE_400
    else:
        return ft.Colors.YELLOW_400


def show_overdue_loans_dialog(page: ft.Page):
    """Build and show the Overdue Loans dialog."""
    overdue_loans = get_overdue_loans_detailed()

    if not overdue_loans:
        # Nothing overdue — quick toast
        ToastNotification.show(page, "✓ No overdue loans found!", NotificationType.SUCCESS)
        return

    total_overdue_balance = sum(l["balance"] for l in overdue_loans)

    # Build table rows
    rows = []
    for idx, loan in enumerate(overdue_loans, 1):
        sev_color = _severity_color(loan["days_overdue"])
        member_badge = ft.Container(
            content=ft.Text(
                "M" if loan["is_member"] else "NM",
                size=11,
                weight="bold",
                color=ft.Colors.WHITE,
            ),
            bgcolor=ft.Colors.BLUE_700 if loan["is_member"] else ft.Colors.ORANGE_700,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=5, vertical=2),
        )

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(idx), color=ft.Colors.WHITE, size=13)),
                    ft.DataCell(
                        ft.Row([
                            ft.Text(loan["borrower"], color=ft.Colors.WHITE, size=13, weight="bold"),
                            member_badge,
                        ], spacing=6)
                    ),
                    ft.DataCell(ft.Text(f"₦{loan['amount']:,.2f}", color=ft.Colors.WHITE, size=13)),
                    ft.DataCell(ft.Text(f"₦{loan['balance']:,.2f}", color=sev_color, size=13, weight="bold")),
                    ft.DataCell(ft.Text(loan["end_date"].strftime("%Y-%m-%d"), color=ft.Colors.GREY, size=13)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(f"{loan['days_overdue']}d", color=ft.Colors.WHITE, size=12, weight="bold"),
                            bgcolor=sev_color,
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        )
                    ),
                ],
            )
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("#", color=ft.Colors.GREY, weight="bold", size=12)),
            ft.DataColumn(ft.Text("BORROWER", color=ft.Colors.GREY, weight="bold", size=12)),
            ft.DataColumn(ft.Text("LOAN AMT", color=ft.Colors.GREY, weight="bold", size=12)),
            ft.DataColumn(ft.Text("BALANCE", color=ft.Colors.GREY, weight="bold", size=12)),
            ft.DataColumn(ft.Text("DUE DATE", color=ft.Colors.GREY, weight="bold", size=12)),
            ft.DataColumn(ft.Text("OVERDUE", color=ft.Colors.GREY, weight="bold", size=12)),
        ],
        rows=rows,
        bgcolor="#1a1a1a",
        divider_thickness=1,
        vertical_lines=ft.border.BorderSide(1, "#2a2a2a"),
        heading_row_height=40,
        data_row_min_height=45,
    )

    # Summary bar
    summary_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED_400, size=22),
                    ft.Text(f"{len(overdue_loans)} overdue loan{'s' if len(overdue_loans) != 1 else ''}",
                            size=15, weight="bold", color=ft.Colors.RED_400),
                ], spacing=8),
                ft.Text(f"Total Outstanding: ₦{total_overdue_balance:,.2f}",
                        size=15, weight="bold", color=ft.Colors.ORANGE_400),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=12,
        bgcolor="#2a2a2a",
        border_radius=8,
    )

    def close_dialog(e):
        dialog.open = False
        try:
            page.overlay.remove(dialog)
        except ValueError:
            pass
        page.update()

    dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_ROUNDED, color=ft.Colors.RED_400, size=30),
            ft.Text("Overdue Loans", size=20, weight="bold", color=ft.Colors.WHITE),
        ], spacing=10),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    summary_bar,
                    ft.Container(height=8),
                    ft.Container(
                        content=table,
                        border_radius=8,
                        border=ft.border.all(1, "#333333"),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=5,
            ),
            width=850,
            height=500,
        ),
        actions=[
            ft.TextButton("Close", on_click=close_dialog),
        ],
        bgcolor="#1e1e1e",
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
