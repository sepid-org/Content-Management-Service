from typing import Any, Optional

from django.db import transaction

from apps.accounts.models import DiscountCode, Merchandise, User
from apps.accounts.utils.user_management import find_user_in_website


class DiscountCodeService:
    @staticmethod
    def get_program_discount_codes(program_slug: str) -> list[DiscountCode]:
        """Get all discount codes for a specific program."""
        return (
            DiscountCode.objects.filter(
                merchandises__program__slug=program_slug
            )
            .distinct()
            .order_by("-id")
        )

    @staticmethod
    @transaction.atomic
    def create_discount_code(
        data: dict[str, Any],
        merchandise_ids: list[str],
        username: Optional[str] = None,
        website: Optional[str] = None,
    ) -> DiscountCode:
        """Create a discount code with associated merchandises and user."""
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

    @staticmethod
    def validate_discount_code(
        code: str, merchandise: Merchandise, user: Optional[User] = None
    ) -> DiscountCode | dict[str, Any]:
        """
        Validate a discount code for a specific merchandise and user.
        Returns the valid discount code or an error dict.
        """
        try:
            discount_code = DiscountCode.objects.get(code=code)

            # User-specific check
            if discount_code.user and user != discount_code.user:
                return {
                    "error": "4038",
                    "message": "Discount code is for another user",
                }

            # Merchandise check
            if merchandise not in discount_code.merchandises.all():
                return {
                    "error": "4040",
                    "message": "Discount code not valid for this merchandise",
                }

            # Expiration check
            if (
                discount_code.expiration_date
                and discount_code.expiration_date < timezone.now()
            ):
                return {"error": "4041", "message": "Discount code has expired"}

            # Remaining uses check
            if not discount_code.remaining > 0:
                return {
                    "error": "4042",
                    "message": "Discount code has no remaining uses",
                }

            return discount_code

        except DiscountCode.DoesNotExist:
            return {"error": "404", "message": "Discount code not found"}
