from apps.attributes.models import Condition, Cost, Enabled, Reward
from apps.attributes.serializers.base import IntrinsicAttributeSerializer


class ConditionSerializer(IntrinsicAttributeSerializer):

    class Meta(IntrinsicAttributeSerializer.Meta):
        model = Condition
        fields = IntrinsicAttributeSerializer.Meta.fields + []
        read_only_fields = IntrinsicAttributeSerializer.Meta.read_only_fields + []


class CostSerializer(IntrinsicAttributeSerializer):

    class Meta(IntrinsicAttributeSerializer.Meta):
        model = Cost
        fields = IntrinsicAttributeSerializer.Meta.fields
        read_only_fields = IntrinsicAttributeSerializer.Meta.read_only_fields + []


class RewardSerializer(IntrinsicAttributeSerializer):

    class Meta(IntrinsicAttributeSerializer.Meta):
        model = Reward
        fields = IntrinsicAttributeSerializer.Meta.fields
        read_only_fields = IntrinsicAttributeSerializer.Meta.read_only_fields + []


class EnabledSerializer(IntrinsicAttributeSerializer):

    class Meta(IntrinsicAttributeSerializer.Meta):
        model = Enabled
        fields = IntrinsicAttributeSerializer.Meta.fields
        read_only_fields = IntrinsicAttributeSerializer.Meta.read_only_fields + []
