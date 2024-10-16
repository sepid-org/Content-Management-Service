
from rest_framework import serializers

from apps.fsm.models import Object
from apps.fsm.models.base import Position
from apps.fsm.serializers.position_serializer import PositionSerializer


class ObjectSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField(
        required=False, read_only=True)

    def get_position(self, obj):
        if not hasattr(obj, 'position'):
            Position.objects.create(
                object=obj,
                x=0,  # Default x position
                y=0,  # Default y position
                width=300,  # Default width
                height=200  # Default height
            )
        return PositionSerializer(obj.position).data

    class Meta:
        model = Object
        fields = ['name', 'title', 'created_at', 'updated_at',
                  'attributes', 'order', 'is_private', 'position', 'is_hidden', 'website']
        read_only_fields = ['created_at', 'attributes', 'position']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if hasattr(instance, 'has_entrance_lock'):
            representation['has_entrance_lock'] = instance.has_entrance_lock
        if hasattr(instance, 'has_transition_lock'):
            representation['has_transition_lock'] = instance.has_transition_lock
        return representation
