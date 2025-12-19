import flet as ft
from views.login_screen import LoginScreen
from main_window import MainWindow
from views.loan_screen import LoanScreen
from views.contribution_screen import ContributionScreen
from views.member_dialog import MemberScreen
from views.settings_screen import SettingsScreen
from database.connection import init_db

def main(page: ft.Page):
    page.title = "Loan Management System"
    page.window_width = 1400
    page.window_height = 900
    
    # Initialize database
    init_db()

    def route_change(route):
        page.views.clear()
        
        # Routing Logic
        if page.route == "/login":
            page.views.append(LoginScreen(page))
        elif page.route == "/dashboard":
            page.views.append(MainWindow(page))
        elif page.route == "/loans":
            page.views.append(LoanScreen(page))
        elif page.route == "/contributions":
            page.views.append(ContributionScreen(page))
        elif page.route == "/members":
            page.views.append(MemberScreen(page))
        elif page.route == "/settings":
            page.views.append(SettingsScreen(page))
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start the app at the login screen
    page.go("/login")

ft.app(target=main)