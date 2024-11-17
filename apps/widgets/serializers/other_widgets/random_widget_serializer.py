from django.shortcuts import get_object_or_404
from apps.fsm.models.base import Widget
from apps.fsm.models.fsm import FSM
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
        from apps.fsm.utils import get_players
        request = self.context.get('request')
        user = request.user
        fsm_id = request.headers.get('FSM')
        fsm = get_object_or_404(FSM, id=fsm_id)
        player = get_players(user, fsm).last()

        representation = super().to_representation(instance)
        representation['widget'] = WidgetPolymorphicSerializer(
            instance.get_random_widget(player)).data
        return representation
