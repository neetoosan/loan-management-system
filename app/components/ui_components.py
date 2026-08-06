"""
Advanced UI components for LMS application
Includes: progress bars, toast notifications, modal dialogs, and operation tracking
"""

import flet as ft
from typing import Callable, Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
from components.error_handler import error_logger


class NotificationType(Enum):
    """Notification types"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ToastNotification:
    """Improved toast notifications with auto-dismiss"""
    
    # Color scheme for different types
    TYPE_COLORS = {
        NotificationType.SUCCESS: (ft.Colors.GREEN_700, "✓"),
        NotificationType.ERROR: (ft.Colors.RED_700, "✗"),
        NotificationType.WARNING: (ft.Colors.ORANGE_700, "⚠"),
        NotificationType.INFO: (ft.Colors.BLUE_700, "ℹ"),
    }
    
    @staticmethod
    def create(message: str, notification_type: NotificationType = NotificationType.INFO,
              duration_ms: int = 4000) -> ft.SnackBar:
        """
        Create a toast notification
        
        Args:
            message: Notification message
            notification_type: Type of notification
            duration_ms: Duration to show (milliseconds)
        
        Returns:
            Flet SnackBar widget
        """
        color, icon = ToastNotification.TYPE_COLORS.get(
            notification_type,
            (ft.Colors.BLUE_700, "ℹ")
        )
        
        # Format message with icon
        display_msg = f"{icon} {message}"
        
        snackbar = ft.SnackBar(
            ft.Text(display_msg, color=ft.Colors.WHITE, weight="bold"),
            bgcolor=color,
            open=False,
            duration=duration_ms,
        )
        
        return snackbar
    
    @staticmethod
    def show(page: ft.Page, message: str, 
            notification_type: NotificationType = NotificationType.INFO,
            duration_ms: int = 4000):
        """Show a toast notification immediately"""
        page.snack_bar = ToastNotification.create(message, notification_type, duration_ms)
        page.snack_bar.open = True
        page.update()


class ProgressDialog:
    """Dialog with progress bar for long operations"""
    
    def __init__(self, title: str, max_value: int = 100, show_percentage: bool = True):
        """
        Initialize progress dialog
        
        Args:
            title: Dialog title
            max_value: Maximum progress value
            show_percentage: Whether to show percentage
        """
        self.title = title
        self.max_value = max_value
        self.show_percentage = show_percentage
        self.current_value = 0
        
        # Progress bar
        self.progress_bar = ft.ProgressBar(
            value=0,
            width=400,
            height=10,
            bgcolor=ft.Colors.GREY_300,
            color=ft.Colors.BLUE_700,
        )
        
        # Progress text
        self.progress_text = ft.Text(
            "0%",
            size=12,
            color=ft.Colors.WHITE,
            weight="bold",
        )
        
        # Status message
        self.status_message = ft.Text(
            "Processing...",
            size=12,
            color=ft.Colors.GREY_400,
        )
        
        # Dialog
        self.dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Column(
                controls=[
                    self.progress_bar,
                    ft.Row(
                        controls=[
                            ft.Text("Progress: ", size=11, color=ft.Colors.GREY_400),
                            self.progress_text,
                        ],
                        spacing=5,
                    ),
                    self.status_message,
                ],
                spacing=15,
                width=450,
            ),
            modal=True,
        )
    
    def update_progress(self, current: int, status: str = ""):
        """
        Update progress
        
        Args:
            current: Current progress value
            status: Status message
        """
        self.current_value = current
        percentage = (current / self.max_value * 100) if self.max_value > 0 else 0
        
        self.progress_bar.value = min(current / self.max_value, 1.0)
        
        if self.show_percentage:
            self.progress_text.value = f"{percentage:.0f}%"
        else:
            self.progress_text.value = f"{current}/{self.max_value}"
        
        if status:
            self.status_message.value = status
    
    def open(self, page: ft.Page):
        """Show the progress dialog"""
        self.dialog.open = True
        page.overlay.append(self.dialog)
        page.update()
    
    def close(self, page: ft.Page):
        """Close the progress dialog"""
        self.dialog.open = False
        page.update()


class ConfirmDialog:
    """Modal confirmation dialog for destructive operations"""
    
    def __init__(self, title: str, content: str, confirm_text: str = "Confirm",
                cancel_text: str = "Cancel", danger: bool = False):
        """
        Initialize confirmation dialog
        
        Args:
            title: Dialog title
            content: Dialog content/message
            confirm_text: Confirm button text
            cancel_text: Cancel button text
            danger: Whether this is a dangerous operation (red button)
        """
        self.title = title
        self.content = content
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.danger = danger
        self.confirm_callback = None
        self.cancel_callback = None
        
        # Dialog
        self.dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(content, size=13),
            actions=[
                ft.TextButton(
                    cancel_text,
                    on_click=self._on_cancel,
                ),
                ft.TextButton(
                    confirm_text,
                    on_click=self._on_confirm,
                    style=ft.ButtonStyle(
                        color=ft.Colors.RED_700 if danger else ft.Colors.BLUE_700
                    ),
                ),
            ],
            modal=True,
        )
    
    def _on_confirm(self, e):
        """Handle confirm click"""
        self.dialog.open = False
        if hasattr(self, '_page'):
            self._page.update()
        if self.confirm_callback:
            self.confirm_callback()
    
    def _on_cancel(self, e):
        """Handle cancel click"""
        self.dialog.open = False
        if hasattr(self, '_page'):
            self._page.update()
        if self.cancel_callback:
            self.cancel_callback()
    
    def on_confirm(self, callback: Callable):
        """Set confirm callback"""
        self.confirm_callback = callback
        return self
    
    def on_cancel(self, callback: Callable):
        """Set cancel callback"""
        self.cancel_callback = callback
        return self
    
    def show(self, page: ft.Page):
        """Show the dialog"""
        self._page = page
        self.dialog.open = True
        page.overlay.append(self.dialog)
        page.update()


class OperationHistory:
    """Track and display operation history"""
    
    class Operation:
        """Single operation record"""
        
        def __init__(self, operation_type: str, description: str, status: str = "pending"):
            self.operation_type = operation_type
            self.description = description
            self.status = status  # pending, in-progress, completed, failed
            self.timestamp = datetime.now()
            self.duration_seconds = 0
            self.error_message = None
            self.result_data = {}
        
        def mark_completed(self, duration: float = 0):
            """Mark operation as completed"""
            self.status = "completed"
            self.duration_seconds = duration
        
        def mark_failed(self, error: str, duration: float = 0):
            """Mark operation as failed"""
            self.status = "failed"
            self.error_message = error
            self.duration_seconds = duration
        
        def get_display_text(self) -> str:
            """Get formatted display text"""
            status_icon = {
                "pending": "⏳",
                "in-progress": "▶",
                "completed": "✓",
                "failed": "✗",
            }.get(self.status, "?")
            
            time_str = self.timestamp.strftime("%H:%M:%S")
            duration_str = f"({self.duration_seconds:.1f}s)" if self.duration_seconds > 0 else ""
            
            return f"{status_icon} [{time_str}] {self.operation_type}: {self.description} {duration_str}"
    
    def __init__(self, max_history: int = 50):
        """
        Initialize operation history
        
        Args:
            max_history: Maximum number of operations to keep
        """
        self.operations: List[OperationHistory.Operation] = []
        self.max_history = max_history
        self.current_operation: Optional[OperationHistory.Operation] = None
    
    def start_operation(self, operation_type: str, description: str) -> Operation:
        """Start tracking an operation"""
        operation = OperationHistory.Operation(operation_type, description, "in-progress")
        self.operations.append(operation)
        self.current_operation = operation
        
        # Keep only max_history operations
        if len(self.operations) > self.max_history:
            self.operations = self.operations[-self.max_history:]
        
        error_logger.info(f"Operation started: {operation_type} - {description}")
        return operation
    
    def end_operation(self, operation: Operation, success: bool = True,
                     error_message: str = None, duration: float = 0):
        """End tracking an operation"""
        if success:
            operation.mark_completed(duration)
            error_logger.info(f"Operation completed: {operation.operation_type} - {duration:.1f}s")
        else:
            operation.mark_failed(error_message or "Unknown error", duration)
            error_logger.error(f"Operation failed: {operation.operation_type} - {error_message}")
    
    def get_history_text(self, limit: int = 10) -> str:
        """Get formatted history text"""
        recent = self.operations[-limit:]
        return "\n".join(op.get_display_text() for op in recent)
    
    def get_history_rows(self, limit: int = 10) -> List[ft.DataRow]:
        """Get history as DataTable rows"""
        rows = []
        recent = self.operations[-limit:]
        
        for op in recent:
            status_color = {
                "pending": ft.Colors.GREY_400,
                "in-progress": ft.Colors.BLUE_400,
                "completed": ft.Colors.GREEN_400,
                "failed": ft.Colors.RED_400,
            }.get(op.status, ft.Colors.GREY_400)
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(op.timestamp.strftime("%H:%M:%S"), size=11, color=ft.Colors.GREY_400)),
                        ft.DataCell(ft.Text(op.operation_type, size=11, color=ft.Colors.WHITE, weight="bold")),
                        ft.DataCell(ft.Text(op.description, size=11, color=ft.Colors.GREY_300)),
                        ft.DataCell(ft.Text(op.status.upper(), size=11, color=status_color, weight="bold")),
                        ft.DataCell(ft.Text(f"{op.duration_seconds:.2f}s", size=11, color=ft.Colors.GREY_400)),
                    ],
                )
            )
        
        return rows


class UndoManager:
    """Manage undo/redo functionality"""
    
    class Action:
        """Single undoable action"""
        
        def __init__(self, description: str, undo_func: Callable, redo_func: Callable):
            self.description = description
            self.undo_func = undo_func
            self.redo_func = redo_func
            self.timestamp = datetime.now()
        
        def undo(self):
            """Execute undo"""
            try:
                self.undo_func()
                error_logger.info(f"Undo: {self.description}")
                return True
            except Exception as e:
                error_logger.error(f"Undo failed: {self.description} - {str(e)}")
                return False
        
        def redo(self):
            """Execute redo"""
            try:
                self.redo_func()
                error_logger.info(f"Redo: {self.description}")
                return True
            except Exception as e:
                error_logger.error(f"Redo failed: {self.description} - {str(e)}")
                return False
    
    def __init__(self, max_stack: int = 20):
        """
        Initialize undo manager
        
        Args:
            max_stack: Maximum undo/redo stack size
        """
        self.undo_stack: List[UndoManager.Action] = []
        self.redo_stack: List[UndoManager.Action] = []
        self.max_stack = max_stack
    
    def record_action(self, description: str, undo_func: Callable, redo_func: Callable):
        """
        Record an action that can be undone
        
        Args:
            description: Action description
            undo_func: Function to undo the action
            redo_func: Function to redo the action
        """
        action = UndoManager.Action(description, undo_func, redo_func)
        self.undo_stack.append(action)
        self.redo_stack.clear()  # Clear redo stack when new action recorded
        
        # Keep stack within max size
        if len(self.undo_stack) > self.max_stack:
            self.undo_stack = self.undo_stack[-self.max_stack:]
        
        error_logger.debug(f"Action recorded: {description}")
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self.redo_stack) > 0
    
    def undo(self) -> bool:
        """Perform undo"""
        if not self.can_undo():
            return False
        
        action = self.undo_stack.pop()
        if action.undo():
            self.redo_stack.append(action)
            return True
        else:
            self.undo_stack.append(action)  # Restore if undo failed
            return False
    
    def redo(self) -> bool:
        """Perform redo"""
        if not self.can_redo():
            return False
        
        action = self.redo_stack.pop()
        if action.redo():
            self.undo_stack.append(action)
            return True
        else:
            self.redo_stack.append(action)  # Restore if redo failed
            return False
    
    def get_undo_description(self) -> str:
        """Get description of next undo action"""
        if self.can_undo():
            return f"Undo: {self.undo_stack[-1].description}"
        return "Nothing to undo"
    
    def get_redo_description(self) -> str:
        """Get description of next redo action"""
        if self.can_redo():
            return f"Redo: {self.redo_stack[-1].description}"
        return "Nothing to redo"


class OperationProgressTracker:
    """Track progress of multi-step operations"""
    
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        """
        Initialize progress tracker
        
        Args:
            total_items: Total number of items to process
            operation_name: Name of the operation
        """
        self.total_items = total_items
        self.operation_name = operation_name
        self.processed_items = 0
        self.failed_items = 0
        self.successful_items = 0
        self.start_time = datetime.now()
    
    def increment_success(self, count: int = 1):
        """Mark items as successfully processed"""
        self.processed_items += count
        self.successful_items += count
    
    def increment_failure(self, count: int = 1):
        """Mark items as failed"""
        self.processed_items += count
        self.failed_items += count
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage"""
        if self.total_items == 0:
            return 0
        return (self.processed_items / self.total_items) * 100
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def estimated_remaining_seconds(self) -> float:
        """Estimate remaining time"""
        if self.processed_items == 0:
            return 0
        avg_per_item = self.elapsed_seconds / self.processed_items
        remaining_items = self.total_items - self.processed_items
        return avg_per_item * remaining_items
    
    def get_status_message(self) -> str:
        """Get formatted status message"""
        msg = f"{self.operation_name}: {self.processed_items}/{self.total_items} "
        msg += f"({self.progress_percentage:.0f}%) "
        msg += f"[✓{self.successful_items} ✗{self.failed_items}]"
        
        if self.processed_items > 0 and self.processed_items < self.total_items:
            remaining = self.estimated_remaining_seconds
            msg += f" ETA: {remaining:.0f}s"
        
        return msg
