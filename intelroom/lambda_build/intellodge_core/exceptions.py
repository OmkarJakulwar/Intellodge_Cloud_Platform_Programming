"""
Custom exceptions for the IntelRev application.
These standardize error handling across modules.
"""

class IntelRevError(Exception):
    """Base class for all IntelRev-specific exceptions."""
    pass

class NotFoundError(IntelRevError):
    """Raised when an item or resource is missing."""
    pass

class ValidationError(IntelRevError):
    """Raised when data validation fails."""
    pass

class PermissionDenied(IntelRevError):
    """Raised when a user is unauthorized for an action."""
    pass

class ServiceError(IntelRevError):
    """Generic service or backend failure."""
    pass
