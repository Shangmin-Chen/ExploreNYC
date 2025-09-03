"""
Error handling utilities for the ExploreNYC application.

This module provides comprehensive error handling including:
- Custom exception classes
- User-friendly error messages
- API error handling and translation
- Validation error handling
- Safe execution wrappers
- Logging and error tracking

Author: ExploreNYC Team
Version: 1.0.0
"""

from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Custom Exception Classes
# =============================================================================

class ExploreNYCError(Exception):
    """
    Base exception class for all ExploreNYC application errors.
    
    This serves as the parent class for all custom exceptions in the application.
    """
    pass

class APIError(ExploreNYCError):
    """
    Exception raised for API-related errors.
    
    This includes network errors, API rate limits, authentication failures,
    and other issues related to external API communication.
    """
    pass

class ConfigurationError(ExploreNYCError):
    """
    Exception raised for configuration-related errors.
    
    This includes missing API keys, invalid configuration values,
    and other setup-related issues.
    """
    pass

class ValidationError(ExploreNYCError):
    """
    Exception raised for data validation errors.
    
    This includes invalid input data, missing required fields,
    and other data integrity issues.
    """
    pass

def handle_api_error(error: Exception) -> str:
    """Handle API errors and return user-friendly messages."""
    error_msg = str(error)
    
    if "TooManyRequestsError" in error_msg or "429" in error_msg:
        return "I'm currently experiencing high traffic. Please wait a moment and try again, or consider upgrading your API plan for higher rate limits."
    elif "API key" in error_msg.lower():
        return "There's an issue with the API configuration. Please check your Cohere API key."
    elif "ConnectionError" in error_msg or "TimeoutError" in error_msg:
        return "I'm having trouble connecting to the service. Please check your internet connection and try again."
    else:
        logger.error(f"Unhandled API error: {error_msg}")
        return f"I'm sorry, I encountered an error while processing your request: {error_msg[:100]}... Please try again."

def handle_validation_error(error: Exception) -> str:
    """Handle validation errors and return user-friendly messages."""
    error_msg = str(error)
    
    if "required" in error_msg.lower():
        return "Please provide all required information to continue."
    elif "invalid" in error_msg.lower():
        return "The information provided is not valid. Please check your input and try again."
    else:
        return f"Validation error: {error_msg}"

def handle_configuration_error(error: Exception) -> str:
    """Handle configuration errors and return user-friendly messages."""
    error_msg = str(error)
    
    if "api key" in error_msg.lower():
        return "API key is missing or invalid. Please check your configuration."
    elif "environment" in error_msg.lower():
        return "Environment configuration is incomplete. Please check your .env file."
    else:
        return f"Configuration error: {error_msg}"

def safe_execute(func, *args, **kwargs) -> tuple[Any, Optional[str]]:
    """
    Safely execute a function and return result with error message.
    
    Returns:
        tuple: (result, error_message)
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except APIError as e:
        return None, handle_api_error(e)
    except ValidationError as e:
        return None, handle_validation_error(e)
    except ConfigurationError as e:
        return None, handle_configuration_error(e)
    except Exception as e:
        logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
        return None, f"An unexpected error occurred: {str(e)[:100]}..."

def log_error(error: Exception, context: str = "") -> None:
    """Log an error with context information."""
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)

def validate_required_fields(data: Dict[str, Any], required_fields: list[str]) -> None:
    """Validate that required fields are present in data."""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

def validate_api_key(api_key: Optional[str], service_name: str) -> None:
    """Validate that an API key is present and not placeholder."""
    if not api_key:
        raise ConfigurationError(f"{service_name} API key is missing")
    
    if api_key in ["your_api_key_here", "your_cohere_api_key_here", ""]:
        raise ConfigurationError(f"Please update your {service_name} API key in the .env file")
