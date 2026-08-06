#!/usr/bin/env python3
"""Minimal test app to debug the blank screen issue"""
import flet as ft
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from database.connection import init_db


def main(page: ft.Page):
    page.title = "Test App"
    print("=== TEST APP STARTED ===")
    print(f"Page object: {page}")
    print(f"Initial page.route: {page.route}")
    
    # Initialize database
    try:
        print("Calling init_db()...")
        init_db()
        print("init_db() completed successfully")
    except Exception as e:
        print(f"ERROR in init_db: {e}")
        import traceback
        traceback.print_exc()
        return
    
    def route_change(route):
        print(f"\n>>> route_change called! route={route}")
        print(f">>> page.route is now: {page.route}")
        page.views.clear()
        
        try:
            if page.route == "/login":
                print(">>> Loading LoginScreen...")
                from views.login_screen import LoginScreen
                
                view = LoginScreen(page)
                print(f">>> LoginScreen returned: {type(view)} - {view}")
                
                if view is None:
                    print(">>> ERROR: LoginScreen returned None!")
                    return
                
                page.views.append(view)
                print(f">>> Appended to page.views")
                print(f">>> page.views length: {len(page.views)}")
                print(f">>> page.views[0] controls: {view.controls if hasattr(view, 'controls') else 'N/A'}")
            
            print(f">>> Calling page.update()...")
            page.update()
            print(f">>> page.update() completed")
            print(f">>> Final page.views: {page.views}")
            
        except Exception as e:
            print(f">>> EXCEPTION in route_change: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nSetting up page callbacks...")
    page.on_route_change = route_change
    
    print(f"\nSetting page.route = '/login'...")
    page.route = "/login"
    print(f"page.route is now: {page.route}")
    
    # Explicitly call route_change to load the initial view
    print("\nExplicitly calling route_change('/login')...")
    route_change("/login")
    
    print("\n=== WAITING FOR USER ACTION ===")


if __name__ == "__main__":
    print("Starting ft.run()...")
    ft.run(main)
