from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apps.fsm.models import WidgetPosition, Widget


class WidgetPositionSerializer(serializers.ModelSerializer):
    paper_id = serializers.SerializerMethodField()

    class Meta:
        model = WidgetPosition
        fields = ['widget', 'paper_id', 'x', 'y', 'width', 'height']

    def get_paper_id(self, obj):
        return obj.widget.paper.id


class WidgetPositionListSerializer(serializers.Serializer):
    positions = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )

    def validate_positions(self, value):
        for position in value:
            if 'widget' not in position:
                raise serializers.ValidationError(
                    "Each position must include a widget id.")
            if not all(key in position for key in ('x', 'y', 'width', 'height')):
                raise serializers.ValidationError(
                    "Each position must include x, y, width, and height.")
        return value

    def create(self, validated_data):
        positions_data = validated_data.pop('positions')
        positions = []
        for position_data in positions_data:
            widget = get_object_or_404(Widget, id=position_data['widget'])
            position, created = WidgetPosition.objects.update_or_create(
                widget=widget,
                defaults={
                    'x': position_data['x'],
                    'y': position_data['y'],
                    'width': position_data['width'],
                    'height': position_data['height']
                }
            )
            positions.append(position)
        return positions
