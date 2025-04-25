from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.core.exceptions import ServiceException


def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    # If it's already handled (e.g., ValidationError), return as is
    if response is not None:
        return response

    # Handle our custom ServiceExceptions
    if isinstance(exc, ServiceException):
        data = {
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        }

        # Add details if provided
        if exc.details:
            data["error"]["details"] = exc.details

        status_code = status.HTTP_400_BAD_REQUEST

        # Map specific exceptions to specific status codes
        if exc.code == "discount_code_not_found":
            status_code = status.HTTP_404_NOT_FOUND

        return Response(data, status=status_code)

    # For unexpected exceptions, return a generic server error
    return Response(
        {
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred",
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
