import flet as ft
from database.connection import (
    get_total_contributions,
    get_total_loans_issued,
    get_active_loans_count,
    get_total_members,
    get_all_contributions,
    get_repayments_by_loan,
    get_all_loans,
    get_all_members,
)
from components.navigation import create_app_bar
from datetime import datetime, timedelta


def create_summary_card(title: str, value: str, icon: str, color: str = ft.Colors.BLUE_200):
    """Create a summary card for dashboard statistics"""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(name=icon, size=40, color=color),
                ft.Text(value, size=28, weight="bold", color=ft.Colors.WHITE),
                ft.Text(title, size=12, color=ft.Colors.GREY),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#1a1a1a",
        border_radius=10,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
    )


def get_contribution_trend_data():
    """Get contribution data for the last 12 months for line chart"""
    contributions = get_all_contributions()
    
    # Group by month
    monthly_data = {}
    for contrib in contributions:
        month_key = contrib.contribution_date.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = 0
        monthly_data[month_key] += contrib.amount
    
    # Sort by month
    sorted_months = sorted(monthly_data.keys())[-12:]  # Last 12 months
    values = [monthly_data.get(month, 0) for month in sorted_months]
    
    return sorted_months, values


def get_member_contribution_data():
    """Get contribution breakdown by member for pie chart"""
    members = get_all_members()
    contributions = get_all_contributions()
    
    # Group by member
    member_totals = {}
    for contrib in contributions:
        if contrib.member_id not in member_totals:
            member_totals[contrib.member_id] = 0
        member_totals[contrib.member_id] += contrib.amount
    
    # Get member names
    data = []
    for member_id, total in member_totals.items():
        member = next((m for m in members if m.id == member_id), None)
        if member:
            data.append((member.name, total))
    
    return data


def get_recent_activities():
    """Get recent activities for the activity table"""
    activities = []
    
    # Get recent contributions
    contributions = get_all_contributions()
    for contrib in sorted(contributions, key=lambda x: x.created_at, reverse=True)[:5]:
        activities.append({
            "type": "Contribution",
            "member_id": contrib.member_id,
            "amount": f"₹{contrib.amount:.2f}",
            "date": contrib.contribution_date.strftime("%Y-%m-%d"),
            "description": f"Contribution recorded"
        })
    
    # Get recent repayments
    loans = get_all_loans()
    for loan in loans:
        repayments = get_repayments_by_loan(loan.id)
        for repay in sorted(repayments, key=lambda x: x.created_at, reverse=True)[:5]:
            activities.append({
                "type": "Repayment",
                "member_id": loan.member_id,
                "amount": f"₹{repay.amount_paid:.2f}",
                "date": repay.payment_date.strftime("%Y-%m-%d"),
                "description": f"Loan repayment"
            })
    
    # Sort by date and return top 10
    return sorted(activities, key=lambda x: x["date"], reverse=True)[:10]


