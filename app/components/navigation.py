import flet as ft


def create_navigation_rail(page: ft.Page, on_route_change):
    """
    Creates a navigation rail component for sidebar navigation
    
    Args:
        page: The Flet page object
        on_route_change: Callback function when a nav item is clicked
    """
    
    nav_items = [
        {"label": "Dashboard", "icon": ft.Icons.DASHBOARD, "route": "/dashboard"},
        {"label": "Members", "icon": ft.Icons.PEOPLE, "route": "/members"},
        {"label": "Loans", "icon": ft.Icons.ATTACH_MONEY, "route": "/loans"},
        {"label": "Contributions", "icon": ft.Icons.SAVINGS, "route": "/contributions"},
        {"label": "Reports", "icon": ft.Icons.DOCUMENT_SCANNER, "route": "/reports"},
        {"label": "Settings", "icon": ft.Icons.SETTINGS, "route": "/settings"},
    ]
    
    selected_index = 0
    
    def on_nav_change(e):
        nonlocal selected_index
        selected_index = e.control.selected_index
        route = nav_items[selected_index]["route"]
        page.go(route)
    
    rail = ft.NavigationRail(
        selected_index=selected_index,
        label_type="all",
        on_change=on_nav_change,
        destinations=[
            ft.NavigationRailDestination(
                icon=item["icon"],
                label=item["label"],
            )
            for item in nav_items
        ],
        bgcolor="#1a1a1a",
        indicator_color=ft.Colors.BLUE_200,
    )
    
    return rail, nav_items


def create_app_bar(title: str, page: ft.Page, on_toggle_sidebar=None):
    """
    Creates a consistent AppBar for all screens
    
    Args:
        title: Title to display in the app bar
        page: The Flet page object
        on_toggle_sidebar: Optional callback function to toggle sidebar
    """
    leading_widget = None
    if on_toggle_sidebar:
        from components.burger_menu import create_burger_menu
        leading_widget = create_burger_menu(on_toggle_sidebar)
    
    return ft.AppBar(
        title=ft.Text(title, size=20, weight="bold", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_900,
        color=ft.Colors.WHITE,
        leading=leading_widget,
        actions=[
            ft.IconButton(
                ft.Icons.LOGOUT,
                tooltip="Logout",
                on_click=lambda _: page.go("/login"),
            )
        ],
    )

