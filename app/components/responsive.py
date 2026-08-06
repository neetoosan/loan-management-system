"""
Responsive design utilities for different screen sizes
Handles layout adjustments for screens from 768x1024 (tablet) to larger screens
"""

import flet as ft


class ResponsiveConfig:
    """Configuration class for responsive design"""
    
    @staticmethod
    def get_screen_type(page: ft.Page):
        """
        Determine screen type based on window dimensions
        Returns: 'mobile' (< 768), 'tablet' (768-1024), 'desktop' (> 1024)
        """
        width = getattr(page, 'width', None) or 1400
        
        if width < 768:
            return 'mobile'
        elif width < 1200:
            return 'tablet'
        else:
            return 'desktop'
    
    @staticmethod
    def is_small_screen(page: ft.Page):
        """Check if screen is small (tablet or mobile)"""
        width = getattr(page, 'width', None) or 1400
        return width < 1200
    
    @staticmethod
    def get_card_width(page: ft.Page, max_width: int = 200):
        """Get responsive card width"""
        width = getattr(page, 'width', None) or 1400
        
        if width < 768:
            return width - 60  # Mobile: full width minus padding
        elif width < 1024:
            return (width - 50) / 2  # Tablet: 2 columns
        else:
            return max_width  # Desktop: standard width
    
    @staticmethod
    def get_table_height(page: ft.Page):
        """Get responsive table height"""
        height = getattr(page, 'height', None) or 900
        
        if height < 800:
            return 300
        elif height < 1024:
            return 400
        else:
            return 500
    
    @staticmethod
    def get_chart_height(page: ft.Page):
        """Get responsive chart height"""
        height = getattr(page, 'height', None) or 900
        
        if height < 800:
            return 200
        elif height < 1024:
            return 250
        else:
            return 300
    
    @staticmethod
    def get_chart_width(page: ft.Page):
        """Get responsive chart width"""
        width = getattr(page, 'width', None) or 1400
        
        if width < 768:
            return width - 40
        elif width < 1024:
            return (width - 50) / 2
        else:
            return 450
    
    @staticmethod
    def get_dialog_width(page: ft.Page):
        """Get responsive dialog width"""
        width = getattr(page, 'width', None) or 1400
        
        if width < 768:
            return width - 40
        elif width < 1024:
            return width - 60
        else:
            return 500


def create_responsive_summary_card(title: str, value: str, icon: str, color: str = ft.Colors.BLUE_200, page: ft.Page = None):
    """Create a responsive summary card that adapts to screen size"""
    
    # Determine sizes based on screen
    if page and (getattr(page, 'width', None) or 1400) < 768:
        icon_size = 28
        value_size = 18
        title_size = 10
        padding = 12
        height = 100
    elif page and (getattr(page, 'width', None) or 1400) < 1024:
        icon_size = 32
        value_size = 20
        title_size = 11
        padding = 14
        height = 120
    else:
        icon_size = 36
        value_size = 24
        title_size = 11
        padding = 16
        height = 140
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(name=icon, size=icon_size, color=color),
                ft.Container(height=6),
                ft.Text(value, size=value_size, weight="bold", color=ft.Colors.WHITE),
                ft.Text(title, size=title_size, color=ft.Colors.GREY, weight="w400"),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor="#252525",
        border_radius=10,
        padding=padding,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK, spread_radius=0),
        height=height,
        expand=True,
    )


def create_responsive_row(controls: list, page: ft.Page, spacing: int = 15, wrap: bool = True):
    """
    Create a responsive row that wraps on small screens
    On small screens (< 1024), converts to column layout
    """
    screen_type = ResponsiveConfig.get_screen_type(page)
    
    if screen_type == 'mobile' or (page and (getattr(page, 'width', None) or 1400) < 768):
        # Mobile: stack vertically
        return ft.Column(
            controls=controls,
            spacing=spacing,
            scroll=ft.ScrollMode.AUTO,
        )
    elif screen_type == 'tablet' or (page and (getattr(page, 'width', None) or 1400) < 1024):
        # Tablet: flexible wrapping row
        return ft.Row(
            controls=controls,
            spacing=spacing,
            wrap=wrap,
            scroll=ft.ScrollMode.AUTO,
        )
    else:
        # Desktop: standard row
        return ft.Row(
            controls=controls,
            spacing=spacing,
            wrap=wrap,
        )


def create_responsive_dialog_content(controls: list, page: ft.Page, scroll: bool = True):
    """Create responsive dialog content that adapts to screen size"""
    
    width = ResponsiveConfig.get_dialog_width(page)
    
    return ft.Container(
        content=ft.Column(
            controls=controls,
            spacing=8,
            scroll=ft.ScrollMode.AUTO if scroll else ft.ScrollMode.NONE,
            tight=True,
        ),
        padding=15,
        width=width,
    )


def get_responsive_padding(page: ft.Page):
    """Get responsive padding based on screen size"""
    width = getattr(page, 'width', None) or 1400
    if width < 768:
        return 10
    elif width < 1024:
        return 15
    else:
        return 20


def get_responsive_font_size(page: ft.Page, base_size: int):
    """Get responsive font size - scales down on small screens"""
    width = getattr(page, 'width', None) or 1400
    if width < 768:
        return int(base_size * 0.8)
    elif width < 1024:
        return int(base_size * 0.9)
    else:
        return base_size


def create_responsive_button_row(buttons: list, page: ft.Page, spacing: int = 10):
    """Create responsive button row that stacks on small screens"""
    
    width = getattr(page, 'width', None) or 1400
    if width < 768:
        # Mobile: stack buttons vertically, full width
        return ft.Column(
            controls=[
                ft.Container(
                    content=btn,
                    expand=True,
                ) for btn in buttons
            ],
            spacing=spacing,
        )
    else:
        # Desktop/Tablet: horizontal row
        return ft.Row(
            controls=buttons,
            spacing=spacing,
            wrap=True,
        )


def create_responsive_table_container(table: ft.DataTable, page: ft.Page):
    """Create a responsive table container that scrolls appropriately"""
    
    return ft.Container(
        content=ft.Column(
            controls=[table],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        alignment=ft.Alignment(-1, -1),
        bgcolor="#2a2a2a",
        border_radius=10,
        padding=10,
        height=ResponsiveConfig.get_table_height(page),
    )
