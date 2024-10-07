from apps.fsm.models.base import Widget
from apps.widgets.models.other_widgets.button import ButtonWidget
from apps.widgets.serializers.widget_serializer import WidgetSerializer


class ButtonWidgetSerializer(WidgetSerializer):
    class Meta(WidgetSerializer.Meta):
        model = ButtonWidget
        fields = WidgetSerializer.Meta.fields + \
            ['label', 'background_image',
                'destination_page_url', 'destination_state_ids']
        read_only_fields = WidgetSerializer.Meta.read_only_fields + []

    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.ButtonWidget
        return super().create(validated_data)
