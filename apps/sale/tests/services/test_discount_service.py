from datetime import datetime, timedelta

from django.test import TestCase

from apps.accounts.models import DiscountCode
from apps.core.exceptions import (
    DiscountCodeExpired,
    DiscountCodeInvalidUser,
    DiscountCodeNonUnique,
    MerchandiseNotFound,
)
from apps.sale.services.discount_service import (
    create_discount_code,
    get_program_discount_codes,
)
from apps.sale.tests.factories import (
    DiscountCodeFactory,
    MerchandiseFactory,
    UserFactory,
    UserWebsiteFactory,
)


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.website = UserWebsiteFactory(user=self.user)
        self.discount_code = DiscountCodeFactory(code="TESTCODE")
        self.merchandise = MerchandiseFactory()


class TestDiscountCodeOperations(BaseTestCase):
    def test_get_program_discount_codes(self):
        codes = get_program_discount_codes()

        self.assertEqual(DiscountCode.objects.count(), 1)
        self.assertEqual(codes[0].code, "TESTCODE")

    def test_create_discount_code_without_user(self):
        data = {
            "code": "DISCODE20",
            "value": 0.2,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 3,
        }

        create_discount_code(
            data=data,
            merchandise_ids=[self.merchandise.id],
        )

        discount_code = get_program_discount_codes()

        self.assertEqual(DiscountCode.objects.count(), 2)
        self.assertEqual(discount_code[0].value, 0.2)
        self.assertEqual(discount_code[0].remaining, 3)
        self.assertIn(self.merchandise, discount_code[0].merchandises.all())

    def test_create_discount_code_with_user(self):
        data = {
            "code": "DISCODE50",
            "value": 0.5,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 1,
        }

        create_discount_code(
            data=data,
            merchandise_ids=[self.merchandise.id],
            username=self.user.username,
        )

        discount_code = get_program_discount_codes()

        self.assertEqual(DiscountCode.objects.count(), 2)
        self.assertEqual(discount_code[0].value, 0.5)
        self.assertEqual(discount_code[0].remaining, 1)
        self.assertIn(self.merchandise, discount_code[0].merchandises.all())
        self.assertEqual(self.user, discount_code[0].user)

    def test_create_discount_code_with_invalid_user(self):
        data = {
            "code": "DISCODE50",
            "value": 0.5,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 1,
        }

        with self.assertRaises(DiscountCodeInvalidUser):
            create_discount_code(
                data=data,
                merchandise_ids=[self.merchandise.id],
                username="invalid_user",
            )

    def test_create_discount_code_with_invalid_merchandise(self):
        data = {
            "code": "DISCODE50",
            "value": 0.5,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 1,
        }

        with self.assertRaises(MerchandiseNotFound):
            create_discount_code(
                data=data,
                merchandise_ids=[9999],  # Invalid merchandise ID
                username=self.user.username,
            )

    def test_create_discount_code_with_expired_date(self):
        data = {
            "code": "DISCODE50",
            "value": 0.5,
            "expiration_date": datetime.now() - timedelta(days=1),  # Expired date
            "remaining": 1,
        }

        with self.assertRaises(DiscountCodeExpired):
            create_discount_code(
                data=data,
                merchandise_ids=[self.merchandise.id],
                username=self.user.username,
            )

    def test_create_discount_code_with_non_unique_code(self):
        data = {
            "code": "TESTCODE",  # Non-unique code
            "value": 0.5,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 1,
        }

        with self.assertRaises(DiscountCodeNonUnique):
            create_discount_code(
                data=data,
                merchandise_ids=[self.merchandise.id],
                username=self.user.username,
            )
