from rest_framework import serializers

from ..models import EducationalInstitute, School, University
from ..validators import phone_number_validator


class InstituteInfoSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalInstitute
        fields = ['id', 'name']


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
