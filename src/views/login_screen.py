import flet as ft

def LoginScreen(page: ft.Page):
    def handle_login(e):
        # Logic for authentication goes here
        page.go("/dashboard")

    return ft.View(
        "/login",
        controls=[
            ft.AppBar(
                title=ft.Text("Login", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_900,
            ),
            ft.Container(
                content=ft.Row([
                    # Left side - Branding and Description
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
                            ft.TextField(
                                label="Username",
                                label_style=ft.TextStyle(color=ft.Colors.GREY),
                                text_style=ft.TextStyle(color=ft.Colors.WHITE),
                                bgcolor="#2a2a2a",
                                border_color=ft.Colors.GREY,
                                width=350,
                            ),
                            ft.TextField(
                                label="Password",
                                password=True,
                                can_reveal_password=True,
                                label_style=ft.TextStyle(color=ft.Colors.GREY),
                                text_style=ft.TextStyle(color=ft.Colors.WHITE),
                                bgcolor="#2a2a2a",
                                border_color=ft.Colors.GREY,
                                width=350,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "Sign In",
                                on_click=handle_login,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_900,
                                    color=ft.Colors.WHITE,
                                ),
                                width=350,
                            )
                        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#2a2a2a",
                        border_radius=10,
                        padding=40,
                        border=ft.border.all(1, ft.Colors.BLUE_900),
                        width=500,
                    )
                ], spacing=40, alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
                bgcolor="#1a1a1a",
                padding=20,
            )
        ],
        bgcolor="#1a1a1a",
    )