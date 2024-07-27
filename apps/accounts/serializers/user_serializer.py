from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError

from errors.error_codes import serialize_error
from manage_content_service.settings.base import DISCOUNT_CODE_LENGTH
from proxies.sms_system.settings import SMS_CODE_LENGTH
from ..models import User, VerificationCode, EducationalInstitute, School, University, SchoolStudentship, Studentship, \
    AcademicStudentship, Merchandise, DiscountCode, Purchase
from ..validators import phone_number_validator, grade_validator, price_validator


class PhoneNumberSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        max_length=15, required=True, validators=[phone_number_validator])
    code_type = serializers.CharField(required=True)
    party_display_name = serializers.CharField(required=True)

    class Meta:
        model = VerificationCode
        fields = ['phone_number', 'code_type', 'party_display_name']


class PhoneNumberVerificationCodeSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        max_length=15, required=True, validators=[phone_number_validator])
    code = serializers.CharField(max_length=SMS_CODE_LENGTH, required=True)

    def validate_code(self, code):
        if len(code) < SMS_CODE_LENGTH:
            raise serializers.ValidationError(serialize_error('4002'))
        return code

    def validate(self, attrs):
        code = attrs.get("code", None)
        phone_number = attrs.get("phone_number", None)
        verification_code = VerificationCode.objects.filter(
            phone_number=phone_number, code=code, is_valid=True).first()

        if not verification_code:
            raise ParseError(serialize_error('4003'))

        if datetime.now(verification_code.expiration_date.tzinfo) > verification_code.expiration_date:
            raise ParseError(serialize_error('4005'))

        return attrs

    class Meta:
        model = VerificationCode
        fields = ['phone_number', 'code']


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        validators=[phone_number_validator], required=False)
    password = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(required=False,)

    def create(self, validated_data):

        # set username
        if validated_data.get('username'):
            pass
        elif validated_data.get('phone_number'):
            validated_data['username'] = validated_data.get('phone_number')
        elif validated_data.get('email'):
            validated_data['username'] = validated_data.get('email')
        else:
            raise Exception("insufficient data")

        # set password
        if validated_data.get('password'):
            validated_data['password'] = make_password(
                validated_data.get('password'))
        else:
            validated_data['password'] = make_password(
                validated_data['username'])

        instance = super().create(validated_data)
        SchoolStudentship.objects.create(
            user=instance, studentship_type=Studentship.StudentshipType.School)
        AcademicStudentship.objects.create(
            user=instance, studentship_type=Studentship.StudentshipType.Academic)
        return instance

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            validated_data['password'] = make_password(
                validated_data.get('password'))
            instance.password = validated_data.get('password')
            instance.save()
        instance = super().update(instance, validated_data)
        return instance

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'first_name',
                  'last_name', 'password', 'username', 'email']
        read_only_fields = ['id']


class MentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class StudentshipSerializer(serializers.ModelSerializer):
    university = serializers.PrimaryKeyRelatedField(
        many=False, queryset=University.objects.all(), required=False)
    degree = serializers.ChoiceField(
        choices=AcademicStudentship.Degree.choices, required=False)
    university_major = serializers.CharField(max_length=30, required=False)

    school = serializers.PrimaryKeyRelatedField(
        many=False, queryset=School.objects.all(), required=False)
    grade = serializers.IntegerField(
        required=False, validators=[grade_validator])
    major = serializers.ChoiceField(
        choices=SchoolStudentship.Major.choices, required=False)

    def create(self, validated_data):
        studentship_type = validated_data.get('studentship_type', None)
        if studentship_type == Studentship.StudentshipType.School.value:
            return SchoolStudentship.objects.create(**validated_data)
        elif studentship_type == Studentship.StudentshipType.Academic.value:
            return AcademicStudentship.objects.create(**validated_data)

    def validate(self, attrs):
        studentship_type = attrs.get('studentship_type', None)
        if studentship_type == 'SCHOOL':
            grade = attrs.get('grade', None)
            major = attrs.get('major', None)
            if grade:
                if 9 < grade <= 12:
                    if not major:
                        raise ParseError(serialize_error('4013'))
                elif major:
                    raise ParseError(serialize_error('4014'))
        elif studentship_type == 'ACADEMIC':
            degree = attrs.get('degree', None)
            if not degree:
                raise ParseError(serialize_error('4015'))
        return attrs

    class Meta:
        model = Studentship
        fields = ['id', 'studentship_type', 'school', 'grade',
                  'degree', 'major', 'university', 'university_major']
        read_only_fields = ['id', 'is_document_verified']


class UserProfileSerializer(serializers.ModelSerializer):
    school_studentship = StudentshipSerializer(read_only=True)
    academic_studentship = StudentshipSerializer(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password')
        return representation

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'school_studentship',
                            'academic_studentship', 'username', 'phone_number', 'password']


class UserProfileSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'bio', 'profile_picture']
        read_only_fields = ['id', 'first_name',
                            'last_name', 'bio', 'profile_picture']
