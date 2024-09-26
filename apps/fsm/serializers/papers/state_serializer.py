from apps.fsm.serializers.fsm_serializers import EdgeSerializer
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.fsm.serializers.papers.hint_serializer import HintSerializer
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import State


class StateSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['name']
        read_only_fields = ['name']


class StateSerializer(PaperSerializer):
    hints = HintSerializer(many=True, read_only=True)
    outward_edges = EdgeSerializer(many=True, read_only=True)
    inward_edges = EdgeSerializer(many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        fsm = validated_data.get('fsm', None)
        instance = super(StateSerializer, self).create(
            {'paper_type': 'State', **validated_data})
        if fsm.first_state is None:
            fsm.first_state = instance
            fsm.save()

        return instance

    def validate(self, attrs):
        fsm = attrs.get('fsm', None)
        user = self.context.get('user', None)
        if user not in fsm.mentors.all():
            raise PermissionDenied(serialize_error('4075'))

        return super(StateSerializer, self).validate(attrs)

    class Meta(PaperSerializer.Meta):
        model = State
        ref_name = 'state'

        fields = PaperSerializer.Meta.get_fields() + \
            ['name', 'fsm', 'hints', 'inward_edges',
                'outward_edges', 'show_appbar', 'is_end']
        read_only_fields = PaperSerializer.Meta.read_only_fields + \
            ['hints', 'inward_edges', 'outward_edges']
