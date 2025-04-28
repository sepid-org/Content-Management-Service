from datetime import datetime, timedelta

from django.test import TestCase

from apps.sale.serializers.discount_code import DiscountCodeSerializer


class TestDiscountCodeSerializer(TestCase):
    def test_create_discount_code_non_datetime_expiration_date(self):
        data = {
            "code": "DISCODE50",
            "value": 0.5,
            "expiration_date": "2025-12-31",  # Non-datetime value
            "remaining": 1,
        }
        serializer = DiscountCodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("expiration_date", serializer.errors)

    def test_create_discount_code_with_invalid_value(self):
        data = {
            "code": "DISCODE50",
            "value": 1.5,  # Invalid value (greater than 1)
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 1,
        }

        serializer = DiscountCodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("value", serializer.errors)

    def test_create_discount_code_with_non_numeric_value(self):
        data = {
            "code": "DISCODEABC",
            "value": "abc",  # Non-numeric value
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 1,
        }

        serializer = DiscountCodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("value", serializer.errors)

    def test_create_discount_code_with_empty_code(self):
        data = {
            "code": "",  # Empty code
            "value": 0.5,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 1,
        }

        serializer = DiscountCodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_create_discount_code_with_zero_remaining(self):
        data = {
            "code": "DISCODE0",
            "value": 0.5,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": 0,  # Zero remaining
        }

        serializer = DiscountCodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("remaining", serializer.errors)

    def test_create_discount_code_with_negative_remaining(self):
        data = {
            "code": "DISCODE-1",
            "value": 0.5,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": -1,  # Negative remaining
        }

        serializer = DiscountCodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("remaining", serializer.errors)

    def test_create_discount_code_with_non_numeric_remaining(self):
        data = {
            "code": "DISCODEABC",
            "value": 0.5,
            "expiration_date": datetime.now() + timedelta(days=30),
            "remaining": "abc",  # Non-numeric remaining
        }

        serializer = DiscountCodeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("remaining", serializer.errors)
