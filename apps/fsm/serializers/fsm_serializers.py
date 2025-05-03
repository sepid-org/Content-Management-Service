from apps.fsm.models.fsm import State
from rest_framework.exceptions import ParseError
from rest_framework import serializers

from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from apps.fsm.serializers.papers.state_serializer import StateSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import Program, FSM, Edge, Team, State, Paper


class FSMPublicListSerializer(serializers.ModelSerializer):
    """
    Public listing serializer for FSMs. Includes nested object info and player count.
    """
    object = ObjectSerializer(source='_object', read_only=True)
    players_count = serializers.SerializerMethodField()

    class Meta:
        model = FSM
        fields = [
            'id', 'object', 'name', 'description',
            'cover_image', 'is_active', 'is_visible', 'card_type',
            'players_count'
        ]
        read_only_fields = fields

    def get_players_count(self, obj):
        return obj.players.count()


class FSMSerializer(serializers.ModelSerializer):
    program_slug = serializers.CharField(source='program.slug', read_only=True)
    object_id = serializers.IntegerField(source='_object_id', read_only=True)
    first_state_id = serializers.IntegerField(
        source='first_state.id', read_only=True)

    class Meta:
        model = FSM
        fields = [
            'id', 'object_id', 'program', 'program_slug', 'name',
            'description', 'cover_image', 'is_active', 'is_visible',
            'first_state_id', 'fsm_learning_type', 'fsm_p_type',
            'show_roadmap', 'show_player_performance_on_end', 'duration',
        ]
        read_only_fields = ['id', 'first_state_id']

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
        team_size = validated_data.get('team_size', None)
        program = validated_data.get('program', None)
        fsm_p_type = validated_data.get('fsm_p_type')
        if team_size is None and program and fsm_p_type != FSM.FSMPType.Individual:
            validated_data['team_size'] = program.team_size

        validated_data['creator'] = creator
        return super(FSMSerializer, self).create(validated_data)

    def to_representation(self, instance):
        # add object fields to representation
        representation = super().to_representation(instance)
        object_instance = instance.object
        representation = {
            **ObjectSerializer(object_instance, context=self.context).data,
            **representation,
        }

        return representation


class FSMAllStatesSerializer(serializers.ModelSerializer):
    states = StateSerializer(many=True)

    class Meta:
        model = FSM
        fields = ['id', 'states']


class FSMAllPapersSerializer(serializers.ModelSerializer):
    papers = serializers.SerializerMethodField()

    class Meta:
        model = FSM
        fields = ['papers']

    def get_papers(self, fsm):
        # grab all Papers linked to any State of this FSM, deduped
        qs = Paper.objects.filter(states__fsm=fsm).distinct()
        return PaperSerializer(qs, many=True, context=self.context).data


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
