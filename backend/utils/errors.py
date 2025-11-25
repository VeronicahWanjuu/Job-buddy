class ValidationError(Exception):
    """Raised when validation fails"""
    pass

class NotFoundError(Exception):
    """Raised when resource not found"""
    pass

class UnauthorizedError(Exception):
    """Raised when user is not authorized"""
    pass