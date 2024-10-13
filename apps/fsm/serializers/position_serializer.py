from rest_framework import serializers
from apps.fsm.models import Position


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ['x', 'y', 'width', 'height']
