from rest_framework import serializers

from apps.attributes.models.performable_actions import Transition
from apps.attributes.serializers.base import PerformableActionSerializer


class TransitionSerializer(PerformableActionSerializer):
    destination_state = serializers.SerializerMethodField()

    class Meta:
        model = Transition
        fields = PerformableActionSerializer.Meta.fields + \
            ['destination_state_id', 'destination_state']
        read_only_fields = PerformableActionSerializer.Meta.read_only_fields + \
            ['destination_state']

    def get_destination_state(self, obj):
        from apps.fsm.models.fsm import State
        try:
            state = State.objects.get(id=obj.destination_state_id)
            return {
                'id': state.id,
                'title': state.title
            }
        except State.DoesNotExist:
            return None
