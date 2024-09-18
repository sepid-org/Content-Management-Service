
from rest_framework import serializers

from apps.fsm.models import Object


class ObjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Object
        fields = ['title', 'created_at', 'updated_at', 'attributes']
        read_only_fields = ['created_at', 'updated_at', 'attributes']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.has_entrance_lock:
            representation['has_entrance_lock'] = instance.has_entrance_lock
        if instance.has_transition_lock:
            representation['has_transition_lock'] = instance.has_transition_lock
        return representation
