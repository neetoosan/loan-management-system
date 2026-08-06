"""
Validation utilities for the LMS application
Provides centralized input validation and business rule checking
"""

import re
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validator:
    """Centralized validation utilities"""
    
    @staticmethod
    def validate_loan_amount(amount) -> tuple:
        """
        Validate loan amount
        Returns: (is_valid, error_message)
        """
        try:
            amt = float(amount)
            if amt <= 0:
                return False, "Loan amount must be greater than 0"
            if amt > 10_000_000:
                return False, "Loan amount exceeds maximum limit (₦10,000,000)"
            return True, ""
        except (ValueError, TypeError):
            return False, "Loan amount must be a valid number"
    
    @staticmethod
    def validate_interest_rate(rate) -> tuple:
        """
        Validate interest rate percentage
        Returns: (is_valid, error_message)
        """
        try:
            r = float(rate)
            if r < 0:
                return False, "Interest rate cannot be negative"
            if r > 100:
                return False, "Interest rate cannot exceed 100%"
            return True, ""
        except (ValueError, TypeError):
            return False, "Interest rate must be a valid number"
    
    @staticmethod
    def validate_duration(duration) -> tuple:
        """
        Validate loan duration in months
        Returns: (is_valid, error_message)
        """
        try:
            d = int(duration)
            if d <= 0:
                return False, "Duration must be at least 1 month"
            if d > 60:
                return False, "Duration cannot exceed 60 months"
            return True, ""
        except (ValueError, TypeError):
            return False, "Duration must be a valid integer"
    
    @staticmethod
    def validate_name(name, field_name="Name") -> tuple:
        """
        Validate name field (must not be empty)
        Returns: (is_valid, error_message)
        """
        if not name or not str(name).strip():
            return False, f"{field_name} cannot be empty"
        if len(str(name).strip()) < 2:
            return False, f"{field_name} must be at least 2 characters"
        if len(str(name).strip()) > 100:
            return False, f"{field_name} must not exceed 100 characters"
        return True, ""
    
    @staticmethod
    def validate_phone(phone) -> tuple:
        """
        Validate phone number format
        Returns: (is_valid, error_message)
        """
        if not phone or not str(phone).strip():
            return False, "Phone number cannot be empty"
        
        # Remove common separators and spaces
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', str(phone))
        
        # Check if it's numeric after cleaning
        if not cleaned.isdigit():
            return False, "Phone number must contain only digits"
        
        # Check length (most phone numbers are 7-15 digits)
        if len(cleaned) < 7 or len(cleaned) > 15:
            return False, "Phone number must be between 7 and 15 digits"
        
        return True, ""
    
    @staticmethod
    def validate_email(email) -> tuple:
        """
        Validate email address format
        Returns: (is_valid, error_message)
        """
        if not email or not str(email).strip():
            return True, ""  # Email is optional
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, str(email).strip()):
            return False, "Please enter a valid email address"
        
        return True, ""
    
    @staticmethod
    def validate_ippis(ippis) -> tuple:
        """
        Validate IPPIS number format
        Returns: (is_valid, error_message)
        """
        if not ippis or not str(ippis).strip():
            return True, ""  # IPPIS is optional
        
        ippis_clean = str(ippis).strip()
        
        # IPPIS should be numeric or alphanumeric
        if not re.match(r'^[a-zA-Z0-9]+$', ippis_clean):
            return False, "IPPIS number must contain only letters and numbers"
        
        if len(ippis_clean) < 4 or len(ippis_clean) > 20:
            return False, "IPPIS number must be between 4 and 20 characters"
        
        return True, ""
    
    @staticmethod
    def validate_date(date_str, date_format="%Y-%m-%d") -> tuple:
        """
        Validate date format
        Returns: (is_valid, error_message, datetime_object or None)
        """
        try:
            dt = datetime.strptime(date_str, date_format)
            return True, "", dt
        except ValueError:
            return False, f"Invalid date format. Expected {date_format}", None
        except Exception as e:
            return False, f"Date validation error: {str(e)}", None
    
    @staticmethod
    def validate_loan_creation(member_id, amount, interest_rate, duration, 
                               guarantor_name, guarantor_phone) -> list:
        """
        Validate all loan creation inputs
        Returns: list of error messages (empty if valid)
        """
        errors = []
        
        if not member_id:
            errors.append("Please select a member")
        
        valid, msg = Validator.validate_loan_amount(amount)
        if not valid:
            errors.append(msg)
        
        valid, msg = Validator.validate_interest_rate(interest_rate)
        if not valid:
            errors.append(msg)
        
        valid, msg = Validator.validate_duration(duration)
        if not valid:
            errors.append(msg)
        
        valid, msg = Validator.validate_name(guarantor_name, "Guarantor name")
        if not valid:
            errors.append(msg)
        
        valid, msg = Validator.validate_phone(guarantor_phone)
        if not valid:
            errors.append(msg)
        
        return errors
    
    @staticmethod
    def validate_member_creation(name, contact, email, ippis_number) -> list:
        """
        Validate all member creation inputs
        Returns: list of error messages (empty if valid)
        """
        errors = []
        
        valid, msg = Validator.validate_name(name, "Name")
        if not valid:
            errors.append(msg)
        
        if contact:
            valid, msg = Validator.validate_phone(contact)
            if not valid:
                errors.append(f"Contact: {msg}")
        
        if email:
            valid, msg = Validator.validate_email(email)
            if not valid:
                errors.append(f"Email: {msg}")
        
        if ippis_number:
            valid, msg = Validator.validate_ippis(ippis_number)
            if not valid:
                errors.append(f"IPPIS: {msg}")
        
        return errors
    
    @staticmethod
    def validate_contribution_amount(amount) -> tuple:
        """
        Validate contribution amount
        Returns: (is_valid, error_message)
        """
        try:
            amt = float(amount)
            if amt <= 0:
                return False, "Contribution amount must be greater than 0"
            if amt > 1_000_000:
                return False, "Contribution amount exceeds limit (₦1,000,000)"
            return True, ""
        except (ValueError, TypeError):
            return False, "Contribution amount must be a valid number"
    
    @staticmethod
    def validate_repayment_amount(amount, loan_total_due) -> tuple:
        """
        Validate repayment amount
        Returns: (is_valid, error_message)
        """
        try:
            amt = float(amount)
            if amt <= 0:
                return False, "Repayment amount must be greater than 0"
            if amt > loan_total_due * 2:  # Allow overpayment but flag suspicious amounts
                return False, "Repayment amount seems too high. Please verify."
            return True, ""
        except (ValueError, TypeError):
            return False, "Repayment amount must be a valid number"


def format_error_message(errors: list) -> str:
    """
    Format list of errors into a user-friendly message
    """
    if not errors:
        return ""
    
    if len(errors) == 1:
        return f"✗ {errors[0]}"
    
    message = "✗ Please fix the following errors:\n"
    for i, error in enumerate(errors, 1):
        message += f"{i}. {error}\n"
    
    return message.strip()

