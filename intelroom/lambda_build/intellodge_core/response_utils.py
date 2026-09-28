"""
Standard response helpers for views, services, and APIs.
Ensures consistent structure across modules.
"""

def success_response(data=None, message="Success"):
    return {
        "status": "success",
        "message": message,
        "data": data or {}
    }

def error_response(error, code=400):
    return {
        "status": "error",
        "message": str(error),
        "code": code
    }

def not_found_response(resource="Item"):
    return {
        "status": "error",
        "message": f"{resource} not found",
        "code": 404
    }

def validation_error_response(errors):
    return {
        "status": "error",
        "message": "Validation failed",
        "errors": errors,
        "code": 422
    }
