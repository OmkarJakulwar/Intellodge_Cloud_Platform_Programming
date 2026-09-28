"""
Authentication & session utility functions.
Used in Django views to manage session-based logic.
"""

def get_current_user(request):
    """Extract current user info from session safely."""
    return {
        "username": request.session.get("username"),
        "email": request.session.get("email"),
        "role": request.session.get("role"),
        "is_authenticated": request.session.get("is_authenticated", False)
    }

def is_admin(request):
    """Check if the current user is an admin."""
    return str(request.session.get("role", "")).lower() == "admin"

def require_login(request):
    """Ensure a user is logged in; raise exception if not."""
    if not request.session.get("is_authenticated"):
        raise PermissionError("User not logged in.")
