"""
Date and time utility functions for the ExploreNYC application.

This module provides comprehensive date and time handling including:
- Date range calculations (weekend, week, month)
- Date string parsing and formatting
- Time frame processing for user queries
- Date validation and conversion utilities

Author: ExploreNYC Team
Version: 1.0.0
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

def calculate_this_weekend(current_date: datetime) -> Tuple[datetime, datetime]:
    """
    Calculate this weekend's date range (Saturday to Sunday).
    
    Args:
        current_date (datetime): The current date to calculate from
        
    Returns:
        Tuple[datetime, datetime]: Start and end dates for this weekend
    """
    days_until_saturday = (5 - current_date.weekday()) % 7
    if days_until_saturday == 0:  # Today is Saturday
        saturday = current_date
    else:
        saturday = current_date + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    return (saturday, sunday)

def calculate_next_weekend(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate next weekend's date range."""
    this_weekend_start, _ = calculate_this_weekend(current_date)
    next_weekend_start = this_weekend_start + timedelta(days=7)
    next_weekend_end = next_weekend_start + timedelta(days=1)
    return (next_weekend_start, next_weekend_end)

def calculate_this_week(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate this week's date range (Monday to Sunday)."""
    days_since_monday = current_date.weekday()
    monday = current_date - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)
    return (monday, sunday)

def calculate_next_week(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate next week's date range."""
    this_week_start, _ = calculate_this_week(current_date)
    next_week_start = this_week_start + timedelta(days=7)
    next_week_end = next_week_start + timedelta(days=6)
    return (next_week_start, next_week_end)

def calculate_this_month(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate this month's date range."""
    start_of_month = current_date.replace(day=1)
    if current_date.month == 12:
        end_of_month = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
    return (start_of_month, end_of_month)

def calculate_next_month(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate next month's date range."""
    if current_date.month == 12:
        start_of_next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
    else:
        start_of_next_month = current_date.replace(month=current_date.month + 1, day=1)
    
    if start_of_next_month.month == 12:
        end_of_next_month = start_of_next_month.replace(year=start_of_next_month.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_next_month = start_of_next_month.replace(month=start_of_next_month.month + 1, day=1) - timedelta(days=1)
    
    return (start_of_next_month, end_of_next_month)

def calculate_today(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate today's date range."""
    return (current_date, current_date)

def calculate_tomorrow(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate tomorrow's date range."""
    tomorrow = current_date + timedelta(days=1)
    return (tomorrow, tomorrow)

def calculate_tonight(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate tonight's date range."""
    return (current_date, current_date)

def calculate_this_evening(current_date: datetime) -> Tuple[datetime, datetime]:
    """Calculate this evening's date range."""
    return (current_date, current_date)

def parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse date string into datetime object."""
    if not date_str:
        return None
    
    from .constants import DATE_FORMATS
    
    try:
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None

def process_time_frames(user_input: str) -> str:
    """
    Process user input to extract and calculate time frames.
    
    This function identifies time-related keywords in user input and appends
    the corresponding date ranges to help the AI agent understand temporal context.
    
    Args:
        user_input (str): The user's input text to process
        
    Returns:
        str: Processed input with date range information appended
    """
    current_date = datetime.now()
    processed_input = user_input
    
    # Define time frame patterns and their corresponding calculation functions
    time_patterns = {
        r'\bthis weekend\b': calculate_this_weekend,
        r'\bnext weekend\b': calculate_next_weekend,
        r'\bthis week\b': calculate_this_week,
        r'\bnext week\b': calculate_next_week,
        r'\bthis month\b': calculate_this_month,
        r'\bnext month\b': calculate_next_month,
        r'\btoday\b': calculate_today,
        r'\btomorrow\b': calculate_tomorrow,
        r'\btonight\b': calculate_tonight,
        r'\bthis evening\b': calculate_this_evening,
    }
    
    # Process each time pattern found in the input
    for pattern, calculator in time_patterns.items():
        if re.search(pattern, user_input, re.IGNORECASE):
            date_range = calculator(current_date)
            if date_range:
                start_date, end_date = date_range
                date_info = f" (date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
                processed_input = re.sub(pattern, f"\\g<0>{date_info}", processed_input, flags=re.IGNORECASE)
    
    return processed_input

def get_date_range_for_time_preference(time_preference: str) -> Optional[Tuple[datetime, datetime]]:
    """Get date range based on time preference string."""
    today = datetime.now().date()
    
    if time_preference == "Today":
        return (today, today)
    elif time_preference == "This weekend":
        return calculate_this_weekend(datetime.now())
    elif time_preference == "This week":
        week_end = today + timedelta(days=7)
        return (today, week_end)
    elif time_preference == "Next week":
        next_week_start = today + timedelta(days=7)
        next_week_end = next_week_start + timedelta(days=7)
        return (next_week_start, next_week_end)
    elif time_preference == "This month":
        month_end = today + timedelta(days=30)
        return (today, month_end)
    
    return None

def format_date_for_display(date_obj) -> str:
    """Format a date object for display."""
    if not date_obj:
        return "Date TBD"
    
    if isinstance(date_obj, str):
        return date_obj
    
    try:
        return date_obj.strftime("%B %d, %Y")
    except:
        return str(date_obj)
