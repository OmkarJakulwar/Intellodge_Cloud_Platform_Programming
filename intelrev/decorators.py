from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def login_required_custom(view_func):
    """Checks if the user is authenticated via Cognito session"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            messages.warning(request, "Please log in to continue.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
    
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.session.get("is_authenticated"):
                return redirect("login")

            user_role = str(request.session.get("role", "")).lower().strip()
            if user_role not in allowed_roles:
                # Forbidden access — optional message
                from django.contrib import messages
                messages.error(request, "Access denied: insufficient privileges.")
                return redirect("home_dashboard")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

