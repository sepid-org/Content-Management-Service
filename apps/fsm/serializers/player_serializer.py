from rest_framework import serializers

from apps.fsm.models import Player, PlayerStateHistory
from apps.fsm.serializers.team_serializer import TeamSerializer


class PlayerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStateHistory
        fields = '__all__'
        read_only_fields = ['id']


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id']


class PlayerStateSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = Player
        fields = ['id', 'team', 'current_state']
        read_only_fields = ['id', 'current_state', 'team']
