from rest_framework import serializers

from apps.fsm.models import Player, PlayerStateHistory


class PlayerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStateHistory
        fields = '__all__'
        read_only_fields = ['id']


class PlayerMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', 'current_state']
        read_only_fields = ['id', 'current_state']


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id']
