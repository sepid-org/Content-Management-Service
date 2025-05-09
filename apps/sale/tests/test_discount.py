import json

from django.test import RequestFactory, TestCase
from rest_framework import status

from apps.sale.tests.factories import (
    DiscountCodeFactory,
    MerchandiseFactory,
    UserFactory,
)
from apps.sale.views.discount_code_view import DiscountCodeViewSet


class BaseTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory()

        self.user = UserFactory()
        self.discount_code = DiscountCodeFactory(code="TEST123")
        self.merchandise = MerchandiseFactory()


class TestDiscountCodeAPI(BaseTestCase):
    def test_get_discount_codes(self):
        request = self.request.get("/discount_codes/")
        response = DiscountCodeViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)

    def test_create_discount_code(self):
        data = {
            "user": self.user.username,
            "code": self.discount_code.code,
            "value": self.discount_code.value,
        }
        request = self.request.post(
            "/discount_codes/",
            data=json.dumps(data),
            content_type="application/json",
        )
        response = DiscountCodeViewSet.as_view({"post": "create"})(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
