
from rest_framework import serializers

from apps.fsm.models import Object
from apps.fsm.serializers.position_serializer import PositionSerializer


class ObjectSerializer(serializers.ModelSerializer):
    position = PositionSerializer(required=False)

    class Meta:
        model = Object
        fields = ['id', 'name', 'title', 'created_at', 'updated_at',
                  'attributes', 'order', 'is_private', 'position', 'is_hidden']
        read_only_fields = ['created_at', 'updated_at', 'attributes']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if hasattr(instance, 'widget'):
            representation['widget'] = instance.widget.id
        if hasattr(instance, 'edge'):
            representation['edge'] = instance.edge.id
        if hasattr(instance, 'fsm'):
            representation['fsm'] = instance.fsm.id
        if hasattr(instance, 'paper'):
            representation['paper'] = instance.paper.id

        if hasattr(instance, 'has_entrance_lock'):
            representation['has_entrance_lock'] = instance.has_entrance_lock
        if hasattr(instance, 'has_transition_lock'):
            representation['has_transition_lock'] = instance.has_transition_lock
        return representation
