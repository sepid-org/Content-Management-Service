from rest_framework.exceptions import ParseError
from rest_framework import serializers

from apps.fsm.serializers.program_contact_info_serializer import ProgramContactInfoSerializer
from apps.fsm.utils import add_admin_to_program
from errors.error_codes import serialize_error
from apps.fsm.models import Program, RegistrationForm


class ProgramSummarySerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super(ProgramSummarySerializer,
                               self).to_representation(instance)
        representation['initial_participants_count'] = len(instance.initial_participants)
        representation['final_participants_count'] = len(instance.final_participants)
        return representation

    class Meta:
        model = Program
        fields = ['id', 'slug', 'cover_page', 'name', 'description', 'program_type',
                  'is_visible', 'is_active', 'team_size', 'is_free']


class ProgramSerializer(serializers.ModelSerializer):
    program_contact_info = ProgramContactInfoSerializer(required=False)
    is_manager = serializers.SerializerMethodField()

    def get_is_manager(self, obj):
        user = self.context.get('user', None)
        if user in obj.modifiers:
            return True
        return False

    def create(self, validated_data):
        website = validated_data.pop('website')
        registration_form = RegistrationForm.objects.create(
            **{'paper_type': RegistrationForm.PaperType.RegistrationForm})

        creator = self.context.get('user', None)
        program = super(ProgramSerializer, self).create(
            {'creator': creator, 'website': website, 'registration_form': registration_form, **validated_data})

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
        representation['initial_participants_count'] = len(instance.initial_participants)
        representation['final_participants_count'] = len(instance.final_participants)
        representation['has_certificate'] = registration_form.has_certificate
        representation['certificates_ready'] = registration_form.certificates_ready
        representation['registration_since'] = registration_form.since
        representation['registration_till'] = registration_form.till
        representation['audience_type'] = registration_form.audience_type
        return representation

    class Meta:
        model = Program
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'is_approved',
                            'registration_form', 'program_contact_info', 'is_free']
