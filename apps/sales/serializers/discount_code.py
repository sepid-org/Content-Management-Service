from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ParseError

from apps.accounts.serializers.user_serializer import UserPublicInfoSerializer
from apps.sales.serializers.merchandise import MerchandiseSerializer
from errors.error_codes import serialize_error
from manage_content_service.settings.base import DISCOUNT_CODE_LENGTH
from apps.accounts.models import DiscountCode


class DiscountCodeSerializer(serializers.ModelSerializer):
    discount_code_limit = serializers.IntegerField(
        required=False, allow_null=True)
    merchandises = MerchandiseSerializer(many=True, required=False)
    user = UserPublicInfoSerializer(required=False, allow_null=True)
    username = serializers.CharField(
        max_length=150, required=False, write_only=True)

    def create(self, validated_data):
        return DiscountCode.objects.create_discount_code(**validated_data)

    class Meta:
        model = DiscountCode
        fields = ['id', 'code', 'value', 'expiration_date', 'remaining',
                  'user', 'merchandises', 'username', 'discount_code_limit']
        read_only_fields = ['id', 'code']


class DiscountCodeValidationSerializer(serializers.ModelSerializer):
    discount_code_limit = serializers.IntegerField(
        required=False, allow_null=True)
    code = serializers.CharField(
        max_length=DISCOUNT_CODE_LENGTH, required=False, allow_null=True)

    def validate(self, attrs):
        code = attrs.get('code', None)
        merchandise = self.context.get('merchandise', None)

        if not merchandise:
            raise ParseError(serialize_error('4039'))
        elif not merchandise.is_active:
            raise ParseError(serialize_error('4043'))

        if code:
            discount_code = get_object_or_404(DiscountCode, code=code)

            if discount_code.user:
                user = self.context.get('user', None)
                if discount_code.user != user:
                    raise NotFound(serialize_error('4038'))

            if merchandise not in discount_code.merchandises.all():
                raise ParseError(serialize_error('4040'))

            if discount_code.expiration_date and discount_code.expiration_date < datetime.now(
                    discount_code.expiration_date.tzinfo):
                raise ParseError(serialize_error('4041'))

            if not discount_code.remaining > 0:
                raise ParseError(serialize_error('4042'))

        return attrs

    class Meta:
        model = DiscountCode
        fields = ['id', 'code', 'value', 'expiration_date',
                  'remaining', 'user', 'discount_code_limit']
        read_only_fields = ['id', 'value',
                            'expiration_date', 'remaining', 'user']
        extra_kwargs = {
            'code': {'validators': []}
        }
