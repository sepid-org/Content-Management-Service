from rest_framework import serializers

from apps.attributes.models.performable_actions import Submission, Transition, Buy
from apps.attributes.serializers.base import PerformableActionSerializer


class TransitionSerializer(PerformableActionSerializer):

    class Meta:
        model = Transition
        fields = PerformableActionSerializer.Meta.fields + \
            ['destination_state_id']
        read_only_fields = PerformableActionSerializer.Meta.read_only_fields + []


class BuySerializer(PerformableActionSerializer):

    class Meta:
        model = Buy
        fields = PerformableActionSerializer.Meta.fields + []
        read_only_fields = PerformableActionSerializer.Meta.read_only_fields + []


class SubmissionSerializer(PerformableActionSerializer):

    class Meta:
        model = Submission
        fields = PerformableActionSerializer.Meta.fields + []
        read_only_fields = PerformableActionSerializer.Meta.read_only_fields + []
