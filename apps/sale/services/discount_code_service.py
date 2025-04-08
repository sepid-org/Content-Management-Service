from typing import Any, Optional

from django.db import transaction

from apps.accounts.models import DiscountCode, Merchandise
from apps.accounts.utils.user_management import find_user_in_website


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


@transaction.atomic()
def create_discount_code(
    data: dict[str, Any],
    merchandise_ids: list[str],
    username: Optional[str] = None,
    website: Optional[str] = None,
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
    # Create discount code
    discount_code = DiscountCode.objects.create_discount_code(**data)

    # Add merchandises
    for merchandise_id in merchandise_ids:
        merchandise = Merchandise.objects.get(id=merchandise_id)
        discount_code.merchandises.add(merchandise)

    # Add user (if provided)
    if username and website:
        target_user = find_user_in_website(
            user_data={"username": username}, website=website
        )
        discount_code.user = target_user
        discount_code.save()

    return discount_code
