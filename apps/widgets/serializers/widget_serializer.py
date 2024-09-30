import re
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from apps.fsm.serializers.object_serializer import ObjectSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import Player, Problem, State, Hint, Widget


class WidgetSerializer(serializers.ModelSerializer):
    widget_type = serializers.ChoiceField(
        choices=Widget.WidgetTypes.choices, required=True)
    hints = serializers.SerializerMethodField()

    def get_hints(self, obj):
        from apps.widgets.serializers.widget_hint_serializer import WidgetHintSerializer
        return WidgetHintSerializer(obj.hints if hasattr(obj, 'hints') else [], many=True).data

    def create(self, validated_data):
        validated_data['creator'] = self.context.get('user', None)
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context.get('user', None)
        paper = attrs.get('paper', None)
        if isinstance(paper, State):
            if user not in paper.fsm.mentors.all():
                raise ParseError(serialize_error('4075'))
        elif isinstance(paper, Hint):
            if user not in paper.reference.fsm.mentors.all():
                raise ParseError(serialize_error('4075'))

        return super(WidgetSerializer, self).validate(attrs)

    def to_representation(self, instance):
        # add object fields to representation
        representation = super().to_representation(instance)
        object_instance = instance.object
        object_serializer = ObjectSerializer()
        representation = {
            **representation,
            **object_serializer.to_representation(object_instance)
        }

        if isinstance(instance, Problem):
            user = self.context.get('user', None)

            # TODO: potentially with BUGS!
            url = self.context.get('request').get_full_path(
            ) if self.context.get('request') else ""
            if "/fsm/player/" in url:
                matcher = re.search(r'\d+', url)
                player_id = matcher.group()
                user = Player.objects.filter(id=player_id).first().user
        return representation

    class Meta:
        model = Widget
        fields = ['id', 'paper', 'creator', 'widget_type', 'hints']
        read_only_fields = ['id', 'creator']
