from apps.core.error_codes import (
    ACCOUNT_ERRORS,
    DISCOUNT_ERRORS,
    MERCHANDISE_ERRORS,
    SALE_ERRORS,
)


class ServiceException(Exception):
    "Base exception for all service-level exceptoins"

    default_message = "An error occurred in the service"
    default_code = "service_error"

    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(message or self.default_message)


# Domain-specific exceptions
class AccountsException(ServiceException):
    "Base exception for accounts module"

    default_message = ACCOUNT_ERRORS["accounts_error"]
    default_code = "accounts_error"


class SaleException(ServiceException):
    "Base exception for sale module"

    default_message = SALE_ERRORS["sale_error"]
    default_code = "sale_error"


# Specific exceptions
class DiscountCodeException(SaleException):
    "Base exception for discount code operations"

    default_message = DISCOUNT_ERRORS["dc_error"]
    default_code = "discount_code_error"


class DiscountCodeNotFound(DiscountCodeException):
    default_message = DISCOUNT_ERRORS["dc_not_found"]
    default_code = "discount_code_not_found"


class DiscountCodeExpired(DiscountCodeException):
    default_message = DISCOUNT_ERRORS["dc_expired"]
    default_code = "discount_code_expired"


class DiscountCodeExhausted(DiscountCodeException):
    default_message = DISCOUNT_ERRORS["dc_exhausted"]
    default_code = "discount_code_exhausted"


class DiscountCodeInvalidUser(DiscountCodeException):
    default_message = DISCOUNT_ERRORS["dc_invalid_user"]
    default_code = "discount_code_invalid_user"


class DiscountCodeInvalidMerchandise(DiscountCodeException):
    default_message = DISCOUNT_ERRORS["dc_invalid_merchandise"]
    default_code = "discount_code_invalid_merchandise"


class MerchandiseException(SaleException):
    default_message = MERCHANDISE_ERRORS["merchandise_error"]
    default_code = "merchandise_error"


class MerchandiseNotFound(SaleException):
    default_message = MERCHANDISE_ERRORS["merchandise_not_found"]
    default_code = "merchandise_not_found"
