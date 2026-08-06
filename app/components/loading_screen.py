"""
Loading screen component for route transitions.
Displays an animated loading indicator while views are being constructed.
"""

import flet as ft


def create_loading_view(route: str = "/loading") -> ft.View:
    """
    Create a loading screen view with animated spinner and branding.
    
    Args:
        route: The route this loading view is shown for.
    
    Returns:
        ft.View with centered loading animation.
    """
    # Animated spinner using Flet's ProgressRing
    spinner = ft.Container(
        content=ft.Stack(
            controls=[
                # Outer subtle ring
                ft.Container(
                    content=ft.ProgressRing(
                        width=120,
                        height=120,
                        stroke_width=2,
                        color="#2a2a2a",
                    ),
                ),
                # Main spinner
                ft.Container(
                    content=ft.ProgressRing(
                        width=100,
                        height=100,
                        stroke_width=4,
                        color=ft.Colors.BLUE_400,
                    ),
                    margin=ft.margin.all(10),
                ),
                # Center icon
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.STAR_ROUNDED,
                        size=32,
                        color=ft.Colors.BLUE_200,
                        opacity=0.7,
                    ),
                    margin=ft.margin.only(left=44, top=44),
                ),
            ],
            width=140,
            height=140,
        ),
    )

    loading_content = ft.Container(
        content=ft.Column(
            controls=[
                # Branding
                ft.Text(
                    "MORNING STAR COOPERATIVE",
                    size=22,
                    weight="bold",
                    color=ft.Colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Loan & Contribution Management System",
                    size=11,
                    color="#555555",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=30),
                # Spinner (centered via Column alignment)
                ft.Row(
                    controls=[spinner],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=20),
                # Loading text
                ft.Text(
                    "Loading...",
                    size=14,
                    weight="w600",
                    color=ft.Colors.BLUE_200,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        ),
        expand=True,
        bgcolor="#1a1a1a",
    )

    return ft.View(
        route=route,
        controls=[
            ft.AppBar(
                title=ft.Text("", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_900,
            ),
            loading_content,
        ],
        bgcolor="#1a1a1a",
    )
