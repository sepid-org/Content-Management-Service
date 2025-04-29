from apps.core.error_codes import DISCOUNT_ERRORS, MERCHANDISE_ERRORS
from apps.core.exceptions import NotFoundException, ValidationException


class DiscountCodeNotFound(NotFoundException):
    default_message = DISCOUNT_ERRORS["not_found"]
    default_code = "discount_code_not_found"


class DiscountCodeExpired(ValidationException):
    default_message = DISCOUNT_ERRORS["expired"]
    default_code = "discount_code_expired"


class DiscountCodeDuplicate(ValidationException):
    default_message = DISCOUNT_ERRORS["duplicate"]
    default_code = "discount_code_duplicate"


class DiscountCodeExhausted(ValidationException):
    default_message = DISCOUNT_ERRORS["exhausted"]
    default_code = "discount_code_exhausted"


class DiscountCodeInvalidUser(ValidationException):
    default_message = DISCOUNT_ERRORS["invalid_user"]
    default_code = "discount_code_invalid_user"


class DiscountCodeInvalidMerchandise(ValidationException):
    default_message = DISCOUNT_ERRORS["invalid_merchandise"]
    default_code = "discount_code_invalid_merchandise"


class MerchandiseNotFound(NotFoundException):
    default_message = MERCHANDISE_ERRORS["not_found"]
    default_code = "merchandise_not_found"
