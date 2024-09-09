from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apps.fsm.models import Position, Widget


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = ['x', 'y', 'width', 'height']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        position_object = instance.object
        for related_object_type in ['edge', 'fsm', 'paper', 'widget']:
            try:
                related_object = getattr(position_object, related_object_type)
                representation[related_object_type] = related_object.id
                break
            except:
                pass
        return representation
