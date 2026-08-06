"""
Comprehensive error handling and logging system for LMS application
Provides: file logging, error decorators, retry logic, user-friendly messages
"""

import logging
import os
import traceback
import time
from functools import wraps
from datetime import datetime
from pathlib import Path


class ErrorLogger:
    """Centralized error logging system"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Initialize logger with file and console handlers"""
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self._logger = logging.getLogger("LMS")
        self._logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # File handler - logs everything
        log_file = log_dir / f"lms_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler - logs warnings and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message"""
        self._logger.info(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self._logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._logger.warning(message)
    
    def error(self, message: str, exc_info=False):
        """Log error message with optional exception info"""
        self._logger.error(message, exc_info=exc_info)
    
    def exception(self, message: str):
        """Log exception with full traceback"""
        self._logger.exception(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self._logger.critical(message)


# Singleton instance
error_logger = ErrorLogger()


class UserFriendlyError(Exception):
    """User-friendly error messages with logging"""
    
    # Error message mappings
    ERROR_MESSAGES = {
        # File operations
        'file_not_found': 'File not found. Please check the file path and try again.',
        'file_read_error': 'Error reading file. File may be corrupted or in use by another application.',
        'file_write_error': 'Error writing file. Check disk space and permissions.',
        'file_format_error': 'Invalid file format. Please use CSV or XLSX files only.',
        
        # Database operations
        'db_connection_error': 'Database connection failed. Please restart the application.',
        'db_commit_error': 'Failed to save data to database.',
        'db_query_error': 'Error retrieving data from database.',
        'db_constraint_error': 'Data constraint violation. Some data may already exist.',
        
        # Validation errors
        'validation_error': 'Invalid input. Please check all fields and try again.',
        'duplicate_entry': 'This record already exists in the database.',
        'missing_required_field': 'Please fill in all required fields.',
        
        # Import/Export errors
        'import_partial_error': 'Some records failed to import. Check the error details.',
        'import_failed': 'Import failed. Please check the file format and try again.',
        'export_failed': 'Failed to export data. Please try again.',
        
        # Network/External
        'network_error': 'Network connection failed. Please check your connection.',
        'timeout_error': 'Operation timed out. Please try again.',
        'external_service_error': 'External service unavailable. Please try again later.',
        
        # Generic
        'unknown_error': 'An unexpected error occurred. Please try again.',
        'operation_failed': 'Operation failed. Please check the error log for details.',
    }
    
    @staticmethod
    def get_message(error_key: str, details: str = '') -> str:
        """
        Get user-friendly error message
        
        Args:
            error_key: Key to look up in ERROR_MESSAGES
            details: Additional details to append
        
        Returns:
            User-friendly error message
        """
        base_message = UserFriendlyError.ERROR_MESSAGES.get(
            error_key,
            UserFriendlyError.ERROR_MESSAGES['unknown_error']
        )
        
        if details:
            return f"{base_message}\n\nDetails: {details}"
        return base_message
    
    @staticmethod
    def format_for_ui(title: str, message: str, error_code: str = '') -> str:
        """Format error for UI display"""
        formatted = f"[ERROR] {title}\n{message}"
        if error_code:
            formatted += f"\n(Code: {error_code})"
        return formatted


def log_exception(func):
    """
    Decorator to log exceptions with full traceback
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_logger.exception(f"Exception in {func.__name__}: {str(e)}")
            raise
    return wrapper


def handle_errors(error_key: str = 'operation_failed', show_dialog=False):
    """
    Decorator to handle errors with user-friendly messages
    
    Usage:
        @handle_errors('import_failed')
        def import_data():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_logger.exception(f"Error in {func.__name__}")
                user_message = UserFriendlyError.get_message(error_key, str(e))
                return {'success': False, 'message': user_message, 'error': str(e)}
        return wrapper
    return decorator


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, 
                 backoff_multiplier: float = 2.0, max_delay: float = 30.0):
        """
        Args:
            max_attempts: Maximum number of attempts
            delay: Initial delay between retries (seconds)
            backoff_multiplier: Multiply delay by this after each attempt
            max_delay: Maximum delay between retries
        """
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay


class RetryableOperation:
    """Handles retryable operations with exponential backoff"""
    
    @staticmethod
    def execute(func, config: RetryConfig = None, *args, **kwargs):
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            config: RetryConfig object
            args, kwargs: Arguments to pass to function
        
        Returns:
            (success: bool, result: any, error_message: str)
        """
        if config is None:
            config = RetryConfig()
        
        last_error = None
        current_delay = config.delay
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                error_logger.debug(f"Attempt {attempt}/{config.max_attempts} for {func.__name__}")
                result = func(*args, **kwargs)
                
                if attempt > 1:
                    error_logger.info(f"{func.__name__} succeeded on attempt {attempt}")
                
                return True, result, None
            
            except Exception as e:
                last_error = str(e)
                error_logger.warning(
                    f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {last_error}"
                )
                
                # Don't retry on last attempt
                if attempt < config.max_attempts:
                    error_logger.debug(f"Retrying in {current_delay:.1f} seconds...")
                    time.sleep(current_delay)
                    current_delay = min(
                        current_delay * config.backoff_multiplier,
                        config.max_delay
                    )
        
        error_logger.error(
            f"All {config.max_attempts} attempts failed for {func.__name__}: {last_error}"
        )
        return False, None, last_error


class FileOperationHandler:
    """Handles file operations with retry logic and error handling"""
    
    DEFAULT_RETRY_CONFIG = RetryConfig(
        max_attempts=3,
        delay=0.5,
        backoff_multiplier=2.0,
        max_delay=5.0
    )
    
    @staticmethod
    def read_file(file_path: str, retry_config: RetryConfig = None) -> tuple:
        """
        Read file with retry logic
        
        Returns:
            (success: bool, content: str or None, error_message: str or None)
        """
        if retry_config is None:
            retry_config = FileOperationHandler.DEFAULT_RETRY_CONFIG
        
        def _read():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        success, content, error = RetryableOperation.execute(
            _read, retry_config
        )
        
        if not success:
            error_msg = UserFriendlyError.get_message('file_read_error', error)
            return False, None, error_msg
        
        return True, content, None
    
    @staticmethod
    def write_file(file_path: str, content: str, 
                  retry_config: RetryConfig = None) -> tuple:
        """
        Write file with retry logic
        
        Returns:
            (success: bool, error_message: str or None)
        """
        if retry_config is None:
            retry_config = FileOperationHandler.DEFAULT_RETRY_CONFIG
        
        def _write():
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        success, _, error = RetryableOperation.execute(
            _write, retry_config
        )
        
        if not success:
            error_msg = UserFriendlyError.get_message('file_write_error', error)
            return False, error_msg
        
        return True, None
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)


class DatabaseOperationHandler:
    """Handles database operations with error recovery"""
    
    @staticmethod
    def safe_commit(session, operation_name: str = 'operation') -> tuple:
        """
        Safely commit database transaction
        
        Returns:
            (success: bool, error_message: str or None)
        """
        try:
            session.commit()
            error_logger.debug(f"Database commit successful for {operation_name}")
            return True, None
        except Exception as e:
            session.rollback()
            error_logger.exception(f"Database commit failed for {operation_name}")
            error_msg = UserFriendlyError.get_message('db_commit_error', str(e))
            return False, error_msg
    
    @staticmethod
    def safe_query(session, query_func, operation_name: str = 'query') -> tuple:
        """
        Safely execute database query
        
        Args:
            session: Database session
            query_func: Function that performs the query
            operation_name: Name of operation for logging
        
        Returns:
            (success: bool, result: any or None, error_message: str or None)
        """
        try:
            result = query_func(session)
            error_logger.debug(f"Database query successful for {operation_name}")
            return True, result, None
        except Exception as e:
            error_logger.exception(f"Database query failed for {operation_name}")
            error_msg = UserFriendlyError.get_message('db_query_error', str(e))
            return False, None, error_msg


class ImportExportHandler:
    """Handles import/export operations with detailed error tracking"""
    
    class ImportResult:
        """Result of import operation"""
        
        def __init__(self):
            self.successful_count = 0
            self.failed_count = 0
            self.errors = []
            self.warnings = []
        
        @property
        def total_count(self):
            return self.successful_count + self.failed_count
        
        @property
        def success_rate(self):
            if self.total_count == 0:
                return 0
            return (self.successful_count / self.total_count) * 100
        
        def add_success(self, item_id: str = ''):
            self.successful_count += 1
            error_logger.debug(f"Import success for item: {item_id}")
        
        def add_error(self, item_id: str, error: str):
            self.failed_count += 1
            self.errors.append(f"Item {item_id}: {error}")
            error_logger.warning(f"Import error for item {item_id}: {error}")
        
        def add_warning(self, warning: str):
            self.warnings.append(warning)
            error_logger.warning(f"Import warning: {warning}")
        
        def get_summary(self) -> str:
            """Get human-readable summary"""
            summary = f"Import Complete: {self.successful_count} successful"
            
            if self.failed_count > 0:
                summary += f", {self.failed_count} failed"
            
            summary += f" ({self.success_rate:.1f}% success rate)"
            
            if self.warnings:
                summary += f"\nWarnings: {len(self.warnings)}"
            
            if self.errors and len(self.errors) <= 5:
                summary += "\nErrors:\n" + "\n".join(self.errors)
            elif self.errors:
                summary += f"\nFirst 5 errors:\n" + "\n".join(self.errors[:5])
                summary += f"\n... and {len(self.errors) - 5} more errors"
            
            return summary
    
    @staticmethod
    def get_import_result() -> 'ImportExportHandler.ImportResult':
        """Create new import result tracker"""
        return ImportExportHandler.ImportResult()


def log_operation(operation_name: str):
    """
    Decorator to log operation start/end with timing
    
    Usage:
        @log_operation('Import Data')
        def import_data():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error_logger.info(f"Starting operation: {operation_name}")
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                error_logger.info(f"Completed operation: {operation_name} ({elapsed:.2f}s)")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                error_logger.error(f"Failed operation: {operation_name} ({elapsed:.2f}s) - {str(e)}")
                raise
        return wrapper
    return decorator


def create_snackbar_message(success: bool, title: str, message: str, 
                           details: str = '') -> str:
    """
    Create formatted message for snack bar
    
    Returns:
        Formatted string ready for UI display
    """
    prefix = "[OK]" if success else "[ERROR]"
    formatted = f"{prefix} {title}\n{message}"
    
    if details:
        formatted += f"\n{details}"
    
    return formatted
