from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.core.exceptions import (
    DuplicateException,
    NotFoundException,
    ServiceException,
)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    if response is not None:
        return response

    # Initialize default error structure
    error_data = {
        "error": {
            "code": "server_error",
            "message": "An unexpected error occurred",
        }
    }
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    # Handle our custom service exceptions
    if isinstance(exc, ServiceException):
        error_data["error"]["code"] = exc.code
        error_data["error"]["message"] = exc.message

        if exc.details:
            error_data["error"]["details"] = exc.details

        # Determine status code based on exception type or code
        if isinstance(exc, NotFoundException) or "not_found" in exc.code:
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, DuplicateException) or "duplicate" in exc.code:
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_400_BAD_REQUEST

    # Handle Django's validation errors
    elif isinstance(exc, ValidationError):
        error_data["error"]["code"] = "validation_error"
        error_data["error"]["message"] = "Validation failed"
        error_data["error"]["details"] = (
            exc.message_dict
            if hasattr(exc, "message_dict")
            else {"non_field_errors": [str(exc)]}
        )
        status_code = status.HTTP_400_BAD_REQUEST

    # Handle database integrity errors (like unique constraint violations)
    elif isinstance(exc, IntegrityError):
        error_data["error"]["code"] = "data_integrity_error"

        if (
            "unique constraint" in str(exc).lower()
            or "duplicate key" in str(exc).lower()
        ):
            error_data["error"]["code"] = "duplicate_resource"
            error_data["error"]["message"] = (
                "A resource with these details already exists"
            )
            status_code = status.HTTP_409_CONFLICT
        else:
            error_data["error"]["message"] = "Data integrity error"
            status_code = status.HTTP_400_BAD_REQUEST

    # Handle other exceptions by reporting a server error
    # but include more details in development
    else:
        import os

        if os.environ.get("DJANGO_DEBUG", "False").lower() == "true":
            error_data["error"]["details"] = str(exc)

        import logging

        logger = logging.getLogger("django")
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return Response(error_data, status=status_code)
