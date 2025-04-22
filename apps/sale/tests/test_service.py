from datetime import datetime, timedelta

from django.test import TestCase

from apps.accounts.models import DiscountCode
from apps.sale.services.discount_code_service import (
    create_discount_code,
    get_program_discount_codes,
)

from .factories import (
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
        
        print(">> User: ", self.user)
        print(">> User Website: ", self.user.user_websites)
        print(">> Website: ", self.website.user)
        print(">> DiscountCode: ", discount_code)

        self.assertEqual(DiscountCode.objects.count(), 2)
        self.assertEqual(discount_code[0].value, 0.5)
        self.assertEqual(discount_code[0].remaining, 1)
        self.assertIn(self.merchandise, discount_code[0].merchandises.all())
        self.assertEqual(self.user, discount_code[0].user)
