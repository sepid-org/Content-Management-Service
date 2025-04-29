class ServiceException(Exception):
    "Base exception for all service exceptoins"

    default_message = "An error occurred"
    default_code = "service_error"

    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(ServiceException):
    """Resource not found exception"""

    default_message = "Resource not found"
    default_code = "not_found"


class DuplicateException(ServiceException):
    """Duplicate resource exception"""

    default_message = "Resource already exists"
    default_code = "duplicate_resource"


class ValidationException(ServiceException):
    """Validation failure exception"""

    default_message = "Validation failed"
    default_code = "validation_error"
