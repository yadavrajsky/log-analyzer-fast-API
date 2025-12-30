from datetime import datetime
from typing import Optional

def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse a timestamp string in the format YYYY-MM-DD HH:MM:SS.
    
    Args:
        timestamp_str: Timestamp string to parse
    
    Returns:
        Parsed datetime object
    
    Raises:
        ValueError: If timestamp format is invalid
    """
    try:
        return datetime.strptime(timestamp_str.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValueError(
            f"Invalid timestamp format: '{timestamp_str}'. "
            f"Expected format: YYYY-MM-DD HH:MM:SS (e.g., 2025-05-07 10:00:00)"
        )


def validate_page_size(page_size: int, max_page_size: int = 200) -> int:
    """
    Validate and constrain page size.
    
    Args:
        page_size: Requested page size
        max_page_size: Maximum allowed page size
    
    Returns:
        Validated page size
    
    Raises:
        ValueError: If page size is invalid
    """
    if page_size < 1:
        raise ValueError("Page size must be at least 1")
    
    if page_size > max_page_size:
        return max_page_size
    
    return page_size


def validate_page_number(page: int) -> int:
    """
    Validate page number.
    
    Args:
        page: Page number to validate
    
    Returns:
        Validated page number
    
    Raises:
        ValueError: If page number is invalid
    """
    if page < 1:
        raise ValueError("Page number must be at least 1")
    
    return page


def format_timestamp_for_query(dt: datetime) -> str:
    """
    Format datetime for query string representation.
    
    Args:
        dt: Datetime object to format
    
    Returns:
        Formatted timestamp string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")
