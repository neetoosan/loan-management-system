import flet as ft
from database.connection import (
    create_user,
    get_user_by_username,
    update_user,
    get_all_users,
    delete_user,
)
from components.ui_components import ToastNotification, NotificationType


def create_account_dialog(page: ft.Page, on_success_callback=None):
    """Create a dialog for creating a new account"""
    
    username_field = ft.TextField(
        label="Username",
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    email_field = ft.TextField(
        label="Email",
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    full_name_field = ft.TextField(
        label="Full Name",
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
    
    confirm_password_field = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    status_text = ft.Text("", size=12, color=ft.Colors.RED_700)
    
    def close_dialog(e=None):
        dialog.open = False
        page.update()
    
    def create_account(e):
        """Handle account creation"""
        username = username_field.value.strip()
        email = email_field.value.strip()
        full_name = full_name_field.value.strip()
        password = password_field.value
        confirm_password = confirm_password_field.value
        
        # Validation
        if not username or not email or not password:
            status_text.value = "⚠ Please fill in all required fields"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if len(username) < 3:
            status_text.value = "⚠ Username must be at least 3 characters"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if len(password) < 6:
            status_text.value = "⚠ Password must be at least 6 characters"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if password != confirm_password:
            status_text.value = "⚠ Passwords do not match"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        # Check if username already exists
        if get_user_by_username(username):
            status_text.value = "⚠ Username already exists"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        try:
            status_text.value = "Creating account..."
            status_text.color = ft.Colors.BLUE_200
            page.update()
            
            # Create the user
            user = create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name or None,
                role="USER"
            )
            
            status_text.value = f"✓ Account created successfully!"
            status_text.color = ft.Colors.GREEN_700
            page.update()
            
            # Call success callback if provided - pass username instead of user object
            if on_success_callback:
                on_success_callback(username)
            
            # Close dialog after short delay
            page.update()
            
        except Exception as e:
            status_text.value = f"✗ Error: {str(e)}"
            status_text.color = ft.Colors.RED_700
            page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Text("Create New Account", color=ft.Colors.BLUE_200),
        content=ft.Column(
            controls=[
                ft.Text("Fill in the details below to create a new account:", size=12, color=ft.Colors.GREY),
                ft.Divider(),
                username_field,
                email_field,
                full_name_field,
                password_field,
                confirm_password_field,
                status_text,
            ],
            spacing=12,
            width=400,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Create Account", on_click=create_account),
        ],
    )
    
    return dialog


def edit_account_dialog(page: ft.Page, user_id: int, on_success_callback=None):
    """Create a dialog for editing user account details"""
    from database.connection import get_session
    from database.models import User
    
    # Get current user info
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()
    
    if not user:
        error_text = ft.Text("User not found", color=ft.Colors.RED_700)
        error_dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=error_text,
            actions=[ft.TextButton("OK", on_click=lambda e: None)],
        )
        return error_dialog
    
    email_field = ft.TextField(
        label="Email",
        value=user.email,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    username_field = ft.TextField(
        label="Username",
        value=user.username,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    full_name_field = ft.TextField(
        label="Full Name",
        value=user.full_name or "",
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    new_password_field = ft.TextField(
        label="New Password (leave blank to keep current)",
        password=True,
        can_reveal_password=True,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    confirm_password_field = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    status_text = ft.Text("", size=12, color=ft.Colors.RED_700)
    
    def close_dialog(e=None):
        dialog.open = False
        page.update()
    
    def save_changes(e):
        """Handle account update"""
        username = username_field.value.strip()
        email = email_field.value.strip()
        full_name = full_name_field.value.strip()
        new_password = new_password_field.value
        confirm_password = confirm_password_field.value
        
        # Validation
        if not username:
            status_text.value = "⚠ Username is required"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if not email:
            status_text.value = "⚠ Email is required"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if new_password and new_password != confirm_password:
            status_text.value = "⚠ Passwords do not match"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if new_password and len(new_password) < 6:
            status_text.value = "⚠ Password must be at least 6 characters"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        try:
            status_text.value = "Updating account..."
            status_text.color = ft.Colors.BLUE_200
            page.update()
            
            # Update the user
            password_to_set = new_password if new_password else None
            updated_user = update_user(
                user_id=user_id,
                username=username,
                email=email,
                full_name=full_name or None,
                password=password_to_set
            )
            
            status_text.value = f"✓ Account updated successfully!"
            status_text.color = ft.Colors.GREEN_700
            page.update()
            
            # Call success callback if provided
            if on_success_callback:
                on_success_callback(updated_user)
            
            # Close dialog after short delay
            
        except Exception as e:
            status_text.value = f"✗ Error: {str(e)}"
            status_text.color = ft.Colors.RED_700
            page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Text("Edit Account", color=ft.Colors.BLUE_200),
        content=ft.Column(
            controls=[
                ft.Text(f"Editing account: {user.username}", size=12, color=ft.Colors.GREY),
                ft.Divider(),
                username_field,
                email_field,
                full_name_field,
                new_password_field,
                confirm_password_field,
                status_text,
            ],
            spacing=12,
            width=400,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Save Changes", on_click=save_changes),
        ],
    )
    
    return dialog


def list_users_dialog(page: ft.Page):
    """Create a dialog showing all users with edit/delete options"""
    
    def refresh_users_list():
        """Refresh the users list"""
        try:
            users = get_all_users()
            user_rows = []
            
            for user in users:
                def edit_user_handler(e, user_id=user.id, username=user.username):
                    dialog.open = False
                    edit_dialog = edit_user_dialog(page, user_id, username)
                    page.overlay.append(edit_dialog)
                    edit_dialog.open = True
                    page.update()
                
                def delete_user_handler(e, user_id=user.id, username=user.username):
                    show_delete_confirmation(user_id, username)
                
                user_rows.append(
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(user.username, weight="bold", color=ft.Colors.WHITE),
                                    ft.Text(user.email, size=10, color=ft.Colors.GREY),
                                    ft.Text(f"Role: {user.role.value}", size=9, color=ft.Colors.GREY),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.Text(
                                "✓ Active" if user.is_active else "✗ Inactive",
                                color=ft.Colors.GREEN_700 if user.is_active else ft.Colors.RED_700,
                                size=10,
                            ),
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.Icons.EDIT,
                                        icon_size=16,
                                        on_click=edit_user_handler,
                                        tooltip="Edit",
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE,
                                        icon_size=16,
                                        on_click=delete_user_handler,
                                        tooltip="Delete",
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                )
            
            if not user_rows:
                content.content = ft.Text("No users found", color=ft.Colors.GREY)
            else:
                content.content = ft.ListView(
                    controls=user_rows,
                    expand=True,
                    spacing=10,
                )
            page.update()
        
        except Exception as e:
            content.content = ft.Text(f"Error loading users: {str(e)}", color=ft.Colors.RED_700)
            page.update()
    
    def show_delete_confirmation(user_id, username):
        """Show delete confirmation dialog"""
        def close_confirm(e=None):
            confirm_dialog.open = False
            page.update()
        
        def confirm_delete(e=None):
            try:
                delete_user(user_id)
                confirm_dialog.open = False
                ToastNotification.show(page, f"User '{username}' deleted successfully!", NotificationType.SUCCESS)
                refresh_users_list()
                page.update()
            except Exception as ex:
                confirm_dialog.open = False
                ToastNotification.show(page, f"Error deleting user: {str(ex)}", NotificationType.ERROR)
                page.update()
        
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Delete User"),
            content=ft.Text(f"Are you sure you want to delete the user '{username}'? This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=close_confirm),
                ft.TextButton("Delete", on_click=confirm_delete),
            ],
        )
        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()
    
    content = ft.Container(
        content=ft.Text("Loading users...", color=ft.Colors.GREY),
        width=600,
        height=350,
    )
    
    def close_dialog(e=None):
        dialog.open = False
        page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Text("User Accounts", color=ft.Colors.BLUE_200),
        content=content,
        actions=[
            ft.TextButton("Close", on_click=close_dialog),
        ],
    )
    
    # Load users after dialog is created
    refresh_users_list()
    
    return dialog


def edit_user_dialog(page: ft.Page, user_id: int, username: str):
    """Create a dialog for editing user account"""
    from database.connection import get_session
    from database.models import User
    
    # Get current user info
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user_data = {
            'email': user.email,
            'full_name': user.full_name or "",
            'role': user.role.value,
        }
    finally:
        session.close()
    
    email_field = ft.TextField(
        label="Email",
        value=user_data['email'],
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    full_name_field = ft.TextField(
        label="Full Name",
        value=user_data['full_name'],
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    username_field = ft.TextField(
        label="Username",
        value=username,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    status_text = ft.Text("", size=12, color=ft.Colors.RED_700)
    
    def close_dialog(e=None):
        dialog.open = False
        page.update()
    
    def save_changes(e):
        """Handle account update"""
        new_username = username_field.value.strip()
        email = email_field.value.strip()
        full_name = full_name_field.value.strip()
        
        if not new_username:
            status_text.value = "⚠ Username is required"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if not email:
            status_text.value = "⚠ Email is required"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        try:
            status_text.value = "Updating account..."
            status_text.color = ft.Colors.BLUE_200
            page.update()
            
            # Update the user
            update_user(
                user_id=user_id,
                username=new_username,
                email=email,
                full_name=full_name or None,
            )
            
            status_text.value = f"✓ Account updated successfully!"
            status_text.color = ft.Colors.GREEN_700
            page.update()
            ToastNotification.show(page, "Account updated successfully!", NotificationType.SUCCESS)
            
        except Exception as e:
            status_text.value = f"✗ Error: {str(e)}"
            status_text.color = ft.Colors.RED_700
            page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Text("Edit Account", color=ft.Colors.BLUE_200),
        content=ft.Column(
            controls=[
                ft.Text(f"Editing account: {username}", size=12, color=ft.Colors.GREY),
                ft.Divider(),
                username_field,
                email_field,
                full_name_field,
                status_text,
            ],
            spacing=12,
            width=400,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Save Changes", on_click=save_changes),
        ],
    )
    
    return dialog


def change_password_dialog(page: ft.Page, user_id: int, username: str):
    """Create a dialog for changing user password"""
    from database.connection import get_session
    from database.models import User
    
    current_password_field = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    new_password_field = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    confirm_password_field = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        label_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor="#2a2a2a",
        border_color=ft.Colors.GREY,
        width=350,
    )
    
    status_text = ft.Text("", size=12, color=ft.Colors.RED_700)
    
    def close_dialog(e=None):
        dialog.open = False
        page.update()
    
    def change_password(e):
        """Handle password change"""
        current_password = current_password_field.value
        new_password = new_password_field.value
        confirm_password = confirm_password_field.value
        
        if not current_password or not new_password:
            status_text.value = "⚠ Please fill in all fields"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if len(new_password) < 6:
            status_text.value = "⚠ Password must be at least 6 characters"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        if new_password != confirm_password:
            status_text.value = "⚠ Passwords do not match"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        # Verify current password
        from database.connection import authenticate_user
        success, _ = authenticate_user(username, current_password)
        if not success:
            status_text.value = "⚠ Current password is incorrect"
            status_text.color = ft.Colors.ORANGE_400
            page.update()
            return
        
        try:
            status_text.value = "Changing password..."
            status_text.color = ft.Colors.BLUE_200
            page.update()
            
            # Update password
            update_user(
                user_id=user_id,
                password=new_password
            )
            
            status_text.value = f"✓ Password changed successfully!"
            status_text.color = ft.Colors.GREEN_700
            page.update()
            ToastNotification.show(page, "Password changed successfully!", NotificationType.SUCCESS)
            
        except Exception as e:
            status_text.value = f"✗ Error: {str(e)}"
            status_text.color = ft.Colors.RED_700
            page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Text("Change Password", color=ft.Colors.BLUE_200),
        content=ft.Column(
            controls=[
                ft.Text(f"User: {username}", size=12, color=ft.Colors.GREY),
                ft.Divider(),
                current_password_field,
                new_password_field,
                confirm_password_field,
                status_text,
            ],
            spacing=12,
            width=400,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Change Password", on_click=change_password),
        ],
    )
    
    return dialog
