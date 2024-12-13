from rest_framework import serializers

from apps.widgets.serializers.widget_polymorphic_serializer import WidgetPolymorphicSerializer
from apps.fsm.models import Paper


class PaperMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Paper
        fields = ['id', 'paper_type']


class PaperSerializer(serializers.ModelSerializer):
    widgets = WidgetPolymorphicSerializer(many=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('widgets'):
            representation['widgets'] = sorted(
                representation['widgets'],
                # Sort by 'order' first, then 'id'
                key=lambda x: (x.get('order', 0), x['id'])
            )
        return representation

    class Meta:
        model = Paper
        fields = ['id', 'widgets', 'paper_type', 'creator']
        read_only_fields = ['id']


class ChangeWidgetOrderSerializer(serializers.Serializer):
    order = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=True)
