from rest_framework import serializers
from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.fsm.models import Widget


class WidgetSerializer(serializers.ModelSerializer):
    widget_type = serializers.ChoiceField(
        choices=Widget.WidgetTypes.choices, required=True)
    hints = serializers.SerializerMethodField()

    def get_hints(self, obj):
        return [hint.id for hint in obj.hints.all()]

    def to_representation(self, instance):
        # add object fields to representation
        representation = super().to_representation(instance)
        object_instance = instance.object
        representation = {
            **representation,
            **ObjectSerializer(object_instance, context=self.context).data
        }

        return representation

    class Meta:
        model = Widget
        fields = ['id', 'paper', 'widget_type', 'creator', 'hints']
        read_only_fields = ['id', 'hints']
