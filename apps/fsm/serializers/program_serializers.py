from rest_framework.exceptions import ParseError
from rest_framework import serializers

from apps.fsm.serializers.form.registration_form_serializer import RegistrationFormSerializer
from apps.fsm.serializers.program_contact_info_serializer import ProgramContactInfoSerializer
from apps.fsm.utils.utils import add_admin_to_program
from errors.error_codes import serialize_error
from apps.fsm.models import Program


class ProgramSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Program
        fields = ['id', 'slug', 'cover_image', 'name', 'description', 'participation_type',
                  'is_visible', 'is_active', 'team_size']


class ProgramSerializer(serializers.ModelSerializer):
    menu_first_state_id = serializers.SerializerMethodField()
    program_contact_info = ProgramContactInfoSerializer(
        required=False, allow_null=True)

    def get_menu_first_state_id(self, obj):
        if obj.menu is not None:
            return obj.menu.first_state_id

    def create(self, validated_data):
        registration_form_serializer = RegistrationFormSerializer(
            data=validated_data)
        registration_form_serializer.is_valid(raise_exception=True)
        registration_form = registration_form_serializer.save()

        creator = self.context.get('user', None)
        validated_data['creator'] = creator
        validated_data['registration_form'] = registration_form
        program = super().create(validated_data)

        add_admin_to_program(creator, program)

        program.registration_form = registration_form
        program.save()
        return program

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
        team_size = attrs.get('team_size') or 0
        participation_type = attrs.get(
            'participation_type', Program.ParticipationType.INDIVIDUAL)
        if (team_size > 0 and participation_type != Program.ParticipationType.TEAM) or (
                participation_type == Program.ParticipationType.TEAM and team_size <= 0):
            raise ParseError(serialize_error('4074'))
        return attrs

    class Meta:
        model = Program
        fields = [
            'id',
            'type',
            'participation_type',
            'slug',
            'name',
            'description',
            'cover_image',
            'is_active',
            'is_approved',
            'start_date',
            'end_date',
            'team_size',
            'accessible_after_closure',
            'show_scores',
            'site_help_paper_id',
            'FAQs_paper_id',
            'is_visible',
            'is_public',
            'creator',
            'registration_form',
            'program_contact_info',
            'website',
            'menu',
            'menu_first_state_id',
        ]
        read_only_fields = [
            'id',
            'slug',
            'creator',
            'is_approved',
            'registration_form',
            'program_contact_info',
        ]
