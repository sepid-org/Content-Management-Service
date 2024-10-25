import re
from rest_framework import serializers
from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.fsm.models import Widget


class WidgetSerializer(serializers.ModelSerializer):
    widget_type = serializers.ChoiceField(
        choices=Widget.WidgetTypes.choices, required=True)
    hints = serializers.SerializerMethodField()

    def get_hints(self, obj):
        return [hint.id for hint in obj.hints.all()]

    def create(self, validated_data):
        validated_data['creator'] = self.context.get('user', None)
        return super().create(validated_data)

    def to_representation(self, instance):
        # add object fields to representation
        representation = super().to_representation(instance)
        object_instance = instance.object
        object_serializer = ObjectSerializer()
        representation = {
            **representation,
            **object_serializer.to_representation(object_instance)
        }

        return representation

    class Meta:
        model = Widget
        fields = ['id', 'paper', 'widget_type', 'creator', 'hints']
        read_only_fields = ['id', 'hints']
