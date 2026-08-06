import flet as ft
from components.responsive import ResponsiveConfig, get_responsive_font_size, get_responsive_padding
from database.connection import authenticate_user, get_all_users

def LoginScreen(page: ft.Page):
    # Store references to text fields
    username_field = None
    password_field = None
    status_text = ft.Text("", size=12, color=ft.Colors.RED_700)
    
    def handle_login(e):
        """Handle login with authentication"""
        username = username_field.value.strip()
        password = password_field.value
        
        if not username or not password:
            status_text.value = "⚠ Please enter username and password"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        # Authenticate user
        success, message = authenticate_user(username, password)
        
        if success:
            status_text.value = f"✓ {message}"
            status_text.color = ft.Colors.GREEN_700
            page.update()
            
            # Navigate to dashboard after successful login
            import time
            page.route = "/dashboard"
            if hasattr(page, 'on_route_change') and page.on_route_change:
                page.on_route_change("/dashboard")
            page.update()
        else:
            status_text.value = f"✗ {message}"
            status_text.color = ft.Colors.RED_700
            password_field.value = ""
            page.update()
    
    is_small_screen = ResponsiveConfig.is_small_screen(page)
    padding = get_responsive_padding(page)
    
    # Determine layout based on screen size
    if is_small_screen:
        # Mobile/Tablet: Single column layout
        username_field = ft.TextField(
            label="Username",
            label_style=ft.TextStyle(color=ft.Colors.GREY),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            bgcolor="#2a2a2a",
            border_color=ft.Colors.GREY,
            expand=True,
        )
        
        password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            label_style=ft.TextStyle(color=ft.Colors.GREY),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            bgcolor="#2a2a2a",
            border_color=ft.Colors.GREY,
            expand=True,
        )
        
        login_content = ft.Column([
            ft.Container(height=20),
            ft.Text(
                "MORNING STAR COOPERATIVE",
                size=get_responsive_font_size(page, 32),
                weight="bold",
                color=ft.Colors.BLUE_200,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=15),
            ft.Text(
                "Loan & Contribution Management System",
                size=get_responsive_font_size(page, 14),
                color=ft.Colors.GREY,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=30),
            ft.Text("Welcome Back", size=get_responsive_font_size(page, 20), weight="bold", color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20),
            username_field,
            password_field,
            status_text,
            ft.Container(height=20),
            ft.ElevatedButton(
                "Sign In",
                on_click=handle_login,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_900,
                    color=ft.Colors.WHITE,
                ),
                expand=True,
            ),
            ft.Container(height=10),
            ft.Text("No account? Create one in Settings", size=10, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        
        login_form = ft.Container(
            content=login_content,
            bgcolor="#2a2a2a",
            border_radius=10,
            padding=padding,
            border=ft.border.all(1, ft.Colors.BLUE_900),
        )
    else:
        # Desktop: Two column layout
        username_field = ft.TextField(
            label="Username",
            label_style=ft.TextStyle(color=ft.Colors.GREY),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            bgcolor="#2a2a2a",
            border_color=ft.Colors.GREY,
            width=350,
        )
        
        password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            label_style=ft.TextStyle(color=ft.Colors.GREY),
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            bgcolor="#2a2a2a",
            border_color=ft.Colors.GREY,
            width=350,
        )
        
        login_form = ft.Row([
            # Left side - Branding
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "MORNING STAR\nCOOPERATIVE",
                        size=48,
                        weight="bold",
                        color=ft.Colors.BLUE_200,
                        text_align=ft.TextAlign.LEFT,
                    ),
                    ft.Container(height=30),
                    ft.Text(
                        "Customized software for Morning Star Cooperative to manage staff loans and contribution effectively. Made to make report more accurate and dependable.",
                        size=16,
                        color=ft.Colors.GREY,
                        text_align=ft.TextAlign.LEFT,
                        width=400,
                    ),
                ], spacing=0, alignment=ft.MainAxisAlignment.START),
                padding=40,
                expand=True,
            ),
            # Right side - Login Form
            ft.Container(
                content=ft.Column([
                    ft.Text("Welcome Back", size=24, weight="bold", color=ft.Colors.WHITE),
                    ft.Container(height=30),
                    username_field,
                    password_field,
                    status_text,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Sign In",
                        on_click=handle_login,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_900,
                            color=ft.Colors.WHITE,
                        ),
                        width=350,
                    ),
                    ft.Container(height=10),
                    ft.Text("No account? Create one in Settings", size=10, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#2a2a2a",
                border_radius=10,
                padding=40,
                border=ft.border.all(1, ft.Colors.BLUE_900),
                width=500,
            )
        ], spacing=40, alignment=ft.MainAxisAlignment.CENTER)

    return ft.View(
        route="/login",
        controls=[
            ft.AppBar(
                title=ft.Text("Login", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_900,
            ),
            ft.Container(
                content=login_form,
                expand=True,
                bgcolor="#1a1a1a",
                padding=padding,
            )
        ],
        bgcolor="#1a1a1a",
    )