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
from components.burger_menu import create_burger_menu, create_sidebar_overlay
from components.magnified_chart import show_magnified_chart
from components.responsive import (
    ResponsiveConfig, 
    get_responsive_padding,
    get_responsive_font_size
)
from datetime import datetime, timedelta
from components.overdue_loans_dialog import show_overdue_loans_dialog


def navigate_to(page: ft.Page, route: str):
    """Navigate to a different route (replaces deprecated page.go)"""
    page.route = route
    page.update()


def create_summary_card(title: str, value: str, icon: str, color: str = ft.Colors.BLUE_200):
    """Create a summary card for dashboard statistics"""
    # Use smaller font for long values to prevent overflow
    value_size = 18 if len(str(value)) > 14 else 22 if len(str(value)) > 10 else 24
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icon, size=38, color=color),
                ft.Container(height=8),
                ft.Text(value, size=value_size, weight="bold", color=ft.Colors.WHITE, no_wrap=True),
                ft.Text(title, size=13, color=ft.Colors.GREY, weight="w400"),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor="#252525",
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=12, vertical=16),
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK, spread_radius=0),
        height=140,
        width=210,
    )


def get_contribution_trend_data(contributions=None):
    """Get contribution data for the last 12 months for line chart"""
    if contributions is None:
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


def get_loan_trend_data(loans=None):
    """Get loan data for the last 12 months for bar chart"""
    if loans is None:
        loans = get_all_loans()
    
    # Group by month
    monthly_data = {}
    for loan in loans:
        month_key = loan.start_date.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = 0
        monthly_data[month_key] += loan.amount
    
    # Sort by month
    sorted_months = sorted(monthly_data.keys())[-12:]  # Last 12 months
    values = [monthly_data.get(month, 0) for month in sorted_months]
    
    return sorted_months, values


def get_total_interest(loans=None):
    """Calculate total interest from all loans"""
    if loans is None:
        loans = get_all_loans()
    return sum(loan.total_interest for loan in loans)


def get_total_interest_last_12_months(loans=None):
    """Calculate total interest from loans created in the last 12 months"""
    if loans is None:
        loans = get_all_loans()
    cutoff = datetime.now() - timedelta(days=365)
    return sum(loan.total_interest for loan in loans if loan.start_date and loan.start_date >= cutoff)


def get_overdue_loans(loans=None):
    """Get list of overdue loans"""
    if loans is None:
        loans = get_all_loans()
    overdue_loans = []
    today = datetime.now()
    
    for loan in loans:
        if loan.end_date and loan.end_date < today and loan.status.value != "Paid":
            # Calculate balance
            balance = max(0, (loan.amount + loan.total_interest + (getattr(loan, "overdue_penalty", 0.0) or 0.0)) - loan.amount_repaid)
            if balance > 0:
                overdue_loans.append({
                    "id": loan.id,
                    "amount": loan.amount,
                    "balance": balance,
                    "end_date": loan.end_date,
                    "days_overdue": (today - loan.end_date).days,
                })
    
    return sorted(overdue_loans, key=lambda x: x["days_overdue"], reverse=True)


def get_top_contributors(members=None, contributions=None, limit=5):
    """Get top N highest contributors"""
    if members is None:
        members = get_all_members()
    if contributions is None:
        contributions = get_all_contributions()
    
    # Build member name lookup dict (O(1) lookups instead of O(N) scans)
    members_dict = {m.id: m.name for m in members}
    
    # Group by member in single pass
    member_totals = {}
    for contrib in contributions:
        if contrib.member_id not in member_totals:
            member_totals[contrib.member_id] = 0
        member_totals[contrib.member_id] += contrib.amount
    
    # Get member names using dict lookup
    data = []
    for member_id, total in member_totals.items():
        name = members_dict.get(member_id)
        if name:
            data.append((name, total))
    
    # Sort by total contribution descending and return top N
    return sorted(data, key=lambda x: x[1], reverse=True)[:limit]


