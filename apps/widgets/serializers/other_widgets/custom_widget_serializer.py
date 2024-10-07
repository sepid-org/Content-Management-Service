from apps.fsm.models.base import Widget
from apps.widgets.models.other_widgets.custom import CustomWidget
from apps.widgets.serializers.widget_serializer import WidgetSerializer


class CustomWidgetSerializer(WidgetSerializer):
    class Meta(WidgetSerializer.Meta):
        model = CustomWidget
        fields = WidgetSerializer.Meta.fields + []
        read_only_fields = WidgetSerializer.Meta.read_only_fields + []

    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.CustomWidget
        return super().create(validated_data)
