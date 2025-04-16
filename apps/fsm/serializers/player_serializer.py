from rest_framework import serializers

from apps.fsm.models import Player


class PlayerMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ['id', 'current_state', 'started_at', 'finished_at']


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id']
