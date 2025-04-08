from datetime import datetime, timedelta

from django.test import RequestFactory, TestCase

from apps.sale.services.discount_code_service import DiscountCodeService
from apps.sale.views.discount_code_view import DiscountCodeViewSet

from .factories import DiscountCodeFactory, MerchandiseFactory


class BaseTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.discount_code = DiscountCodeFactory()


class TestDiscountCodeAPI(BaseTestCase):
    def test_get_program_discount_codes(self):
        codes = DiscountCodeService.get_program_discount_codes()

        self.assertEqual(len(codes), 1)
    
    def test_create_discount_code(self):
        merchandise = MerchandiseFactory()

        data = {
            "code": "TESTCODE",
            "value": 10,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 1,
        }

        DiscountCodeService.create_discount_code(
            data=data, merchandise_ids=[merchandise.id]
        )

        self.assertEqual(DiscountCodeService.get_program_discount_codes(), 2)


class TestDiscountCodeView(BaseTestCase): ...
