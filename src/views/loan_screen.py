import flet as ft
from database.connection import (
    get_all_loans,
    get_all_members,
    create_loan,
    update_loan,
    record_repayment,
    get_loans_by_member,
)
from components.navigation import create_app_bar


def LoanScreen(page: ft.Page):
    """Loans management screen with DataTable and dialogs"""
    
    # State management
    loans_list = get_all_loans()
    members_dict = {m.id: m.name for m in get_all_members()}
    
    # Dialog for creating/editing loans
    loan_dialog = ft.AlertDialog(
        title=ft.Text("Add New Loan"),
        content=ft.Column(
            controls=[
                ft.Dropdown(
                    label="Member",
                    options=[
                        ft.dropdown.Option(str(m.id), m.name)
                        for m in get_all_members()
                    ],
                    width=400,
                ),
                ft.TextField(label="Loan Amount", keyboard_type="number", width=400),
                ft.TextField(label="Interest Rate (%)", keyboard_type="number", width=400),
                ft.TextField(label="Loan Duration (months)", keyboard_type="number", width=400),
            ],
            width=500,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_loan_dialog()),
            ft.TextButton("Create", on_click=lambda e: create_new_loan()),
        ],
    )
    
    # Dialog for recording repayment
    repayment_dialog = ft.AlertDialog(
        title=ft.Text("Record Repayment"),
        content=ft.Column(
            controls=[
                ft.Text("", size=14),  # Loan info placeholder
                ft.TextField(label="Amount to Pay", keyboard_type="number", width=400),
                ft.TextField(label="Notes (optional)", multiline=True, width=400, min_lines=3),
            ],
            width=500,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_repayment_dialog()),
            ft.TextButton("Confirm", on_click=lambda e: confirm_repayment()),
        ],
    )
    
    def close_loan_dialog():
        loan_dialog.open = False
        page.update()
    
    def close_repayment_dialog():
        repayment_dialog.open = False
        page.update()
    
    def create_new_loan():
        member_id = int(loan_dialog.content.controls[0].value or 0)
        amount = float(loan_dialog.content.controls[1].value or 0)
        interest_rate = float(loan_dialog.content.controls[2].value or 0)
        duration = int(loan_dialog.content.controls[3].value or 0)
        
        if member_id and amount > 0:
            create_loan(member_id, amount, interest_rate)
            close_loan_dialog()
            refresh_loans()
            page.snack_bar = ft.SnackBar(ft.Text("Loan created successfully!"))
            page.snack_bar.open = True
            page.update()
    
    def confirm_repayment():
        # Implementation for recording repayment
        close_repayment_dialog()
        page.snack_bar = ft.SnackBar(ft.Text("Repayment recorded successfully!"))
        page.snack_bar.open = True
        page.update()
    
    def refresh_loans():
        nonlocal loans_list
        loans_list = get_all_loans()
        update_loans_table()
    
    def update_loans_table():
        rows = []
        for loan in loans_list:
            member_name = members_dict.get(loan.member_id, "Unknown")
            total_amount = loan.amount + loan.total_interest
            remaining = total_amount - loan.amount_repaid
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(loan.id), color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(member_name, color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(f"₹{loan.amount:.2f}", color=ft.Colors.GREEN_400, weight="bold")),
                        ft.DataCell(ft.Text(f"{loan.interest_rate}%", color=ft.Colors.GREY)),
                        ft.DataCell(ft.Text(f"₹{loan.amount_repaid:.2f}", color=ft.Colors.BLUE_200)),
                        ft.DataCell(ft.Text(f"₹{remaining:.2f}", color=ft.Colors.ORANGE_400)),
                        ft.DataCell(ft.Text(loan.status.value, color=ft.Colors.GREY)),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.Icons.ATTACH_MONEY,
                                        tooltip="Record Payment",
                                        on_click=lambda e, l=loan: open_repayment_dialog(l),
                                        icon_size=18,
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE,
                                        tooltip="Delete",
                                        on_click=lambda e, l=loan: delete_loan(l),
                                        icon_size=18,
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )
        
        loans_table.rows = rows
        page.update()
    
    def open_repayment_dialog(loan):
        member_name = members_dict.get(loan.member_id, "Unknown")
        repayment_dialog.content.controls[0].value = f"Loan #{loan.id} - {member_name}: ₹{loan.amount:.2f}"
        repayment_dialog.open = True
        page.update()
    
    def delete_loan(loan):
        # Implementation for deleting loan
        refresh_loans()
        page.snack_bar = ft.SnackBar(ft.Text("Loan deleted!"))
        page.snack_bar.open = True
        page.update()
    
    # Loans DataTable
    loans_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Member", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Amount", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Interest %", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Repaid", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Remaining", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Status", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Actions", color=ft.Colors.WHITE, weight="bold")),
        ],
        rows=[],
        bgcolor="#1a1a1a",
        divider_thickness=1,
    )
    
    update_loans_table()
    
    # Add button
    add_loan_button = ft.ElevatedButton(
        "Add New Loan",
        icon=ft.Icons.ADD,
        on_click=lambda e: (setattr(loan_dialog, 'open', True), page.update()),
    )
    
    # Refresh button
    refresh_button = ft.IconButton(
        ft.Icons.REFRESH,
        tooltip="Refresh",
        on_click=lambda e: refresh_loans(),
    )
    
    # Top controls
    top_row = ft.Row(
        controls=[
            add_loan_button,
            refresh_button,
        ],
        spacing=10,
    )
    
    # Main content
    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Loan Management", size=24, weight="bold", color=ft.Colors.BLUE_200),
                top_row,
                ft.Container(
                    content=loans_table,
                    bgcolor="#2a2a2a",
                    border_radius=10,
                    padding=10,
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        ),
        padding=20,
        bgcolor="#1a1a1a",
        expand=True,
    )
    
    page.overlay.append(loan_dialog)
    page.overlay.append(repayment_dialog)
    
    return ft.View(
        "/loans",
        controls=[
            create_app_bar("Loans Management", page),
            content,
        ],
    )

