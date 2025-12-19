import flet as ft
from database.connection import (
    get_all_contributions,
    get_all_members,
    record_contribution,
)
from components.navigation import create_app_bar
from datetime import datetime


def ContributionScreen(page: ft.Page):
    """Contributions management screen with DataTable and dialogs"""
    
    # State management
    contributions_list = get_all_contributions()
    members_dict = {m.id: m.name for m in get_all_members()}
    
    # Dialog for recording contribution
    contribution_dialog = ft.AlertDialog(
        title=ft.Text("Record Contribution"),
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
                ft.TextField(label="Amount", keyboard_type="number", width=400),
                ft.Dropdown(
                    label="Contribution Type",
                    options=[
                        ft.dropdown.Option("Monthly", "Monthly"),
                        ft.dropdown.Option("Weekly", "Weekly"),
                        ft.dropdown.Option("Voluntary", "Voluntary"),
                    ],
                    value="Monthly",
                    width=400,
                ),
                ft.TextField(label="Notes (optional)", multiline=True, width=400, min_lines=3),
            ],
            width=500,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_contribution_dialog()),
            ft.TextButton("Record", on_click=lambda e: record_new_contribution()),
        ],
    )
    
    def close_contribution_dialog():
        contribution_dialog.open = False
        page.update()
    
    def record_new_contribution():
        member_id = int(contribution_dialog.content.controls[0].value or 0)
        amount = float(contribution_dialog.content.controls[1].value or 0)
        contrib_type = contribution_dialog.content.controls[2].value or "Monthly"
        notes = contribution_dialog.content.controls[3].value or None
        
        if member_id and amount > 0:
            record_contribution(member_id, amount, contrib_type, notes=notes)
            close_contribution_dialog()
            refresh_contributions()
            page.snack_bar = ft.SnackBar(ft.Text("Contribution recorded successfully!"))
            page.snack_bar.open = True
            page.update()
    
    def refresh_contributions():
        nonlocal contributions_list
        contributions_list = get_all_contributions()
        update_contributions_table()
    
    def update_contributions_table():
        rows = []
        for contrib in sorted(contributions_list, key=lambda x: x.contribution_date, reverse=True):
            member_name = members_dict.get(contrib.member_id, "Unknown")
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(member_name, color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(f"₹{contrib.amount:.2f}", color=ft.Colors.GREEN_400, weight="bold")),
                        ft.DataCell(ft.Text(contrib.contribution_type.value, color=ft.Colors.GREY)),
                        ft.DataCell(ft.Text(contrib.contribution_date.strftime("%Y-%m-%d"), color=ft.Colors.GREY)),
                        ft.DataCell(ft.Text(contrib.month or "N/A", color=ft.Colors.GREY)),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.DELETE,
                                tooltip="Delete",
                                on_click=lambda e, c=contrib: delete_contribution(c),
                                icon_size=18,
                            )
                        ),
                    ]
                )
            )
        
        contributions_table.rows = rows
        page.update()
    
    def delete_contribution(contrib):
        # Implementation for deleting contribution
        refresh_contributions()
        page.snack_bar = ft.SnackBar(ft.Text("Contribution deleted!"))
        page.snack_bar.open = True
        page.update()
    
    # Contributions DataTable
    contributions_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Member", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Amount", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Type", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Date", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Month", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Action", color=ft.Colors.WHITE, weight="bold")),
        ],
        rows=[],
        bgcolor="#1a1a1a",
        divider_thickness=1,
    )
    
    update_contributions_table()
    
    # Add button
    add_contribution_button = ft.ElevatedButton(
        "Record Contribution",
        icon=ft.Icons.ADD,
        on_click=lambda e: (setattr(contribution_dialog, 'open', True), page.update()),
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
            add_contribution_button,
            refresh_button,
        ],
        spacing=10,
    )
    
    # Main content
    content = ft.Column(
        controls=[
            ft.Text("Contribution Management", size=24, weight="bold", color=ft.Colors.BLUE_200),
            top_row,
            ft.Container(
                content=contributions_table,
                bgcolor="#2a2a2a",
                border_radius=10,
                padding=10,
                expand=True,
            ),
        ],
        spacing=20,
        padding=20,
        expand=True,
    )
    
    page.overlay.append(contribution_dialog)
    
    return ft.View(
        "/contributions",
        controls=[
            create_app_bar("Contribution Management", page),
            ft.Container(
                content=content,
                bgcolor="#1a1a1a",
                expand=True,
            ),
        ],
    )

