from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ParseError
from rest_framework import serializers

from apps.accounts.serializers.serializers import MerchandiseSerializer
from apps.fsm.serializers.program_contact_info_serializer import ProgramContactInfoSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import Program, RegistrationForm, RegistrationReceipt


class ProgramSummarySerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super(ProgramSummarySerializer,
                               self).to_representation(instance)
        representation['participants_count'] = len(instance.participants)
        representation['registration_since'] = instance.registration_form.since
        representation['registration_till'] = instance.registration_form.till
        representation['audience_type'] = instance.registration_form.audience_type

        representation['is_free'] = bool(instance.merchandise)
        return representation

    class Meta:
        model = Program
        fields = ['id', 'cover_page', 'name', 'description',
                  'program_type', 'is_visible', 'is_active', 'team_size']


class ProgramSerializer(serializers.ModelSerializer):
    merchandise = MerchandiseSerializer(required=False, read_only=True)
    program_contact_info = ProgramContactInfoSerializer(required=False)
    is_manager = serializers.SerializerMethodField()

    def get_is_manager(self, obj):
        user = self.context.get('user', None)
        if user in obj.modifiers:
            return True
        return False

    def create(self, validated_data):
        merchandise = validated_data.pop('merchandise', None)
        website = validated_data.pop('website')
        registration_form = RegistrationForm.objects.create(
            **{'paper_type': RegistrationForm.PaperType.RegistrationForm})

        creator = self.context.get('user', None)
        instance = super(ProgramSerializer, self).create(
            {'creator': creator, 'website': website, 'registration_form': registration_form, **validated_data})
        instance.admins.add(creator)
        if merchandise and merchandise.get('name', None) is None:
            merchandise['name'] = validated_data.get('name')
            serializer = MerchandiseSerializer(data=merchandise)
            serializer.is_valid(raise_exception=True)
            merchandise_instance = serializer.save()
            instance.merchandise = merchandise_instance
        instance.registration_form = registration_form
        instance.save()
        return instance

    def update(self, instance, validated_data):
        program_contact_info = validated_data.pop('program_contact_info', None)
        program_contact_info_instance = instance.program_contact_info
        instance = super().update(instance, validated_data)
        if program_contact_info:
            if program_contact_info_instance:
                program_contact_info_serializer = ProgramContactInfoSerializer(
                    program_contact_info_instance, data=program_contact_info, partial=True)
            else:
                program_contact_info_serializer = ProgramContactInfoSerializer(
                    data=program_contact_info)
            program_contact_info_serializer.is_valid(raise_exception=True)
            program_contact_info_instance = program_contact_info_serializer.save()
            instance.program_contact_info = program_contact_info_instance
            instance.save()
        return instance

    def validate(self, attrs):
        team_size = attrs.get('team_size', 0)
        program_type = attrs.get(
            'program_type', Program.ProgramType.Individual)
        if (team_size > 0 and program_type != Program.ProgramType.Team) or (
                program_type == Program.ProgramType.Team and team_size <= 0):
            raise ParseError(serialize_error('4074'))
        return attrs

    def to_representation(self, instance):
        representation = super(
            ProgramSerializer, self).to_representation(instance)
        registration_form = instance.registration_form
        representation['participants_count'] = len(instance.participants)
        representation['has_certificate'] = registration_form.has_certificate
        representation['certificates_ready'] = registration_form.certificates_ready
        representation['registration_since'] = registration_form.since
        representation['registration_till'] = registration_form.till
        representation['audience_type'] = registration_form.audience_type
        return representation

    class Meta:
        model = Program
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'merchandise',
                            'is_approved', 'registration_form', 'program_contact_info']
