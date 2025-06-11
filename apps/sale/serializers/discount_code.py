from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ParseError

from apps.accounts.serializers.user_serializer import UserPublicInfoSerializer
from apps.sale.serializers.merchandise import MerchandiseSerializer
from errors.error_codes import serialize_error
from content_management_service.settings.base import DISCOUNT_CODE_LENGTH
from apps.accounts.models import DiscountCode, Merchandise, User


class DiscountCodeSerializer(serializers.ModelSerializer):
    user = UserPublicInfoSerializer(read_only=True)
    username = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        source='user'  # maps into the .user FK on your model
    )

    merchandises = MerchandiseSerializer(many=True, read_only=True)
    merchandise_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Merchandise.objects.all(),
        source='merchandises'
    )

    max_discount_amount = serializers.IntegerField(
        required=False,
        allow_null=True,
        source='discount_code_limit'
    )

    class Meta:
        model = DiscountCode
        fields = [
            'id', 'code', 'value', 'expiration_date', 'remaining',
            'user', 'username',
            'merchandises', 'merchandise_ids',
            'max_discount_amount',
        ]
        read_only_fields = ['id', 'code', 'user', 'remaining']

    def create(self, validated_data):
        return DiscountCode.objects.create_unique(**validated_data)


class DiscountCodeValidationSerializer(serializers.ModelSerializer):
    max_discount_amount = serializers.IntegerField(
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

            if discount_code.remaining is not None or discount_code.remaining == 0:
                raise ParseError(serialize_error('4042'))

        return attrs

    class Meta:
        model = DiscountCode
        fields = ['id', 'code', 'value', 'expiration_date',
                  'remaining', 'user', 'max_discount_amount']
        read_only_fields = ['id', 'value',
                            'expiration_date', 'remaining', 'user']
        extra_kwargs = {
            'code': {'validators': []}
        }