def get_interest_trend_data(loans=None):
    """Get interest data for the last 12 months"""
    if loans is None:
        loans = get_all_loans()
    
    # Group by month (using start date)
    monthly_interest = {}
    for loan in loans:
        month_key = loan.start_date.strftime("%Y-%m")
        if month_key not in monthly_interest:
            monthly_interest[month_key] = 0
        monthly_interest[month_key] += loan.total_interest
    
    # Sort by month
    sorted_months = sorted(monthly_interest.keys())[-12:]  # Last 12 months
    values = [monthly_interest.get(month, 0) for month in sorted_months]
    
    return sorted_months, values


def _fmt_month(month_key):
    """Convert '2025-03' → 'Mar 25'"""
    try:
        dt = datetime.strptime(month_key, "%Y-%m")
        return dt.strftime("%b %y")
    except Exception:
        return month_key


def MainWindow(page: ft.Page):
    """Main dashboard screen with charts and statistics"""
    print(">>> MainWindow function started")
    
    # Responsive configuration
    is_small_screen = ResponsiveConfig.is_small_screen(page)
    
    # ===== LOAD ALL DATA ONCE =====
    _all_loans = get_all_loans()
    _all_contributions = get_all_contributions()
    _all_members = get_all_members()
    
    # Summary statistics (scalar queries are fast, keep them)
    total_members = str(get_total_members())
    total_contributions = f"₦{get_total_contributions():.2f}"
    total_loans = f"₦{get_total_loans_issued():.2f}"
    active_loans = str(get_active_loans_count())
    total_interest = f"₦{get_total_interest(_all_loans):.2f}"
    overdue_loans = str(len(get_overdue_loans(_all_loans)))
    
    # Create responsive summary cards
    # Create the overdue card separately so it can be clickable
    overdue_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.WARNING, size=38, color=ft.Colors.RED_600),
                ft.Container(height=8),
                ft.Text(overdue_loans, size=26, weight="bold", color=ft.Colors.WHITE),
                ft.Text("Overdue Loans", size=13, color=ft.Colors.GREY, weight="w400"),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor="#252525",
        border_radius=12,
        padding=16,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK, spread_radius=0),
        height=140,
        width=200,
        on_click=lambda _: show_overdue_loans_dialog(page),
        ink=True,
        tooltip="Click to view overdue loans",
    )

    summary_cards = [
        create_summary_card("Total Members", total_members, ft.Icons.PEOPLE, ft.Colors.BLUE_200),
        create_summary_card("Total Contributions", total_contributions, ft.Icons.SAVINGS, ft.Colors.GREEN_400),
        create_summary_card("Total Loans Issued", total_loans, ft.Icons.ATTACH_MONEY, ft.Colors.ORANGE_400),
        create_summary_card("Active Loans", active_loans, ft.Icons.TRENDING_UP, ft.Colors.RED_400),
        create_summary_card("Total Interest", total_interest, ft.Icons.PERCENT, ft.Colors.PURPLE_400),
        overdue_card,
    ]
    
    # Create responsive row for summary cards
    if is_small_screen:
        summary_row = ft.Column(
            controls=summary_cards,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )
    else:
        summary_row = ft.Row(
            controls=summary_cards,
            spacing=15,
            wrap=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    # Contribution Trend Line Chart
    months_contrib, values_contrib = get_contribution_trend_data(_all_contributions)
    chart_height = ResponsiveConfig.get_chart_height(page)
    
    # Create a line chart visualization for contribution trends
    if months_contrib and values_contrib:
        max_contrib = max(values_contrib) if values_contrib else 1
        
        # Create data points display
        line_points = []
        for i, (month, value) in enumerate(zip(months_contrib, values_contrib)):
            line_points.append({
                'month': month,
                'value': value,
                'index': i
            })
        
        # Build the visual line chart
        line_chart_controls = []
        
        # Create area/bar visualization
        chart_items = []
        for point in line_points:
            bar_height = min((point['value'] / max_contrib * 150), 150) if max_contrib > 0 else 5
            chart_items.append(
                ft.Column([
                    ft.Container(
                        height=int(bar_height),
                        width=35,
                        bgcolor=ft.Colors.GREEN_400,
                        border_radius=3,
                    ),
                    ft.Text(_fmt_month(point['month']), size=10, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"₦{point['value']:.0f}", size=10, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        # Create visual chart row
        visual_chart = ft.Row(
            controls=chart_items,
            spacing=3,
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=False,
            scroll=ft.ScrollMode.AUTO,
        )
        
        contribution_chart = ft.Container(
            content=ft.Column([
                ft.Text("Contribution Trends (Last 12 Months)", size=16, weight="bold", color=ft.Colors.WHITE),
                ft.Container(height=10),
                visual_chart,
                ft.Container(height=10),
                ft.Divider(height=1, color=ft.Colors.GREY_800),
                ft.Container(height=5),
                ft.Text(f"Max: ₦{max_contrib:.0f} | Total: ₦{sum(values_contrib):.0f}", size=12, color=ft.Colors.GREY),
            ], spacing=5, expand=True),
            height=chart_height,
            expand=True,
            bgcolor="#252525",
            border_radius=12,
            padding=16,
        )
    else:
        contribution_chart = ft.Container(
            content=ft.Column([
                ft.Text("Contribution Trends", size=16, weight="bold", color=ft.Colors.WHITE),
                ft.Text("No data available", size=14, color=ft.Colors.GREY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            height=chart_height,
            expand=True,
            bgcolor="#252525",
            border_radius=12,
            padding=16,
        )
    
    # Loan Trend Chart with actual data display
    months_loan, values_loan = get_loan_trend_data(_all_loans)
    
    if months_loan and values_loan:
        max_loan = max(values_loan) if values_loan else 1
        loan_bars = ft.Column([
            ft.Row([
                ft.Text(_fmt_month(month), size=12, color=ft.Colors.GREY, width=60),
                ft.Container(
                    height=20,
                    width=min((value / max_loan) * 200, 200) if max_loan > 0 else 1,
                    bgcolor=ft.Colors.ORANGE_400,
                    border_radius=3,
                ),
                ft.Text(f"₦{value:.0f}", size=12, color=ft.Colors.WHITE, width=100),
            ], spacing=10, alignment=ft.MainAxisAlignment.START)
            for month, value in zip(months_loan, values_loan)
        ], spacing=8)
        
        loan_chart = ft.Container(
            content=ft.Column([
                ft.Text("Loan Trends (Last 12 Months)", size=16, weight="bold", color=ft.Colors.WHITE),
                ft.Container(height=10),
                ft.Container(
                    content=loan_bars,
                    expand=True,
                    padding=10,
                )
            ], expand=True),
            height=chart_height,
            expand=True,
            bgcolor="#252525",
            border_radius=12,
            padding=16,
        )
    else:
        loan_chart = ft.Container(
            content=ft.Column([
                ft.Text("Loan Trends", size=16, weight="bold", color=ft.Colors.WHITE),
                ft.Text("No data available", size=14, color=ft.Colors.GREY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            height=chart_height,
            expand=True,
            bgcolor="#252525",
            border_radius=12,
            padding=16,
        )
    
    # Overdue Loans Table (Bottom Right)
    overdue_loans_data = get_overdue_loans(_all_loans)
    overdue_rows = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(f"#{loan['id']}", size=13, color=ft.Colors.BLUE_200, weight="bold")),
                ft.DataCell(ft.Text(f"₦{loan['amount']:.2f}", size=13, color=ft.Colors.WHITE)),
                ft.DataCell(ft.Text(f"₦{loan['balance']:.2f}", size=13, color=ft.Colors.RED_400, weight="bold")),
                ft.DataCell(ft.Text(f"{loan['days_overdue']} days", size=13, color=ft.Colors.ORANGE_400)),
            ]
        )
        for loan in overdue_loans_data[:10]  # Show top 10 overdue loans
    ]
    
    overdue_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Loan ID", weight="bold", color=ft.Colors.WHITE, size=13)),
            ft.DataColumn(ft.Text("Amount", weight="bold", color=ft.Colors.WHITE, size=13)),
            ft.DataColumn(ft.Text("Balance Due", weight="bold", color=ft.Colors.WHITE, size=13)),
            ft.DataColumn(ft.Text("Days Overdue", weight="bold", color=ft.Colors.WHITE, size=13)),
        ],
        rows=overdue_rows,
        bgcolor="#2a2a2a",
        height=300,
    ) if overdue_loans_data else ft.Container(
        content=ft.Column(
            controls=[ft.Text("No overdue loans", color=ft.Colors.GREY, size=16)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        height=300,
        bgcolor="#2a2a2a",
        border_radius=10,
    )
    
    # Top 5 Contributors Container
    top_contributors = get_top_contributors(_all_members, _all_contributions, 5)
    contributor_rows = []
    
    if top_contributors:
        for rank, (name, total) in enumerate(top_contributors, 1):
            contributor_rows.append(
                ft.Row([
                    ft.Text(f"{rank}", size=14, color=ft.Colors.BLUE_200, weight="bold", width=30),
                    ft.Text(name, size=13, color=ft.Colors.WHITE, expand=True),
                    ft.Text(f"₦{total:.2f}", size=13, color=ft.Colors.GREEN_400, weight="bold", width=120),
                ], spacing=10)
            )
    
    top_contributors_container = ft.Container(
        content=ft.Column([
            ft.Text("Top 5 Contributors", size=16, weight="bold", color=ft.Colors.WHITE),
            ft.Container(height=8),
            ft.Column(
                controls=contributor_rows if contributor_rows else [
                    ft.Text("No contributors yet", color=ft.Colors.GREY, size=14)
                ],
                spacing=8
            )
        ], spacing=5, expand=True),
        height=250,
        expand=True,
        bgcolor="#252525",
        border_radius=12,
        padding=16,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK, spread_radius=1),
    )
    
    # Interest Trend Chart
    months_interest, values_interest = get_interest_trend_data(_all_loans)
    
    if months_interest and values_interest:
        max_interest = max(values_interest) if values_interest else 1
        
        # Create interest chart items
        interest_items = []
        for month, value in zip(months_interest, values_interest):
            bar_height = min((value / max_interest * 120), 120) if max_interest > 0 else 5
            interest_items.append(
                ft.Column([
                    ft.Container(
                        height=int(bar_height),
                        width=30,
                        bgcolor=ft.Colors.PURPLE_400,
                        border_radius=3,
                    ),
                    ft.Text(_fmt_month(month), size=9, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"₦{value:.0f}", size=9, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        # Create visual interest chart row
        visual_interest_chart = ft.Row(
            controls=interest_items,
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=False,
            scroll=ft.ScrollMode.AUTO,
        )
        
        interest_chart = ft.Container(
            content=ft.Column([
                ft.Text("Interest Trends (Last 12 Months)", size=16, weight="bold", color=ft.Colors.WHITE),
                ft.Text("Click to expand", size=11, color=ft.Colors.BLUE_200, italic=True),
                ft.Container(height=8),
                visual_interest_chart,
                ft.Container(height=8),
                ft.Text(f"Last 12 Months: \u20a6{sum(values_interest):,.2f}", size=12, color=ft.Colors.GREY),
                ft.Text(f"All Time: \u20a6{get_total_interest(_all_loans):,.2f}", size=12, color=ft.Colors.PURPLE_200),
            ], spacing=5, expand=True),
            height=250,
            expand=True,
            bgcolor="#252525",
            border_radius=12,
            padding=16,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK, spread_radius=1),
            on_click=lambda e: show_magnified_chart(page, "Interest Trends (Last 12 Months)", "interest", values_interest, months_interest),
        )
    else:
        interest_chart = ft.Container(
            content=ft.Column([
                ft.Text("Interest Trends", size=16, weight="bold", color=ft.Colors.WHITE),
                ft.Text("No interest data available", size=14, color=ft.Colors.GREY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            height=250,
            expand=True,
            bgcolor="#252525",
            border_radius=12,
            padding=16,
        )
    
    # Charts container - Responsive layout
    if is_small_screen:
        # Mobile/Tablet: Stack charts vertically
        charts_row = ft.Column(
            controls=[
                # Contribution chart
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Contribution Trend (Last 12 Months)", size=16, weight="bold", color=ft.Colors.WHITE),
                            ft.Text("Click to expand", size=11, color=ft.Colors.BLUE_200, italic=True),
                            ft.Container(height=10),
                            contribution_chart,
                        ],
                        spacing=0,
                    ),
                    expand=True,
                    border_radius=12,
                    padding=20,
                    bgcolor="#252525",
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK, spread_radius=1),
                    on_click=lambda e: show_magnified_chart(page, "Contribution Trend (Last 12 Months)", "pie", values_contrib, months_contrib),
                ),
                ft.Container(height=15),
                # Loan chart
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Loan Trend (Last 12 Months)", size=16, weight="bold", color=ft.Colors.WHITE),
                            ft.Text("Click to expand", size=11, color=ft.Colors.BLUE_200, italic=True),
                            ft.Container(height=10),
                            loan_chart,
                        ],
                        spacing=0,
                    ),
                    expand=True,
                    border_radius=12,
                    padding=20,
                    bgcolor="#252525",
                    shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK, spread_radius=1),
                    on_click=lambda e: show_magnified_chart(page, "Loan Trend (Last 12 Months)", "bar", values_loan, months_loan),
                ),
            ],
            expand=True,
            spacing=10,
        )
    else:
        # Desktop: Side by side
        charts_row = ft.Row(
            controls=[
                # Contribution chart
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Contribution Trend (Last 12 Months)", size=19, weight="bold", color=ft.Colors.WHITE),
                            ft.Text("Click to expand", size=12, color=ft.Colors.BLUE_200, italic=True),
                            ft.Container(height=15),
                            contribution_chart,
                        ],
                        spacing=0,
                    ),
                    expand=True,
                    border_radius=15,
                    padding=30,
                    bgcolor="#252525",
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK, spread_radius=1),
                    on_click=lambda e: show_magnified_chart(page, "Contribution Trend (Last 12 Months)", "pie", values_contrib, months_contrib),
                ),
                ft.Container(width=20),
                # Loan chart
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Loan Trend (Last 12 Months)", size=19, weight="bold", color=ft.Colors.WHITE),
                            ft.Text("Click to expand", size=12, color=ft.Colors.BLUE_200, italic=True),
                            ft.Container(height=15),
                            loan_chart,
                        ],
                        spacing=0,
                    ),
                    expand=True,
                    border_radius=15,
                    padding=30,
                    bgcolor="#252525",
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK, spread_radius=1),
                    on_click=lambda e: show_magnified_chart(page, "Loan Trend (Last 12 Months)", "bar", values_loan, months_loan),
                ),
            ],
            expand=True,
            spacing=0,
        )
    
    # Main content
    padding = get_responsive_padding(page)
    
    dashboard_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Dashboard", size=get_responsive_font_size(page, 32), weight="bold", color=ft.Colors.BLUE_200),
                            ft.Text("Welcome to Morning Star Cooperative Management System", size=get_responsive_font_size(page, 13), color=ft.Colors.GREY),
                        ],
                        spacing=5,
                    ),
                ),
                ft.Container(height=15),
                # Summary cards section
                ft.Container(
                    content=summary_row,
                    expand=False,
                ),
                ft.Container(height=20),
                # Charts section
                ft.Container(
                    content=charts_row,
                    expand=True,
                ),
                ft.Container(height=20),
                # Top Contributors and Interest Trends Row
                ft.Row(
                    controls=[
                        top_contributors_container,
                        interest_chart,
                    ],
                    spacing=20,
                    expand=True,
                ) if not is_small_screen else ft.Column(
                    controls=[
                        top_contributors_container,
                        ft.Container(height=15),
                        interest_chart,
                    ],
                    spacing=10,
                    expand=True,
                ),
            ],
            spacing=0,
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
        title=ft.Text("Loan & Contribution Manager - Dashboard", size=22, weight="bold", color=ft.Colors.WHITE),
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
        route="/dashboard",
        controls=[
            app_bar,
            ft.Stack(
                controls=[
                    dashboard_content,
                    backdrop,
                    sidebar_wrapper,
                ],
                expand=True,
            ),
        ],
    )
