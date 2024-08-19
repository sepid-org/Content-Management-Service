from rest_framework import serializers


class ContentSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.has_entrance_lock:
            representation['has_entrance_lock'] = instance.has_entrance_lock
        if instance.has_transition_lock:
            representation['has_transition_lock'] = instance.has_transition_lock
        return representation
