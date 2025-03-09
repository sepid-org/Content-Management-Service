from django.test import RequestFactory, TestCase

from apps.sale.services.discount_code_service import DiscountCodeService
from apps.sale.views.discount_code_view import DiscountCodeViewSet

from .factories import DiscountCodeFactory


class BaseTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.discount_code = DiscountCodeFactory()


class TestDiscountCodeView(BaseTestCase):
    def test_get_program_discount_codes(self):
        codes = DiscountCodeService.get_program_discount_codes()

        self.assertEqual(len(codes), 1)

    def test_create_discount_code(self):
        request = self.factory.post("/discount-code")
        request.user = self.user

        response = DiscountCodeViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["discount_code"], self.discount_code)
