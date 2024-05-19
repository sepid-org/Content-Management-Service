from rest_framework import serializers

from apps.fsm.models import Player, PlayerStateHistory
from apps.fsm.serializers.paper_serializers import StateSerializer
from apps.fsm.serializers.team_serializer import TeamSerializer


class PlayerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStateHistory
        fields = '__all__'
        read_only_fields = ['id']


class PlayerSerializer(serializers.ModelSerializer):
    current_state = StateSerializer()
    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['id', 'current_state', 'team']
        read_only_fields = ['id']
