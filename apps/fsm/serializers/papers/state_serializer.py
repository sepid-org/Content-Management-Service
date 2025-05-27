from django.db import transaction
from rest_framework import serializers

from apps.fsm.models.base import Paper, Position
from apps.fsm.serializers.object_serializer import ObjectSerializer
from apps.fsm.models import State


class StateSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'title']


class StateSerializer(ObjectSerializer):
    papers = serializers.SerializerMethodField()

    def get_papers(self, obj):
        papers = obj.papers.all().order_by('statepaper__order')
        return [paper.id for paper in papers]

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(validated_data)

        fsm = validated_data.get('fsm', None)
        if fsm.first_state is None:
            fsm.first_state = instance
            fsm.save()

        paper = Paper.objects.create()
        instance.papers.add(paper)

        Position.objects.create(
            object=instance,
            x=0,
            y=0,
            width=1600,
            height=900
        )

        return instance

    class Meta(ObjectSerializer.Meta):
        model = State
        ref_name = 'state'

        fields = ObjectSerializer.Meta.fields + \
            ['id', 'papers', 'template', 'fsm', 'show_appbar', 'is_end']
        read_only_fields = ObjectSerializer.Meta.read_only_fields + []
