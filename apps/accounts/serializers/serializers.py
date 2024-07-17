from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError

from errors.error_codes import serialize_error
from manage_content_service.settings.base import DISCOUNT_CODE_LENGTH
from ..models import User, EducationalInstitute, School, University, Merchandise, DiscountCode, Purchase
from ..validators import phone_number_validator, price_validator


class InstituteSerializer(serializers.ModelSerializer):
    principal_name = serializers.CharField(max_length=30, required=False)
    principal_phone = serializers.CharField(
        max_length=15, validators=[phone_number_validator], required=False)
    phone_number = serializers.CharField(max_length=15, validators=[
                                         phone_number_validator], required=False)
    school_type = serializers.ChoiceField(
        choices=School.SchoolType.choices, required=False)
    gender_type = serializers.ChoiceField(
        choices=School.Gender.choices, required=False)

    is_approved = serializers.BooleanField(read_only=True)
    creator = serializers.PrimaryKeyRelatedField(
        many=False, required=False, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(
        many=False, required=False, read_only=True)
    admins = serializers.PrimaryKeyRelatedField(
        many=True, required=False, read_only=True)

    def create(self, validated_data):
        institute_type = validated_data.get('institute_type', None)
        if institute_type == 'School':
            return School.objects.create(**validated_data)
        elif institute_type == 'University':
            return University.objects.create(**validated_data)
        else:
            return super().create(validated_data)

    class Meta:
        model = EducationalInstitute
        fields = ['id', 'name', 'institute_type', 'school_type', 'gender_type', 'address', 'province', 'city', 'postal_code',
                  'phone_number', 'contact_info', 'description', 'principal_name', 'principal_phone', 'is_approved',
                  'created_at', 'owner', 'admins', 'date_added', 'creator']
        read_only_fields = ['id', 'date_added']


class MerchandiseSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(
        required=True, validators=[price_validator])
    discounted_price = serializers.IntegerField(
        required=False, validators=[price_validator])

    class Meta:
        model = Merchandise
        fields = '__all__'
        read_only_fields = ['id']


class DiscountCodeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150, required=False, write_only=True)

    def validate(self, attrs):
        merchandise = attrs.get('merchandise', None)
        creator = self.context.get('user', None)
        username = attrs.get('username', None)
        user = attrs.get('user', None)
        if creator not in merchandise.program_or_fsm.modifiers:
            raise PermissionDenied(serialize_error('4066'))
        if user is None:
            if username is not None:
                attrs['user'] = get_object_or_404(User, username=username)
        return attrs

    def create(self, validated_data):
        validated_data.pop(
            'username') if 'username' in validated_data.keys() else None
        return DiscountCode.objects.create_discount_code(**validated_data)

    def to_representation(self, instance):
        representation = super(DiscountCodeSerializer,
                               self).to_representation(instance)
        representation['first_name'] = instance.user.first_name if instance.user else None
        representation['last_name'] = instance.user.last_name if instance.user else None
        representation['phone_number'] = instance.user.phone_number if instance.user else None
        return representation

    class Meta:
        model = DiscountCode
        fields = ['id', 'code', 'value', 'expiration_date',
                  'remaining', 'user', 'merchandise', 'username']
        read_only_fields = ['id', 'code']


class DiscountCodeValidationSerializer(serializers.ModelSerializer):
    merchandise = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Merchandise.objects.all())
    code = serializers.CharField(
        max_length=DISCOUNT_CODE_LENGTH, required=False)

    def validate(self, attrs):
        code = attrs.get('code', None)
        merchandise = attrs.get('merchandise', None)

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

            if discount_code.merchandise:
                if merchandise != discount_code.merchandise:
                    raise ParseError(serialize_error('4040'))

            if discount_code.expiration_date and discount_code.expiration_date < datetime.now(
                    discount_code.expiration_date.tzinfo):
                raise ParseError(serialize_error('4041'))

            if not discount_code.remaining > 0:
                raise ParseError(serialize_error('4042'))

        return attrs

    class Meta:
        model = DiscountCode
        fields = '__all__'
        read_only_fields = ['id', 'value',
                            'expiration_date', 'remaining', 'user']
        extra_kwargs = {
            'code': {'validators': []}
        }


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['id']
