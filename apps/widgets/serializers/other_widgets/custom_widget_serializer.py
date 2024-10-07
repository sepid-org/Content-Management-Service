from apps.widgets.serializers.widget_serializer import WidgetSerializer


class CustomWidgetSerializer(WidgetSerializer):
    class Meta(WidgetSerializer.Meta):
        fields = WidgetSerializer.Meta.fields + []
        read_only_fields = WidgetSerializer.Meta.read_only_fields + []
