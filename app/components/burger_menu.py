import flet as ft


def create_burger_menu(on_toggle_sidebar):
    """
    Creates a burger menu (hamburger menu) icon button for toggling sidebar
    
    Args:
        on_toggle_sidebar: Callback function to toggle sidebar visibility
        
    Returns:
        ft.IconButton: Burger menu button
    """
    burger_button = ft.IconButton(
        ft.Icons.MENU,
        tooltip="Toggle Navigation",
        on_click=on_toggle_sidebar,
        icon_size=24,
    )
    return burger_button


def create_app_bar_with_burger(title: str, page: ft.Page, on_toggle_sidebar):
    """
    Creates an AppBar with a burger menu button for mobile-friendly navigation
    
    Args:
        title: Title to display in the app bar
        page: The Flet page object
        on_toggle_sidebar: Callback function to toggle sidebar visibility
        
    Returns:
        ft.AppBar: App bar with burger menu and logout button
    """
    burger_button = create_burger_menu(on_toggle_sidebar)
    
    return ft.AppBar(
        title=ft.Text(title, size=20, weight="bold", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_900,
        color=ft.Colors.WHITE,
        leading=burger_button,
        actions=[
            ft.IconButton(
                ft.Icons.LOGOUT,
                tooltip="Logout",
                on_click=lambda _: page.go("/login"),
            )
        ],
    )


def create_sidebar_overlay(page: ft.Page):
    """
    Creates a reusable sidebar overlay component for all screens with Morning Star Cooperative branding
    
    Args:
        page: The Flet page object
        
    Returns:
        Tuple containing:
            - sidebar_wrapper: Container holding the sidebar
            - backdrop: Backdrop overlay
            - sidebar_visible: State dict for visibility
            - toggle_sidebar: Function to toggle sidebar
            - close_sidebar: Function to close sidebar
    """
    from components.navigation import create_navigation_rail
    
    # State for sidebar visibility
    sidebar_visible = {"value": False}
    
    # Create navigation rail
    rail, nav_items = create_navigation_rail(page, lambda: None)
    
    # Create custom nav item handler
    def create_nav_item(label: str, icon: str, route: str):
        def on_click(e):
            sidebar_visible["value"] = False
            sidebar_wrapper.visible = False
            backdrop.visible = False
            page.go(route)
            page.update()
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=20, color=ft.Colors.BLUE_200),
                    ft.Text(label, size=13, color=ft.Colors.WHITE, weight="w500"),
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.symmetric(vertical=14, horizontal=20),
            on_click=on_click,
            bgcolor="transparent",
        )
    
    # Sidebar container with Morning Star Cooperative branding
    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                # Header section with branding
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("MORNING STAR", size=18, weight="bold", color=ft.Colors.BLUE_200),
                            ft.Text("Cooperative", size=11, color=ft.Colors.GREY, weight="w400"),
                        ],
                        spacing=3,
                    ),
                    padding=ft.padding.symmetric(horizontal=24, vertical=24),
                    border_radius=12,
                ),
                ft.Container(height=5),
                # Navigation section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("NAVIGATION", size=11, weight="bold", color=ft.Colors.GREY),
                            ft.Container(height=3),
                            create_nav_item("Dashboard", ft.Icons.DASHBOARD, "/dashboard"),
                            create_nav_item("Members", ft.Icons.PEOPLE, "/members"),
                            create_nav_item("Loans", ft.Icons.ATTACH_MONEY, "/loans"),
                            create_nav_item("Contributions", ft.Icons.SAVINGS, "/contributions"),
                            create_nav_item("Reports", ft.Icons.DOCUMENT_SCANNER, "/reports"),
                        ],
                        spacing=2,
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                ),
                ft.Container(height=8),
                # Settings section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("SETTINGS", size=11, weight="bold", color=ft.Colors.GREY),
                            ft.Container(height=3),
                            create_nav_item("Settings", ft.Icons.SETTINGS, "/settings"),
                        ],
                        spacing=2,
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                ),
                ft.Container(expand=True),
                # Logout section
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Divider(height=1),
                            ft.Container(height=5),
                            create_nav_item("Logout", ft.Icons.LOGOUT, "/login"),
                        ],
                        spacing=0,
                    ),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=280,
        bgcolor="#1e1e1e",
        border_radius=ft.border_radius.only(
            top_right=15,
            bottom_right=15,
        ),
        expand=True,
    )
    
    # Backdrop overlay
    backdrop = ft.Container(
        visible=False,
        bgcolor=ft.Colors.with_opacity(0.5, "#000000"),
        expand=True,
    )
    
    # Sidebar wrapper
    sidebar_wrapper = ft.Container(
        visible=False,
        content=sidebar,
        padding=0,
    )
    
    # Toggle sidebar function
    def toggle_sidebar(e):
        sidebar_visible["value"] = not sidebar_visible["value"]
        sidebar_wrapper.visible = sidebar_visible["value"]
        backdrop.visible = sidebar_visible["value"]
        page.update()
    
    # Close sidebar function
    def close_sidebar(e):
        sidebar_visible["value"] = False
        sidebar_wrapper.visible = False
        backdrop.visible = False
        page.update()
    
    backdrop.on_click = close_sidebar
    
    return sidebar_wrapper, backdrop, sidebar_visible, toggle_sidebar, close_sidebar

