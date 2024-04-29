from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ParseError
from rest_framework import serializers

from apps.accounts.serializers import MerchandiseSerializer
from apps.fsm.serializers.program_contact_info_serializer import ProgramContactInfoSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import Event, RegistrationReceipt


class ProgramSerializer(serializers.ModelSerializer):
    merchandise = MerchandiseSerializer(required=False)
    program_contact_info = ProgramContactInfoSerializer(required=False)
    is_manager = serializers.SerializerMethodField()

    def get_is_manager(self, obj):
        user = self.context.get('user', None)
        if user in obj.modifiers:
            return True
        return False

    def create(self, validated_data):
        merchandise = validated_data.pop('merchandise', None)

        creator = self.context.get('user', None)
        instance = super(ProgramSerializer, self).create(
            {'creator': creator, **validated_data})
        if merchandise and merchandise.get('name', None) is None:
            merchandise['name'] = validated_data.get('name', 'unnamed_event')
            serializer = MerchandiseSerializer(data=merchandise)
            if serializer.is_valid(raise_exception=True):
                merchandise_instance = serializer.save()
                instance.merchandise = merchandise_instance
                instance.save()
        return instance

    def update(self, instance, validated_data):
        program_contact_info = validated_data['program_contact_info']
        del validated_data['program_contact_info']
        program_contact_info_instance = instance.program_contact_info
        if program_contact_info_instance:
            program_contact_info_serializer = ProgramContactInfoSerializer(
                program_contact_info_instance, data=program_contact_info, partial=True)
        else:
            program_contact_info_serializer = ProgramContactInfoSerializer(
                data=program_contact_info)
        program_contact_info_serializer.is_valid()
        program_contact_info_instance = program_contact_info_serializer.save()
        instance = super().update(instance, validated_data)
        instance.program_contact_info = program_contact_info_instance
        instance.save()
        return instance

    def validate(self, attrs):
        team_size = attrs.get('team_size', 0)
        event_type = attrs.get('event_type', Event.EventType.Individual)
        if (team_size > 0 and event_type != Event.EventType.Team) or (
                event_type == Event.EventType.Team and team_size <= 0):
            raise ParseError(serialize_error('4074'))
        creator = self.context.get('user', None)
        holder = attrs.get('holder', None)
        if holder and creator not in holder.admins.all():
            raise ParseError(serialize_error('4031'))
        return attrs

    def to_representation(self, instance):
        representation = super(
            ProgramSerializer, self).to_representation(instance)
        user = self.context.get('request', None).user
        receipt = RegistrationReceipt.objects.filter(user=user, answer_sheet_of=instance.registration_form).last(
        ) if not isinstance(user, AnonymousUser) else None
        representation['participants_count'] = len(instance.participants)
        if instance.registration_form:
            representation['has_certificate'] = instance.registration_form.has_certificate
            representation['certificates_ready'] = instance.registration_form.certificates_ready
            representation['registration_since'] = instance.registration_form.since
            representation['registration_till'] = instance.registration_form.till
            representation['audience_type'] = instance.registration_form.audience_type
        if receipt:
            representation[
                'user_registration_status'] = instance.registration_form.check_time() if instance.registration_form.check_time() != 'ok' else receipt.status
            representation['is_paid'] = receipt.is_paid
            representation['is_user_participating'] = receipt.is_participating
            representation['registration_receipt'] = receipt.id
        else:
            representation['user_registration_status'] = instance.registration_form.get_user_permission_status(
                user) if instance.registration_form else None
            representation['is_paid'] = False
            representation['is_user_participating'] = False
            representation['registration_receipt'] = None
        if receipt and receipt.is_participating and instance.event_type == Event.EventType.Team:
            if receipt.team:
                representation['team'] = receipt.team.id
                if receipt.team.team_head:
                    representation['team_head_name'] = receipt.team.team_head.user.full_name
                    representation['is_team_head'] = receipt.team.team_head.id == receipt.id
            else:
                representation['team'] = 'TeamNotCreatedYet'
                representation['team_head_name'] = None
                representation['is_team_head'] = False

        return representation

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'creator',
                            'is_approved', 'registration_form']
