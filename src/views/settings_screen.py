import flet as ft
from components.navigation import create_app_bar
from database.connection import init_db
from datetime import datetime
import os
import csv


def SettingsScreen(page: ft.Page):
    """Settings screen with backup, export, and app info"""
    
    # Export status text
    export_status = ft.Text("No export in progress", size=12, color=ft.Colors.GREY)
    
    def export_to_csv():
        """Export data to CSV files"""
        try:
            from database.connection import (
                get_all_members,
                get_all_loans,
                get_all_contributions,
            )
            
            # Create exports folder if not exists
            exports_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
            os.makedirs(exports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export members
            members = get_all_members()
            members_file = os.path.join(exports_dir, f"members_{timestamp}.csv")
            with open(members_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Contact", "Email", "Status", "Join Date"])
                for m in members:
                    writer.writerow([
                        m.id, m.name, m.contact or "", m.email or "",
                        m.status.value, m.join_date.strftime("%Y-%m-%d")
                    ])
            
            # Export loans
            loans = get_all_loans()
            loans_file = os.path.join(exports_dir, f"loans_{timestamp}.csv")
            with open(loans_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Member ID", "Amount", "Interest %", "Repaid", "Status", "Start Date"
                ])
                for l in loans:
                    writer.writerow([
                        l.id, l.member_id, l.amount, l.interest_rate,
                        l.amount_repaid, l.status.value, l.start_date.strftime("%Y-%m-%d")
                    ])
            
            # Export contributions
            contributions = get_all_contributions()
            contrib_file = os.path.join(exports_dir, f"contributions_{timestamp}.csv")
            with open(contrib_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Member ID", "Amount", "Type", "Date", "Month"
                ])
                for c in contributions:
                    writer.writerow([
                        c.id, c.member_id, c.amount, c.contribution_type.value,
                        c.contribution_date.strftime("%Y-%m-%d"), c.month or ""
                    ])
            
            export_status.value = f"✓ Exported successfully to {exports_dir}"
            export_status.color = ft.Colors.GREEN_700
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Data exported to {exports_dir}")
            )
            page.snack_bar.open = True
            
        except Exception as e:
            export_status.value = f"✗ Export failed: {str(e)}"
            export_status.color = ft.Colors.RED_700
            page.snack_bar = ft.SnackBar(ft.Text(f"Export failed: {str(e)}"))
            page.snack_bar.open = True
        
        page.update()
    
    def reset_database():
        """Reset database with confirmation"""
        
        def confirm_reset(e):
            init_db()
            confirm_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Database reset successfully!"))
            page.snack_bar.open = True
            page.update()
        
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Reset Database"),
            content=ft.Text(
                "Are you sure? This will delete all data and create a fresh database."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: (
                    setattr(confirm_dialog, 'open', False),
                    page.update()
                )),
                ft.TextButton("Reset", on_click=confirm_reset),
            ],
        )
        
        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()
    
    # Settings cards
    data_management_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Data Management", size=16, weight="bold", color=ft.Colors.BLUE_200),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Export Data", size=12, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Download all data as CSV files for backup or analysis",
                                    size=11,
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
                export_status,
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Reset Database", size=12, weight="bold", color=ft.Colors.WHITE),
                                ft.Text(
                                    "Delete all data and reset to fresh database",
                                    size=11,
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
                ft.Text("About", size=16, weight="bold", color=ft.Colors.BLUE_200),
                ft.Divider(),
                ft.Text("Loan & Contribution Management System", size=14, weight="bold", color=ft.Colors.WHITE),
                ft.Text("Version 1.0.0", size=12, color=ft.Colors.GREY),
                ft.Divider(),
                ft.Text(
                    "An offline, single-user desktop application for managing member contributions and loan lifecycles with ease and transparency.",
                    size=11,
                    color=ft.Colors.GREY,
                ),
                ft.Divider(),
                ft.Text("Technology Stack:", weight="bold", color=ft.Colors.WHITE),
                ft.Text("• Frontend: Flet (Flutter for Python)", size=11, color=ft.Colors.GREY),
                ft.Text("• Database: SQLite", size=11, color=ft.Colors.GREY),
                ft.Text("• ORM: SQLAlchemy", size=11, color=ft.Colors.GREY),
            ],
            spacing=10,
        ),
        padding=20,
        bgcolor="#2a2a2a",
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
    )
    
    # Main content
    content = ft.Column(
        controls=[
            ft.Text("Settings", size=24, weight="bold", color=ft.Colors.BLUE_200),
            ft.Text("Manage your application and data", size=12, color=ft.Colors.GREY),
            ft.Container(height=20),
            data_management_card,
            app_info_card,
        ],
        spacing=20,
        padding=20,
        expand=True,
    )
    
    return ft.View(
        "/settings",
        controls=[
            create_app_bar("Settings", page),
            ft.Container(
                content=content,
                expand=True,
                bgcolor="#1a1a1a",
            ),
        ],
    )

