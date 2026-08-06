import flet as ft
import asyncio
from database.connection import init_db, update_overdue_non_member_interest
from components.loading_screen import create_loading_view


def navigate_to(page: ft.Page, route: str):
    """Navigate to a different route (replaces deprecated page.go)"""
    page.route = route
    page.update()


def main(page: ft.Page):
    page.title = "Loan Management System"
    page.window.min_width = 800
    page.window.min_height = 600
    
    # Initialize database
    init_db()
    
    # Update overdue non-member loan interest on startup
    try:
        updated = update_overdue_non_member_interest()
        if updated:
            print(f"✓ Startup: Updated interest for {len(updated)} overdue non-member loan(s)")
    except Exception as e:
        print(f"Warning: Could not update overdue interest on startup: {e}")

    def _build_view(route_path: str):
        """Build and return the view for a given route."""
        if route_path == "/login":
            from views.login_screen import LoginScreen
            return LoginScreen(page)
        elif route_path == "/dashboard":
            from main_window import MainWindow
            return MainWindow(page)
        elif route_path == "/loans":
            from views.loan_screen import LoanScreen
            return LoanScreen(page)
        elif route_path == "/contributions":
            from views.contribution_screen import ContributionScreen
            return ContributionScreen(page)
        elif route_path == "/members":
            from views.member_dialog import MemberScreen
            return MemberScreen(page)
        elif route_path == "/settings":
            from views.settings_screen import SettingsScreen
            return SettingsScreen(page)
        elif route_path == "/reports":
            from views.report_screen import ReportScreen
            return ReportScreen(page)
        return None

    def route_change(route):
        """Handle route changes with loading screen transition"""
        # Extract route string from RouteChangeEvent if needed
        if hasattr(route, 'route'):
            route_path = route.route
        else:
            route_path = route
        
        print(f"DEBUG: route_change called with route: {route}")
        print(f"DEBUG: current page.route: {page.route}")
        
        current_route = page.route
        
        # For login, load directly (no loading screen)
        if current_route == "/login":
            page.views.clear()
            view = _build_view(current_route)
            if view:
                page.views.append(view)
            page.update()
            return
        
        # For all other routes, show loading screen first
        page.views.clear()
        loading_view = create_loading_view(current_route)
        page.views.append(loading_view)
        page.update()
        
        # Build the actual view in an async task so the loading UI renders
        async def _load_actual_view():
            # Small delay to let the loading screen render
            await asyncio.sleep(0.3)
            try:
                view = _build_view(current_route)
                if view:
                    page.views.clear()
                    page.views.append(view)
                    page.update()
                    print(f"DEBUG: {current_route} loaded successfully")
                else:
                    print(f"DEBUG: Unknown route: {current_route}, defaulting to login")
                    page.route = "/login"
                    route_change("/login")
            except Exception as e:
                print(f"Route error: {e}")
                import traceback
                traceback.print_exc()
                page.route = "/login"
                route_change("/login")
        
        page.run_task(_load_actual_view)

    def view_pop(view):
        """Handle back button navigation"""
        try:
            page.views.pop()
            top_view = page.views[-1]
            navigate_to(page, top_view.route)
        except Exception as e:
            print(f"View pop error: {e}")
            navigate_to(page, "/login")

    page.on_view_pop = view_pop
    
    # Start the app at the login screen
    page.route = "/login"
    # Explicitly call route_change to load the initial view
    route_change("/login")
    
    # Set up callback for route changes from other components
    def on_route_change_handler(route):
        print(f">>> Route changed to: {route}")
        route_change(route)
    
    page.on_route_change = on_route_change_handler


if __name__ == "__main__":
    ft.run(main)