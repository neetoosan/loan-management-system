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
                content=ft.Column([
                    ft.Text("Loan Management System", size=32, weight="bold", color=ft.Colors.BLUE_200, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=30),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Welcome Back", size=20, weight="bold", color=ft.Colors.WHITE),
                            ft.Container(height=20),
                            ft.TextField(
                                label="Username",
                                label_style=ft.TextStyle(color=ft.Colors.GREY),
                                text_style=ft.TextStyle(color=ft.Colors.WHITE),
                                bgcolor="#2a2a2a",
                                border_color=ft.Colors.GREY,
                            ),
                            ft.TextField(
                                label="Password",
                                password=True,
                                can_reveal_password=True,
                                label_style=ft.TextStyle(color=ft.Colors.GREY),
                                text_style=ft.TextStyle(color=ft.Colors.WHITE),
                                bgcolor="#2a2a2a",
                                border_color=ft.Colors.GREY,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "Sign In",
                                on_click=handle_login,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_900,
                                    color=ft.Colors.WHITE,
                                ),
                                width=300,
                            )
                        ], spacing=10, width=400),
                        bgcolor="#1a1a1a",
                        border_radius=10,
                        padding=30,
                        border=ft.border.all(1, ft.Colors.GREY),
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                bgcolor="#1a1a1a",
            )
        ],
        bgcolor="#1a1a1a",
    )