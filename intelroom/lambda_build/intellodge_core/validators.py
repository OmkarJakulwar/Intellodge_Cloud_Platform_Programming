"""
Validation utilities for checking input fields and data structures.
Used across all service and form layers.
"""

def require_fields(data, required_fields):
    """Ensure required fields exist and are not empty."""
    missing = [f for f in required_fields if f not in data or data[f] in [None, ""]]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

def validate_email(email):
    import re
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, email):
        raise ValueError("Invalid email format.")
    return True

def validate_role(role, allowed_roles=("admin", "staff", "guest")):
    if role.lower() not in allowed_roles:
        raise ValueError(f"Invalid role '{role}'. Allowed: {', '.join(allowed_roles)}")
    return True
