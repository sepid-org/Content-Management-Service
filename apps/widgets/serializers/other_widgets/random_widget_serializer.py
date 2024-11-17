from apps.fsm.models.base import Widget
from apps.widgets.models.other_widgets.random import RandomWidget
from apps.widgets.serializers.widget_serializer import WidgetSerializer


class RandomWidgetSerializer(WidgetSerializer):
    class Meta(WidgetSerializer.Meta):
        model = RandomWidget
        fields = WidgetSerializer.Meta.fields + \
            ['box_paper_id', 'unique_widgets_only']
        read_only_fields = WidgetSerializer.Meta.read_only_fields + []

    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.RandomWidget
        return super().create(validated_data)

    def to_representation(self, instance):
        from apps.widgets.serializers.widget_polymorphic_serializer import WidgetPolymorphicSerializer
        user = self.context.get('request').user
        representation = super().to_representation(instance)
        representation['widget'] = WidgetPolymorphicSerializer(
            instance.get_random_widget(user)).data
        return representation
