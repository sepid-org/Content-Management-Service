import os
import re
import datetime
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from errors.error_codes import serialize_error

from apps.scoring.serializers.cost_serializer import CostSerializer
from apps.scoring.serializers.reward_serializer import RewardSerializer
from apps.fsm.models import Player, Problem, State, Hint, \
    Widget


def add_datetime_to_filename(file):
    filename, extension = os.path.splitext(file.name)
    file.name = f'{filename}_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}{extension}'
    return file


class WidgetSerializer(serializers.ModelSerializer):
    widget_type = serializers.ChoiceField(
        choices=Widget.WidgetTypes.choices, required=True)
    hints = serializers.SerializerMethodField()
    cost = CostSerializer(required=False, allow_null=True)
    reward = RewardSerializer(required=False, allow_null=True)
    

    def get_hints(self, obj):
        from apps.fsm.serializers.paper_serializers import WidgetHintSerializer
        return WidgetHintSerializer(obj.hints if hasattr(obj, 'hints') else [], many=True).data

    def create(self, validated_data):
        if validated_data.get('file'):
            validated_data['file'] = add_datetime_to_filename(
                validated_data['file'])
        return super().create({'creator': self.context.get('user', None), **validated_data})

    def update(self, instance, validated_data):
        if validated_data.get('file'):
            validated_data['file'] = add_datetime_to_filename(
                validated_data['file'])
        return super().update(instance, validated_data)

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
        from apps.fsm.serializers.answer_polymorphic import AnswerPolymorphicSerializer
        representation = super(
            WidgetSerializer, self).to_representation(instance)
        if 'solution' in representation.keys() and instance.paper.is_exam:
            representation.pop('solution')
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
