from datetime import datetime
from typing import Any, Optional

from django.db import IntegrityError, transaction

from apps.accounts.models import DiscountCode, Merchandise
from apps.accounts.utils.user_management import find_user
from apps.sale.exceptions import (
    DiscountCodeDuplicate,
    DiscountCodeExpired,
    DiscountCodeInvalidUser,
    MerchandiseNotFound,
)


def get_program_discount_codes(
    program_slug: Optional[str] = None,
) -> list[DiscountCode]:
    """
    Get discount codes, optionally filtered by program slug.

    Args:
        program_slug: Optional program slug to filter by

    Returns:
        List of DiscountCode instances
    """
    queryset = DiscountCode.objects.order_by("-id")

    if program_slug:
        queryset = queryset.filter(
            merchandises__program__slug=program_slug
        ).distinct()

    return list(queryset)


@transaction.atomic
def create_discount_code(
    data: dict[str, Any],
    merchandise_ids: list[str],
    username: Optional[str] = None,
) -> DiscountCode:
    """
    Create a discount code with associated merchandises and user.

    Args:
        data: The discount code data (value, expiration_date, etc.)
        merchandise_ids: List of merchandise IDs to associate
        username: Optional username to find and associate
        website: Optional website for user lookup

    Returns:
        The created DiscountCode instance
    """
    expires_at = data.get("expiration_date")
    if expires_at is not None and expires_at < datetime.now():
        raise DiscountCodeExpired(details={"expiration_date": expires_at})

    # Create discount code
    try:
        discount_code = DiscountCode.objects.create_discount_code(**data)
    except IntegrityError as err:
        raise DiscountCodeDuplicate(details={"code": data["code"]}) from err

    # Add merchandises
    for merchandise_id in merchandise_ids:
        try:
            merchandise = Merchandise.objects.get(id=merchandise_id)
        except Merchandise.DoesNotExist as err:
            raise MerchandiseNotFound(
                details={"merchandise": merchandise_id}
            ) from err
        discount_code.merchandises.add(merchandise)

    # Add user (if provided)
    if username:
        target_user = find_user(user_data={"username": username})

        if target_user is None:
            raise DiscountCodeInvalidUser(details={"username": username})

        discount_code.user = target_user
        discount_code.save()

    return discount_code
