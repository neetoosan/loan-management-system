import flet as ft
from datetime import datetime


def _fmt(month_key):
    """Convert '2025-03' → 'Mar 25'"""
    try:
        dt = datetime.strptime(month_key, "%Y-%m")
        return dt.strftime("%b %y")
    except Exception:
        return month_key


def create_magnified_chart_view(page: ft.Page, chart_title: str, chart_type: str, data_points, months_labels):
    """
    Create a magnified/expanded view of a chart
    
    Args:
        page: Flet page object
        chart_title: Title of the chart
        chart_type: Type of chart ('pie', 'bar')
        data_points: List of data values
        months_labels: List of month labels for x-axis
    """
    
    if chart_type == "pie":
        # For "pie" type, show line/area chart (contribution trends)
        if data_points:
            max_value = max(data_points) if data_points else 1
            
            # Create bar chart visualization for line chart representation
            line_items = []
            
            for month, value in zip(months_labels, data_points):
                bar_height = (value / max_value * 300) if max_value > 0 else 0
                line_items.append(
                    ft.Row([
                        ft.Column([
                            ft.Container(
                                height=int(bar_height),
                                width=40,
                                bgcolor=ft.Colors.GREEN_400,
                                border_radius=3,
                            ),
                            ft.Text(_fmt(month), size=10, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                        ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=3)
                )
            
            expanded_chart = ft.Column([
                ft.Row(
                    controls=line_items,
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=False,
                    scroll=ft.ScrollMode.AUTO,
                )
            ], spacing=10, expand=True)
        else:
            expanded_chart = ft.Container(
                content=ft.Text("No data available", color=ft.Colors.GREY, size=14),
                alignment=ft.Alignment(0, 0),
            )
    
    elif chart_type == "bar":
        # Create a bar chart visualization
        if data_points:
            max_value = max(data_points) if data_points else 1
            bar_items = []
            
            for month, value in zip(months_labels, data_points):
                bar_width = (value / max_value * 400) if max_value > 0 else 0
                bar_items.append(
                    ft.Row([
                        ft.Text(_fmt(month), size=11, width=60, color=ft.Colors.GREY),
                        ft.Container(
                            height=25,
                            width=int(bar_width),
                            bgcolor=ft.Colors.ORANGE_400,
                            border_radius=3,
                        ),
                        ft.Text(f"₦{value:.0f}", size=11, width=120, color=ft.Colors.WHITE),
                    ], spacing=15, alignment=ft.MainAxisAlignment.START)
                )
            
            expanded_chart = ft.Column(
                controls=bar_items,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            expanded_chart = ft.Container(
                content=ft.Text("No data available", color=ft.Colors.GREY, size=14),
                alignment=ft.Alignment(0, 0),
            )
    
    elif chart_type == "interest":
        # Interest chart - horizontal bars in purple
        if data_points:
            max_value = max(data_points) if data_points else 1
            bar_items = []
            
            for month, value in zip(months_labels, data_points):
                bar_width = (value / max_value * 400) if max_value > 0 else 0
                bar_items.append(
                    ft.Row([
                        ft.Text(_fmt(month), size=11, width=60, color=ft.Colors.GREY),
                        ft.Container(
                            height=25,
                            width=int(bar_width),
                            bgcolor=ft.Colors.PURPLE_400,
                            border_radius=3,
                        ),
                        ft.Text(f"₦{value:.0f}", size=11, width=120, color=ft.Colors.WHITE),
                    ], spacing=15, alignment=ft.MainAxisAlignment.START)
                )
            
            total_interest = sum(data_points)
            expanded_chart = ft.Column(
                controls=bar_items + [
                    ft.Divider(height=1, color=ft.Colors.GREY_800),
                    ft.Text(f"Total Interest: ₦{total_interest:,.2f}", size=14, weight="bold", color=ft.Colors.PURPLE_200),
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            expanded_chart = ft.Container(
                content=ft.Text("No data available", color=ft.Colors.GREY, size=14),
                alignment=ft.Alignment(0, 0),
            )
    
    else:
        expanded_chart = ft.Container(
            content=ft.Text("Chart type not supported", color=ft.Colors.RED_400),
        )
    
    # Close button
    def close_magnified_view(e):
        magnified_dialog.open = False
        page.update()
    
    # Magnified chart dialog
    magnified_dialog = ft.AlertDialog(
        title=ft.Text(chart_title, size=20, weight="bold", color=ft.Colors.BLUE_200),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", size=10, color=ft.Colors.GREY),
                    ft.Container(height=20),
                    expanded_chart,
                ],
                spacing=10,
            ),
            width=900,
            height=700,
        ),
        actions=[
            ft.TextButton("Close", on_click=close_magnified_view),
        ],
        modal=True,
    )
    
    return magnified_dialog


def show_magnified_chart(page: ft.Page, chart_title: str, chart_type: str, data_points, months_labels):
    """
    Show magnified chart in a dialog
    
    Args:
        page: Flet page object
        chart_title: Title of the chart
        chart_type: Type of chart ('pie', 'bar')
        data_points: List of data values
        months_labels: List of month labels for x-axis
    """
    magnified_dialog = create_magnified_chart_view(page, chart_title, chart_type, data_points, months_labels)
    page.overlay.append(magnified_dialog)
    magnified_dialog.open = True
    page.update()
