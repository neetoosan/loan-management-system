import flet as ft
from database.connection import (
    get_all_members,
    create_member,
    update_member,
    delete_member,
    get_contributions_by_member,
    get_loans_by_member,
)
from components.navigation import create_app_bar


def MemberScreen(page: ft.Page):
    """Members management screen with DataTable and dialogs"""
    
    # State management
    members_list = get_all_members()
    
    # Dialog for creating/editing member
    member_dialog = ft.AlertDialog(
        title=ft.Text("Add New Member"),
        content=ft.Column(
            controls=[
                ft.TextField(label="Full Name", width=400),
                ft.TextField(label="Contact Number", width=400),
                ft.TextField(label="Email Address", width=400),
                ft.Dropdown(
                    label="Status",
                    options=[
                        ft.dropdown.Option("Active", "Active"),
                        ft.dropdown.Option("Inactive", "Inactive"),
                        ft.dropdown.Option("Suspended", "Suspended"),
                    ],
                    value="Active",
                    width=400,
                ),
            ],
            width=500,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: close_member_dialog()),
            ft.TextButton("Save", on_click=lambda e: save_member()),
        ],
    )
    
    # Dialog for viewing member details
    details_dialog = ft.AlertDialog(
        title=ft.Text("Member Details"),
        content=ft.Column(
            controls=[
                ft.Text("", size=14, weight="bold"),  # Member name
                ft.Text("", size=12),  # Member info
                ft.Divider(),
                ft.Text("Contributions", weight="bold"),
                ft.Text("", size=12),  # Contributions info
                ft.Divider(),
                ft.Text("Active Loans", weight="bold"),
                ft.Text("", size=12),  # Loans info
            ],
            width=500,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Close", on_click=lambda e: close_details_dialog()),
        ],
    )
    
    def close_member_dialog():
        member_dialog.open = False
        page.update()
    
    def close_details_dialog():
        details_dialog.open = False
        page.update()
    
    def save_member():
        name = member_dialog.content.controls[0].value
        contact = member_dialog.content.controls[1].value
        email = member_dialog.content.controls[2].value
        status = member_dialog.content.controls[3].value or "Active"
        
        if name:
            create_member(name, contact or None, email or None, status)
            close_member_dialog()
            refresh_members()
            page.snack_bar = ft.SnackBar(ft.Text("Member added successfully!"))
            page.snack_bar.open = True
            page.update()
    
    def refresh_members():
        nonlocal members_list
        members_list = get_all_members()
        update_members_table()
    
    def update_members_table():
        rows = []
        for member in members_list:
            contributions = get_contributions_by_member(member.id)
            loans = get_loans_by_member(member.id)
            total_contrib = sum(c.amount for c in contributions)
            active_loans = sum(1 for l in loans if l.status.value == "Active")
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(member.name, color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(member.contact or "N/A", color=ft.Colors.GREY)),
                        ft.DataCell(ft.Text(member.email or "N/A", color=ft.Colors.GREY)),
                        ft.DataCell(ft.Text(member.status.value, color=ft.Colors.GREEN_400 if member.status.value == "Active" else ft.Colors.ORANGE_400)),
                        ft.DataCell(ft.Text(f"₹{total_contrib:.2f}", color=ft.Colors.GREEN_400, weight="bold")),
                        ft.DataCell(ft.Text(str(active_loans), color=ft.Colors.ORANGE_400)),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.Icons.VISIBILITY,
                                        tooltip="View Details",
                                        on_click=lambda e, m=member: view_member_details(m),
                                        icon_size=18,
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE,
                                        tooltip="Delete",
                                        on_click=lambda e, m=member: delete_member_record(m),
                                        icon_size=18,
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )
        
        members_table.rows = rows
        page.update()
    
    def view_member_details(member):
        contributions = get_contributions_by_member(member.id)
        loans = get_loans_by_member(member.id)
        
        total_contrib = sum(c.amount for c in contributions)
        loan_info = f"Total: {len(loans)}, Active: {sum(1 for l in loans if l.status.value == 'Active')}"
        
        details_dialog.content.controls[0].value = member.name
        details_dialog.content.controls[1].value = f"Contact: {member.contact or 'N/A'} | Email: {member.email or 'N/A'}"
        details_dialog.content.controls[3].value = f"Total Contributions: ₹{total_contrib:.2f}"
        details_dialog.content.controls[5].value = loan_info
        
        details_dialog.open = True
        page.update()
    
    def delete_member_record(member):
        delete_member(member.id)
        refresh_members()
        page.snack_bar = ft.SnackBar(ft.Text("Member deleted!"))
        page.snack_bar.open = True
        page.update()
    
    # Members DataTable
    members_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Contact", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Email", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Status", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Total Contributions", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Active Loans", color=ft.Colors.WHITE, weight="bold")),
            ft.DataColumn(ft.Text("Actions", color=ft.Colors.WHITE, weight="bold")),
        ],
        rows=[],
        bgcolor="#1a1a1a",
        divider_thickness=1,
    )
    
    update_members_table()
    
    # Add button
    add_member_button = ft.ElevatedButton(
        "Add Member",
        icon=ft.Icons.ADD,
        on_click=lambda e: (
            setattr(member_dialog.title, "value", "Add New Member"),
            # Clear fields
            [setattr(member_dialog.content.controls[i], "value", "") for i in range(3)],
            setattr(member_dialog.content.controls[3], "value", "Active"),
            setattr(member_dialog, 'open', True),
            page.update()
        ),
    )
    
    # Refresh button
    refresh_button = ft.IconButton(
        ft.Icons.REFRESH,
        tooltip="Refresh",
        on_click=lambda e: refresh_members(),
    )
    
    # Top controls
    top_row = ft.Row(
        controls=[
            add_member_button,
            refresh_button,
        ],
        spacing=10,
    )
    
    # Main content
    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Member Management", size=24, weight="bold", color=ft.Colors.BLUE_200),
                top_row,
                ft.Container(
                    content=members_table,
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
    
    page.overlay.append(member_dialog)
    page.overlay.append(details_dialog)
    
    return ft.View(
        "/members",
        controls=[
            create_app_bar("Member Management", page),
            content,
        ],
    )