def MainWindow(page: ft.Page):
    """Main dashboard screen with charts and statistics"""
    
    # State for sidebar visibility
    sidebar_visible = {"value": False}
    
    # Create sidebar navigation
    def create_nav_item(label: str, icon: str, route: str):
        def on_click(e):
            sidebar_visible["value"] = False
            sidebar.visible = False
            page.go(route)
            page.update()
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=24, color=ft.Colors.BLUE_200),
                    ft.Text(label, size=16, color=ft.Colors.WHITE, weight="bold"),
                ],
                spacing=15,
            ),
            padding=15,
            on_click=on_click,
        )
    
    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Menu", size=20, weight="bold", color=ft.Colors.BLUE_200),
                            ft.IconButton(
                                ft.Icons.CLOSE,
                                icon_size=24,
                                on_click=lambda e: (
                                    sidebar_visible.update({"value": False}),
                                    setattr(sidebar, "visible", False),
                                    page.update()
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=15,
                ),
                ft.Divider(height=1),
                create_nav_item("Dashboard", ft.Icons.DASHBOARD, "/dashboard"),
                create_nav_item("Members", ft.Icons.PEOPLE, "/members"),
                create_nav_item("Loans", ft.Icons.ATTACH_MONEY, "/loans"),
                create_nav_item("Contributions", ft.Icons.SAVINGS, "/contributions"),
                create_nav_item("Settings", ft.Icons.SETTINGS, "/settings"),
                ft.Divider(height=1),
                create_nav_item("Logout", ft.Icons.LOGOUT, "/login"),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=250,
        bgcolor="#2a2a2a",
        visible=False,
        expand_loose=True,
    )
    
    # Summary statistics
    total_members = str(get_total_members())
    total_contributions = f"₹{get_total_contributions():.2f}"
    total_loans = f"₹{get_total_loans_issued():.2f}"
    active_loans = str(get_active_loans_count())
    
    # Summary cards
    summary_row = ft.Row(
        controls=[
            create_summary_card(
                title="Total Members",
                value=total_members,
                icon=ft.Icons.PEOPLE,
                color=ft.Colors.BLUE_200,
            ),
            create_summary_card(
                title="Total Contributions",
                value=total_contributions,
                icon=ft.Icons.SAVINGS,
                color=ft.Colors.GREEN_400,
            ),
            create_summary_card(
                title="Total Loans Issued",
                value=total_loans,
                icon=ft.Icons.ATTACH_MONEY,
                color=ft.Colors.ORANGE_400,
            ),
            create_summary_card(
                title="Active Loans",
                value=active_loans,
                icon=ft.Icons.TRENDING_UP,
                color=ft.Colors.RED_400,
            ),
        ],
        wrap=True,
        spacing=20,
        run_spacing=20,
    )
    
    # Contribution Trend Line Chart
    months, values = get_contribution_trend_data()
    
    # Create a simple bar chart for contribution trends
    max_value = max(values) if values else 1
    bar_chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=v,
                        width=15,
                        color=ft.Colors.BLUE_200,
                        tooltip=f"₹{v:.0f}",
                    ),
                ],
            )
            for i, v in enumerate(values)
        ],
        border=ft.border.all(1, ft.Colors.GREY_700),
        left_axis=ft.ChartAxis(labels_size=40),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=i, label=ft.Text(month[-5:], size=10, color=ft.Colors.GREY_400))
                for i, month in enumerate(months)
            ],
            labels_size=40,
        ),
        animate=500,
        height=300,
        expand=True,
    )
    
    # Member Contribution Pie Chart
    member_data = get_member_contribution_data()
    pie_chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                value=amount,
                title=name[:15],  # Truncate long names
                color=ft.colors.random_color(),
            )
            for name, amount in member_data[:8]  # Limit to 8 slices
        ],
        animate=500,
        height=300,
        expand=True,
    )
    
    # Charts container
    charts_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Contribution Trend (Last 12 Months)", weight="bold", color=ft.Colors.WHITE),
                        bar_chart,
                    ]
                ),
                expand=1,
                border_radius=10,
                padding=20,
                bgcolor="#2a2a2a",
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Contributions by Member", weight="bold", color=ft.Colors.WHITE),
                        pie_chart,
                    ]
                ),
                expand=1,
                border_radius=10,
                padding=20,
                bgcolor="#2a2a2a",
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
            ),
        ],
        expand=True,
        spacing=20,
    )
    
    # Recent Activities Table
    activities = get_recent_activities()
    activity_rows = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(activity["type"], size=12, color=ft.Colors.WHITE)),
                ft.DataCell(ft.Text(activity["amount"], size=12, weight="bold", color=ft.Colors.GREEN_400)),
                ft.DataCell(ft.Text(activity["date"], size=12, color=ft.Colors.GREY)),
                ft.DataCell(ft.Text(activity["description"], size=12, color=ft.Colors.GREY)),
            ]
        )
        for activity in activities
    ]
    
    recent_activities_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Type", weight="bold", color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Amount", weight="bold", color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Date", weight="bold", color=ft.Colors.WHITE)),
            ft.DataColumn(ft.Text("Description", weight="bold", color=ft.Colors.WHITE)),
        ],
        rows=activity_rows,
        bgcolor="#2a2a2a",
    )
    
    recent_activities_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Recent Activities", size=16, weight="bold", color=ft.Colors.WHITE),
                recent_activities_table,
            ],
            spacing=10,
        ),
        padding=20,
        border_radius=10,
        bgcolor="#2a2a2a",
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK),
    )
    
    # Main content
    dashboard_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Dashboard", size=24, weight="bold", color=ft.Colors.BLUE_200),
                summary_row,
                charts_row,
                recent_activities_container,
            ],
            spacing=20,
            expand=True,
        ),
        padding=20,
        bgcolor="#1a1a1a",
        expand=True,
    )
    
    return ft.View(
        "/dashboard",
        controls=[
            ft.AppBar(
                title=ft.Text("Loan & Contribution Manager - Dashboard", size=20, weight="bold", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_900,
                leading=ft.IconButton(
                    ft.Icons.MENU,
                    on_click=lambda e: (
                        sidebar_visible.update({"value": not sidebar_visible["value"]}),
                        setattr(sidebar, "visible", sidebar_visible["value"]),
                        page.update()
                    ),
                ),
                actions=[
                    ft.IconButton(
                        ft.Icons.LOGOUT,
                        tooltip="Logout",
                        on_click=lambda _: page.go("/login"),
                    )
                ],
            ),
            ft.Row(
                controls=[
                    sidebar,
                    dashboard_content,
                ],
                spacing=0,
                expand=True,
            ),
        ],
    )