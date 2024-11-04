from apps.fsm.models.fsm import State
from rest_framework.exceptions import ParseError
from rest_framework import serializers
from apps.fsm.models import Player

from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.sale.serializers.merchandise import MerchandiseSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import Program, FSM, Edge, Team


class FSMMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = FSM
        fields = ['id', 'name', 'description', 'cover_page', 'is_active', 'is_visible',
                  'fsm_learning_type', 'fsm_p_type', 'card_type', 'show_roadmap']

    def to_representation(self, instance):
        representation = super(FSMMinimalSerializer,
                               self).to_representation(instance)
        user = self.context.get('user', None)
        representation['players_count'] = len(
            Player.objects.filter(fsm=instance))
        return representation


class FSMSerializer(serializers.ModelSerializer):
    program_slug = serializers.SerializerMethodField()

    def get_program_slug(self, obj):
        return obj.program.slug

    def validate(self, attrs):
        program = attrs.get('program', None)
        team_size = attrs.get('team_size', None)
        merchandise = attrs.get('merchandise', None)
        registration_form = attrs.get('registration_form', None)
        fsm_p_type = attrs.get('fsm_p_type', FSM.FSMPType.Individual)
        creator = self.context.get('user', None)
        if program:
            if merchandise or registration_form:
                raise ParseError(serialize_error('4069'))
            if fsm_p_type == FSM.FSMPType.Team:
                if program.participation_type == Program.ParticipationType.INDIVIDUAL:
                    raise ParseError(serialize_error('4071'))
                if team_size and team_size != program.team_size:
                    raise ParseError(serialize_error('4072'))
            if creator not in program.modifiers:
                raise ParseError(serialize_error('4073'))
        else:
            if fsm_p_type == FSM.FSMPType.Team and team_size is None:
                raise ParseError(serialize_error('4074'))
        return attrs

    def create(self, validated_data):
        creator = self.context.get('user', None)
        merchandise = validated_data.pop('merchandise', None)
        team_size = validated_data.get('team_size', None)
        program = validated_data.get('program', None)
        fsm_p_type = validated_data.get('fsm_p_type')
        if team_size is None and program and fsm_p_type != FSM.FSMPType.Individual:
            validated_data['team_size'] = program.team_size

        instance = super(FSMSerializer, self).create(
            {'creator': creator, **validated_data})

        if merchandise and merchandise.get('name', None) is None:
            merchandise['name'] = validated_data.get('name', 'unnamed_program')
            serializer = MerchandiseSerializer(data=merchandise)
            if serializer.is_valid(raise_exception=True):
                merchandise_instance = serializer.save()
                instance.merchandise = merchandise_instance
                instance.save()
        return instance

    class Meta:
        model = FSM
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'mentors', 'first_state']


class EdgeSerializer(serializers.ModelSerializer):
    tail = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    head = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())

    class Meta:
        model = Edge
        fields = ['id', 'tail', 'head',
                  'is_back_enabled', 'is_visible']


class TeamGetSerializer(serializers.Serializer):
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), required=True)
