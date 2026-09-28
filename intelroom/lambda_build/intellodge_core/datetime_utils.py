"""
Datetime utility functions for standardized timestamps and formatting.
"""

from datetime import datetime, timezone

def now_utc():
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()

def format_date(dt):
    """Convert datetime object to human-readable format."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_date(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    """Parse a string into a datetime object."""
    return datetime.strptime(date_str, fmt)
