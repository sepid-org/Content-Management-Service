from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.fsm.models.base import Paper
from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.fsm.serializers.papers.hint_serializer import HintSerializer
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import State


class StateSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['name']
        read_only_fields = ['name']


class StateSerializer(ObjectSerializer):
    hints = HintSerializer(many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(validated_data)

        fsm = validated_data.get('fsm', None)
        if fsm.first_state is None:
            fsm.first_state = instance
            fsm.save()

        paper = Paper.objects.create()
        instance.papers.add(paper)

        return instance

    def validate(self, attrs):
        fsm = attrs.get('fsm', None)
        user = self.context.get('user', None)
        if user not in fsm.mentors.all():
            raise PermissionDenied(serialize_error('4075'))

        return super(StateSerializer, self).validate(attrs)

    class Meta(ObjectSerializer.Meta):
        model = State
        ref_name = 'state'

        fields = ObjectSerializer.Meta.fields + \
            ['id', 'papers', 'template', 'fsm', 'hints', 'show_appbar', 'is_end']
        read_only_fields = ObjectSerializer.Meta.read_only_fields + ['hints']
